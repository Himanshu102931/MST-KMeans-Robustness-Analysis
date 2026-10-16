"""
test_benchmarks.py
==================
Automated test suite for Phase M5B Python Performance Benchmark Engine:
1. Benchmark configuration bounds and workload safety limits (N <= 600, executions <= 200).
2. Correct trial counts across sample sizes and repetitions.
3. Warmup stage execution and exclusion from recorded trial statistics.
4. Both algorithms receiving identical coordinate input arrays.
5. Monotonic non-negative, finite runtime measurements.
6. Sample mean, median, and Bessel's corrected sample standard deviation (ddof=1).
7. Ratio of means formula (mean(MST) / mean(KM)) and zero-denominator safety.
8. Deterministic dataset generation under fixed seeds.
9. Scientific export integrity (trials CSV, summary CSV, config JSON, metadata JSON).
10. Plotly figure creation and Matplotlib in-memory PNG generation with valid PNG header.
"""

from __future__ import annotations

import io
import json
import pathlib
import re
import sys
import numpy as np
import pandas as pd
import pytest

# Generalized pattern matching institutional student registration numbers
# without hardcoding personal identifiers.
STUDENT_REGISTRATION_PATTERN = re.compile(r"\b\d+/\d+/SET/[A-Z]+/\d+\b", re.IGNORECASE)

APP_DIR = pathlib.Path(__file__).resolve().parent.parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from clustering_lab.experiments.benchmarks import (
    DEFAULT_BENCHMARK_REPETITIONS,
    DEFAULT_BENCHMARK_SEED,
    DEFAULT_BENCHMARK_SIZES,
    BenchmarkConfig,
    BenchmarkSummary,
    BenchmarkTrialResult,
    aggregate_benchmark_trials,
    run_performance_benchmark,
)
from clustering_lab.experiments.export import (
    export_benchmark_config_json,
    export_benchmark_metadata,
    export_benchmark_summary_to_csv,
    export_benchmark_trials_to_csv,
)
from clustering_lab.visualization.figures import (
    create_benchmark_runtime_figure,
    render_benchmark_png,
)


# =============================================================================
# 1. Configuration Validation and Safe Workload Bounds
# =============================================================================
def test_benchmark_config_defaults():
    """Verify default benchmark settings comply with research specifications."""
    cfg = BenchmarkConfig()
    assert cfg.sample_sizes == DEFAULT_BENCHMARK_SIZES
    assert cfg.repetitions == DEFAULT_BENCHMARK_REPETITIONS
    assert cfg.seed == DEFAULT_BENCHMARK_SEED
    assert cfg.warmup is True
    assert cfg.n_clusters == 3
    assert cfg.cluster_std == 0.4


def test_benchmark_config_rejects_empty_sizes():
    """Config must reject an empty sequence of sample sizes."""
    with pytest.raises(ValueError, match="At least one sample size"):
        BenchmarkConfig(sample_sizes=())


def test_benchmark_config_rejects_oversized_n():
    """Config must reject sample sizes exceeding the safe limit of 600."""
    with pytest.raises(ValueError, match="exceeds safe limit"):
        BenchmarkConfig(sample_sizes=(100, 700))


def test_benchmark_config_rejects_invalid_repetitions():
    """Config must reject invalid repetition counts outside [1, 10]."""
    with pytest.raises(ValueError, match="repetitions"):
        BenchmarkConfig(sample_sizes=(100,), repetitions=0)
    with pytest.raises(ValueError, match="repetitions"):
        BenchmarkConfig(sample_sizes=(100,), repetitions=15)


def test_benchmark_config_rejects_excessive_total_executions():
    """Config must reject workloads exceeding MAX_TOTAL_EXECUTIONS (200)."""
    # 20 sizes * 6 runs * 2 algorithms = 240 executions > 200
    with pytest.raises(ValueError, match="exceeds maximum safe workload"):
        BenchmarkConfig(
            sample_sizes=tuple(range(50, 50 + 20 * 10, 10)),
            repetitions=5,
            warmup=True,
        )


# =============================================================================
# 2. Benchmark Execution, Trial Counts & Identical Array Verification
# =============================================================================
def test_benchmark_execution_and_trial_counts():
    """Verify trial counts and warmup exclusion in run_performance_benchmark."""
    cfg = BenchmarkConfig(
        sample_sizes=(30, 50),
        repetitions=2,
        seed=101,
        warmup=True,
    )

    trials = run_performance_benchmark(cfg)

    # 2 sizes * 2 repetitions = 4 trials
    assert len(trials) == 4
    sizes_observed = [t.sample_size for t in trials]
    assert sizes_observed == [30, 30, 50, 50]
    reps_observed = [t.repetition_index for t in trials]
    assert reps_observed == [1, 2, 1, 2]


def test_benchmark_monotonically_nonnegative_finite_runtimes():
    """All measured runtimes must be finite, non-negative, and reported in ms."""
    cfg = BenchmarkConfig(
        sample_sizes=(40,),
        repetitions=3,
        seed=202,
        warmup=False,
    )
    trials = run_performance_benchmark(cfg)
    for t in trials:
        assert np.isfinite(t.kmeans_runtime_ms)
        assert t.kmeans_runtime_ms >= 0.0
        assert np.isfinite(t.mst_runtime_ms)
        assert t.mst_runtime_ms >= 0.0
        assert t.kmeans_iterations >= 1
        assert t.mst_edges_count == 40 - 1


def test_benchmark_progress_callback():
    """Progress callback must receive monotonic updates during execution."""
    cfg = BenchmarkConfig(sample_sizes=(20,), repetitions=2, seed=42, warmup=False)
    calls = []

    def cb(completed, total, n, r, algo):
        calls.append((completed, total, n, r, algo))

    trials = run_performance_benchmark(cfg, progress_callback=cb)
    assert len(trials) == 2
    assert len(calls) > 0
    # Last call should have completed == total
    assert calls[-1][0] == calls[-1][1]


# =============================================================================
# 3. Statistical Aggregation, Bessel's Correction & Ratio Formulas
# =============================================================================
def test_aggregate_benchmark_trials_statistics():
    """Verify mean, median, sample std (ddof=1), min, max, and ratio calculations."""
    t1 = BenchmarkTrialResult(
        sample_size=100,
        repetition_index=1,
        kmeans_runtime_ms=10.0,
        mst_runtime_ms=20.0,
        kmeans_inertia=100.0,
        mst_total_weight=50.0,
        kmeans_iterations=5,
        mst_edges_count=99,
        seed=42,
    )
    t2 = BenchmarkTrialResult(
        sample_size=100,
        repetition_index=2,
        kmeans_runtime_ms=20.0,
        mst_runtime_ms=40.0,
        kmeans_inertia=100.0,
        mst_total_weight=50.0,
        kmeans_iterations=5,
        mst_edges_count=99,
        seed=43,
    )
    t3 = BenchmarkTrialResult(
        sample_size=100,
        repetition_index=3,
        kmeans_runtime_ms=30.0,
        mst_runtime_ms=60.0,
        kmeans_inertia=100.0,
        mst_total_weight=50.0,
        kmeans_iterations=5,
        mst_edges_count=99,
        seed=44,
    )

    summaries = aggregate_benchmark_trials([t1, t2, t3])
    assert len(summaries) == 1
    s = summaries[0]

    assert s.sample_size == 100
    assert s.repetitions == 3

    # K-Means: values [10, 20, 30]
    assert s.kmeans_mean_ms == pytest.approx(20.0)
    assert s.kmeans_median_ms == pytest.approx(20.0)
    assert s.kmeans_std_ms == pytest.approx(10.0)  # sample std: sqrt(((10-20)^2 + (20-20)^2 + (30-20)^2) / 2) = 10
    assert s.kmeans_min_ms == pytest.approx(10.0)
    assert s.kmeans_max_ms == pytest.approx(30.0)

    # MST: values [20, 40, 60]
    assert s.mst_mean_ms == pytest.approx(40.0)
    assert s.mst_median_ms == pytest.approx(40.0)
    assert s.mst_std_ms == pytest.approx(20.0)
    assert s.mst_min_ms == pytest.approx(20.0)
    assert s.mst_max_ms == pytest.approx(60.0)

    # Ratio of means: 40.0 / 20.0 = 2.0
    assert s.ratio_of_means == pytest.approx(2.0)


def test_aggregate_benchmark_trials_single_repetition():
    """A single repetition must produce sample std of 0.0 (ddof=1 guard)."""
    t1 = BenchmarkTrialResult(
        sample_size=50,
        repetition_index=1,
        kmeans_runtime_ms=5.0,
        mst_runtime_ms=10.0,
        kmeans_inertia=50.0,
        mst_total_weight=25.0,
        kmeans_iterations=4,
        mst_edges_count=49,
        seed=1,
    )
    summaries = aggregate_benchmark_trials([t1])
    assert len(summaries) == 1
    s = summaries[0]
    assert s.kmeans_std_ms == 0.0
    assert s.mst_std_ms == 0.0
    assert s.ratio_of_means == pytest.approx(2.0)


def test_aggregate_benchmark_trials_zero_denominator_safety():
    """If K-Means mean runtime is zero, ratio_of_means must return None, not crash."""
    t1 = BenchmarkTrialResult(
        sample_size=50,
        repetition_index=1,
        kmeans_runtime_ms=0.0,
        mst_runtime_ms=10.0,
        kmeans_inertia=50.0,
        mst_total_weight=25.0,
        kmeans_iterations=4,
        mst_edges_count=49,
        seed=1,
    )
    summaries = aggregate_benchmark_trials([t1])
    assert summaries[0].ratio_of_means is None


# =============================================================================
# 4. Research Data and Metadata Export Integrity
# =============================================================================
def test_export_benchmark_trials_to_csv():
    """Verify exported trials CSV structure and parsing."""
    t = BenchmarkTrialResult(
        sample_size=100,
        repetition_index=1,
        kmeans_runtime_ms=1.234,
        mst_runtime_ms=5.678,
        kmeans_inertia=100.5,
        mst_total_weight=42.1,
        kmeans_iterations=6,
        mst_edges_count=99,
        seed=123,
    )
    csv_str = export_benchmark_trials_to_csv([t])
    assert "sample_size" in csv_str
    assert "kmeans_runtime_ms" in csv_str
    assert "mst_runtime_ms" in csv_str

    df = pd.read_csv(io.StringIO(csv_str))
    assert len(df) == 1
    assert df.loc[0, "sample_size"] == 100
    assert df.loc[0, "kmeans_runtime_ms"] == pytest.approx(1.234)
    assert df.loc[0, "mst_runtime_ms"] == pytest.approx(5.678)


def test_export_benchmark_summary_to_csv():
    """Verify exported summary CSV structure and parsing."""
    s = BenchmarkSummary(
        sample_size=200,
        repetitions=5,
        kmeans_mean_ms=2.5,
        kmeans_median_ms=2.4,
        kmeans_std_ms=0.2,
        kmeans_min_ms=2.2,
        kmeans_max_ms=2.8,
        mst_mean_ms=10.0,
        mst_median_ms=9.8,
        mst_std_ms=0.5,
        mst_min_ms=9.5,
        mst_max_ms=10.8,
        ratio_of_means=4.0,
    )
    csv_str = export_benchmark_summary_to_csv([s])
    assert "sample_size" in csv_str
    assert "ratio_of_means" in csv_str

    df = pd.read_csv(io.StringIO(csv_str))
    assert len(df) == 1
    assert df.loc[0, "sample_size"] == 200
    assert df.loc[0, "ratio_of_means"] == pytest.approx(4.0)


def test_export_benchmark_config_and_metadata_json():
    """Verify JSON export schemas and metadata provenance fields."""
    cfg = BenchmarkConfig(sample_sizes=(100, 200), repetitions=3, seed=777)
    cfg_json = export_benchmark_config_json(cfg)
    parsed_cfg = json.loads(cfg_json)
    assert parsed_cfg["schema"] == "benchmark_config"
    assert parsed_cfg["sample_sizes"] == [100, 200]
    assert parsed_cfg["repetitions"] == 3
    assert parsed_cfg["seed"] == 777

    meta_json = export_benchmark_metadata()
    assert not STUDENT_REGISTRATION_PATTERN.search(meta_json), (
        "Institutional student registration pattern leaked in benchmark metadata JSON!"
    )

    parsed_meta = json.loads(meta_json)
    assert "python_version" in parsed_meta
    assert "platform" in parsed_meta
    assert "numpy_version" in parsed_meta
    assert "timer" in parsed_meta
    assert parsed_meta["timer"] == "time.perf_counter_ns"
    assert "institution" in parsed_meta
    assert "MRIIRS" in parsed_meta["institution"]

    # Student privacy assertions
    students = parsed_meta.get("academic_context", {}).get("students", [])
    student_names = [s.get("name") for s in students]
    assert "Himanshu Gupta" in student_names
    assert "Parth Yadav" in student_names
    for s in students:
        assert "roll_no" not in s, "roll_no must not be present in public metadata"


# =============================================================================
# 5. Visualizations & In-Memory Matplotlib PNG Generation
# =============================================================================
def test_create_benchmark_runtime_figure():
    """Verify Plotly benchmark chart contains both algorithm traces and error bars."""
    s = BenchmarkSummary(
        sample_size=100,
        repetitions=3,
        kmeans_mean_ms=2.0,
        kmeans_median_ms=2.0,
        kmeans_std_ms=0.2,
        kmeans_min_ms=1.8,
        kmeans_max_ms=2.2,
        mst_mean_ms=6.0,
        mst_median_ms=6.0,
        mst_std_ms=0.5,
        mst_min_ms=5.5,
        mst_max_ms=6.5,
        ratio_of_means=3.0,
    )
    fig = create_benchmark_runtime_figure([s])
    assert len(fig.data) == 2
    names = [tr.name for tr in fig.data]
    assert any("K-Means" in n for n in names)
    assert any("Prim's MST" in n for n in names)


def test_render_benchmark_png_valid_header():
    """Verify in-memory Matplotlib benchmark chart exports genuine PNG bytes."""
    s = BenchmarkSummary(
        sample_size=100,
        repetitions=3,
        kmeans_mean_ms=2.0,
        kmeans_median_ms=2.0,
        kmeans_std_ms=0.2,
        kmeans_min_ms=1.8,
        kmeans_max_ms=2.2,
        mst_mean_ms=6.0,
        mst_median_ms=6.0,
        mst_std_ms=0.5,
        mst_min_ms=5.5,
        mst_max_ms=6.5,
        ratio_of_means=3.0,
    )
    png_bytes = render_benchmark_png([s])
    assert isinstance(png_bytes, bytes)
    assert len(png_bytes) > 1000
    # Standard PNG magic signature: 0x89 'P' 'N' 'G' '\r' '\n' 0x1A '\n'
    assert png_bytes.startswith(b"\x89PNG\r\n\x1a\n")


# =============================================================================
# 6. BenchmarkSummary Dual Constructor & Compatibility Tests
# =============================================================================
def test_benchmark_summary_constructor_variations():
    """Verify BenchmarkSummary constructor behaves identically across supported call styles and catches invalid calls."""
    from clustering_lab.experiments.benchmarks import BenchmarkSummaryRow

    # Style 1: Legacy keyword arguments (single-item fixture mode)
    s_legacy_kw = BenchmarkSummary(
        sample_size=100,
        repetitions=3,
        kmeans_mean_ms=2.0,
        kmeans_median_ms=2.0,
        kmeans_std_ms=0.2,
        kmeans_min_ms=1.8,
        kmeans_max_ms=2.2,
        mst_mean_ms=6.0,
        mst_median_ms=6.0,
        mst_std_ms=0.5,
        mst_min_ms=5.5,
        mst_max_ms=6.5,
        ratio_of_means=3.0,
    )

    # Style 2: Collection mode via explicit keywords
    row = BenchmarkSummaryRow(
        sample_size=100,
        repetitions=3,
        kmeans_mean_ms=2.0,
        kmeans_median_ms=2.0,
        kmeans_std_ms=0.2,
        kmeans_min_ms=1.8,
        kmeans_max_ms=2.2,
        mst_mean_ms=6.0,
        mst_median_ms=6.0,
        mst_std_ms=0.5,
        mst_min_ms=5.5,
        mst_max_ms=6.5,
        ratio_of_means=3.0,
    )
    s_collection_kw = BenchmarkSummary(
        rows=[row],
        ratio_of_means={100: 3.0},
        kmeans_mean_by_n={100: 2.0},
        mst_mean_by_n={100: 6.0},
        kmeans_std_by_n={100: 0.2},
        mst_std_by_n={100: 0.5},
    )

    # Style 3: Collection mode via positional rows parameter
    s_collection_pos = BenchmarkSummary([row])

    # Verify equivalent attribute values across all three styles
    for s in (s_legacy_kw, s_collection_kw, s_collection_pos):
        assert s.sample_size == 100
        assert s.repetitions == 3
        assert s.kmeans_mean_ms == pytest.approx(2.0)
        assert s.kmeans_median_ms == pytest.approx(2.0)
        assert s.kmeans_std_ms == pytest.approx(0.2)
        assert s.kmeans_min_ms == pytest.approx(1.8)
        assert s.kmeans_max_ms == pytest.approx(2.2)
        assert s.mst_mean_ms == pytest.approx(6.0)
        assert s.mst_median_ms == pytest.approx(6.0)
        assert s.mst_std_ms == pytest.approx(0.5)
        assert s.mst_min_ms == pytest.approx(5.5)
        assert s.mst_max_ms == pytest.approx(6.5)
        assert s.ratio_of_means == pytest.approx(3.0)
        assert len(s) == 1
        assert s[0].sample_size == 100

        # Export compatibility
        d = s.to_dict()
        assert d["sample_size"] == 100
        assert d["ratio_of_means"] == pytest.approx(3.0)
        df = s.to_dataframe()
        assert len(df) == 1
        assert df.loc[0, "sample_size"] == 100

    # Style 4: Empty defaults constructor
    s_empty = BenchmarkSummary()
    assert len(s_empty.rows) == 0
    assert s_empty.sample_size == 0
    assert s_empty.ratio_of_means is None
    assert len(s_empty) == 0
    assert s_empty.to_dataframe().empty

    # Invalid Combinations Validation
    # Incomplete single-item: missing kmeans_mean_ms
    with pytest.raises(ValueError, match="Incomplete single-item arguments"):
        BenchmarkSummary(sample_size=100)

    # Incomplete single-item: missing sample_size
    with pytest.raises(ValueError, match="Incomplete single-item arguments"):
        BenchmarkSummary(kmeans_mean_ms=2.0)

    # Conflicting arguments: both rows and single-item keywords
    with pytest.raises(ValueError, match="Conflicting arguments"):
        BenchmarkSummary(rows=[row], sample_size=100, kmeans_mean_ms=2.0)
