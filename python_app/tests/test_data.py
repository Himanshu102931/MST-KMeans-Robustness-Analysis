"""
test_data.py
============
Scientific test suite for synthetic dataset generation, noise/outlier contamination,
and mathematical invariants.

Covers:
- Shapes, sample counts, and cluster counts across Blobs, Moons, and Circles.
- Deterministic reproducibility with identical seeds.
- Seed divergence across different random seeds.
- Independent, decoupled contamination streams (noise vs outliers).
- Outlier rate rounding and label assignment (-1).
- Inlier mask integrity and label preservation under Gaussian jitter.
- Zero-noise and zero-outlier baseline behavior.
- Support for duplicate points without deduplication.
- Invalid parameter rejection.
- Dual-algorithm interoperability: both custom K-Means and MST execute on generated datasets.
- Immutability of generated arrays.
"""

import pathlib
import sys
import numpy as np
import pytest

# Ensure python_app root is on sys.path
APP_DIR = pathlib.Path(__file__).resolve().parent.parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from clustering_lab.algorithms.kmeans import kmeans
from clustering_lab.algorithms.mst import mst_clustering
from clustering_lab.data.dataset import Dataset
from clustering_lab.data.noise import (
    apply_gaussian_noise,
    contaminate_dataset,
    generate_uniform_outliers,
)
from clustering_lab.data.synthetic import (
    generate_blobs,
    generate_circles,
    generate_moons,
    generate_synthetic_dataset,
)


def test_blobs_generation_shapes_and_labels():
    """Verify Gaussian Blobs generator produces expected shapes, counts, and labels."""
    dataset = generate_blobs(n_samples=300, n_clusters=3, cluster_std=0.3, seed=42)

    assert isinstance(dataset, Dataset)
    assert dataset.dataset_family == "blobs"
    assert dataset.X.shape == (300, 2)
    assert dataset.labels is not None
    assert dataset.labels.shape == (300,)
    assert dataset.inlier_mask.shape == (300,)
    assert np.all(dataset.inlier_mask)  # zero outliers
    assert dataset.n_inliers == 300
    assert dataset.n_outliers == 0
    assert dataset.n_samples == 300
    assert len(np.unique(dataset.labels)) == 3
    assert set(np.unique(dataset.labels)) == {0, 1, 2}
    assert dataset.clean_X is not None
    assert dataset.clean_X.shape == (300, 2)


def test_moons_generation_shapes_and_labels():
    """Verify Two Moons generator produces expected interlocking shapes and 2 clusters."""
    dataset = generate_moons(n_samples=250, noise=0.05, seed=42)

    assert dataset.dataset_family == "moons"
    assert dataset.X.shape == (250, 2)
    assert dataset.labels is not None
    assert dataset.labels.shape == (250,)
    assert dataset.n_inliers == 250
    assert dataset.n_outliers == 0
    assert set(np.unique(dataset.labels)) == {0, 1}


def test_circles_generation_shapes_and_labels():
    """Verify Concentric Circles generator produces expected nested rings and 2 clusters."""
    dataset = generate_circles(n_samples=200, factor=0.4, noise=0.04, seed=42)

    assert dataset.dataset_family == "circles"
    assert dataset.X.shape == (200, 2)
    assert dataset.labels is not None
    assert set(np.unique(dataset.labels)) == {0, 1}
    assert dataset.n_samples == 200


def test_exact_reproducibility_with_identical_seed():
    """Verify that identical parameters and seed produce bitwise identical coordinates."""
    d1 = generate_blobs(n_samples=150, n_clusters=3, noise=0.1, outlier_rate=0.1, seed=123)
    d2 = generate_blobs(n_samples=150, n_clusters=3, noise=0.1, outlier_rate=0.1, seed=123)

    assert np.array_equal(d1.X, d2.X)
    assert np.array_equal(d1.labels, d2.labels)
    assert np.array_equal(d1.inlier_mask, d2.inlier_mask)


def test_divergence_with_different_seeds():
    """Verify that different random seeds produce statistically distinct coordinates."""
    d1 = generate_moons(n_samples=100, noise=0.1, seed=42)
    d2 = generate_moons(n_samples=100, noise=0.1, seed=99)

    assert not np.array_equal(d1.X, d2.X)


def test_outlier_rate_rounding_and_label_assignment():
    """Verify that uniform outliers follow rounding formula, label -1, and inlier mask False."""
    # 300 inliers with 5%, 10%, 20% outlier rates
    for rate, expected_outliers in [(0.05, 15), (0.10, 30), (0.20, 60)]:
        dataset = generate_blobs(n_samples=300, n_clusters=3, outlier_rate=rate, seed=42)

        assert dataset.n_inliers == 300
        assert dataset.n_outliers == expected_outliers
        assert dataset.n_samples == 300 + expected_outliers
        assert dataset.X.shape == (300 + expected_outliers, 2)

        # Inlier mask checks
        assert int(np.sum(dataset.inlier_mask)) == 300
        assert int(np.sum(~dataset.inlier_mask)) == expected_outliers

        # Outlier label checks
        assert dataset.labels is not None
        outlier_labels = dataset.labels[~dataset.inlier_mask]
        assert np.all(outlier_labels == -1)

        # Inlier labels must be 0, 1, or 2
        inlier_labels = dataset.labels[dataset.inlier_mask]
        assert set(np.unique(inlier_labels)) == {0, 1, 2}


def test_noisy_inlier_label_preservation():
    """Verify that adding Gaussian noise to inliers preserves their ground-truth labels."""
    clean = generate_circles(n_samples=100, noise=0.0, seed=42)
    noisy = generate_circles(n_samples=100, noise=0.25, seed=42)

    assert clean.labels is not None and noisy.labels is not None
    # Ground-truth labels must be exactly identical
    assert np.array_equal(clean.labels, noisy.labels)
    # Coordinates must differ due to noise
    assert not np.array_equal(clean.X, noisy.X)


def test_decoupled_contamination_independence():
    """Verify that noise and outliers are generated using decoupled independent streams.

    Altering outlier_rate must NOT alter the coordinates of the noisy inliers.
    """
    d_no_outliers = generate_blobs(n_samples=200, n_clusters=3, noise=0.15, outlier_rate=0.0, seed=77)
    d_with_outliers = generate_blobs(n_samples=200, n_clusters=3, noise=0.15, outlier_rate=0.1, seed=77)

    # Inliers occupy the first 200 rows in both datasets
    inliers_1 = d_no_outliers.X[:200]
    inliers_2 = d_with_outliers.X[:200]

    assert np.allclose(inliers_1, inliers_2, atol=1e-12), (
        "Inlier coordinates changed when modifying outlier_rate; PRNG streams are coupled!"
    )


def test_zero_noise_and_zero_outlier_baseline():
    """Verify clean baseline: noise=0.0 produces clean_X == X."""
    dataset = generate_blobs(n_samples=100, n_clusters=2, noise=0.0, outlier_rate=0.0, seed=42)

    assert dataset.clean_X is not None
    assert np.array_equal(dataset.X, dataset.clean_X)
    assert dataset.n_outliers == 0


def test_duplicate_point_support_without_deduplication():
    """Verify that duplicate/identical points can be stored and processed without error."""
    X_dups = np.array([[1.0, 1.0], [1.0, 1.0], [5.0, 5.0], [5.0, 5.0]])
    labels = np.array([0, 0, 1, 1], dtype=np.int32)
    mask = np.ones(4, dtype=bool)

    dataset = Dataset(
        X=X_dups,
        labels=labels,
        inlier_mask=mask,
        dataset_family="custom",
        seed=None,
        params={},
        n_inliers=4,
        n_outliers=0,
        n_samples=4,
    )

    # Must preserve exact row count of 4 (no silent dropping)
    assert dataset.X.shape == (4, 2)
    assert dataset.n_samples == 4


def test_invalid_parameter_rejection():
    """Verify appropriate exception handling on invalid generator and contamination inputs."""
    # Negative noise
    with pytest.raises(ValueError, match="noise_sigma"):
        apply_gaussian_noise(np.ones((10, 2)), noise_sigma=-0.1, rng=np.random.default_rng())

    # Invalid outlier rate
    with pytest.raises(ValueError, match="interval"):
        generate_uniform_outliers(np.ones((10, 2)), outlier_rate=-0.05, rng=np.random.default_rng())
    with pytest.raises(ValueError, match="interval"):
        generate_uniform_outliers(np.ones((10, 2)), outlier_rate=1.0, rng=np.random.default_rng())

    # Insufficient samples
    with pytest.raises(ValueError, match="n_clusters"):
        generate_blobs(n_samples=2, n_clusters=3)

    # Invalid factor for circles
    with pytest.raises(ValueError, match="factor"):
        generate_circles(n_samples=50, factor=1.5)

    # Non-finite coordinates in Dataset
    with pytest.raises(ValueError, match="non-finite"):
        Dataset(
            X=np.array([[1.0, np.nan], [2.0, 3.0]]),
            labels=np.array([0, 1]),
            inlier_mask=np.array([True, True]),
            dataset_family="blobs",
            seed=None,
            params={},
            n_inliers=2,
            n_outliers=0,
            n_samples=2,
        )


def test_dual_clustering_algorithms_interoperability():
    """Verify that both custom K-Means and MST algorithms successfully execute on generated datasets."""
    dataset = generate_synthetic_dataset(
        family="blobs",
        n_samples=60,
        n_clusters=3,
        noise=0.05,
        outlier_rate=0.05,
        seed=42,
    )

    # Both algorithms must accept identical input X
    km_res = kmeans(dataset.X, k=3, seed=42)
    mst_res = mst_clustering(dataset.X, k=3)

    assert km_res.labels.shape == (dataset.n_samples,)
    assert mst_res.labels.shape == (dataset.n_samples,)
    assert len(np.unique(km_res.labels)) == 3
    assert len(np.unique(mst_res.labels)) == 3


def test_input_immutability():
    """Verify that calling generators does not mutate any caller buffers."""
    d = generate_moons(n_samples=50, seed=42)
    X_original = d.X.copy()

    # Pass to clustering algorithms
    kmeans(d.X, k=2, seed=42)
    mst_clustering(d.X, k=2)

    assert np.array_equal(d.X, X_original)


def test_direct_generator_dispatch_all_topologies_and_kwargs_filtering():
    """Test A (S06-DEFECT-002): Verify generate_synthetic_dataset dispatches correctly for all topologies.

    Specifically verifies that:
    1. Blobs forwards n_clusters, cluster_std, radius, and ignores irrelevant kwargs (e.g. factor).
    2. Moons ignores radius, cluster_std, and n_clusters without raising TypeError.
    3. Circles forwards factor, and ignores radius, cluster_std, and n_clusters without raising TypeError.
    4. Two finite coordinate dimensions, correct counts, valid labels, and deterministic reproducibility.
    """
    # 1. Blobs with extra kwargs (e.g. factor)
    ds_blobs = generate_synthetic_dataset(
        family="blobs",
        n_samples=40,
        seed=42,
        noise=0.0,
        outlier_rate=0.0,
        n_clusters=3,
        cluster_std=0.35,
        radius=4.0,
        factor=0.45,  # Irrelevant to blobs, must be filtered safely
    )
    assert ds_blobs.X.shape == (40, 2)
    assert np.all(np.isfinite(ds_blobs.X))
    assert len(np.unique(ds_blobs.labels)) == 3
    assert ds_blobs.dataset_family == "blobs"
    assert ds_blobs.params["radius"] == 4.0
    assert ds_blobs.params["cluster_std"] == 0.35

    # Seed reproducibility check
    ds_blobs_rep = generate_synthetic_dataset(
        family="blobs",
        n_samples=40,
        seed=42,
        n_clusters=3,
        cluster_std=0.35,
        radius=4.0,
    )
    assert np.array_equal(ds_blobs.X, ds_blobs_rep.X)
    assert np.array_equal(ds_blobs.labels, ds_blobs_rep.labels)

    # 2. Moons with extra kwargs (radius, cluster_std, n_clusters)
    ds_moons = generate_synthetic_dataset(
        family="moons",
        n_samples=40,
        seed=42,
        noise=0.05,
        outlier_rate=0.0,
        n_clusters=2,
        cluster_std=0.4,
        radius=3.5,  # Must NOT raise TypeError: generate_moons() got unexpected keyword argument 'radius'
    )
    assert ds_moons.X.shape == (40, 2)
    assert np.all(np.isfinite(ds_moons.X))
    assert len(np.unique(ds_moons.labels)) == 2
    assert ds_moons.dataset_family == "moons"
    assert ds_moons.params["n_clusters"] == 2

    ds_moons_rep = generate_synthetic_dataset(
        family="moons",
        n_samples=40,
        seed=42,
        noise=0.05,
    )
    assert np.array_equal(ds_moons.X, ds_moons_rep.X)
    assert np.array_equal(ds_moons.labels, ds_moons_rep.labels)

    # 3. Circles with extra kwargs (radius, cluster_std, n_clusters) and supported factor
    ds_circles = generate_synthetic_dataset(
        family="circles",
        n_samples=40,
        seed=42,
        noise=0.05,
        outlier_rate=0.0,
        factor=0.55,
        radius=3.5,  # Must NOT raise TypeError: generate_circles() got unexpected keyword argument 'radius'
        cluster_std=0.4,
        n_clusters=2,
    )
    assert ds_circles.X.shape == (40, 2)
    assert np.all(np.isfinite(ds_circles.X))
    assert len(np.unique(ds_circles.labels)) == 2
    assert ds_circles.dataset_family == "circles"
    assert ds_circles.params["factor"] == 0.55

    ds_circles_rep = generate_synthetic_dataset(
        family="circles",
        n_samples=40,
        seed=42,
        noise=0.05,
        factor=0.55,
    )
    assert np.array_equal(ds_circles.X, ds_circles_rep.X)
    assert np.array_equal(ds_circles.labels, ds_circles_rep.labels)


def test_dataset_parameter_boundaries_and_rejection():
    """Test C: Boundary values and error rejection across all synthetic topologies."""
    # Boundary: Small N=20 (minimum Explorer size)
    for fam in ["blobs", "moons", "circles"]:
        ds = generate_synthetic_dataset(family=fam, n_samples=20, seed=100)
        assert ds.X.shape == (20, 2)

    # Boundary: Max Explorer micro-observations N=60
    for fam in ["blobs", "moons", "circles"]:
        ds = generate_synthetic_dataset(family=fam, n_samples=60, seed=100)
        assert ds.X.shape == (60, 2)

    # Seed changes produce distinct feature matrices on stochastic generators
    d1 = generate_synthetic_dataset(family="blobs", n_samples=30, seed=11)
    d2 = generate_synthetic_dataset(family="blobs", n_samples=30, seed=22)
    assert not np.allclose(d1.X, d2.X)

    # For moons with noise, seed alters the jitter perturbation
    m1 = generate_synthetic_dataset(family="moons", n_samples=30, noise=0.05, seed=11)
    m2 = generate_synthetic_dataset(family="moons", n_samples=30, noise=0.05, seed=22)
    assert not np.allclose(m1.X, m2.X)

    # Invalid family rejection
    with pytest.raises(ValueError, match="Unsupported dataset family"):
        generate_synthetic_dataset(family="spiral", n_samples=30)

    # Invalid factor for circles
    with pytest.raises(ValueError, match="Circle separation factor"):
        generate_synthetic_dataset(family="circles", n_samples=30, factor=1.5)

    # Invalid n_samples for blobs (n_samples < n_clusters)
    with pytest.raises(ValueError, match="must be >= n_clusters"):
        generate_synthetic_dataset(family="blobs", n_samples=2, n_clusters=3)
