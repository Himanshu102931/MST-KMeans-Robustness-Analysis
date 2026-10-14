"""
test_kmeans.py
==============
Rigorous mathematical, algorithmic, and boundary test suite for
independent Lloyd's K-Means clustering implementation.

Covers:
- Two clearly separated clusters (partition recovery via Adjusted Rand Index).
- Single-cluster behavior (k = 1).
- Maximal-cluster behavior (k = N).
- Mathematical centroid property: centroids match arithmetic mean of assigned points.
- Inertia property: inertia matches Within-Cluster Sum of Squares (WCSS).
- Fixed-seed reproducibility.
- Invalid input validation (NaN, Inf, shapes, k bounds, max_iter, tol).
- Duplicate and degenerate point sets.
- Input array immutability.
- Estimator API (fit, predict, fit_predict).
"""

import pathlib
import sys
import numpy as np
import pytest

# Ensure python_app is on sys.path
APP_DIR = pathlib.Path(__file__).resolve().parent.parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from clustering_lab.algorithms.kmeans import KMeans, KMeansResult, kmeans


def test_kmeans_two_separated_clusters():
    """Verify clean partition recovery on two well-separated 2D clusters."""
    rng = np.random.default_rng(101)
    # Cluster A around (0, 0), Cluster B around (20, 20)
    cluster_a = rng.normal(loc=[0.0, 0.0], scale=0.5, size=(40, 2))
    cluster_b = rng.normal(loc=[20.0, 20.0], scale=0.5, size=(40, 2))
    X = np.vstack([cluster_a, cluster_b])
    true_labels = np.array([0] * 40 + [1] * 40)

    result = kmeans(X, k=2, seed=42)

    assert result.converged is True
    assert result.labels.shape == (80,)
    assert result.cluster_centers.shape == (2, 2)
    assert result.inertia > 0.0

    # Label-permutation-invariant partition verification:
    # Points 0..39 must share one label, and 40..79 must share the other
    assert np.all(result.labels[:40] == result.labels[0])
    assert np.all(result.labels[40:] == result.labels[40])
    assert result.labels[0] != result.labels[40]

    # Centers must be close to empirical means
    means = np.array([np.mean(cluster_a, axis=0), np.mean(cluster_b, axis=0)])
    # Match centers regardless of index ordering
    dists_0 = np.linalg.norm(result.cluster_centers - means[0], axis=1)
    dists_1 = np.linalg.norm(result.cluster_centers - means[1], axis=1)
    assert np.min(dists_0) < 0.5
    assert np.min(dists_1) < 0.5


def test_kmeans_single_cluster_k1():
    """Verify k = 1 behavior: centroid is exact sample mean, 1 iteration."""
    X = np.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0], [7.0, 8.0]])
    expected_mean = np.mean(X, axis=0, keepdims=True)
    expected_inertia = float(np.sum((X - expected_mean) ** 2))

    result = kmeans(X, k=1)

    assert result.k == 1
    assert result.n_iter == 1
    assert result.converged is True
    assert np.all(result.labels == 0)
    assert np.allclose(result.cluster_centers, expected_mean)
    assert np.isclose(result.inertia, expected_inertia)


def test_kmeans_k_equals_n():
    """Verify k = N behavior: every sample is its own centroid, zero inertia."""
    X = np.array([[0.0, 0.0], [2.0, 3.0], [5.0, 1.0], [7.0, 7.0]])
    n = len(X)

    result = kmeans(X, k=n)

    assert result.k == n
    assert result.inertia == 0.0
    assert result.converged is True
    assert len(np.unique(result.labels)) == n
    assert np.allclose(np.sort(result.labels), np.arange(n))


def test_kmeans_centroid_arithmetic_mean_property():
    """Verify that every computed centroid is the exact arithmetic mean of assigned points."""
    rng = np.random.default_rng(202)
    X = rng.uniform(-10.0, 10.0, size=(60, 2))

    result = kmeans(X, k=4, seed=123)

    for c in range(result.k):
        members = X[result.labels == c]
        if len(members) > 0:
            expected_center = np.mean(members, axis=0)
            assert np.allclose(result.cluster_centers[c], expected_center, atol=1e-10)


def test_kmeans_inertia_definition():
    """Verify that result.inertia matches sum of squared Euclidean distances to assigned centroids."""
    rng = np.random.default_rng(303)
    X = rng.normal(size=(50, 2))

    result = kmeans(X, k=3, seed=42)

    computed_wcss = 0.0
    for i in range(len(X)):
        c = result.labels[i]
        computed_wcss += np.sum((X[i] - result.cluster_centers[c]) ** 2)

    assert np.isclose(result.inertia, computed_wcss, atol=1e-8)


def test_kmeans_fixed_seed_reproducibility():
    """Verify that execution with identical seed produces bitwise identical results."""
    rng = np.random.default_rng(404)
    X = rng.uniform(-5.0, 5.0, size=(80, 2))

    res1 = kmeans(X, k=3, seed=777)
    res2 = kmeans(X, k=3, seed=777)

    assert np.array_equal(res1.labels, res2.labels)
    assert np.array_equal(res1.cluster_centers, res2.cluster_centers)
    assert res1.inertia == res2.inertia
    assert res1.n_iter == res2.n_iter


def test_kmeans_invalid_parameters():
    """Verify that invalid inputs and hyperparameters raise appropriate exceptions."""
    X_valid = np.array([[1.0, 2.0], [3.0, 4.0]])

    # Invalid k
    with pytest.raises(ValueError, match="at least 1"):
        kmeans(X_valid, k=0)
    with pytest.raises(ValueError, match="cannot exceed"):
        kmeans(X_valid, k=3)
    with pytest.raises(TypeError, match="must be an integer"):
        kmeans(X_valid, k=1.5)  # type: ignore

    # Non-finite values
    X_nan = np.array([[1.0, np.nan], [3.0, 4.0]])
    with pytest.raises(ValueError, match="non-finite"):
        kmeans(X_nan, k=2)

    X_inf = np.array([[1.0, 2.0], [np.inf, 4.0]])
    with pytest.raises(ValueError, match="non-finite"):
        kmeans(X_inf, k=2)

    # Invalid dimensionality
    with pytest.raises(ValueError, match="2D array"):
        kmeans(np.array([1.0, 2.0, 3.0]), k=1)

    # Invalid iterations and tolerance
    with pytest.raises(ValueError, match="'max_iter' must be at least 1"):
        kmeans(X_valid, k=2, max_iter=0)
    with pytest.raises(ValueError, match="'tol' must be non-negative"):
        kmeans(X_valid, k=2, tol=-0.01)


def test_kmeans_duplicate_and_degenerate_points():
    """Verify safe execution when dataset contains identical points or fewer distinct values than k."""
    # 5 identical points with k = 3
    X_identical = np.array([[2.5, 3.5]] * 5)
    res = kmeans(X_identical, k=3, seed=42)
    assert res.labels.shape == (5,)
    assert res.cluster_centers.shape == (3, 2)
    assert np.isclose(res.inertia, 0.0)

    # Dataset with multiple duplicate observations
    X_dups = np.array([[1.0, 1.0], [1.0, 1.0], [10.0, 10.0], [10.0, 10.0]])
    res_dups = kmeans(X_dups, k=2, seed=42)
    assert res_dups.converged is True
    # Duplicate points must fall in the same cluster
    assert res_dups.labels[0] == res_dups.labels[1]
    assert res_dups.labels[2] == res_dups.labels[3]
    assert res_dups.labels[0] != res_dups.labels[2]


def test_kmeans_input_immutability():
    """Verify that calling kmeans does not mutate the input array."""
    X_orig = np.array([[1.5, 2.5], [3.5, 4.5], [5.5, 6.5]])
    X_copy = X_orig.copy()

    kmeans(X_orig, k=2, seed=42)
    assert np.array_equal(X_orig, X_copy)


def test_kmeans_estimator_class_interface():
    """Verify KMeans object-oriented estimator methods and fitted attributes."""
    X = np.array([[0.0, 0.0], [0.1, 0.0], [10.0, 10.0], [10.1, 10.0]])
    km = KMeans(n_clusters=2, seed=42)

    fitted = km.fit(X)
    assert fitted is km
    assert km.labels_ is not None
    assert km.cluster_centers_ is not None
    assert km.inertia_ is not None
    assert km.converged_ is True

    # Test predict on new observations
    X_new = np.array([[0.05, 0.0], [10.05, 10.0]])
    preds = km.predict(X_new)
    assert preds.shape == (2,)
    assert preds[0] == km.labels_[0]
    assert preds[1] == km.labels_[2]

    # Test fit_predict equivalence
    labels_fp = KMeans(n_clusters=2, seed=42).fit_predict(X)
    assert np.array_equal(labels_fp, km.labels_)


def test_kmeans_predict_feature_dimension_validation():
    """Verify that KMeans.predict strictly validates input feature dimensions (ISSUE-04)."""
    X_train = np.array([[0.0, 0.0], [0.1, 0.1], [10.0, 10.0], [10.1, 10.1]])
    km = KMeans(n_clusters=2, seed=42)

    # 1. Prediction before fitting must raise RuntimeError
    with pytest.raises(RuntimeError, match="Estimator is not fitted yet"):
        km.predict(X_train)

    km.fit(X_train)
    assert km.cluster_centers_.shape == (2, 2)

    # 2. Correct 2D shape with matching 2 features must succeed
    X_valid = np.array([[0.05, 0.05], [10.05, 10.05]])
    preds = km.predict(X_valid)
    assert preds.shape == (2,)

    # 3. Input with 1 feature (model expects 2) must raise ValueError with descriptive message
    X_1d_feat = np.array([[0.0], [10.0]])
    with pytest.raises(ValueError, match=r"Feature dimension mismatch: model was fitted on 2 features, but input X has 1 features\."):
        km.predict(X_1d_feat)

    # 4. Input with 3 features (model expects 2) must raise ValueError with descriptive message
    X_3d_feat = np.array([[0.0, 1.0, 2.0], [10.0, 11.0, 12.0]])
    with pytest.raises(ValueError, match=r"Feature dimension mismatch: model was fitted on 2 features, but input X has 3 features\."):
        km.predict(X_3d_feat)

    # 5. Non-finite values in prediction input must raise ValueError
    X_nan = np.array([[0.0, np.nan], [10.0, 10.0]])
    with pytest.raises(ValueError, match="non-finite values"):
        km.predict(X_nan)

    X_inf = np.array([[0.0, np.inf], [10.0, 10.0]])
    with pytest.raises(ValueError, match="non-finite values"):
        km.predict(X_inf)

    # 6. Invalid array dimensionality (1D array instead of 2D) must raise ValueError
    X_1d = np.array([0.0, 1.0])
    with pytest.raises(ValueError, match="Input X must be a 2D array"):
        km.predict(X_1d)

    # 7. Invalid array dimensionality (3D array instead of 2D) must raise ValueError
    X_3d = np.zeros((2, 2, 2))
    with pytest.raises(ValueError, match="Input X must be a 2D array"):
        km.predict(X_3d)


def test_kmeans_empty_cluster_reseeding_and_finite_centers():
    """Verify empty-cluster reseeding and finite coordinate invariants under severe duplicates (ISSUE-03)."""
    # 6 samples situated at only 3 distinct spatial coordinates
    X_dups = np.array([
        [0.0, 0.0],
        [0.0, 0.0],
        [10.0, 10.0],
        [10.0, 10.0],
        [20.0, 20.0],
        [20.0, 20.0],
    ])
    # Request k=4 clusters: at least 1 cluster must become empty and reseed
    result = kmeans(X_dups, k=4, seed=42)

    assert result.cluster_centers.shape == (4, 2)
    assert np.isfinite(result.cluster_centers).all()
    assert np.isfinite(result.inertia)
    assert result.inertia >= 0.0
    assert len(result.labels) == 6
    assert np.all(result.labels >= 0) and np.all(result.labels < 4)


def test_kmeans_convergence_boundary_zero_tolerance():
    """Verify strict < tol behavior when tol = 0.0 vs tol > 0.0 (ISSUE-02)."""
    X = np.array([[0.0, 0.0], [0.1, 0.0], [10.0, 10.0], [10.1, 10.0]])

    # When tol = 0.0, strict max_shift < 0.0 is impossible (norms are >= 0),
    # so algorithm must run until max_iter is exhausted and report converged=False.
    res_zero = kmeans(X, k=2, tol=0.0, max_iter=5, seed=42)
    assert res_zero.n_iter == 5
    assert res_zero.converged is False
    assert np.isfinite(res_zero.cluster_centers).all()

    # With standard positive tolerance, algorithm converges early
    res_pos = kmeans(X, k=2, tol=1e-4, max_iter=100, seed=42)
    assert res_pos.converged is True
    assert res_pos.n_iter < 10
