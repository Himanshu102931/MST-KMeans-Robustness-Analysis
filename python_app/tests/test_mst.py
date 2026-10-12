"""
test_mst.py
===========
Rigorous mathematical, graph-theoretic, and boundary test suite for
Euclidean Minimum Spanning Tree (MST) clustering implementation.

Covers:
- Classical 3-4-5 right triangle geometry (exact weight = 7.0).
- Collinear four-point geometry (MST weight = 3.0).
- Degenerate single point (N = 1, k = 1).
- Single cluster boundary (k = 1): 0 cut edges, total_weight == retained_weight.
- Maximal cluster boundary (k = N): N - 1 cut edges, retained_weight == 0.0.
- Invariant: MST contains exactly N - 1 edges for N >= 2.
- Invariant: Partition contains exactly k connected components.
- Deterministic tie-breaking on symmetric/equilateral configurations.
- Duplicate observations and zero-weight edges.
- Invalid parameter validation (NaN, Inf, shapes, k bounds).
- Input array immutability.
- Estimator API (fit, fit_predict).
"""

import pathlib
import sys
import numpy as np
import pytest

# Ensure python_app is on sys.path
APP_DIR = pathlib.Path(__file__).resolve().parent.parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from clustering_lab.algorithms.mst import (
    MSTClustering,
    MSTClusteringResult,
    mst_clustering,
)


def test_mst_three_point_triangle_weight_and_cut():
    """Verify 3-4-5 right triangle: MST total weight must equal exactly 7.0.

    Geometry:
        P0 = (0, 0), P1 = (4, 0), P2 = (0, 3)
        Pairwise Euclidean distances:
            dist(P0, P1) = 4.0
            dist(P0, P2) = 3.0
            dist(P1, P2) = 5.0
        MST must select edges with weights 3.0 and 4.0.
        Total MST weight = 3.0 + 4.0 = 7.0.
    """
    X = np.array([[0.0, 0.0], [4.0, 0.0], [0.0, 3.0]])

    # k = 1: Uncut tree
    res_k1 = mst_clustering(X, k=1)
    assert len(res_k1.mst_edges) == 2
    assert len(res_k1.cut_edges) == 0
    assert np.isclose(res_k1.total_mst_weight, 7.0)
    assert np.isclose(res_k1.retained_weight, 7.0)
    assert np.all(res_k1.labels == 0)

    # Edge weights present in tree must be 3.0 and 4.0
    tree_weights = sorted([e.weight for e in res_k1.mst_edges])
    assert np.isclose(tree_weights[0], 3.0)
    assert np.isclose(tree_weights[1], 4.0)

    # k = 2: Cut longest edge (weight 4.0)
    res_k2 = mst_clustering(X, k=2)
    assert len(res_k2.cut_edges) == 1
    assert np.isclose(res_k2.cut_edges[0].weight, 4.0)
    assert np.isclose(res_k2.retained_weight, 3.0)
    assert np.isclose(res_k2.total_mst_weight, 7.0)
    assert len(np.unique(res_k2.labels)) == 2

    # P0 (0,0) and P2 (0,3) are connected by the weight-3.0 edge; P1 (4,0) is separate
    assert res_k2.labels[0] == res_k2.labels[2]
    assert res_k2.labels[0] != res_k2.labels[1]


def test_mst_collinear_four_points():
    """Verify collinear four-point geometry (0,0), (1,0), (2,0), (3,0)."""
    X = np.array([[0.0, 0.0], [1.0, 0.0], [2.0, 0.0], [3.0, 0.0]])

    res_k1 = mst_clustering(X, k=1)
    assert len(res_k1.mst_edges) == 3
    assert np.isclose(res_k1.total_mst_weight, 3.0)
    for edge in res_k1.mst_edges:
        assert np.isclose(edge.weight, 1.0)

    res_k3 = mst_clustering(X, k=3)
    assert len(res_k3.cut_edges) == 2
    assert np.isclose(res_k3.retained_weight, 1.0)
    assert len(np.unique(res_k3.labels)) == 3


def test_mst_single_point_n1():
    """Verify degenerate N = 1 behavior: 0 edges, weight 0.0, label [0]."""
    X = np.array([[5.0, -2.5]])
    res = mst_clustering(X, k=1)

    assert res.n_samples == 1
    assert res.k == 1
    assert len(res.mst_edges) == 0
    assert len(res.cut_edges) == 0
    assert res.total_mst_weight == 0.0
    assert res.retained_weight == 0.0
    assert np.array_equal(res.labels, np.array([0]))


def test_mst_k_equals_n():
    """Verify k = N: all N - 1 edges cut, retained weight is 0.0, N components."""
    X = np.array([[1.0, 2.0], [4.0, 6.0], [9.0, 1.0], [-2.0, 3.0]])
    n = len(X)

    res = mst_clustering(X, k=n)

    assert len(res.mst_edges) == n - 1
    assert len(res.cut_edges) == n - 1
    assert np.isclose(res.retained_weight, 0.0)
    assert res.total_mst_weight > 0.0
    assert len(np.unique(res.labels)) == n


def test_mst_edge_count_and_k_components_invariant():
    """Verify that MST always has N - 1 edges and cuts produce exactly k components."""
    rng = np.random.default_rng(505)

    for n in [5, 12, 20]:
        X = rng.uniform(-10.0, 10.0, size=(n, 2))
        for k in [1, 2, n // 2, n]:
            res = mst_clustering(X, k=k)
            assert len(res.mst_edges) == n - 1
            assert len(res.cut_edges) == k - 1
            assert len(np.unique(res.labels)) == k
            assert np.isclose(
                res.total_mst_weight,
                res.retained_weight + sum(e.weight for e in res.cut_edges),
            )


def test_mst_deterministic_tie_breaking():
    """Verify deterministic tie-breaking on equilateral triangle with symmetric edge weights."""
    # Equilateral triangle: all 3 pairwise distances equal 2.0
    h = np.sqrt(3.0)
    X = np.array([[0.0, 0.0], [2.0, 0.0], [1.0, h]])

    res1 = mst_clustering(X, k=2)
    res2 = mst_clustering(X, k=2)

    assert np.array_equal(res1.labels, res2.labels)
    assert res1.total_mst_weight == res2.total_mst_weight
    assert len(res1.cut_edges) == len(res2.cut_edges)
    assert res1.cut_edges[0].edge_id == res2.cut_edges[0].edge_id


def test_mst_duplicate_points_and_zero_weight_edges():
    """Verify handling of duplicate observations resulting in zero-weight edges."""
    X = np.array([
        [0.0, 0.0],
        [0.0, 0.0],  # Duplicate of point 0
        [10.0, 10.0],
        [10.0, 10.0],  # Duplicate of point 2
    ])

    res = mst_clustering(X, k=2)

    # Must contain exactly N - 1 = 3 edges
    assert len(res.mst_edges) == 3
    # Two zero-weight edges between duplicate pairs
    zero_edges = [e for e in res.mst_edges if np.isclose(e.weight, 0.0)]
    assert len(zero_edges) == 2

    # Longest edge between the two distant pairs should be cut
    assert len(res.cut_edges) == 1
    assert res.cut_edges[0].weight > 10.0

    # Duplicates must share cluster labels
    assert res.labels[0] == res.labels[1]
    assert res.labels[2] == res.labels[3]
    assert res.labels[0] != res.labels[2]


def test_mst_invalid_parameters():
    """Verify exception handling for invalid inputs."""
    X_valid = np.array([[1.0, 2.0], [3.0, 4.0]])

    with pytest.raises(ValueError, match="at least 1"):
        mst_clustering(X_valid, k=0)
    with pytest.raises(ValueError, match="cannot exceed"):
        mst_clustering(X_valid, k=3)
    with pytest.raises(TypeError, match="must be an integer"):
        mst_clustering(X_valid, k=1.5)  # type: ignore

    X_nan = np.array([[1.0, np.nan], [3.0, 4.0]])
    with pytest.raises(ValueError, match="non-finite"):
        mst_clustering(X_nan, k=2)

    with pytest.raises(ValueError, match="2D array"):
        mst_clustering(np.array([1.0, 2.0]), k=1)


def test_mst_input_immutability():
    """Verify that calling mst_clustering does not mutate input array."""
    X_orig = np.array([[2.0, 3.0], [5.0, 7.0], [11.0, 13.0]])
    X_copy = X_orig.copy()

    mst_clustering(X_orig, k=2)
    assert np.array_equal(X_orig, X_copy)


def test_mst_estimator_class_interface():
    """Verify MSTClustering object-oriented estimator methods and fitted attributes."""
    X = np.array([[0.0, 0.0], [1.0, 0.0], [10.0, 0.0], [11.0, 0.0]])
    estimator = MSTClustering(n_clusters=2)

    fitted = estimator.fit(X)
    assert fitted is estimator
    assert estimator.labels_ is not None
    assert estimator.total_mst_weight_ is not None
    assert estimator.k_ == 2
    assert estimator.n_samples_ == 4

    labels_fp = MSTClustering(n_clusters=2).fit_predict(X)
    assert np.array_equal(labels_fp, estimator.labels_)
