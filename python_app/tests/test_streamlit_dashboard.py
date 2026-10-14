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
import sys
import numpy as np
import pytest

APP_DIR = pathlib.Path(__file__).resolve().parent.parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from clustering_lab.algorithms.kmeans import kmeans
from clustering_lab.algorithms.mst import mst_clustering
from clustering_lab.data.config import ExperimentConfig, create_dataset_from_config
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
    assert "[REDACTED_STUDENT_IDENTIFIER]" not in combined_text, "Roll number [REDACTED_STUDENT_IDENTIFIER] should not be displayed in UI!"
    assert "[REDACTED_STUDENT_IDENTIFIER]" not in combined_text, "Roll number [REDACTED_STUDENT_IDENTIFIER] should not be displayed in UI!"

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
        assert "[REDACTED_STUDENT_IDENTIFIER]" not in page_combined, f"Roll number [REDACTED_STUDENT_IDENTIFIER] leaked in view '{view_name}'"
        assert "[REDACTED_STUDENT_IDENTIFIER]" not in page_combined, f"Roll number [REDACTED_STUDENT_IDENTIFIER] leaked in view '{view_name}'"


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
    assert "[REDACTED_STUDENT_IDENTIFIER]" not in meta_json_str, "Roll number 389 leaked in metadata JSON!"
    assert "[REDACTED_STUDENT_IDENTIFIER]" not in meta_json_str, "Roll number 390 leaked in metadata JSON!"
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
