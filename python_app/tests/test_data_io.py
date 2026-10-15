"""
test_data_io.py
===============
Test suite for CSV dataset importing and versioned JSON configuration serialization.

Covers:
- Loading CSV files with numerical and categorical labels.
- Loading unlabeled CSV files with ARI availability flags.
- Column indexing (string headers and integer column positions).
- Safe CSV parsing across bytes, StringIO, and string sources.
- Error rejection: empty inputs, missing columns, duplicate headers, NaNs, non-numerics, size limits.
- Row alignment preservation between features and labels.
- ExperimentConfig serialization and round-trip fidelity.
- Instantiation of Dataset from ExperimentConfig across all families.
- Schema version checks and boundary value validation.
"""

import io
import pathlib
import sys
import numpy as np
import pytest

# Ensure python_app root is on sys.path
APP_DIR = pathlib.Path(__file__).resolve().parent.parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from clustering_lab.data.config import (
    SCHEMA_VERSION,
    ExperimentConfig,
    create_dataset_from_config,
)
from clustering_lab.data.csv_loader import MAX_CSV_BYTES, load_dataset_from_csv
from clustering_lab.data.dataset import Dataset


# ---------------------------------------------------------------------------
# CSV Loader Tests
# ---------------------------------------------------------------------------

def test_load_csv_with_integer_labels():
    """Verify loading CSV with two feature columns and integer ground-truth labels."""
    csv_text = (
        "feat_x,feat_y,target\n"
        "1.0,2.0,0\n"
        "3.0,4.0,0\n"
        "10.0,11.0,1\n"
        "12.0,13.0,1\n"
    )

    dataset = load_dataset_from_csv(
        source=csv_text,
        feature_cols=("feat_x", "feat_y"),
        label_col="target",
        dataset_name="test_int_labels",
    )

    assert isinstance(dataset, Dataset)
    assert dataset.dataset_family == "csv"
    assert dataset.X.shape == (4, 2)
    assert np.allclose(dataset.X[0], [1.0, 2.0])
    assert dataset.labels is not None
    assert np.array_equal(dataset.labels, [0, 0, 1, 1])
    assert dataset.metadata["has_ground_truth"] is True
    assert dataset.metadata["ari_available"] is True


def test_load_csv_with_categorical_labels():
    """Verify categorical string labels are deterministically encoded into integer IDs."""
    csv_text = (
        "x,y,species\n"
        "0.5,1.2,versicolor\n"
        "0.4,1.0,setosa\n"
        "5.1,6.0,virginica\n"
        "0.6,1.1,setosa\n"
    )

    dataset = load_dataset_from_csv(
        source=csv_text,
        feature_cols=["x", "y"],
        label_col="species",
    )

    assert dataset.labels is not None
    assert dataset.labels.shape == (4,)
    # Sorted unique: setosa -> 0, versicolor -> 1, virginica -> 2
    # Row 0: versicolor (1), Row 1: setosa (0), Row 2: virginica (2), Row 3: setosa (0)
    assert list(dataset.labels) == [1, 0, 2, 0]
    assert "label_encoding" in dataset.metadata
    assert dataset.metadata["label_encoding"]["setosa"] == 0
    assert dataset.metadata["label_encoding"]["versicolor"] == 1
    assert dataset.metadata["label_encoding"]["virginica"] == 2


def test_load_csv_without_labels():
    """Verify unlabeled CSV loads with labels=None and ari_available=False."""
    csv_text = (
        "dim1,dim2,ignored_comment\n"
        "1.5,2.5,alpha\n"
        "3.5,4.5,beta\n"
        "5.5,6.5,gamma\n"
    )

    dataset = load_dataset_from_csv(
        source=csv_text,
        feature_cols=("dim1", "dim2"),
        label_col=None,
    )

    assert dataset.labels is None
    assert dataset.metadata["has_ground_truth"] is False
    assert dataset.metadata["ari_available"] is False
    assert dataset.X.shape == (3, 2)
    assert np.all(dataset.inlier_mask)


def test_load_csv_by_integer_column_indices():
    """Verify column selection by 0-based integer positions."""
    csv_text = "id,f1,extra,f2\n1,0.1,foo,0.2\n2,0.3,bar,0.4\n"
    dataset = load_dataset_from_csv(
        source=csv_text,
        feature_cols=(1, 3),  # f1 is col 1, f2 is col 3
    )
    assert dataset.X.shape == (2, 2)
    assert np.allclose(dataset.X[0], [0.1, 0.2])


def test_load_csv_from_bytes_and_stringio():
    """Verify loading from bytes and StringIO objects."""
    csv_bytes = b"a,b\n1.0,2.0\n3.0,4.0\n"
    d_bytes = load_dataset_from_csv(csv_bytes, feature_cols=("a", "b"))
    assert d_bytes.X.shape == (2, 2)

    sio = io.StringIO("a,b\n1.0,2.0\n3.0,4.0\n")
    d_sio = load_dataset_from_csv(sio, feature_cols=("a", "b"))
    assert d_sio.X.shape == (2, 2)


def test_csv_validation_errors():
    """Verify error handling on invalid, malformed, or hostile CSV inputs."""
    # Empty CSV
    with pytest.raises(ValueError, match="empty"):
        load_dataset_from_csv("", feature_cols=("x", "y"))

    # Missing column
    with pytest.raises(KeyError, match="not found"):
        load_dataset_from_csv("x,y\n1,2\n", feature_cols=("x", "nonexistent"))

    # Duplicate column headers
    with pytest.raises(ValueError, match="duplicate"):
        load_dataset_from_csv("x,x\n1,2\n", feature_cols=("x", "x"))

    # Same column for both features
    with pytest.raises(ValueError, match="distinct"):
        load_dataset_from_csv("x,y\n1,2\n", feature_cols=("x", "x"))

    # Non-numeric features
    with pytest.raises(TypeError, match="non-numerical"):
        load_dataset_from_csv("x,y\n1,foo\n2,bar\n", feature_cols=("x", "y"))

    # Non-finite values (NaN)
    with pytest.raises(ValueError, match="non-finite"):
        load_dataset_from_csv("x,y\n1,2\n3,nan\n", feature_cols=("x", "y"))

    # Missing values in label column
    with pytest.raises(ValueError, match="missing"):
        load_dataset_from_csv("x,y,lbl\n1,2,0\n3,4,\n", feature_cols=("x", "y"), label_col="lbl")


# ---------------------------------------------------------------------------
# Configuration JSON Tests
# ---------------------------------------------------------------------------

def test_experiment_config_roundtrip():
    """Verify JSON serialization and deserialization preserves all parameters."""
    cfg = ExperimentConfig(
        dataset_family="blobs",
        n_samples=250,
        n_clusters=4,
        seed=101,
        noise=0.12,
        outlier_rate=0.08,
        dataset_params={"cluster_std": 0.35, "radius": 4.0},
    )

    json_str = cfg.to_json()
    cfg_loaded = ExperimentConfig.from_json(json_str)

    assert cfg_loaded == cfg
    assert cfg_loaded.dataset_family == "blobs"
    assert cfg_loaded.n_samples == 250
    assert cfg_loaded.n_clusters == 4
    assert cfg_loaded.seed == 101
    assert cfg_loaded.noise == 0.12
    assert cfg_loaded.outlier_rate == 0.08
    assert cfg_loaded.dataset_params == {"cluster_std": 0.35, "radius": 4.0}
    assert cfg_loaded.schema_version == SCHEMA_VERSION


def test_create_dataset_from_config():
    """Verify generating datasets from configuration objects across all families."""
    for family in ["blobs", "moons", "circles"]:
        cfg = ExperimentConfig(
            dataset_family=family,
            n_samples=100,
            n_clusters=3 if family == "blobs" else 2,
            seed=42,
            noise=0.05,
            outlier_rate=0.1,
        )
        dataset = create_dataset_from_config(cfg)

        assert isinstance(dataset, Dataset)
        assert dataset.dataset_family == family
        assert dataset.n_inliers == 100
        assert dataset.n_outliers == 10
        assert dataset.n_samples == 110


def test_experiment_config_validation_rules():
    """Verify strict validation and rejection of out-of-range or malformed configs."""
    # Unsupported major schema version
    with pytest.raises(ValueError, match="schema_version"):
        ExperimentConfig(dataset_family="blobs", schema_version="2.0.0")

    # Unknown family
    with pytest.raises(ValueError, match="Unknown dataset_family"):
        ExperimentConfig(dataset_family="spirals")

    # Moons with n_clusters != 2
    with pytest.raises(ValueError, match="n_clusters=2"):
        ExperimentConfig(dataset_family="moons", n_clusters=3)

    # Circles with n_clusters != 2
    with pytest.raises(ValueError, match="n_clusters=2"):
        ExperimentConfig(dataset_family="circles", n_clusters=4)

    # Out of range samples
    with pytest.raises(ValueError, match="n_samples"):
        ExperimentConfig(dataset_family="blobs", n_samples=5)
    with pytest.raises(ValueError, match="n_samples"):
        ExperimentConfig(dataset_family="blobs", n_samples=10000)

    # Negative seed or noise
    with pytest.raises(ValueError, match="seed"):
        ExperimentConfig(dataset_family="blobs", seed=-1)
    with pytest.raises(ValueError, match="noise"):
        ExperimentConfig(dataset_family="blobs", noise=-0.5)

    # Outlier rate > 0.5
    with pytest.raises(ValueError, match="outlier_rate"):
        ExperimentConfig(dataset_family="blobs", outlier_rate=0.6)

    # Malformed JSON
    with pytest.raises(ValueError, match="Malformed"):
        ExperimentConfig.from_json("{not valid json}")


# =============================================================================
# Stage 05 Task 5.3: Comprehensive CSV Import Regression Tests
# =============================================================================

def test_csv_loader_comprehensive_edge_cases():
    """Verify CSV loader handles headers/headerless, whitespace trimming, indices, and size limits."""
    # 1. Headerless CSV (has_header=False) with integer column positions
    csv_no_header = (
        "1.0,2.0,0\n"
        "3.0,4.0,1\n"
        "5.0,6.0,1\n"
    )
    ds_no_header = load_dataset_from_csv(
        source=csv_no_header,
        feature_cols=(0, 1),
        label_col=2,
        has_header=False,
    )
    assert ds_no_header.X.shape == (3, 2)
    assert np.allclose(ds_no_header.X[0], [1.0, 2.0])
    assert ds_no_header.labels is not None
    assert np.array_equal(ds_no_header.labels, [0, 1, 1])

    # 2. Whitespace-padded column headers trimmed automatically
    csv_padded_headers = (
        "   coord_x   ,   coord_y   ,   cluster_id   \n"
        "10.0, 20.0, alpha\n"
        "30.0, 40.0, beta\n"
    )
    ds_padded = load_dataset_from_csv(
        source=csv_padded_headers,
        feature_cols=("coord_x", "coord_y"),
        label_col="cluster_id",
    )
    assert ds_padded.X.shape == (2, 2)
    assert np.allclose(ds_padded.X[0], [10.0, 20.0])
    assert ds_padded.labels is not None
    assert list(ds_padded.labels) == [0, 1]

    # Also test whitespace in the argument tuple itself
    ds_padded_args = load_dataset_from_csv(
        source=csv_padded_headers,
        feature_cols=(" coord_x ", " coord_y "),
        label_col=" cluster_id ",
    )
    assert ds_padded_args.X.shape == (2, 2)

    # 3. Non-contiguous integer column indices
    csv_non_contiguous = (
        "id,val1,skip1,val2,skip2,grp\n"
        "100,1.5,foo,2.5,bar,0\n"
        "200,3.5,baz,4.5,qux,1\n"
    )
    ds_non_contig = load_dataset_from_csv(
        source=csv_non_contiguous,
        feature_cols=(1, 3),
        label_col=5,
    )
    assert ds_non_contig.X.shape == (2, 2)
    assert np.allclose(ds_non_contig.X[0], [1.5, 2.5])
    assert np.allclose(ds_non_contig.X[1], [3.5, 4.5])
    assert list(ds_non_contig.labels) == [0, 1]

    # 4. Quoted numeric text conversion
    csv_numeric_text = (
        '"feat_a","feat_b","target"\n'
        '"10.5","20.5","0"\n'
        '"30.5","40.5","1"\n'
    )
    ds_num_text = load_dataset_from_csv(
        source=csv_numeric_text,
        feature_cols=("feat_a", "feat_b"),
        label_col="target",
    )
    assert ds_num_text.X.shape == (2, 2)
    assert np.allclose(ds_num_text.X[0], [10.5, 20.5])

    # 5. Oversized byte stream exceeding MAX_CSV_BYTES (5 MB)
    oversized_bytes = b"x,y\n" + b"1.0,2.0\n" * ((MAX_CSV_BYTES // 8) + 100)
    assert len(oversized_bytes) > MAX_CSV_BYTES
    with pytest.raises(ValueError, match="exceeds safety limit"):
        load_dataset_from_csv(oversized_bytes, feature_cols=("x", "y"))

    # 6. Completely empty bytes and whitespace-only strings
    with pytest.raises(ValueError, match="empty"):
        load_dataset_from_csv(b"", feature_cols=("x", "y"))
    with pytest.raises(ValueError, match="empty"):
        load_dataset_from_csv("   \n   \n", feature_cols=("x", "y"))


# =============================================================================
# Stage 05 Task 5.4: Configuration Round-Trip and Preset Restoration Tests
# =============================================================================

def test_all_presets_json_roundtrip_fidelity():
    """Verify versioned JSON round-trip fidelity across Blobs, Moons, and Circles presets."""
    # 1. Blobs Preset
    cfg_blobs = ExperimentConfig(
        dataset_family="blobs",
        n_samples=300,
        n_clusters=3,
        seed=42,
        noise=0.05,
        outlier_rate=0.05,
        dataset_params={"cluster_std": 0.4, "radius": 3.5},
    )
    json_blobs = cfg_blobs.to_json()
    restored_blobs = ExperimentConfig.from_json(json_blobs)
    assert restored_blobs == cfg_blobs
    ds_b1 = create_dataset_from_config(cfg_blobs)
    ds_b2 = create_dataset_from_config(restored_blobs)
    assert np.array_equal(ds_b1.X, ds_b2.X)
    assert np.array_equal(ds_b1.labels, ds_b2.labels)

    # 2. Moons Preset
    cfg_moons = ExperimentConfig(
        dataset_family="moons",
        n_samples=250,
        n_clusters=2,
        seed=123,
        noise=0.08,
        outlier_rate=0.04,
    )
    json_moons = cfg_moons.to_json()
    restored_moons = ExperimentConfig.from_json(json_moons)
    assert restored_moons == cfg_moons
    ds_m1 = create_dataset_from_config(cfg_moons)
    ds_m2 = create_dataset_from_config(restored_moons)
    assert np.array_equal(ds_m1.X, ds_m2.X)
    assert np.array_equal(ds_m1.labels, ds_m2.labels)

    # 3. Circles Preset
    cfg_circles = ExperimentConfig(
        dataset_family="circles",
        n_samples=200,
        n_clusters=2,
        seed=77,
        noise=0.04,
        outlier_rate=0.02,
        dataset_params={"factor": 0.5},
    )
    json_circles = cfg_circles.to_json()
    restored_circles = ExperimentConfig.from_json(json_circles)
    assert restored_circles == cfg_circles
    ds_c1 = create_dataset_from_config(cfg_circles)
    ds_c2 = create_dataset_from_config(restored_circles)
    assert np.array_equal(ds_c1.X, ds_c2.X)
    assert np.array_equal(ds_c1.labels, ds_c2.labels)


def test_benchmark_and_sweep_config_roundtrips():
    """Verify JSON round-trip fidelity for BenchmarkConfig and SweepConfig presets."""
    import json
    from clustering_lab.experiments.benchmarks import BenchmarkConfig
    from clustering_lab.experiments.sweeps import SweepConfig
    from clustering_lab.experiments.export import export_benchmark_config_json, export_config_json

    # 1. BenchmarkConfig Round-Trip
    bm_cfg = BenchmarkConfig(
        sample_sizes=[100, 200, 400],
        n_repetitions=5,
        seed=42,
        blobs_k=3,
        blobs_cluster_std=0.4,
        blobs_radius=3.5,
        warmup=True,
    )
    bm_json = export_benchmark_config_json(bm_cfg)
    bm_restored = BenchmarkConfig.from_dict(json.loads(bm_json))
    assert bm_restored.sample_sizes == bm_cfg.sample_sizes
    assert bm_restored.n_repetitions == bm_cfg.n_repetitions
    assert bm_restored.seed == bm_cfg.seed
    assert bm_restored.blobs_k == bm_cfg.blobs_k
    assert bm_restored.blobs_cluster_std == pytest.approx(bm_cfg.blobs_cluster_std)
    assert bm_restored.blobs_radius == pytest.approx(bm_cfg.blobs_radius)
    assert bm_restored.warmup == bm_cfg.warmup

    # 2. SweepConfig Round-Trip (Noise & Outlier Sweeps)
    sw_cfg = SweepConfig(
        dataset_families=["blobs", "moons", "circles"],
        n_inliers=250,
        seeds=[11, 22, 33],
        sweep_types=["noise", "outlier"],
        noise_levels=[0.0, 0.05, 0.1],
        outlier_rates=[0.0, 0.05, 0.1],
        mode="custom",
    )
    sw_json = export_config_json(sw_cfg)
    sw_restored = SweepConfig.from_dict(json.loads(sw_json))
    assert sw_restored.dataset_families == sw_cfg.dataset_families
    assert sw_restored.n_inliers == sw_cfg.n_inliers
    assert sw_restored.seeds == sw_cfg.seeds
    assert sw_restored.sweep_types == sw_cfg.sweep_types
    assert sw_restored.noise_levels == sw_cfg.noise_levels
    assert sw_restored.outlier_rates == sw_cfg.outlier_rates
    assert sw_restored.mode == sw_cfg.mode


def test_config_rejection_boundary_and_corruption_cases():
    """Verify boundary rejections for corrupted, incompatible, or oversized configs."""
    from clustering_lab.data.config import MAX_CONFIG_JSON_BYTES

    # Incompatible clusters for Moons/Circles
    with pytest.raises(ValueError, match="n_clusters=2"):
        ExperimentConfig(dataset_family="moons", n_clusters=4)
    with pytest.raises(ValueError, match="n_clusters=2"):
        ExperimentConfig(dataset_family="circles", n_clusters=5)

    # Missing required key
    with pytest.raises(ValueError, match="Missing required configuration key"):
        ExperimentConfig.from_dict({})

    # Non-dictionary input
    with pytest.raises(TypeError, match="must be a dictionary"):
        ExperimentConfig.from_dict(["not", "a", "dict"])  # type: ignore

    # Non-string input to from_json
    with pytest.raises(TypeError, match="must be a JSON string"):
        ExperimentConfig.from_json(12345)  # type: ignore

    # Empty JSON string
    with pytest.raises(ValueError, match="empty"):
        ExperimentConfig.from_json("   ")

    # Oversized JSON string (> 100 KB)
    huge_json = '{"dataset_family": "blobs", "padding": "' + ("A" * (MAX_CONFIG_JSON_BYTES + 10)) + '"}'
    with pytest.raises(ValueError, match="exceeds maximum size limit"):
        ExperimentConfig.from_json(huge_json)
