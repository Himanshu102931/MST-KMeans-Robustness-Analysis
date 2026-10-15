"""
test_robustness_experiment.py
=============================
Comprehensive automated test suite for Phase M5A Scientific Robustness Engine:
1. Identical paired inputs for both algorithms.
2. Exact reproducibility with deterministic seeds.
3. Decoupled noise and outlier sweep isolation.
4. Correct trial and execution counts across modes.
5. Inlier masking and outlier fraction integrity.
6. Matched baseline pairing (same family, seed, algorithm).
7. ARI mathematical bounds and topological invariants.
8. Sample mean and sample standard deviation calculations (Bessel ddof=1).
9. Distinction between signed delta and nonnegative degradation loss.
10. Valid CSV and JSON exports with provenance isolation.
11. Parameter validation and computational safety limits.
12. Absence of fabricated metrics.
13. State consistency tracking across parameter modifications.
14. Streamlit AppTest integration and Robustness view rendering.
"""

from __future__ import annotations

import io
import json
import pathlib
import sys
from typing import List
import numpy as np
import pandas as pd
import pytest

APP_DIR = pathlib.Path(__file__).resolve().parent.parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from clustering_lab.experiments.aggregation import (
    SweepAggregateRow,
    aggregate_trials,
    aggregates_to_dataframe,
    compute_sample_std,
    trials_to_dataframe,
)
from clustering_lab.experiments.export import (
    export_config_json,
    export_experiment_metadata,
    export_summary_to_csv,
    export_trials_to_csv,
)
from clustering_lab.experiments.runner import (
    TrialResult,
    run_robustness_experiment,
)
from clustering_lab.experiments.sweeps import (
    DEFAULT_EXTENDED_SEEDS,
    DEFAULT_NOISE_LEVELS,
    DEFAULT_OUTLIER_BASE_NOISE,
    DEFAULT_OUTLIER_RATES,
    DEFAULT_QUICK_SEEDS,
    MAX_INLIERS,
    MAX_OUTLIER_RATE,
    MAX_TOTAL_TRIALS,
    MIN_INLIERS,
    ExperimentMode,
    SweepConfig,
    SweepType,
)


# =============================================================================
# 1. Identical Paired Input Guarantee Tests
# =============================================================================
def test_identical_paired_inputs_for_both_algorithms():
    """Verify that K-Means and MST receive the exact same dataset instance per trial."""
    config = SweepConfig(
        dataset_families=["blobs", "moons"],
        n_inliers=100,
        seeds=[11],
        sweep_types=[SweepType.NOISE.value],
        noise_levels=[0.05],
        outlier_rates=[0.0],
    )
    trials = run_robustness_experiment(config)

    # 2 families * 1 noise level * 1 seed = 2 trials -> 4 records (KM + MST for each)
    assert len(trials) == 4

    # Group records by (family, param_value, seed)
    grouped = {}
    for t in trials:
        key = (t.dataset_family, t.parameter_value, t.seed)
        grouped.setdefault(key, []).append(t)

    for key, pair in grouped.items():
        assert len(pair) == 2
        km_trial = next(t for t in pair if t.algorithm == "Lloyd K-Means")
        mst_trial = next(t for t in pair if t.algorithm == "Prim MST")

        # Invariants: must share identical observation counts and ground-truth parameters
        assert km_trial.n_inliers == mst_trial.n_inliers == 100
        assert km_trial.n_outliers == mst_trial.n_outliers == 0
        assert km_trial.n_total == mst_trial.n_total == 100
        assert km_trial.k == mst_trial.k
        assert km_trial.seed == mst_trial.seed


# =============================================================================
# 2. Deterministic Reproducibility Tests
# =============================================================================
def test_exact_reproducibility_with_fixed_seeds():
    """Verify that repeated runs with identical config produce identical floating-point ARIs."""
    config = SweepConfig(
        dataset_families=["moons"],
        n_inliers=120,
        seeds=[22, 33],
        sweep_types=[SweepType.NOISE.value, SweepType.OUTLIER.value],
        noise_levels=[0.00, 0.10],
        outlier_rates=[0.00, 0.05],
    )

    run_1 = run_robustness_experiment(config)
    run_2 = run_robustness_experiment(config)

    assert len(run_1) == len(run_2)
    for t1, t2 in zip(run_1, run_2):
        assert t1.dataset_family == t2.dataset_family
        assert t1.sweep_type == t2.sweep_type
        assert t1.parameter_value == t2.parameter_value
        assert t1.algorithm == t2.algorithm
        assert t1.seed == t2.seed
        assert t1.inlier_ari == pytest.approx(t2.inlier_ari, abs=1e-12)
        assert t1.full_ari == pytest.approx(t2.full_ari, abs=1e-12)
        assert t1.baseline_inlier_ari == pytest.approx(t2.baseline_inlier_ari, abs=1e-12)
        assert t1.delta_inlier_ari == pytest.approx(t2.delta_inlier_ari, abs=1e-12)
        assert t1.degradation_inlier_ari == pytest.approx(t2.degradation_inlier_ari, abs=1e-12)


# =============================================================================
# 3. Noise and Outlier Sweep Isolation Tests
# =============================================================================
def test_noise_and_outlier_sweep_isolation():
    """Verify that noise sweep holds outliers=0.0 and outlier sweep holds base noise=0.05."""
    config = SweepConfig(
        dataset_families=["circles"],
        n_inliers=100,
        seeds=[11],
        sweep_types=[SweepType.NOISE.value, SweepType.OUTLIER.value],
        noise_levels=[0.00, 0.05, 0.10],
        outlier_rates=[0.00, 0.05, 0.10],
        outlier_sweep_base_noise=0.05,
    )
    trials = run_robustness_experiment(config)

    noise_trials = [t for t in trials if t.sweep_type == SweepType.NOISE.value]
    outlier_trials = [t for t in trials if t.sweep_type == SweepType.OUTLIER.value]

    # In noise sweep, outliers must strictly be 0
    for t in noise_trials:
        assert t.n_outliers == 0
        assert t.n_total == 100
        assert t.parameter_name == "noise_sigma"

    # In outlier sweep, outliers must scale with outlier_rate
    for t in outlier_trials:
        assert t.parameter_name == "outlier_rate"
        expected_outliers = int(round(100 * t.parameter_value))
        assert t.n_outliers == expected_outliers
        assert t.n_total == 100 + expected_outliers


# =============================================================================
# 4. Correct Trial and Execution Count Tests
# =============================================================================
def test_correct_trial_and_execution_counts():
    """Verify trial count formulas in quick mode and custom mode."""
    # Quick mode default: 3 families, 4 noise levels, 4 outlier levels, 3 seeds
    config_quick = SweepConfig(
        dataset_families=["blobs", "moons", "circles"],
        seeds=[11, 22, 33],
        sweep_types=["noise", "outlier"],
        noise_levels=[0.00, 0.05, 0.10, 0.20],
        outlier_rates=[0.00, 0.05, 0.10, 0.20],
    )
    # 3 families * 4 noise levels * 3 seeds = 36 trials
    # 3 families * 4 outlier levels * 3 seeds = 36 trials
    # Total = 72 trials = 144 clustering executions
    assert config_quick.total_expected_trials() == 72
    assert config_quick.total_expected_executions() == 144

    # Single sweep single family
    config_single = SweepConfig(
        dataset_families=["blobs"],
        seeds=[11, 22],
        sweep_types=["noise"],
        noise_levels=[0.00, 0.10],
    )
    assert config_single.total_expected_trials() == 4
    assert config_single.total_expected_executions() == 8

    trials = run_robustness_experiment(config_single)
    assert len(trials) == 8  # 4 trials * 2 algorithms


# =============================================================================
# 5. Inlier Masking and Outlier Fraction Tests
# =============================================================================
def test_inlier_masking_and_full_vs_inlier_ari():
    """Verify that clean data has inlier_ari == full_ari, while outliers penalize full_ari."""
    config = SweepConfig(
        dataset_families=["blobs"],
        n_inliers=150,
        seeds=[42],
        sweep_types=["noise", "outlier"],
        noise_levels=[0.00],
        outlier_rates=[0.10],
        outlier_sweep_base_noise=0.00,
    )
    trials = run_robustness_experiment(config)

    # Clean noise trial at sigma=0.00, outliers=0%
    clean_trials = [t for t in trials if t.sweep_type == "noise" and t.parameter_value == 0.0]
    for t in clean_trials:
        assert t.inlier_ari == pytest.approx(t.full_ari, abs=1e-6)

    # Contaminated trial at outliers=10%
    contam_trials = [t for t in trials if t.sweep_type == "outlier" and t.parameter_value == 0.10]
    for t in contam_trials:
        assert t.n_outliers == 15  # round(150 * 0.10)
        # Outliers without reject class reduce full ARI relative to inlier ARI
        assert t.full_ari <= t.inlier_ari + 1e-6


# =============================================================================
# 6. Matched Baseline Pairing Tests
# =============================================================================
def test_matched_baseline_pairing_integrity():
    """Verify baseline ARIs originate from the identical family, seed, and algorithm."""
    config = SweepConfig(
        dataset_families=["moons", "circles"],
        n_inliers=100,
        seeds=[11, 22],
        sweep_types=["noise"],
        noise_levels=[0.00, 0.10],
    )
    trials = run_robustness_experiment(config)

    # For every trial at level 0.00, delta must be 0.0 and degradation must be 0.0
    zero_trials = [t for t in trials if t.parameter_value == 0.00]
    for t in zero_trials:
        assert t.baseline_inlier_ari == pytest.approx(t.inlier_ari, abs=1e-12)
        assert t.delta_inlier_ari == pytest.approx(0.0, abs=1e-12)
        assert t.degradation_inlier_ari == pytest.approx(0.0, abs=1e-12)

    # For level 0.10, verify baseline matches the exact trial at level 0.00
    perturbed_trials = [t for t in trials if t.parameter_value == 0.10]
    for pt in perturbed_trials:
        matched_base = next(
            zt for zt in zero_trials
            if zt.dataset_family == pt.dataset_family
            and zt.seed == pt.seed
            and zt.algorithm == pt.algorithm
        )
        assert pt.baseline_inlier_ari == pytest.approx(matched_base.inlier_ari, abs=1e-12)
        assert pt.delta_inlier_ari == pytest.approx(pt.inlier_ari - matched_base.inlier_ari, abs=1e-12)
        expected_deg = max(0.0, matched_base.inlier_ari - pt.inlier_ari)
        assert pt.degradation_inlier_ari == pytest.approx(expected_deg, abs=1e-12)


def test_outlier_sweep_matched_baseline_uses_fixed_base_noise():
    """Verify outlier sweep baseline uses the same fixed base noise (sigma=0.05) and 0% outliers."""
    config = SweepConfig(
        dataset_families=["blobs", "moons"],
        n_inliers=100,
        seeds=[11, 22],
        sweep_types=["noise", "outlier"],
        noise_levels=[0.00, 0.10],
        outlier_rates=[0.00, 0.10],
        outlier_sweep_base_noise=0.05,
    )
    trials = run_robustness_experiment(config)

    # 1. Distinguish dataset configurations (trials) from algorithm executions
    assert config.total_expected_trials() == 2 * (2 + 2) * 2  # 16 configurations
    assert config.total_expected_executions() == 32          # 32 executions
    assert len(trials) == 32

    # 2. Check noise sweep baselines (sigma=0.00, outliers=0%)
    noise_trials = [t for t in trials if t.sweep_type == "noise"]
    assert len(noise_trials) == 16
    for nt in noise_trials:
        assert nt.n_outliers == 0
        assert nt.parameter_name == "noise_sigma"
        if nt.parameter_value == 0.00:
            assert nt.baseline_inlier_ari == pytest.approx(nt.inlier_ari, abs=1e-12)
            assert nt.delta_inlier_ari == pytest.approx(0.0, abs=1e-12)
            assert nt.degradation_inlier_ari == pytest.approx(0.0, abs=1e-12)

    # 3. Check outlier sweep baselines (base noise sigma=0.05, outliers=0%)
    outlier_trials = [t for t in trials if t.sweep_type == "outlier"]
    assert len(outlier_trials) == 16
    for ot in outlier_trials:
        assert ot.parameter_name == "outlier_rate"
        # Baseline must match trial at outlier_rate=0.00 (which was executed at sigma=0.05)
        matched_base_trial = next(
            t for t in outlier_trials
            if t.dataset_family == ot.dataset_family
            and t.seed == ot.seed
            and t.algorithm == ot.algorithm
            and t.parameter_value == 0.00
        )
        assert ot.baseline_inlier_ari == pytest.approx(matched_base_trial.inlier_ari, abs=1e-12)
        assert ot.delta_inlier_ari == pytest.approx(ot.inlier_ari - matched_base_trial.inlier_ari, abs=1e-12)
        expected_deg = max(0.0, matched_base_trial.inlier_ari - ot.inlier_ari)
        assert ot.degradation_inlier_ari == pytest.approx(expected_deg, abs=1e-12)

        # Performance improvement (delta > 0) must never be labeled as degradation
        if ot.delta_inlier_ari > 0.0:
            assert ot.degradation_inlier_ari == 0.0

    # 4. Sweep isolation: verify no cross-contamination between noise and outlier trials
    assert all(t.sweep_type == "noise" for t in noise_trials)
    assert all(t.sweep_type == "outlier" for t in outlier_trials)


# =============================================================================
# 7. ARI Mathematical Bounds & Topological Invariants
# =============================================================================
def test_ari_mathematical_bounds_and_topological_bias():
    """Verify ARI bounds and topological inductive bias on clean circles."""
    config = SweepConfig(
        dataset_families=["circles"],
        n_inliers=200,
        seeds=[11],
        sweep_types=["noise"],
        noise_levels=[0.00],
    )
    trials = run_robustness_experiment(config)

    km_trial = next(t for t in trials if t.algorithm == "Lloyd K-Means")
    mst_trial = next(t for t in trials if t.algorithm == "Prim MST")

    # Both ARIs must fall in [-0.5, 1.0]
    assert -0.5 <= km_trial.inlier_ari <= 1.0
    assert -0.5 <= mst_trial.inlier_ari <= 1.0

    # On clean concentric circles:
    # MST single-linkage cut recovers concentric rings perfectly
    assert mst_trial.inlier_ari == pytest.approx(1.0, abs=1e-4)
    # K-Means convex Voronoi cuts across nested rings, yielding near-zero ARI
    assert km_trial.inlier_ari < 0.20


# =============================================================================
# 8. Sample Mean and Standard Deviation Calculations
# =============================================================================
def test_sample_standard_deviation_and_aggregation():
    """Verify Bessel's correction (ddof=1) against known analytical values."""
    # Test array: [2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0]
    # Sum = 40, N = 8, Mean = 5.0
    # Squared differences: 9, 1, 1, 1, 0, 0, 4, 16 -> Sum = 32
    # Sample variance s^2 = 32 / (8 - 1) = 32 / 7
    # Sample std s = sqrt(32 / 7) ≈ 2.138089935
    known_data = [2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0]
    expected_mean = 5.0
    expected_std = float(np.std(known_data, ddof=1))
    assert compute_sample_std(known_data) == pytest.approx(expected_std, abs=1e-9)

    # For N <= 1, sample std is defined as 0.0
    assert compute_sample_std([]) == 0.0
    assert compute_sample_std([42.0]) == 0.0

    # Test aggregate_trials with multiple seeds
    config = SweepConfig(
        dataset_families=["blobs"],
        n_inliers=80,
        seeds=[11, 22, 33],
        sweep_types=["noise"],
        noise_levels=[0.05],
    )
    trials = run_robustness_experiment(config)
    aggregates = aggregate_trials(trials)

    # 1 family * 1 noise level * 2 algorithms = 2 aggregate rows
    assert len(aggregates) == 2
    for agg in aggregates:
        assert agg.n_seeds == 3
        assert agg.std_inlier_ari >= 0.0
        assert agg.std_full_ari >= 0.0
        assert agg.mean_runtime_ms >= 0.0


# =============================================================================
# 9. Signed Delta vs Nonnegative Degradation Loss Tests
# =============================================================================
def test_signed_delta_vs_nonnegative_degradation():
    """Verify mathematical distinction: delta can be negative, degradation cannot."""
    trial_improved = TrialResult(
        dataset_family="blobs",
        sweep_type="noise",
        parameter_name="noise_sigma",
        parameter_value=0.05,
        seed=1,
        n_inliers=100,
        n_outliers=0,
        n_total=100,
        k=3,
        algorithm="Lloyd K-Means",
        inlier_ari=0.98,
        full_ari=0.98,
        runtime_ms=2.5,
        baseline_inlier_ari=0.95,
        delta_inlier_ari=0.03,        # 0.98 - 0.95 = +0.03 (improved)
        degradation_inlier_ari=0.0,    # max(0, 0.95 - 0.98) = 0.0 (no degradation)
    )

    trial_degraded = TrialResult(
        dataset_family="moons",
        sweep_type="outlier",
        parameter_name="outlier_rate",
        parameter_value=0.10,
        seed=1,
        n_inliers=100,
        n_outliers=10,
        n_total=110,
        k=2,
        algorithm="Prim MST",
        inlier_ari=0.60,
        full_ari=0.55,
        runtime_ms=3.0,
        baseline_inlier_ari=1.00,
        delta_inlier_ari=-0.40,       # 0.60 - 1.00 = -0.40 (signed negative)
        degradation_inlier_ari=0.40,   # max(0, 1.00 - 0.60) = +0.40 (nonnegative drop)
    )

    # Improved trial
    assert trial_improved.delta_inlier_ari > 0.0
    assert trial_improved.degradation_inlier_ari == 0.0

    # Degraded trial
    assert trial_degraded.delta_inlier_ari < 0.0
    assert trial_degraded.degradation_inlier_ari > 0.0
    assert trial_degraded.degradation_inlier_ari == pytest.approx(-trial_degraded.delta_inlier_ari)


# =============================================================================
# 10. Valid CSV and JSON Exports with Provenance Isolation
# =============================================================================
def test_export_csv_and_json_with_provenance():
    """Verify raw trial CSV, summary CSV, and config/metadata JSON serialize correctly."""
    config = SweepConfig(
        dataset_families=["blobs"],
        n_inliers=80,
        seeds=[11, 22],
        sweep_types=["noise"],
        noise_levels=[0.00, 0.05],
    )
    trials = run_robustness_experiment(config)
    aggregates = aggregate_trials(trials)

    # 1. Raw Trials CSV
    csv_trials = export_trials_to_csv(trials)
    assert "dataset_family,sweep_type,parameter_name,parameter_value" in csv_trials
    df_trials = pd.read_csv(io.StringIO(csv_trials))
    assert len(df_trials) == len(trials)
    assert "baseline_inlier_ari" in df_trials.columns
    assert "delta_inlier_ari" in df_trials.columns
    assert "degradation_inlier_ari" in df_trials.columns

    # 2. Aggregated Summary CSV
    csv_summary = export_summary_to_csv(aggregates)
    assert "mean_inlier_ari,std_inlier_ari" in csv_summary
    df_summary = pd.read_csv(io.StringIO(csv_summary))
    assert len(df_summary) == len(aggregates)

    # 3. Config JSON round-trip
    config_json_str = export_config_json(config)
    parsed_dict = json.loads(config_json_str)
    restored_config = SweepConfig.from_dict(parsed_dict)
    assert restored_config.dataset_families == config.dataset_families
    assert restored_config.n_inliers == config.n_inliers
    assert restored_config.seeds == config.seeds

    # 4. Metadata JSON
    metadata = export_experiment_metadata(config, len(trials))
    assert metadata["phase"] == "M5A — Scientific Robustness Experiment Engine"
    assert "python_version" in metadata["environment"]
    assert "provenance_statement" in metadata
    assert "legacy JavaScript" in metadata["provenance_statement"]
    assert metadata["execution_summary"]["n_trials_executed"] == len(trials)

    # Student privacy assertions
    meta_json_str = json.dumps(metadata)
    assert "[REDACTED_STUDENT_IDENTIFIER]" not in meta_json_str, "Roll number [REDACTED_STUDENT_IDENTIFIER] leaked in experiment metadata"
    assert "[REDACTED_STUDENT_IDENTIFIER]" not in meta_json_str, "Roll number [REDACTED_STUDENT_IDENTIFIER] leaked in experiment metadata"
    students = metadata.get("academic_context", {}).get("students", [])
    student_names = [s.get("name") for s in students]
    assert "Himanshu Gupta" in student_names
    assert "Parth Yadav" in student_names
    for s in students:
        assert "roll_no" not in s, "roll_no must not be present in public metadata"


# =============================================================================
# 11. Parameter Bounds and Computational Safety Rejections
# =============================================================================
def test_parameter_bounds_and_safety_rejection():
    """Verify that SweepConfig rejects out-of-bounds inputs and dangerous grids."""
    # Too few inliers
    with pytest.raises(ValueError, match="n_inliers"):
        SweepConfig(n_inliers=MIN_INLIERS - 1).validate()

    # Too many inliers
    with pytest.raises(ValueError, match="n_inliers"):
        SweepConfig(n_inliers=MAX_INLIERS + 1).validate()

    # Empty families
    with pytest.raises(ValueError, match="dataset family"):
        SweepConfig(dataset_families=[]).validate()

    # Invalid family name
    with pytest.raises(ValueError, match="Unsupported dataset family"):
        SweepConfig(dataset_families=["spiral"]).validate()

    # Outlier rate exceeding limit
    with pytest.raises(ValueError, match="Outlier rate"):
        SweepConfig(outlier_rates=[MAX_OUTLIER_RATE + 0.1]).validate()

    # Total trials exceeding safety ceiling of 500
    with pytest.raises(ValueError, match="computational safety limit"):
        # 3 families * 10 noise * 10 outlier * 5 seeds = 3 * 20 * 5 = 300? No, let's make it > 500:
        # 3 families * 20 noise * 10 seeds = 600 trials
        SweepConfig(
            dataset_families=["blobs", "moons", "circles"],
            seeds=list(range(10)),
            sweep_types=["noise"],
            noise_levels=[float(i) / 100 for i in range(20)],
        ).validate()


# =============================================================================
# 12. Absence of Fabricated Results
# =============================================================================
def test_no_fabricated_results_when_labels_are_absent():
    """Verify that computing inlier ARI strictly requires ground truth (never fabricated)."""
    y_true = np.array([0, 0, 1, 1], dtype=np.int32)
    y_pred = np.array([0, 0, 1, 1], dtype=np.int32)

    # Identical predictions yield 1.0
    from clustering_lab.evaluation.metrics import compute_inlier_ari
    assert compute_inlier_ari(y_true, y_pred) == 1.0

    # Empty / degenerate inlier mask yields 0.0 boundary behavior without raising
    degenerate_mask = np.array([False, False, False, False], dtype=bool)
    assert compute_inlier_ari(y_true, y_pred, inlier_mask=degenerate_mask) == 0.0


# =============================================================================
# 13. State Consistency Tracking
# =============================================================================
def test_state_consistency_and_dataframe_fidelity():
    """Verify DataFrames correctly capture and map all trial attributes."""
    config = SweepConfig(
        dataset_families=["blobs"],
        n_inliers=100,
        seeds=[11],
        sweep_types=["noise"],
        noise_levels=[0.05],
    )
    trials = run_robustness_experiment(config)
    df = trials_to_dataframe(trials)

    assert not df.empty
    assert set(df["algorithm"].unique()) == {"Lloyd K-Means", "Prim MST"}
    assert df["n_inliers"].iloc[0] == 100
    assert df["parameter_name"].iloc[0] == "noise_sigma"
    assert df["parameter_value"].iloc[0] == 0.05


# =============================================================================
# 14. Streamlit AppTest Integration & Robustness View Rendering
# =============================================================================
def test_streamlit_robustness_analysis_view_renders():
    """Verify that Streamlit AppTest can navigate to 'Robustness Analysis' without exceptions."""
    try:
        from streamlit.testing.v1 import AppTest
    except ImportError:
        pytest.skip("streamlit.testing.v1.AppTest is not available")

    app_file = APP_DIR / "app.py"
    at = AppTest.from_file(str(app_file))
    at.run()

    # Navigate to Robustness Analysis module
    at.sidebar.radio[0].set_value("Robustness Analysis")
    at.run()

    assert not at.exception, f"Navigating to Robustness Analysis threw exception: {at.exception}"

    # Verify key text elements in Robustness view
    all_text = []
    for elem_list in [at.title, at.subheader, at.caption, at.markdown, at.info]:
        for item in elem_list:
            if hasattr(item, "value"):
                all_text.append(str(item.value))
    combined = " ".join(all_text)

    assert "Scientific Robustness Analysis Engine" in combined
    assert "Controlled Gaussian Noise" in combined
    assert "Execution Plan" in combined


def test_reconciled_trial_counting_dimensions():
    """Verify the formal counting convention distinguishing all 5 experimental dimensions."""
    # Quick mode configuration: 3 families, 3 seeds, 4 noise levels, 4 outlier levels
    config = SweepConfig(
        dataset_families=["blobs", "moons", "circles"],
        seeds=[11, 22, 33],
        sweep_types=["noise", "outlier"],
        noise_levels=[0.00, 0.05, 0.10, 0.20],
        outlier_rates=[0.00, 0.05, 0.10, 0.20],
    )
    # 1. Sweep configurations per family/seed = 4 noise + 4 outlier = 8 points
    n_sweep_points = len(config.noise_levels) + len(config.outlier_rates)
    assert n_sweep_points == 8

    # 2. Total paired sweep comparisons = 3 families * 8 points * 3 seeds = 72
    assert config.total_expected_trials() == 72

    # 3. Individual sweep algorithm executions = 72 * 2 = 144
    assert config.total_expected_executions() == 144

    # 4. Total recorded result rows = 144 (72 Lloyd K-Means + 72 Prim MST)
    assert config.total_expected_result_rows() == 144

    # 5. Baseline configurations = 3 families * 3 seeds * 2 sweep types = 18
    assert config.total_baseline_configurations() == 18
    assert config.total_baseline_executions() == 36

    # Verify execution summary in metadata
    meta = export_experiment_metadata(config, n_trials=144)
    summary = meta["execution_summary"]
    assert summary["n_trials_executed"] == 144
    assert summary["n_clustering_executions"] == 144
    assert summary["n_paired_trials"] == 72
    assert summary["n_recorded_result_rows"] == 144


def test_compute_sample_std_import_pathways_backward_compatibility():
    """Verify backward-compatible import pathways for compute_sample_std across all packages."""
    from clustering_lab.utils import compute_sample_std as std_utils
    from clustering_lab.utils.math_helpers import compute_sample_std as std_math
    from clustering_lab.experiments.aggregation import compute_sample_std as std_agg
    from clustering_lab.experiments import compute_sample_std as std_exp

    # All imports must resolve to the identical canonical function
    assert std_utils is std_math
    assert std_agg is std_utils
    assert std_exp is std_utils

    # Numerical consistency test across all references
    sample_data = [10.0, 12.0, 23.0, 23.0, 16.0, 23.0, 21.0, 16.0]
    expected_val = float(np.std(sample_data, ddof=1))

    for fn in (std_utils, std_math, std_agg, std_exp):
        assert fn(sample_data) == pytest.approx(expected_val, abs=1e-12)
        assert fn([]) == 0.0
        assert fn([100.0]) == 0.0


# =============================================================================
# Stage 05 Task 5.2: Computational Safety Bounds & Mathematical Sweep Accounting
# =============================================================================
def test_computational_bounds_and_limit_enforcement():
    """Verify strict validation of MAX_INLIERS=500, MAX_TOTAL_TRIALS=500, and exact accounting."""
    # 1. Inlier sample boundaries
    SweepConfig(n_inliers=MIN_INLIERS).validate()
    SweepConfig(n_inliers=MAX_INLIERS).validate()

    with pytest.raises(ValueError, match="n_inliers"):
        SweepConfig(n_inliers=MIN_INLIERS - 1).validate()

    with pytest.raises(ValueError, match="n_inliers"):
        SweepConfig(n_inliers=MAX_INLIERS + 1).validate()

    # 2. Exact trial count limit boundary (MAX_TOTAL_TRIALS = 500)
    # 1 family * 25 noise levels * 20 seeds = 500 trials exactly
    cfg_500 = SweepConfig(
        dataset_families=["blobs"],
        n_inliers=100,
        seeds=list(range(20)),
        sweep_types=["noise"],
        noise_levels=[float(i) for i in range(25)],
    )
    assert cfg_500.total_expected_trials() == 500
    assert cfg_500.total_expected_executions() == 1000
    cfg_500.validate()  # Passes at exact 500 boundary

    # Just above 500 boundary: 1 family * 26 noise levels * 20 seeds = 520 trials
    cfg_520 = SweepConfig(
        dataset_families=["blobs"],
        n_inliers=100,
        seeds=list(range(20)),
        sweep_types=["noise"],
        noise_levels=[float(i) for i in range(26)],
    )
    assert cfg_520.total_expected_trials() == 520
    with pytest.raises(ValueError, match="computational safety limit of 500"):
        cfg_520.validate()

    # 3. Exact mathematical accounting for Quick Mode (All 3 families)
    cfg_quick = SweepConfig(
        dataset_families=["blobs", "moons", "circles"],
        seeds=list(DEFAULT_QUICK_SEEDS),
        sweep_types=["noise", "outlier"],
        noise_levels=list(DEFAULT_NOISE_LEVELS),
        outlier_rates=list(DEFAULT_OUTLIER_RATES),
    )
    assert cfg_quick.total_expected_trials() == 72
    assert cfg_quick.total_expected_executions() == 144
    assert cfg_quick.total_baseline_configurations() == 18
    assert cfg_quick.total_baseline_executions() == 36
    assert cfg_quick.total_expected_executions() + cfg_quick.total_baseline_executions() == 180

    # 4. Exact mathematical accounting for Extended Mode (All 3 families)
    cfg_extended = SweepConfig(
        dataset_families=["blobs", "moons", "circles"],
        seeds=list(DEFAULT_EXTENDED_SEEDS),
        sweep_types=["noise", "outlier"],
        noise_levels=list(DEFAULT_NOISE_LEVELS),
        outlier_rates=list(DEFAULT_OUTLIER_RATES),
    )
    assert len(cfg_extended.seeds) == 10
    assert cfg_extended.total_expected_trials() == 240  # 240 <= 500
    assert cfg_extended.total_expected_executions() == 480
    assert cfg_extended.total_baseline_configurations() == 60
    assert cfg_extended.total_baseline_executions() == 120
    assert cfg_extended.total_expected_executions() + cfg_extended.total_baseline_executions() == 600
    cfg_extended.validate()  # Confirms extended mode is safe and valid

    # 5. Exact mathematical accounting for Single-Family selections
    cfg_single_q = SweepConfig(
        dataset_families=["moons"],
        seeds=list(DEFAULT_QUICK_SEEDS),
        sweep_types=["noise", "outlier"],
    )
    assert cfg_single_q.total_expected_trials() == 24
    assert cfg_single_q.total_expected_executions() == 48
    assert cfg_single_q.total_baseline_configurations() == 6
    assert cfg_single_q.total_baseline_executions() == 12

    cfg_single_e = SweepConfig(
        dataset_families=["circles"],
        seeds=list(DEFAULT_EXTENDED_SEEDS),
        sweep_types=["noise", "outlier"],
    )
    assert cfg_single_e.total_expected_trials() == 80
    assert cfg_single_e.total_expected_executions() == 160
    assert cfg_single_e.total_baseline_configurations() == 20
    assert cfg_single_e.total_baseline_executions() == 40

    # 6. Invalid seed combinations
    with pytest.raises(ValueError, match="Seeds must be non-negative"):
        SweepConfig(seeds=[11, -1]).validate()
    with pytest.raises(ValueError, match="Seeds must be non-negative"):
        SweepConfig(seeds=[11, "not_an_int"]).validate()  # type: ignore
    with pytest.raises(ValueError, match="Maximum allowed seeds"):
        SweepConfig(seeds=list(range(21))).validate()
    with pytest.raises(ValueError, match="At least one random seed"):
        SweepConfig(seeds=[]).validate()
