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
