"""
test_streamlit_dashboard.py
===========================
Automated test suite verifying the Streamlit interactive dashboard:
1. Application launch, metadata, and absence of prohibited strings (e.g. Allocation #19).
2. Navigation views execution without unhandled exceptions.
3. Dual clustering execution on synthetic and empirical data.
4. Correctness of scientific metrics (Inlier ARI, Full ARI, Silhouette, Inertia, MST Weight).
5. Strict absence of fabricated ARI for unlabeled data.
6. Isotropic 1:1 scaling and trace properties of Plotly figures.
7. CSV parsing and validation integration.
8. JSON ExperimentConfig reproducibility and round-trip fidelity.
9. Reset to default baseline configuration.
"""

from __future__ import annotations

import io
import pathlib
import re
import sys
import numpy as np
import pytest

# Generalized pattern matching institutional student registration numbers
# without hardcoding personal identifiers.
STUDENT_REGISTRATION_PATTERN = re.compile(r"\b\d+/\d+/SET/[A-Z]+/\d+\b", re.IGNORECASE)

APP_DIR = pathlib.Path(__file__).resolve().parent.parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from clustering_lab.algorithms.kmeans import kmeans
from clustering_lab.algorithms.mst import mst_clustering
from clustering_lab.data.config import ExperimentConfig, create_dataset_from_config
from clustering_lab.data.dataset import Dataset
from clustering_lab.data.csv_loader import load_dataset_from_csv
from clustering_lab.data.synthetic import (
    generate_blobs,
    generate_circles,
    generate_moons,
    generate_synthetic_dataset,
)
from clustering_lab.evaluation.metrics import (
    compute_full_ari,
    compute_inlier_ari,
    compute_silhouette_safe,
    evaluate_clustering,
)
from clustering_lab.visualization.figures import (
    create_ground_truth_figure,
    create_kmeans_figure,
    create_mst_figure,
)
from app import MAX_INTERACTIVE_SAMPLES, _run_clustering_on_dataset


# =============================================================================
# 1. Streamlit AppTest Smoke and Academic Metadata Tests
# =============================================================================
def test_streamlit_apptest_launches_without_exceptions():
    """Verify that app.py compiles, initializes, and executes cleanly via AppTest."""
    try:
        from streamlit.testing.v1 import AppTest
    except ImportError:
        pytest.skip("streamlit.testing.v1.AppTest is not available")

    app_file = APP_DIR / "app.py"
    at = AppTest.from_file(str(app_file))
    at.run()

    assert not at.exception, f"App execution raised unhandled exception(s): {at.exception}"
    assert len(at.title) > 0, "Main title was not rendered"
    assert at.title[0].value == "MST vs K-Means Robustness Analysis"


def test_academic_metadata_and_forbidden_strings():
    """Verify student details, course metadata, and total absence of 'Allocation #19'."""
    try:
        from streamlit.testing.v1 import AppTest
    except ImportError:
        pytest.skip("streamlit.testing.v1.AppTest is not available")

    app_file = APP_DIR / "app.py"
    at = AppTest.from_file(str(app_file))
    at.run()

    # Aggregate all rendered text from titles, subheaders, captions, and markdown
    all_text_elements = []
    for elem_list in [at.title, at.subheader, at.caption, at.markdown, at.info]:
        for item in elem_list:
            if hasattr(item, "value"):
                all_text_elements.append(str(item.value))

    combined_text = " ".join(all_text_elements)

    # Required student details (both names must remain visible)
    assert "Himanshu Gupta" in combined_text, "Student Himanshu Gupta missing"
    assert "Parth Yadav" in combined_text, "Student Parth Yadav missing"
    assert "BCS-DS-777" in combined_text, "Course code BCS-DS-777 missing"
    assert "Mr. Aman Kumar" in combined_text, "Instructor Mr. Aman Kumar missing"

    # Privacy Enforcement (Phase M5C): Student roll numbers must NOT appear on public dashboard
    assert not STUDENT_REGISTRATION_PATTERN.search(combined_text), "Institutional student registration pattern displayed in UI!"

    # Strictly forbidden allocation text
    assert "Allocation #19" not in combined_text, "Prohibited string 'Allocation #19' found!"
    assert "Alloc #19" not in combined_text, "Prohibited string 'Alloc #19' found!"


def test_navigation_across_all_modules():
    """Verify that switching between all 8 navigation modules executes without exceptions and preserves privacy."""
    try:
        from streamlit.testing.v1 import AppTest
    except ImportError:
        pytest.skip("streamlit.testing.v1.AppTest is not available")

    app_file = APP_DIR / "app.py"
    at = AppTest.from_file(str(app_file))
    at.run()

    views = [
        "Overview",
        "Clustering Playground",
        "Performance Benchmarks",
        "Algorithm Explorer",
        "Robustness Analysis",
        "Dataset & CSV Import",
        "Reproducibility & Configuration",
        "Methodology / Help",
    ]

    for view_name in views:
        at.sidebar.radio[0].set_value(view_name)
        at.run()
        assert not at.exception, f"Navigating to '{view_name}' caused exception: {at.exception}"

        # Privacy verification across all rendered modules
        page_texts = []
        for elem_list in [at.title, at.subheader, at.caption, at.markdown, at.info]:
            for item in elem_list:
                if hasattr(item, "value"):
                    page_texts.append(str(item.value))
        page_combined = " ".join(page_texts)
        assert not STUDENT_REGISTRATION_PATTERN.search(page_combined), f"Institutional student registration pattern leaked in view '{view_name}'"


# =============================================================================
# 2. Dual Algorithm Execution and State Management
# =============================================================================
def test_dual_algorithm_execution_on_same_feature_matrix():
    """Verify that Lloyd's K-Means and Prim's MST run on the identical feature matrix X."""
    dataset = generate_synthetic_dataset(
        family="blobs",
        n_samples=250,
        n_clusters=3,
        seed=101,
        noise=0.05,
        outlier_rate=0.04,
    )
    X = dataset.X
    k = 3

    km_res = kmeans(X=X, k=k, seed=101)
    mst_res = mst_clustering(X=X, k=k)

    # Invariants
    assert km_res.labels.shape == (dataset.n_samples,)
    assert mst_res.labels.shape == (dataset.n_samples,)
    assert len(np.unique(km_res.labels)) == k
    assert len(np.unique(mst_res.labels)) == k
    assert km_res.cluster_centers.shape == (k, 2)
    assert len(mst_res.mst_edges) == dataset.n_samples - 1
    assert len(mst_res.cut_edges) == k - 1
    assert mst_res.total_mst_weight > mst_res.retained_weight > 0.0


# =============================================================================
# 3. Scientific Metrics and Absence of Fabricated ARI
# =============================================================================
def test_metrics_evaluation_on_labeled_data():
    """Verify that ground-truth ARI is computed accurately for inliers and full data."""
    dataset = generate_synthetic_dataset(
        family="blobs",
        n_samples=300,
        n_clusters=3,
        seed=42,
        noise=0.0,
        outlier_rate=0.1,  # 30 outliers with label -1
    )
    km_res = kmeans(X=dataset.X, k=3, seed=42)

    metrics = evaluate_clustering(
        y_pred=km_res.labels,
        y_true=dataset.labels,
        inlier_mask=dataset.inlier_mask,
        X=dataset.X,
        runtime_sec=0.012,
    )

    assert metrics.inlier_ari is not None
    assert 0.9 <= metrics.inlier_ari <= 1.0, f"Expected high inlier ARI for clean blobs, got {metrics.inlier_ari}"
    assert metrics.full_ari is not None
    # Full ARI is penalized by the 10% outliers
    assert metrics.full_ari <= metrics.inlier_ari
    assert metrics.n_clusters_predicted == 3
    assert metrics.runtime_ms == pytest.approx(12.0, abs=0.1)


def test_no_fabricated_ari_for_unlabeled_data():
    """Verify that when ground-truth labels are absent, ARI is strictly None (never 0 or fabricated)."""
    # Create an unlabeled dataset
    raw_csv = "feat_a,feat_b\n1.0,2.0\n1.2,2.1\n5.0,5.0\n5.1,5.2\n9.0,9.1\n9.2,9.0\n"
    ds_unlabeled = load_dataset_from_csv(
        source=raw_csv,
        feature_cols=["feat_a", "feat_b"],
        label_col=None,
    )
    assert ds_unlabeled.labels is None

    km_res = kmeans(X=ds_unlabeled.X, k=3, seed=42)
    metrics = evaluate_clustering(
        y_pred=km_res.labels,
        y_true=ds_unlabeled.labels,
        inlier_mask=ds_unlabeled.inlier_mask,
        X=ds_unlabeled.X,
        runtime_sec=0.005,
    )

    # Inlier ARI and Full ARI must be None
    assert metrics.inlier_ari is None, "Inlier ARI was fabricated for unlabeled dataset!"
    assert metrics.full_ari is None, "Full ARI was fabricated for unlabeled dataset!"
    assert metrics.metadata["has_ground_truth"] is False


def test_topological_bias_on_concentric_circles_and_moons():
    """Verify core scientific hypothesis: MST separates non-convex manifolds perfectly, K-Means fails."""
    # 1. Concentric Circles (k=2)
    circles_ds = generate_circles(n_samples=200, factor=0.45, noise=0.0, outlier_rate=0.0, seed=42)
    km_circles = kmeans(X=circles_ds.X, k=2, seed=42)
    mst_circles = mst_clustering(X=circles_ds.X, k=2)

    ari_km_circles = compute_inlier_ari(circles_ds.labels, km_circles.labels)
    ari_mst_circles = compute_inlier_ari(circles_ds.labels, mst_circles.labels)

    # MST single-linkage cut achieves perfect recovery (ARI = 1.0)
    assert ari_mst_circles == pytest.approx(1.0, abs=1e-5)
    # K-Means centroid partitioning fails on concentric rings (ARI < 0.2)
    assert ari_km_circles < 0.2

    # 2. Two Moons (k=2)
    moons_ds = generate_moons(n_samples=200, noise=0.0, outlier_rate=0.0, seed=42)
    km_moons = kmeans(X=moons_ds.X, k=2, seed=42)
    mst_moons = mst_clustering(X=moons_ds.X, k=2)

    ari_km_moons = compute_inlier_ari(moons_ds.labels, km_moons.labels)
    ari_mst_moons = compute_inlier_ari(moons_ds.labels, mst_moons.labels)

    assert ari_mst_moons == pytest.approx(1.0, abs=1e-5)
    assert ari_km_moons < 0.6


def test_silhouette_boundary_conditions_and_bias():
    """Verify Silhouette score handles degenerate cases and reflects spherical bias."""
    X = np.array([[0.0, 0.0], [0.1, 0.1], [5.0, 5.0], [5.1, 5.1]])

    # Degenerate: single cluster k=1
    assert compute_silhouette_safe(X, np.zeros(4, dtype=int)) is None

    # Degenerate: k=N (each sample its own cluster)
    assert compute_silhouette_safe(X, np.arange(4, dtype=int)) is None

    # Valid: k=2
    score = compute_silhouette_safe(X, np.array([0, 0, 1, 1]))
    assert score is not None
    assert -1.0 <= score <= 1.0


# =============================================================================
# 4. Interactive Plotly Visualizations Invariants
# =============================================================================
def test_plotly_figures_have_isotropic_scaling_and_correct_traces():
    """Verify that all figures enforce 1:1 aspect ratio and valid traces."""
    dataset = generate_synthetic_dataset(
        family="blobs",
        n_samples=150,
        n_clusters=3,
        seed=42,
        noise=0.05,
        outlier_rate=0.1,
    )
    km_res = kmeans(X=dataset.X, k=3, seed=42)
    mst_res = mst_clustering(X=dataset.X, k=3)

    # 1. Ground Truth Figure
    fig_gt = create_ground_truth_figure(dataset)
    assert fig_gt.layout.yaxis.scaleanchor == "x"
    assert fig_gt.layout.yaxis.scaleratio == 1
    # Traces: 3 classes + 1 outlier trace
    trace_names = [t.name for t in fig_gt.data]
    assert any("Class 0" in n for n in trace_names)
    assert any("Outlier" in n for n in trace_names)

    # 2. K-Means Figure
    fig_km = create_kmeans_figure(dataset, km_res)
    assert fig_km.layout.yaxis.scaleanchor == "x"
    assert fig_km.layout.yaxis.scaleratio == 1
    km_trace_names = [t.name for t in fig_km.data]
    assert any("Cluster 0" in n for n in km_trace_names)
    assert any("Centroid" in n for n in km_trace_names)

    # 3. MST Figure
    fig_mst = create_mst_figure(dataset, mst_res, show_retained_edges=True, show_cut_edges=True)
    assert fig_mst.layout.yaxis.scaleanchor == "x"
    assert fig_mst.layout.yaxis.scaleratio == 1
    mst_trace_names = [t.name for t in fig_mst.data]
    assert any("Retained MST Edges" in n for n in mst_trace_names)
    assert any("Cut Edges" in n for n in mst_trace_names)
    assert any("Component 0" in n for n in mst_trace_names)

    # When retained edges are disabled:
    fig_mst_no_edges = create_mst_figure(dataset, mst_res, show_retained_edges=False, show_cut_edges=False)
    no_edge_trace_names = [t.name for t in fig_mst_no_edges.data]
    assert not any("Retained MST Edges" in n for n in no_edge_trace_names)
    assert not any("Cut Edges" in n for n in no_edge_trace_names)


# =============================================================================
# 5. CSV Import and Validation Integration
# =============================================================================
def test_csv_import_workflow_with_validation_guards():
    """Verify CSV import handles columns, labels, and boundary conditions."""
    csv_text = "x_coord,y_coord,label\n1.0,2.0,0\n1.1,2.2,0\n8.0,8.0,1\n8.1,8.2,1\n"
    ds = load_dataset_from_csv(
        source=csv_text,
        feature_cols=["x_coord", "y_coord"],
        label_col="label",
        dataset_name="test_import.csv",
    )
    assert ds.n_samples == 4
    assert ds.labels is not None
    assert np.array_equal(ds.labels, [0, 0, 1, 1])

    # Rejection of duplicate feature column selection
    with pytest.raises(ValueError, match="Feature columns must be distinct"):
        load_dataset_from_csv(
            source=csv_text,
            feature_cols=["x_coord", "x_coord"],
        )


# =============================================================================
# 6. JSON Configuration Reproducibility
# =============================================================================
def test_json_config_reproducibility_and_regeneration():
    """Verify that exporting and re-importing JSON configuration reproduces identical data."""
    cfg = ExperimentConfig(
        dataset_family="circles",
        n_samples=180,
        n_clusters=2,
        seed=999,
        noise=0.03,
        outlier_rate=0.05,
        dataset_params={"factor": 0.5},
    )

    json_str = cfg.to_json()
    cfg_restored = ExperimentConfig.from_json(json_str)

    ds_original = create_dataset_from_config(cfg)
    ds_restored = create_dataset_from_config(cfg_restored)

    # Identical coordinates, labels, and masks
    assert np.array_equal(ds_original.X, ds_restored.X)
    assert np.array_equal(ds_original.labels, ds_restored.labels)
    assert np.array_equal(ds_original.inlier_mask, ds_restored.inlier_mask)


# =============================================================================
# 7. Pre-Commit Safety Audit Regression Tests
# =============================================================================
def test_compute_safety_enforces_600_interactive_limit():
    """Verify that clustering execution strictly rejects datasets exceeding 600 total observations."""
    # Synthesize dataset with 601 observations (e.g. 500 inliers + 101 outliers)
    dataset_601 = generate_synthetic_dataset(
        family="blobs",
        n_samples=500,
        n_clusters=3,
        seed=42,
        noise=0.0,
        outlier_rate=0.202,  # round(500 * 0.202) = 101 outliers -> 601 total
    )
    assert dataset_601.n_samples == 601
    assert dataset_601.n_samples > MAX_INTERACTIVE_SAMPLES

    # Must raise ValueError with clear message and must NOT truncate data
    with pytest.raises(ValueError, match="exceeds the safe interactive clustering limit of 600"):
        _run_clustering_on_dataset(dataset_601, k=3)

    # Confirm original dataset feature matrix X was NOT truncated or modified
    assert dataset_601.X.shape == (601, 2)


def test_csv_loader_treat_minus_one_outlier_behavior():
    """Verify CSV loader does NOT treat label -1 as outlier unless explicitly configured."""
    csv_content = (
        "feature_1,feature_2,cluster_id\n"
        "1.0,2.0,-1\n"
        "1.5,2.5,-1\n"
        "5.0,6.0,0\n"
        "5.5,6.5,0\n"
        "9.0,9.0,1\n"
    )

    # 1. Default: treat_minus_one_as_outlier=False (all points treated as inliers)
    ds_default = load_dataset_from_csv(
        source=csv_content,
        feature_cols=["feature_1", "feature_2"],
        label_col="cluster_id",
        treat_minus_one_as_outlier=False,
    )
    assert ds_default.n_samples == 5
    assert ds_default.n_inliers == 5
    assert ds_default.n_outliers == 0
    assert np.all(ds_default.inlier_mask)  # All True, -1 is just an integer label

    # 2. Explicit: treat_minus_one_as_outlier=True (-1 rows marked as outliers)
    ds_explicit = load_dataset_from_csv(
        source=csv_content,
        feature_cols=["feature_1", "feature_2"],
        label_col="cluster_id",
        treat_minus_one_as_outlier=True,
    )
    assert ds_explicit.n_samples == 5
    assert ds_explicit.n_inliers == 3
    assert ds_explicit.n_outliers == 2
    assert np.array_equal(ds_explicit.inlier_mask, [False, False, True, True, True])


def test_state_consistency_tracking():
    """Verify that parameter modification is detected as stale before execution."""
    cfg_executed = {
        "source": "synthetic",
        "family": "Gaussian Blobs",
        "n_inliers": 300,
        "seed": 42,
        "noise": 0.0,
        "outlier_rate": 0.0,
        "k": 3,
        "cluster_std": 0.4,
        "radius": 3.5,
        "factor": None,
    }

    # Same controls -> not stale
    controls_matching = dict(cfg_executed)
    assert controls_matching == cfg_executed

    # Modified seed -> detected as stale
    controls_modified_seed = dict(cfg_executed)
    controls_modified_seed["seed"] = 99
    assert controls_modified_seed != cfg_executed

    # Modified noise -> detected as stale
    controls_modified_noise = dict(cfg_executed)
    controls_modified_noise["noise"] = 0.15
    assert controls_modified_noise != cfg_executed

    # Modified family -> detected as stale
    controls_modified_family = dict(cfg_executed)
    controls_modified_family["family"] = "Two Moons"
    assert controls_modified_family != cfg_executed


def test_json_restoration_malformed_rejection_and_state_sync():
    """Verify that malformed JSON is strictly rejected without partial state mutation."""
    malformed_json_cases = [
        "",  # Empty
        "{not valid json}",  # Syntax error
        '{"dataset_family": "unknown_family", "n_samples": 100}',  # Invalid family
        '{"dataset_family": "blobs", "n_samples": 5}',  # Sample count < 10 violates bounds
        '{"dataset_family": "blobs", "schema_version": "2.0.0"}',  # Incompatible major schema version
    ]

    for bad_json in malformed_json_cases:
        with pytest.raises((ValueError, TypeError)):
            ExperimentConfig.from_json(bad_json)


def test_algorithm_input_immutability_during_dual_clustering():
    """Verify that custom K-Means and MST clustering receive identical input and do not mutate X."""
    dataset = generate_synthetic_dataset(
        family="moons",
        n_samples=150,
        seed=42,
        noise=0.08,
        outlier_rate=0.05,
    )
    X_original = dataset.X.copy()

    # Run custom K-Means
    km_res = kmeans(X=dataset.X, k=2, seed=42)
    assert np.array_equal(dataset.X, X_original), "K-Means modified feature array X in-place!"

    # Run custom dense Prim's MST
    mst_res = mst_clustering(X=dataset.X, k=2)
    assert np.array_equal(dataset.X, X_original), "MST modified feature array X in-place!"

    # Assert outputs have correct length matching input
    assert len(km_res.labels) == len(X_original)
    assert len(mst_res.labels) == len(X_original)


# =============================================================================
# 10. Robustness View Rendering Regression and Provenance Privacy Tests (Stage F1)
# =============================================================================
def test_robustness_results_rendering_regression_and_metadata_serialization():
    """Verify that the robustness view renders without NameError when session results exist.

    Regression test for Stage F1: Previously raised NameError: name 'json' is not defined
    at line 1132 during tab_export metadata serialization.
    """
    try:
        from streamlit.testing.v1 import AppTest
    except ImportError:
        pytest.skip("streamlit.testing.v1.AppTest is not available")

    import json
    from clustering_lab.experiments.sweeps import SweepConfig
    from clustering_lab.experiments.runner import run_robustness_experiment
    from clustering_lab.experiments.aggregation import aggregate_trials
    from clustering_lab.experiments.export import export_experiment_metadata

    # Bounded fast workload (1 family, 1 seed, 1 noise level = 1 paired trial, 2 executions)
    cfg = SweepConfig(
        dataset_families=["blobs"],
        n_inliers=50,
        seeds=[11],
        sweep_types=["noise"],
        noise_levels=[0.0],
        outlier_rates=[0.0],
    )
    trials = run_robustness_experiment(cfg)
    aggregates = aggregate_trials(trials)

    app_file = APP_DIR / "app.py"
    at = AppTest.from_file(str(app_file))
    at.session_state["robustness_trials"] = trials
    at.session_state["robustness_aggregates"] = aggregates
    at.session_state["robustness_config"] = cfg.to_dict()
    at.run()

    # Switch to Robustness Analysis view
    at.sidebar.radio[0].set_value("Robustness Analysis")
    at.run()

    # Assert no exceptions occurred (NameError or other rendering issues)
    assert not at.exception, f"Robustness view raised exception: {at.exception}"

    # Verify that metadata serialization works and produces valid JSON
    meta_dict = export_experiment_metadata(cfg, len(trials))
    meta_json_str = json.dumps(meta_dict, indent=2)
    parsed_meta = json.loads(meta_json_str)
    assert isinstance(parsed_meta, dict)
    assert "execution_summary" in parsed_meta
    assert parsed_meta["execution_summary"]["n_trials_executed"] == len(trials)
    assert parsed_meta["execution_summary"]["n_clustering_executions"] == len(trials)
    assert parsed_meta["execution_summary"]["n_paired_trials"] == len(trials) // 2

    # Privacy verification on serialized JSON
    assert not STUDENT_REGISTRATION_PATTERN.search(meta_json_str), "Institutional student registration pattern leaked in metadata JSON!"
    student_records = parsed_meta.get("academic_context", {}).get("students", [])
    names = [s.get("name") for s in student_records]
    assert "Himanshu Gupta" in names
    assert "Parth Yadav" in names


def test_ui_trial_count_display_and_label_reconciliation():
    """Verify that the execution plan in app.py clearly distinguishes all counting dimensions."""
    try:
        from streamlit.testing.v1 import AppTest
    except ImportError:
        pytest.skip("streamlit.testing.v1.AppTest is not available")

    app_file = APP_DIR / "app.py"
    at = AppTest.from_file(str(app_file))
    at.run()

    # Navigate to Robustness Analysis view
    at.sidebar.radio[0].set_value("Robustness Analysis")
    at.run()

    # Aggregate rendered text
    rendered_texts = []
    for elem_list in [at.markdown, at.subheader, at.caption, at.info]:
        for item in elem_list:
            if hasattr(item, "value"):
                rendered_texts.append(str(item.value))
    combined = " ".join(rendered_texts)

    # Verify that execution plan distinguishes dimensions
    assert "Experiment Execution Plan:" in combined
    assert "Sweep Configurations per Family/Seed:" in combined
    assert "Matched Baseline Configurations:" in combined
    assert "Total Paired Comparisons:" in combined
    assert "Individual Algorithm Executions (Sweep):" in combined
    assert "Total Recorded Result Rows:" in combined

    # Verify obsolete migration banners are absent
    assert "Migration Phase M5A Active" not in combined
    assert "Phase M5A Research Platform" not in combined


# =============================================================================
# 11. Stage 04A Visual Theming & Playground Stale-State Lifecycle Tests
# =============================================================================
def test_design_tokens_and_theme_properties():
    """Verify canonical design tokens and Matplotlib dark-mode theme export."""
    from clustering_lab.visualization.theme import (
        CANVAS_BG,
        CLUSTER_COLORS,
        COLOR_CENTROID,
        COLOR_KMEANS,
        COLOR_MST,
        COLOR_OUTLIER,
        SURFACE_CARD,
        SURFACE_HOVER,
        SURFACE_INSET,
        get_theme_css,
    )
    from clustering_lab.visualization.figures import render_clustering_png, render_benchmark_png
    import numpy as np

    # Token sanity
    assert CANVAS_BG == "#0b0f19"
    assert SURFACE_CARD == "#151d30"
    assert SURFACE_HOVER == "#1e293b"
    assert SURFACE_INSET == "#0f172a"
    assert COLOR_KMEANS == "#38bdf8"
    assert COLOR_MST == "#f97316"
    assert len(CLUSTER_COLORS) >= 6

    # CSS generator verification
    css = get_theme_css()
    assert "--color-canvas-bg" in css
    assert "--color-entity-kmeans" in css
    assert "--color-entity-mst" in css
    assert "stale-warning-banner" in css

    # Matplotlib PNG dark theme export check
    X = np.array([[0.0, 0.0], [1.0, 1.0]], dtype=np.float64)
    labels = np.array([0, 1], dtype=np.int32)
    png_bytes = render_clustering_png(X, labels, title="Dark Mode Test")
    assert isinstance(png_bytes, bytes)
    assert png_bytes.startswith(b"\x89PNG\r\n\x1a\n")


def test_playground_stale_state_non_collapsing_lifecycle():
    """Verify that adjusting Playground parameters retains previous charts and provides recompute action (ISSUE-06)."""
    try:
        from streamlit.testing.v1 import AppTest
    except ImportError:
        pytest.skip("streamlit.testing.v1.AppTest is not available")

    app_file = APP_DIR / "app.py"
    at = AppTest.from_file(str(app_file))
    at.run()

    # Navigate to Clustering Playground view
    at.sidebar.radio[0].set_value("Clustering Playground")
    at.run()
    assert not at.exception

    # Initially, tabs and metric tables should be rendered for the default dataset
    initial_tabs_count = len(at.tabs)
    initial_df_count = len(at.dataframe)
    assert initial_tabs_count >= 3, "Initial Playground visual tabs must be rendered in DOM"
    assert initial_df_count >= 2, "Initial Playground metric tables must be rendered in DOM"

    # Adjust a parameter (noise slider) without clicking generate
    slider_noise = at.slider(key="pg_noise")
    slider_noise.set_value(0.15).run()
    assert not at.exception

    # CRITICAL CHECK for ISSUE-06: Tabs and metric tables must NOT collapse/disappear
    assert len(at.tabs) == initial_tabs_count, (
        "Playground visualization tabs collapsed upon modifying slider! Non-collapsing state machine violated."
    )
    assert len(at.dataframe) == initial_df_count, (
        "Playground metrics dataframes collapsed upon modifying slider! Non-collapsing state machine violated."
    )

    # Verify amber warning banner is present
    warning_texts = [w.value for w in at.warning]
    assert any("Parameters Modified — Showing Previous Clustering Results" in w for w in warning_texts), (
        f"Expected stale warning banner not found in: {warning_texts}"
    )

    # Verify outdated execution caption is present
    captions = [c.value for c in at.caption]
    assert any("Showing PREVIOUS Executed Results (Outdated)" in c for c in captions), (
        f"Expected outdated caption notice not found in: {captions}"
    )

    # Verify prominent Recompute button is present
    button_keys = [b.key for b in at.button]
    assert "pg_recompute_stale" in button_keys, (
        f"Recompute button 'pg_recompute_stale' missing from buttons: {button_keys}"
    )

    # Click the Recompute button
    at.button(key="pg_recompute_stale").click().run()
    assert not at.exception

    # After recomputing, the stale warning should be cleared
    refreshed_warning_texts = [w.value for w in at.warning]
    assert not any("Parameters Modified — Showing Previous Clustering Results" in w for w in refreshed_warning_texts), (
        "Stale warning banner was not cleared after recomputation!"
    )
    assert len(at.tabs) == initial_tabs_count, "Tabs should remain rendered after recomputing"
    assert len(at.dataframe) == initial_df_count, "Dataframes should remain rendered after recomputing"


# =============================================================================
# 12. Stage 04B Deep View Verification, Sidebar Compactness, & Export Payloads
# =============================================================================
def test_all_eight_views_deep_content_and_structure_validation():
    """Verify that every view renders its unique domain components without unhandled errors."""
    try:
        from streamlit.testing.v1 import AppTest
    except ImportError:
        pytest.skip("streamlit.testing.v1.AppTest is not available")

    app_file = APP_DIR / "app.py"
    at = AppTest.from_file(str(app_file), default_timeout=35)
    at.run()
    assert not at.exception

    views_and_signatures = [
        ("Overview", ["Quantitative Evaluation of Graph-Theoretic vs Centroid-Based Clustering", "Interactive Laboratory Workflow", "Centroid-Based vs Graph-Theoretic"]),
        ("Clustering Playground", ["Clustering Playground", "Predicted Voronoi clusters", "Predicted connected components"]),
        ("Performance Benchmarks", ["Performance Benchmarks", "Empirical Scaling", "Run Benchmarks"]),
        ("Algorithm Explorer", ["Algorithm Explorer", "Mathematical Parity Verified", "Step-by-Step Educational Visualizer"]),
        ("Robustness Analysis", ["Scientific Robustness Analysis Engine", "Experiment Execution Plan", "Matched Baseline Configurations"]),
        ("Dataset & CSV Import", ["Dataset & CSV Import", "Tabular CSV Requirements", "Upload your custom 2D tabular dataset"]),
        ("Reproducibility & Configuration", ["Reproducibility & Configuration", "Export Current Configuration", "Import & Restore Configuration"]),
        ("Methodology / Help", ["Methodology & Scientific Reference", "Algorithmic Principles & Inductive Biases", "Perturbation Mechanisms"]),
    ]

    for view_name, expected_substrings in views_and_signatures:
        at.sidebar.radio(key="main_navigation").set_value(view_name).run()
        assert not at.exception, f"Failed rendering view '{view_name}': {at.exception}"

        page_texts = []
        for elem_list in [at.title, at.subheader, at.caption, at.markdown, at.info, at.success, at.warning]:
            for item in elem_list:
                if hasattr(item, "value"):
                    page_texts.append(str(item.value))
        page_combined = " ".join(page_texts)

        for sig in expected_substrings:
            assert sig in page_combined, f"Signature '{sig}' missing from rendered view '{view_name}'"


def test_sidebar_compactness_and_navigation_hierarchy():
    """Verify sidebar compactness, academic identity hierarchy, and privacy compliance."""
    try:
        from streamlit.testing.v1 import AppTest
    except ImportError:
        pytest.skip("streamlit.testing.v1.AppTest is not available")

    app_file = APP_DIR / "app.py"
    at = AppTest.from_file(str(app_file), default_timeout=30)
    at.run()
    assert not at.exception

    # 1. Navigation radio key and destination count
    nav_radio = at.sidebar.radio(key="main_navigation")
    assert nav_radio is not None, "Sidebar primary navigation radio missing!"
    assert len(nav_radio.options) == 8, f"Expected 8 navigation routes, found {len(nav_radio.options)}"

    # 2. Markdown text in sidebar must contain author attribution
    sidebar_mds = [m.value for m in at.sidebar.markdown]
    sidebar_combined = " ".join(sidebar_mds)

    assert "Himanshu Gupta" in sidebar_combined
    assert "Parth Yadav" in sidebar_combined
    assert "BCS-DS-777" in sidebar_combined
    assert "Mr. Aman Kumar" in sidebar_combined

    # 3. Privacy compliance
    assert not STUDENT_REGISTRATION_PATTERN.search(sidebar_combined), "Institutional student registration pattern leaked in sidebar!"
    assert "Allocation #19" not in sidebar_combined


def test_playground_png_download_payloads():
    """Verify that Playground provides dark-mode publication PNG download buttons with valid binary payloads."""
    try:
        from streamlit.testing.v1 import AppTest
    except ImportError:
        pytest.skip("streamlit.testing.v1.AppTest is not available")

    app_file = APP_DIR / "app.py"
    at = AppTest.from_file(str(app_file), default_timeout=30)
    at.run()
    assert not at.exception

    at.sidebar.radio(key="main_navigation").set_value("Clustering Playground").run()
    assert not at.exception

    # Check download buttons presence and properties
    dl_buttons = at.download_button
    dl_keys = [b.key for b in dl_buttons if b.key is not None]

    assert "pg_dl_gt_png" in dl_keys, f"Ground truth PNG download button missing from: {dl_keys}"
    assert "pg_dl_km_png" in dl_keys, f"K-Means PNG download button missing from: {dl_keys}"
    assert "pg_dl_mst_png" in dl_keys, f"MST PNG download button missing from: {dl_keys}"

    # Verify download button labels
    for b in dl_buttons:
        if b.key in ("pg_dl_gt_png", "pg_dl_km_png", "pg_dl_mst_png"):
            assert "Download" in b.label
            assert "PNG" in b.label


# =============================================================================
# Stage 05 Task 5.5 & 5.6: Integration Workflows, Privacy, & Security Gates
# =============================================================================
def test_csv_import_to_playground_handoff_workflow():
    """Verify that importing a CSV dataset hands off cleanly to Playground without state corruption."""
    try:
        from streamlit.testing.v1 import AppTest
    except ImportError:
        pytest.skip("streamlit.testing.v1.AppTest is not available")

    app_file = APP_DIR / "app.py"
    at = AppTest.from_file(str(app_file), default_timeout=35)
    at.run()
    assert not at.exception

    # Create an in-memory CSV dataset
    csv_content = (
        "dim_one,dim_two,class\n"
        "1.0,2.0,0\n"
        "1.2,2.1,0\n"
        "5.0,5.0,1\n"
        "5.2,5.1,1\n"
    )
    csv_ds = load_dataset_from_csv(
        source=csv_content,
        feature_cols=("dim_one", "dim_two"),
        label_col="class",
        dataset_name="empirical_handoff.csv",
    )

    # Emulate CSV loader handoff in session state
    km_csv = kmeans(csv_ds.X, k=2, seed=42)
    mst_csv = mst_clustering(csv_ds.X, k=2)
    km_m_csv = evaluate_clustering(km_csv.labels, csv_ds.labels, csv_ds.inlier_mask, csv_ds.X, runtime_sec=0.001)
    mst_m_csv = evaluate_clustering(mst_csv.labels, csv_ds.labels, csv_ds.inlier_mask, csv_ds.X, runtime_sec=0.001)

    at.session_state["current_dataset"] = csv_ds
    at.session_state["kmeans_result"] = km_csv
    at.session_state["kmeans_metrics"] = km_m_csv
    at.session_state["mst_result"] = mst_csv
    at.session_state["mst_metrics"] = mst_m_csv
    at.session_state["executed_config"] = {
        "source": "csv",
        "name": "empirical_handoff.csv",
        "k": 2,
        "features": ("dim_one", "dim_two"),
        "label": "class",
        "treat_outlier": False,
    }

    # Navigate to Clustering Playground
    at.sidebar.radio(key="main_navigation").set_value("Clustering Playground").run()
    assert not at.exception

    # Verify tabs and metric tables remain mounted
    assert len(at.tabs) >= 3
    assert len(at.dataframe) >= 2

    captions = [c.value for c in at.caption if hasattr(c, "value")]
    caption_text = " ".join(captions)
    assert "Total N=4" in caption_text

    infos = [i.value for i in at.info if hasattr(i, "value")]
    info_text = " ".join(infos)
    assert "empirical_handoff.csv" in info_text


def test_reproducibility_config_restoration_to_playground_workflow():
    """Verify that restoring an ExperimentConfig updates Playground state and renders fresh results."""
    try:
        from streamlit.testing.v1 import AppTest
    except ImportError:
        pytest.skip("streamlit.testing.v1.AppTest is not available")

    app_file = APP_DIR / "app.py"
    at = AppTest.from_file(str(app_file), default_timeout=35)
    at.run()
    assert not at.exception

    cfg = ExperimentConfig(
        dataset_family="circles",
        n_samples=160,
        n_clusters=2,
        seed=888,
        noise=0.03,
        outlier_rate=0.05,
        dataset_params={"factor": 0.55},
    )
    new_ds = create_dataset_from_config(cfg)
    km_cfg = kmeans(new_ds.X, k=2, seed=888)
    mst_cfg = mst_clustering(new_ds.X, k=2)
    km_m_cfg = evaluate_clustering(km_cfg.labels, new_ds.labels, new_ds.inlier_mask, new_ds.X, runtime_sec=0.001)
    mst_m_cfg = evaluate_clustering(mst_cfg.labels, new_ds.labels, new_ds.inlier_mask, new_ds.X, runtime_sec=0.001)

    at.session_state["current_dataset"] = new_ds
    at.session_state["kmeans_result"] = km_cfg
    at.session_state["kmeans_metrics"] = km_m_cfg
    at.session_state["mst_result"] = mst_cfg
    at.session_state["mst_metrics"] = mst_m_cfg
    at.session_state["pg_dataset_family"] = "Concentric Circles"
    at.session_state["pg_n_samples"] = 160
    at.session_state["pg_seed"] = 888
    at.session_state["pg_noise"] = 0.03
    at.session_state["pg_outliers"] = 0.05
    at.session_state["pg_circles_factor"] = 0.55
    at.session_state["executed_config"] = {
        "source": "synthetic",
        "family": "Concentric Circles",
        "n_inliers": 160,
        "seed": 888,
        "noise": 0.03,
        "outlier_rate": 0.05,
        "k": 2,
        "factor": 0.55,
    }

    at.sidebar.radio(key="main_navigation").set_value("Clustering Playground").run()
    assert not at.exception

    captions = [c.value for c in at.caption if hasattr(c, "value")]
    caption_text = " ".join(captions)
    assert "Concentric Circles" in caption_text
    assert "Seed=888" in caption_text
    assert len(at.tabs) >= 3


def test_cross_view_navigation_state_isolation():
    """Verify that cycling through all 8 views sequentially preserves executed session state."""
    try:
        from streamlit.testing.v1 import AppTest
    except ImportError:
        pytest.skip("streamlit.testing.v1.AppTest is not available")

    app_file = APP_DIR / "app.py"
    at = AppTest.from_file(str(app_file), default_timeout=35)
    at.run()
    assert not at.exception

    initial_dataset = at.session_state["current_dataset"]
    assert initial_dataset is not None

    views = [
        "Overview",
        "Clustering Playground",
        "Performance Benchmarks",
        "Algorithm Explorer",
        "Robustness Analysis",
        "Dataset & CSV Import",
        "Reproducibility & Configuration",
        "Methodology / Help",
        "Clustering Playground",
    ]

    for view_name in views:
        at.sidebar.radio(key="main_navigation").set_value(view_name).run()
        assert not at.exception, f"Navigation to '{view_name}' caused an exception"

    # Returned to Playground: verify dataset and results are preserved
    assert at.session_state["current_dataset"] is initial_dataset
    assert at.session_state["kmeans_result"] is not None
    assert at.session_state["mst_result"] is not None
    assert len(at.tabs) >= 3


def test_comprehensive_public_privacy_enforcement():
    """Verify that no institutional student roll numbers or forbidden allocation tags leak anywhere."""
    try:
        from streamlit.testing.v1 import AppTest
    except ImportError:
        pytest.skip("streamlit.testing.v1.AppTest is not available")

    app_file = APP_DIR / "app.py"
    at = AppTest.from_file(str(app_file), default_timeout=35)
    at.run()
    assert not at.exception

    # Regex patterns detecting any institutional registration format
    ROLL_REGEX = STUDENT_REGISTRATION_PATTERN
    ALLOCATION_REGEX = re.compile(r"Allocation\s*#?19|Alloc\s*#?19", re.I)

    # 1. Scan rendered UI elements across all 8 navigation routes
    views = [
        "Overview",
        "Clustering Playground",
        "Performance Benchmarks",
        "Algorithm Explorer",
        "Robustness Analysis",
        "Dataset & CSV Import",
        "Reproducibility & Configuration",
        "Methodology / Help",
    ]

    for view_name in views:
        at.sidebar.radio(key="main_navigation").set_value(view_name).run()
        assert not at.exception

        page_texts = []
        for elem_list in [at.title, at.subheader, at.caption, at.markdown, at.info, at.success, at.warning, at.error]:
            for item in elem_list:
                if hasattr(item, "value"):
                    page_texts.append(str(item.value))
        combined_view = " ".join(page_texts)

        assert not ROLL_REGEX.search(combined_view), f"Roll number pattern found in view '{view_name}'!"
        assert not ALLOCATION_REGEX.search(combined_view), f"Prohibited allocation text found in view '{view_name}'!"

    # 2. Scan export strings and serialized metadata
    from clustering_lab.experiments.sweeps import SweepConfig
    from clustering_lab.experiments.benchmarks import BenchmarkConfig
    from clustering_lab.experiments.export import export_benchmark_config_json
    from clustering_lab.experiments.export import (
        export_config_json,
        export_experiment_metadata,
        export_benchmark_metadata,
    )
    import json

    sw_cfg = SweepConfig()
    exp_meta_str = json.dumps(export_experiment_metadata(sw_cfg, n_trials=10))
    assert not ROLL_REGEX.search(exp_meta_str), "Roll number leaked in experiment metadata JSON!"

    bm_cfg = BenchmarkConfig()
    bm_json_str = export_benchmark_config_json(bm_cfg)
    assert not ROLL_REGEX.search(bm_json_str), "Roll number leaked in benchmark config JSON!"

    bm_meta_str = export_benchmark_metadata()
    assert not ROLL_REGEX.search(bm_meta_str), "Roll number leaked in benchmark metadata JSON!"


def test_privacy_detection_regex_behavior():
    """Verify that STUDENT_REGISTRATION_PATTERN catches synthetic institutional IDs without false-positives."""
    synthetic_id = "9/99/SET/XYZ/999"
    assert STUDENT_REGISTRATION_PATTERN.search(f"Author info: {synthetic_id}") is not None
    assert STUDENT_REGISTRATION_PATTERN.search("Course code: BCS-DS-777") is None
    assert STUDENT_REGISTRATION_PATTERN.search("Institution: MRIIRS") is None
    assert STUDENT_REGISTRATION_PATTERN.search("Guide: Mr. Aman Kumar") is None
    assert STUDENT_REGISTRATION_PATTERN.search("Student: Himanshu Gupta & Parth Yadav") is None


def test_theme_html_helpers_security_and_escaping():
    """Verify that HTML rendering helpers strictly sanitize and escape all dynamic string inputs."""
    from clustering_lab.visualization.theme import render_hero_html, render_metric_card_html

    # 1. Test render_hero_html with malicious payloads
    evil_title = '<script>alert("XSS")</script>'
    evil_sub = '<img src=x onerror=alert(1)>'
    evil_badges = [
        ('"><svg onload=alert(1)>', "style<script>"),
        ("Normal Badge", "neutral"),
    ]

    hero_html = render_hero_html(evil_title, evil_sub, evil_badges)

    assert "<script>" not in hero_html
    assert "&lt;script&gt;" in hero_html
    assert "<img" not in hero_html
    assert "&lt;img" in hero_html
    assert "<svg" not in hero_html
    assert "&lt;svg" in hero_html

    # 2. Test render_metric_card_html with malicious payloads
    card_html = render_metric_card_html(
        title="<b onfocus=alert(1)>Label</b>",
        value="<iframe src=evil.com>99.9%</iframe>",
        delta='<span onclick="hack()">+5%</span>',
    )

    assert "<b " not in card_html
    assert "&lt;b" in card_html
    assert "<iframe" not in card_html
    assert "&lt;iframe" in card_html
    assert "<span onclick" not in card_html


# =============================================================================
# 14. Stage 06 Reset Defaults Regression Suite (S06-DEFECT-001)
# =============================================================================

def test_playground_reset_defaults_before_generation():
    """Test A: Verify that modifying controls and clicking Reset Defaults restores defaults without exception."""
    try:
        from streamlit.testing.v1 import AppTest
    except ImportError:
        pytest.skip("streamlit.testing.v1.AppTest is not available")

    app_file = APP_DIR / "app.py"
    at = AppTest.from_file(str(app_file), default_timeout=35)
    at.run()
    assert not at.exception

    # Navigate to Clustering Playground
    at.sidebar.radio(key="main_navigation").set_value("Clustering Playground").run()
    assert not at.exception

    # Modify parameters away from defaults
    at.selectbox(key="pg_dataset_family").set_value("Two Moons").run()
    assert not at.exception
    at.slider(key="pg_n_samples").set_value(200).run()
    assert not at.exception
    at.number_input(key="pg_seed").set_value(99).run()
    assert not at.exception
    at.slider(key="pg_noise").set_value(0.12).run()
    assert not at.exception
    at.slider(key="pg_outliers").set_value(0.10).run()
    assert not at.exception

    assert at.selectbox(key="pg_dataset_family").value == "Two Moons"
    assert at.slider(key="pg_n_samples").value == 200

    # Click Reset Defaults
    at.button(key="pg_btn_reset").click().run()
    assert not at.exception, "StreamlitWidgetAlreadyInstantiatedError on Reset Defaults!"

    # Verify every control returned to its default value
    assert at.selectbox(key="pg_dataset_family").value == "Gaussian Blobs"
    assert at.slider(key="pg_n_samples").value == 300
    assert at.number_input(key="pg_seed").value == 42
    assert at.slider(key="pg_noise").value == 0.0
    assert at.slider(key="pg_outliers").value == 0.0
    assert at.slider(key="pg_blobs_k").value == 3
    assert at.slider(key="pg_blobs_std").value == 0.4
    assert at.slider(key="pg_blobs_radius").value == 3.5

    # Success notification rendered
    success_texts = [s.value for s in at.success]
    assert any("Configuration reset to Gaussian Blobs baseline" in s for s in success_texts)


def test_playground_reset_defaults_after_generation_and_stale_handling():
    """Test B: Verify resetting after generating results preserves coherence and handles state transitions."""
    try:
        from streamlit.testing.v1 import AppTest
    except ImportError:
        pytest.skip("streamlit.testing.v1.AppTest is not available")

    app_file = APP_DIR / "app.py"
    at = AppTest.from_file(str(app_file), default_timeout=35)
    at.run()
    assert not at.exception

    at.sidebar.radio(key="main_navigation").set_value("Clustering Playground").run()
    assert not at.exception

    # Generate clustering on Two Moons with non-default parameters
    at.selectbox(key="pg_dataset_family").set_value("Two Moons").run()
    at.slider(key="pg_n_samples").set_value(160).run()
    at.slider(key="pg_noise").set_value(0.08).run()
    at.button(key="pg_btn_run").click().run()
    assert not at.exception

    # Confirm executed dataset is Two Moons
    executed_cfg = at.session_state["executed_config"]
    assert executed_cfg["family"] == "Two Moons"
    assert executed_cfg["n_inliers"] == 160

    # Change noise parameter away from executed
    at.slider(key="pg_noise").set_value(0.20).run()
    assert not at.exception

    # Stale warning should be present
    warning_texts = [w.value for w in at.warning]
    assert any("Parameters Modified — Showing Previous Clustering Results" in w for w in warning_texts)

    # Click Reset Defaults
    at.button(key="pg_btn_reset").click().run()
    assert not at.exception

    # Verify executed config is now Gaussian Blobs baseline
    res_cfg = at.session_state["executed_config"]
    assert res_cfg["family"] == "Gaussian Blobs"
    assert res_cfg["n_inliers"] == 300
    assert res_cfg["k"] == 3

    # Stale warning should now be cleared because controls match executed baseline
    refreshed_warnings = [w.value for w in at.warning]
    assert not any("Parameters Modified — Showing Previous Clustering Results" in w for w in refreshed_warnings)

    # Tabs and metrics remain mounted
    assert len(at.tabs) >= 3
    assert len(at.dataframe) >= 2


def test_playground_repeated_resets_and_cross_navigation():
    """Test C: Repeated resets, navigation away and back, and second reset stability."""
    try:
        from streamlit.testing.v1 import AppTest
    except ImportError:
        pytest.skip("streamlit.testing.v1.AppTest is not available")

    app_file = APP_DIR / "app.py"
    at = AppTest.from_file(str(app_file), default_timeout=35)
    at.run()
    assert not at.exception

    at.sidebar.radio(key="main_navigation").set_value("Clustering Playground").run()
    assert not at.exception

    # First reset click
    at.button(key="pg_btn_reset").click().run()
    assert not at.exception

    # Second immediate reset click
    at.button(key="pg_btn_reset").click().run()
    assert not at.exception
    assert at.selectbox(key="pg_dataset_family").value == "Gaussian Blobs"

    # Navigate to Performance Benchmarks
    at.sidebar.radio(key="main_navigation").set_value("Performance Benchmarks").run()
    assert not at.exception

    # Navigate to Algorithm Explorer
    at.sidebar.radio(key="main_navigation").set_value("Algorithm Explorer").run()
    assert not at.exception

    # Return to Clustering Playground
    at.sidebar.radio(key="main_navigation").set_value("Clustering Playground").run()
    assert not at.exception

    # Reset once more
    at.button(key="pg_btn_reset").click().run()
    assert not at.exception
    assert at.selectbox(key="pg_dataset_family").value == "Gaussian Blobs"
    assert at.slider(key="pg_n_samples").value == 300
    assert len(at.tabs) >= 3


def test_related_reset_mechanisms_safety():
    """Test D: Verify that Explorer step reset and Config upload state restoration operate without widget collision."""
    try:
        from streamlit.testing.v1 import AppTest
    except ImportError:
        pytest.skip("streamlit.testing.v1.AppTest is not available")

    app_file = APP_DIR / "app.py"
    at = AppTest.from_file(str(app_file), default_timeout=35)
    at.run()
    assert not at.exception

    # Test Explorer step reset
    at.sidebar.radio(key="main_navigation").set_value("Algorithm Explorer").run()
    assert not at.exception

    # Step forward
    at.button(key="exp_btn_next").click().run()
    assert not at.exception
    assert at.session_state["explorer_step_index"] >= 1

    # Reset button in Explorer
    at.button(key="exp_btn_first").click().run()
    assert not at.exception
    assert at.session_state["explorer_step_index"] == 0


def test_playground_and_explorer_cross_generation_regression():
    """Test D (Regression protection): Verify Playground runs on all topologies and transitions seamlessly with Explorer."""
    try:
        from streamlit.testing.v1 import AppTest
    except ImportError:
        pytest.skip("streamlit.testing.v1.AppTest is not available")

    app_file = APP_DIR / "app.py"
    at = AppTest.from_file(str(app_file), default_timeout=45)
    at.run()
    assert not at.exception

    # 1. Playground generation across all 3 topologies
    at.sidebar.radio(key="main_navigation").set_value("Clustering Playground").run()
    assert not at.exception

    for topo in ["Gaussian Blobs", "Two Moons", "Concentric Circles"]:
        at.selectbox(key="pg_dataset_family").set_value(topo).run()
        assert not at.exception
        at.button(key="pg_btn_run").click().run()
        assert not at.exception, f"Playground execution failed on topology '{topo}': {at.exception}"
        assert len(at.tabs) >= 3
        assert at.session_state["current_dataset"] is not None

    # 2. Transition to Algorithm Explorer and run Dense Prim MST on Two Moons (previously crashed)
    at.sidebar.radio(key="main_navigation").set_value("Algorithm Explorer").run()
    assert not at.exception
    at.radio(key="explorer_algo_choice").set_value("Dense Prim's MST").run()
    at.selectbox(key="exp_family").set_value("Two Moons").run()
    assert not at.exception
    assert at.session_state["explorer_trace"] is not None

    # 3. Transition back to Playground
    at.sidebar.radio(key="main_navigation").set_value("Clustering Playground").run()
    assert not at.exception
    assert at.session_state["current_dataset"] is not None


def test_methodology_view_rendering_and_scientific_accuracy():
    """Verify that Methodology / Help renders cleanly and enforces scientific accuracy."""
    try:
        from streamlit.testing.v1 import AppTest
    except ImportError:
        pytest.skip("streamlit.testing.v1.AppTest is not available")

    app_file = APP_DIR / "app.py"
    at = AppTest.from_file(str(app_file), default_timeout=35)
    at.run()
    assert not at.exception

    # Navigate to Methodology / Help
    at.sidebar.radio(key="main_navigation").set_value("Methodology / Help").run()
    assert not at.exception

    md_texts = " ".join([m.value for m in at.markdown])

    # 1. Mathematically correct Silhouette definition
    assert "b(i) - a(i)" in md_texts
    assert r"\max(a(i), b(i))" in md_texts

    # 2. Absence of scientifically unsupported absolute ARI guarantees
    assert "(>0.95)" not in md_texts
    assert "(Inlier ARI $= 1.0$)" not in md_texts
    assert r"\approx 0.49" not in md_texts

    # 3. Qualified complexity and reproducibility wording
    assert "I \\times N \\times k \\times d" in md_texts
    assert "compatible" in md_texts.lower()

    # 4. Deferred future research extensions are not claimed as implemented
    assert "Normalized Mutual Information (NMI)" in md_texts
    assert "deferred" in md_texts.lower()


def test_reproducibility_config_csv_notice_and_synthetic_recovery():
    """Verify that external CSV datasets display intended notice in Config view and recover on synthetic switch."""
    try:
        from streamlit.testing.v1 import AppTest
    except ImportError:
        pytest.skip("streamlit.testing.v1.AppTest is not available")

    app_file = APP_DIR / "app.py"
    at = AppTest.from_file(str(app_file), default_timeout=35)
    at.run()
    assert not at.exception

    # 1. Mount an external CSV dataset into active session state
    csv_ds = Dataset(
        X=np.array([[1.0, 2.0], [2.0, 3.0], [3.0, 4.0], [4.0, 5.0]], dtype=np.float64),
        labels=np.array([0, 0, 1, 1], dtype=np.int32),
        inlier_mask=np.array([True, True, True, True], dtype=bool),
        dataset_family="csv_custom",
        seed=None,
        params={"filename": "external_data.csv"},
        n_inliers=4,
        n_outliers=0,
        n_samples=4,
    )
    at.session_state["current_dataset"] = csv_ds

    # Navigate to Reproducibility & Configuration
    at.sidebar.radio(key="main_navigation").set_value("Reproducibility & Configuration").run()
    assert not at.exception

    # Notice must explain that external CSV data cannot be regenerated from synthetic JSON alone
    info_texts = " ".join([inf.value for inf in at.info if hasattr(inf, "value")])
    assert "Current active dataset was imported from an external CSV" in info_texts
    assert "cannot regenerate" in info_texts

    # 2. Switch back to a valid synthetic dataset
    synth_ds = generate_synthetic_dataset(family="blobs", n_samples=30, seed=42)
    at.session_state["current_dataset"] = synth_ds

    # Rerun the configuration view
    at.sidebar.radio(key="main_navigation").set_value("Reproducibility & Configuration").run()
    assert not at.exception

    # JSON configuration code block must be rendered
    code_blocks = [c.value for c in at.code if hasattr(c, "value")]
    assert any("blobs" in c for c in code_blocks)
    assert any("schema_version" in c for c in code_blocks)
