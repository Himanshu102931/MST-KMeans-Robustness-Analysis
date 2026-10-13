"""
test_algorithm_explorer.py
==========================
Automated test suite for Phase M5B Algorithm Explorers:
1. K-Means Explorer trace generation:
   - Step 0 unassigned observations.
   - K-Means++ D(x)^2 centroid selection sequence.
   - Lloyd Voronoi assignment and arithmetic centroid update steps.
   - Final convergence and inertia invariants.
   - Exact mathematical parity with production custom kmeans() algorithm.
   - Deterministic execution under fixed seeds.
2. Prim's MST Explorer trace generation:
   - Step 0 root vertex selection.
   - N-1 sequential edge expansion steps with minimal cut edge selection.
   - Completed MST with exactly N-1 edges.
   - Removal of the k-1 longest tree edges.
   - Final connected-component labeling via DSU.
   - Exact mathematical parity with production custom mst_clustering() algorithm.
   - Edge weight and component count invariants.
3. Visualization functions:
   - 1:1 isotropic scaling on Plotly figures.
   - Valid in-memory Matplotlib PNG rendering (b'\\x89PNG\\r\\n\\x1a\\n').
4. Streamlit AppTest view integration:
   - Performance Benchmarks view renders cleanly.
   - Algorithm Explorer view renders cleanly with step cockpit.
"""

from __future__ import annotations

import io
import pathlib
import sys
import numpy as np
import pytest

APP_DIR = pathlib.Path(__file__).resolve().parent.parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from clustering_lab.algorithms.explorer import (
    KMeansTraceResult,
    KMeansTraceStep,
    MSTTraceResult,
    MSTTraceStep,
    run_kmeans_trace,
    run_mst_trace,
)
from clustering_lab.algorithms.kmeans import kmeans
from clustering_lab.algorithms.mst import mst_clustering
from clustering_lab.data.synthetic import generate_synthetic_dataset
from clustering_lab.visualization.figures import (
    create_kmeans_explorer_figure,
    create_mst_explorer_figure,
    render_clustering_png,
)


# =============================================================================
# 1. K-Means Algorithm Explorer Trace & Mathematical Parity
# =============================================================================
def test_kmeans_trace_step_sequence():
    """Verify the chronological structure of steps in the K-Means trace."""
    X = np.array([
        [0.0, 0.0],
        [0.1, 0.2],
        [5.0, 5.0],
        [5.2, 5.1],
        [10.0, 0.0],
        [10.1, 0.1],
    ], dtype=np.float64)
    k = 3
    seed = 42

    trace = run_kmeans_trace(X=X, k=k, seed=seed)

    # Step 0: Initial unassigned state
    step0 = trace.steps[0]
    assert step0.step_type == "init"
    assert (step0.labels == -1).all()
    assert step0.centroids.shape[0] == 0
    assert step0.iteration == 0

    # Steps 1..k: K-Means++ centroid initialization
    kpp_steps = [s for s in trace.steps if s.step_type == "kmeans_plus_plus"]
    assert len(kpp_steps) == k
    for i, s in enumerate(kpp_steps):
        assert s.centroids is not None
        assert s.centroids.shape == (i + 1, 2)

    # Subsequent Lloyd assignment & update steps
    assign_steps = [s for s in trace.steps if s.step_type == "assignment"]
    update_steps = [s for s in trace.steps if s.step_type == "update"]
    assert len(assign_steps) >= 1
    assert len(update_steps) >= 1

    # Final step: converged
    final_step = trace.steps[-1]
    assert final_step.step_type == "converged"
    assert final_step.labels is not None
    assert len(np.unique(final_step.labels)) == k
    assert final_step.centroids.shape == (k, 2)
    assert final_step.inertia is not None


def test_kmeans_trace_exact_parity_with_production():
    """Explorer final result must match production kmeans() with 100% agreement."""
    ds = generate_synthetic_dataset(family="blobs", n_samples=30, seed=42, n_clusters=3)
    X = ds.X
    k = 3
    seed = 42

    trace = run_kmeans_trace(X=X, k=k, seed=seed)
    prod = kmeans(X=X, k=k, seed=seed)

    assert trace.final_parity_verified is True
    assert np.array_equal(trace.final_result.labels, prod.labels)
    assert np.allclose(trace.final_result.centroids, prod.centroids)
    assert trace.final_result.inertia == pytest.approx(prod.inertia, rel=1e-6)
    assert trace.final_result.n_iter == prod.n_iter


def test_kmeans_trace_deterministic_reproducibility():
    """Running trace twice with identical inputs must produce identical step sequences."""
    ds = generate_synthetic_dataset(family="moons", n_samples=25, seed=123)
    t1 = run_kmeans_trace(X=ds.X, k=2, seed=123)
    t2 = run_kmeans_trace(X=ds.X, k=2, seed=123)

    assert len(t1.steps) == len(t2.steps)
    for s1, s2 in zip(t1.steps, t2.steps):
        assert s1.step_type == s2.step_type
        if s1.centroids is not None and s2.centroids is not None:
            assert np.allclose(s1.centroids, s2.centroids)
        if s1.labels is not None and s2.labels is not None:
            assert np.array_equal(s1.labels, s2.labels)


# =============================================================================
# 2. Prim's MST Algorithm Explorer Trace & Mathematical Parity
# =============================================================================
def test_mst_trace_step_sequence():
    """Verify chronological structure and graph properties of MST explorer trace."""
    X = np.array([
        [0.0, 0.0],
        [1.0, 0.0],
        [0.0, 2.0],
        [5.0, 5.0],
        [6.0, 5.0],
    ], dtype=np.float64)
    N = len(X)
    k = 2

    trace = run_mst_trace(X=X, k=k)

    # Step 0: Root vertex initialization
    step0 = trace.steps[0]
    assert step0.step_type == "init"
    assert len(step0.tree_edges) == 0
    assert len(step0.in_tree_vertices) == 1

    # Steps 1 to N-1: Sequential edge expansion
    add_edge_steps = [s for s in trace.steps if s.step_type in ("add_edge", "tree_growth")]
    assert len(add_edge_steps) == N - 1
    for i, s in enumerate(add_edge_steps):
        assert len(s.tree_edges) == i + 1
        assert len(s.in_tree_vertices) == i + 2
        assert s.new_edge is not None

    # Completed MST step
    complete_step = [s for s in trace.steps if s.step_type == "mst_complete"][0]
    assert len(complete_step.tree_edges) == N - 1
    assert len(complete_step.in_tree_vertices) == N

    # Cut edges step: exactly k-1 edges cut
    cut_step = [s for s in trace.steps if s.step_type in ("cut_edges", "cutting_edges")][0]
    assert len(cut_step.cut_edges) == k - 1
    assert len(cut_step.retained_edges) == (N - 1) - (k - 1)

    # Final connected components partition step
    final_step = trace.steps[-1]
    assert final_step.step_type in ("final_clusters", "connected_components")
    assert final_step.labels is not None
    assert len(np.unique(final_step.labels)) == k


def test_mst_trace_exact_parity_with_production():
    """Explorer final result must match production mst_clustering() with 100% agreement."""
    ds = generate_synthetic_dataset(family="circles", n_samples=35, seed=42)
    X = ds.X
    k = 2

    trace = run_mst_trace(X=X, k=k)
    prod = mst_clustering(X=X, k=k)

    assert trace.final_parity_verified is True
    assert np.array_equal(trace.final_result.labels, prod.labels)
    assert trace.final_result.total_weight == pytest.approx(prod.total_weight, rel=1e-6)
    assert len(trace.final_result.cut_edges) == len(prod.cut_edges)
    assert len(trace.final_result.mst_edges) == len(prod.mst_edges)


def test_mst_trace_duplicate_points_handling():
    """MST trace must execute robustly on identical duplicate coordinates."""
    X = np.array([
        [1.0, 1.0],
        [1.0, 1.0],
        [2.0, 2.0],
        [2.0, 2.0],
    ], dtype=np.float64)
    trace = run_mst_trace(X=X, k=2)
    assert trace.final_parity_verified is True
    assert len(trace.final_result.mst_edges) == 3


# =============================================================================
# 3. Explorer Visualization and In-Memory PNG Generation
# =============================================================================
def test_create_kmeans_explorer_figure():
    """Verify Plotly figure generation for K-Means explorer steps."""
    ds = generate_synthetic_dataset(family="blobs", n_samples=20, seed=42, n_clusters=3)
    trace = run_kmeans_trace(X=ds.X, k=3, seed=42)

    # Test init step figure
    fig_init = create_kmeans_explorer_figure(ds.X, trace.steps[0])
    assert len(fig_init.data) >= 1
    assert fig_init.layout.yaxis.scaleanchor == "x"

    # Test converged step figure (contains centroid stars)
    fig_final = create_kmeans_explorer_figure(ds.X, trace.steps[-1])
    assert len(fig_final.data) >= 2


def test_create_mst_explorer_figure():
    """Verify Plotly figure generation for MST explorer steps."""
    ds = generate_synthetic_dataset(family="moons", n_samples=20, seed=42)
    trace = run_mst_trace(X=ds.X, k=2)

    # Test add_edge step figure
    fig_edge = create_mst_explorer_figure(ds.X, trace.steps[5])
    assert len(fig_edge.data) >= 1
    assert fig_edge.layout.yaxis.scaleanchor == "x"

    # Test final step figure
    fig_final = create_mst_explorer_figure(ds.X, trace.steps[-1])
    assert len(fig_final.data) >= 1


def test_render_clustering_png_valid_signature():
    """Verify in-memory Matplotlib clustering figure exports genuine PNG bytes."""
    X = np.array([[0.0, 0.0], [1.0, 1.0], [5.0, 5.0]], dtype=np.float64)
    labels = np.array([0, 0, 1])
    png_bytes = render_clustering_png(X, labels, title="Test Exploration")

    assert isinstance(png_bytes, bytes)
    assert len(png_bytes) > 500
    assert png_bytes.startswith(b"\x89PNG\r\n\x1a\n")


# =============================================================================
# 4. Streamlit AppTest Navigation Views
# =============================================================================
def test_streamlit_apptest_navigates_to_benchmarks_view():
    """AppTest must render the Performance Benchmarks view without errors."""
    try:
        from streamlit.testing.v1 import AppTest
    except ImportError:
        pytest.skip("streamlit.testing.v1.AppTest is not available")

    app_path = str(APP_DIR / "app.py")
    at = AppTest.from_file(app_path, default_timeout=30).run()
    assert not at.exception

    # Select Performance Benchmarks navigation
    radio = at.sidebar.radio(key="main_navigation")
    radio.set_value("Performance Benchmarks").run()
    assert not at.exception

    # Verify header rendered
    subheaders = [s.value for s in at.subheader]
    assert any("Performance Benchmarks" in s for s in subheaders)


def test_streamlit_apptest_navigates_to_algorithm_explorer_view():
    """AppTest must render the Algorithm Explorer view without errors."""
    try:
        from streamlit.testing.v1 import AppTest
    except ImportError:
        pytest.skip("streamlit.testing.v1.AppTest is not available")

    app_path = str(APP_DIR / "app.py")
    at = AppTest.from_file(app_path, default_timeout=30).run()
    assert not at.exception

    # Select Algorithm Explorer navigation
    radio = at.sidebar.radio(key="main_navigation")
    radio.set_value("Algorithm Explorer").run()
    assert not at.exception

    # Verify header rendered and parity text present
    subheaders = [s.value for s in at.subheader]
    assert any("Algorithm Explorer" in s for s in subheaders)
    successes = [s.value for s in at.success]
    assert any("Mathematical Parity Verified" in s for s in successes)
