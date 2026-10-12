"""
test_reference_validation.py
=============================
Independent reference validation against established scientific packages
(SciPy and scikit-learn) on controlled benchmark geometries.

Validates:
- MST total weight against SciPy's csgraph.minimum_spanning_tree on distinct-point geometries.
- K-Means partition quality and inertia against scikit-learn on well-separated Gaussian clusters.
- Fundamental mathematical invariants across both algorithms.
- Uniform input compatibility: identical dataset passed to both algorithms.
"""

import pathlib
import sys
import numpy as np
import pytest

# Ensure python_app is on sys.path
APP_DIR = pathlib.Path(__file__).resolve().parent.parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from clustering_lab.algorithms.kmeans import kmeans
from clustering_lab.algorithms.mst import mst_clustering


def test_mst_total_weight_against_scipy_reference():
    """Verify our dense Prim's MST total weight matches SciPy's minimum_spanning_tree.

    Scientific Note:
        SciPy's sparse CSR matrix representation treats numerical zeros as absent edges.
        Therefore, reference validation is conducted on geometries with strictly distinct
        observations (pairwise distance d_ij > 0) to avoid sparse representation ambiguity.
    """
    from scipy.spatial.distance import pdist, squareform
    from scipy.sparse.csgraph import minimum_spanning_tree

    rng = np.random.default_rng(606)

    for n_samples in [4, 10, 25]:
        # Generate distinct 2D coordinates
        X = rng.uniform(-15.0, 15.0, size=(n_samples, 2))

        # Compute full pairwise distance matrix
        dist_matrix = squareform(pdist(X, metric="euclidean"))

        # Reference MST calculation via SciPy
        scipy_mst = minimum_spanning_tree(dist_matrix)
        expected_total_weight = float(scipy_mst.sum())

        # Our independent Prim's MST implementation
        our_result = mst_clustering(X, k=1)

        assert np.isclose(our_result.total_mst_weight, expected_total_weight, atol=1e-10), (
            f"MST weight mismatch for N={n_samples}: our={our_result.total_mst_weight}, scipy={expected_total_weight}"
        )


def test_kmeans_partition_against_sklearn_reference():
    """Verify K-Means partition recovery against scikit-learn on well-separated isotropic clusters."""
    from sklearn.cluster import KMeans as SklearnKMeans
    from sklearn.metrics import adjusted_rand_score

    rng = np.random.default_rng(707)
    # Three well-separated Gaussian clusters
    c1 = rng.normal(loc=[-15.0, 0.0], scale=0.4, size=(30, 2))
    c2 = rng.normal(loc=[0.0, 15.0], scale=0.4, size=(30, 2))
    c3 = rng.normal(loc=[15.0, 0.0], scale=0.4, size=(30, 2))
    X = np.vstack([c1, c2, c3])

    # Our from-scratch implementation
    our_res = kmeans(X, k=3, seed=42)

    # Scikit-learn reference implementation
    sk_km = SklearnKMeans(n_clusters=3, random_state=42, n_init=10)
    sk_labels = sk_km.fit_predict(X)

    # Evaluate partition agreement via Adjusted Rand Index (label-permutation invariant)
    ari = adjusted_rand_score(our_res.labels, sk_labels)
    assert ari == 1.0, f"Expected perfect cluster agreement on well-separated blobs, got ARI={ari}"

    # Inertias should be in close relative agreement
    assert np.isclose(our_res.inertia, sk_km.inertia_, rtol=0.05)


def test_numerical_invariants_across_both_algorithms():
    """Verify core numerical bounds and energy conservation invariants."""
    rng = np.random.default_rng(808)
    X = rng.uniform(-5.0, 5.0, size=(20, 2))

    # K-Means invariants
    km_res = kmeans(X, k=3, seed=42)
    assert km_res.inertia >= 0.0
    assert km_res.n_iter >= 1
    assert km_res.cluster_centers.shape == (3, 2)

    # MST invariants
    mst_res = mst_clustering(X, k=3)
    assert mst_res.total_mst_weight >= 0.0
    assert mst_res.retained_weight >= 0.0
    assert mst_res.retained_weight <= mst_res.total_mst_weight
    sum_cuts = sum(e.weight for e in mst_res.cut_edges)
    assert np.isclose(mst_res.total_mst_weight, mst_res.retained_weight + sum_cuts)


def test_uniform_dataset_interoperability():
    """Verify that the same dataset can be cleanly clustered by both algorithms."""
    X = np.array([
        [0.0, 0.0], [0.5, 0.2],
        [5.0, 5.0], [5.2, 4.8],
        [-5.0, 5.0], [-4.8, 5.2]
    ])

    km_res = kmeans(X, k=3, seed=42)
    mst_res = mst_clustering(X, k=3)

    assert km_res.labels.shape == (6,)
    assert mst_res.labels.shape == (6,)
    assert len(np.unique(km_res.labels)) == 3
    assert len(np.unique(mst_res.labels)) == 3
