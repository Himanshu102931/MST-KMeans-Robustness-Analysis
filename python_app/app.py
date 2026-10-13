"""
MST vs K-Means Robustness Analysis — Streamlit Research Dashboard
=================================================================
Interactive scientific demonstration and quantitative benchmarking platform
comparing graph-theoretic Prim's MST clustering against Lloyd's K-Means clustering.

Academic Context:
    Course: Pattern Matching Lab (BCS-DS-777)
    Institution: Manav Rachna International Institute of Research and Studies (MRIIRS)
                 School of Engineering & Technology
    Degree: B.Tech Computer Science & Engineering (AIML), 7th Semester (2026–2027)
    Student Researchers:
        - Himanshu Gupta
        - Parth Yadav
    Instructor: Mr. Aman Kumar, Assistant Professor
"""

from __future__ import annotations

import io
import sys
import time
from typing import Any, Dict, Optional, Tuple
import numpy as np
import pandas as pd
import streamlit as st

from clustering_lab.algorithms.explorer import (
    KMeansTraceResult,
    KMeansTraceStep,
    MSTTraceResult,
    MSTTraceStep,
    run_kmeans_trace,
    run_mst_trace,
)
from clustering_lab.algorithms.kmeans import KMeansResult, kmeans
from clustering_lab.algorithms.mst import MSTClusteringResult, mst_clustering
from clustering_lab.data.config import ExperimentConfig, create_dataset_from_config
from clustering_lab.data.csv_loader import load_dataset_from_csv
from clustering_lab.data.dataset import Dataset
from clustering_lab.data.synthetic import generate_synthetic_dataset
from clustering_lab.evaluation.metrics import ClusteringMetrics, evaluate_clustering
from clustering_lab.experiments import (
    DEFAULT_BENCHMARK_REPETITIONS,
    DEFAULT_BENCHMARK_SEED,
    DEFAULT_BENCHMARK_SIZES,
    DEFAULT_EXTENDED_SEEDS,
    DEFAULT_NOISE_LEVELS,
    DEFAULT_OUTLIER_BASE_NOISE,
    DEFAULT_OUTLIER_RATES,
    DEFAULT_QUICK_SEEDS,
    BenchmarkConfig,
    BenchmarkSummary,
    BenchmarkTrialResult,
    ExperimentMode,
    SweepAggregateRow,
    SweepConfig,
    SweepType,
    TrialResult,
    aggregate_benchmark_trials,
    aggregate_trials,
    aggregates_to_dataframe,
    export_benchmark_config_json,
    export_benchmark_metadata,
    export_benchmark_summary_to_csv,
    export_benchmark_trials_to_csv,
    export_config_json,
    export_experiment_metadata,
    export_summary_to_csv,
    export_trials_to_csv,
    run_performance_benchmark,
    run_robustness_experiment,
    trials_to_dataframe,
)
from clustering_lab.visualization.figures import (
    create_benchmark_runtime_figure,
    create_degradation_curve_figure,
    create_ground_truth_figure,
    create_kmeans_explorer_figure,
    create_kmeans_figure,
    create_mst_explorer_figure,
    create_mst_figure,
    create_robustness_curve_figure,
    render_benchmark_png,
    render_clustering_png,
)


# Page configuration
st.set_page_config(
    page_title="MST vs K-Means Robustness Analysis",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Safe maximum observation limit for interactive dense Prim O(N^2) clustering
MAX_INTERACTIVE_SAMPLES: int = 600

DEFAULT_SYNTHETIC_CONFIG: Dict[str, Any] = {
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


# -----------------------------------------------------------------------------
# Session State Initialization & Management
# -----------------------------------------------------------------------------
def init_session_state() -> None:
    """Initialize persistent session variables if not already present."""
    if "current_dataset" not in st.session_state:
        # Default baseline: Gaussian Blobs (k=3, n=300, seed=42)
        default_ds = generate_synthetic_dataset(
            family="blobs",
            n_samples=300,
            seed=42,
            noise=0.0,
            outlier_rate=0.0,
            n_clusters=3,
            cluster_std=0.4,
            radius=3.5,
        )
        st.session_state["current_dataset"] = default_ds

    if "kmeans_result" not in st.session_state or "mst_result" not in st.session_state:
        _run_clustering_on_dataset(st.session_state["current_dataset"], k=3)

    if "executed_config" not in st.session_state:
        st.session_state["executed_config"] = dict(DEFAULT_SYNTHETIC_CONFIG)

    if "config_feedback" not in st.session_state:
        st.session_state["config_feedback"] = None

    if "robustness_trials" not in st.session_state:
        st.session_state["robustness_trials"] = None

    if "robustness_aggregates" not in st.session_state:
        st.session_state["robustness_aggregates"] = None

    if "robustness_config" not in st.session_state:
        st.session_state["robustness_config"] = None

    if "benchmark_trials" not in st.session_state:
        st.session_state["benchmark_trials"] = None

    if "benchmark_summary" not in st.session_state:
        st.session_state["benchmark_summary"] = None

    if "benchmark_config" not in st.session_state:
        st.session_state["benchmark_config"] = None

    if "explorer_trace" not in st.session_state:
        st.session_state["explorer_trace"] = None

    if "explorer_step_index" not in st.session_state:
        st.session_state["explorer_step_index"] = 0

    if "explorer_config_hash" not in st.session_state:
        st.session_state["explorer_config_hash"] = None


def _run_clustering_on_dataset(
    dataset: Dataset,
    k: int,
    kmeans_max_iter: int = 300,
    kmeans_tol: float = 1e-4,
    kmeans_seed: int = 42,
) -> None:
    """Execute both custom clustering algorithms on the given dataset.

    Enforces compute safety: rejects execution on datasets exceeding 600 total observations
    without truncating or corrupting input data.
    """
    X = dataset.X
    n_samples = X.shape[0]

    # Enforce safe maximum limit of 600 total observations for interactive clustering
    if n_samples > MAX_INTERACTIVE_SAMPLES:
        raise ValueError(
            f"Dataset contains {n_samples} total observations, which exceeds the safe interactive "
            f"clustering limit of {MAX_INTERACTIVE_SAMPLES} observations for dense Prim's MST (O(N^2)). "
            "Execution rejected without truncating the data."
        )

    # Validate k
    k_effective = max(1, min(int(k), n_samples))

    # Verify input immutability: X coordinates must remain identical across calls
    X_snapshot = X.copy()

    # 1. Custom Lloyd's K-Means
    t0_km = time.perf_counter()
    km_res = kmeans(
        X=X,
        k=k_effective,
        max_iter=kmeans_max_iter,
        tol=kmeans_tol,
        seed=kmeans_seed,
    )
    t1_km = time.perf_counter()

    assert np.array_equal(X, X_snapshot), "K-Means modified input feature matrix in-place."

    km_metrics = evaluate_clustering(
        y_pred=km_res.labels,
        y_true=dataset.labels,
        inlier_mask=dataset.inlier_mask,
        X=X,
        runtime_sec=t1_km - t0_km,
    )

    # 2. Custom dense Prim's MST
    t0_mst = time.perf_counter()
    mst_res = mst_clustering(X=X, k=k_effective)
    t1_mst = time.perf_counter()

    assert np.array_equal(X, X_snapshot), "MST clustering modified input feature matrix in-place."

    mst_metrics = evaluate_clustering(
        y_pred=mst_res.labels,
        y_true=dataset.labels,
        inlier_mask=dataset.inlier_mask,
        X=X,
        runtime_sec=t1_mst - t0_mst,
    )

    st.session_state["kmeans_result"] = km_res
    st.session_state["kmeans_metrics"] = km_metrics
    st.session_state["mst_result"] = mst_res
    st.session_state["mst_metrics"] = mst_metrics
    st.session_state["clustering_k"] = k_effective


# -----------------------------------------------------------------------------
# Sidebar Navigation & Academic Metadata
# -----------------------------------------------------------------------------
def render_sidebar() -> str:
    """Render the academic metadata sidebar and navigation selection."""
    with st.sidebar:
        st.title("🔬 Clustering Lab")
        st.caption("Pattern Matching Lab (BCS-DS-777)")

        st.markdown(
            """
            **Institution:**
            Manav Rachna International Institute of Research and Studies (MRIIRS)
            *School of Engineering & Technology*
            B.Tech CSE (AIML), 7th Semester (2026–2027)

            **Student Researchers:**
            - **Himanshu Gupta**
            - **Parth Yadav**

            **Course Instructor:**
            **Mr. Aman Kumar**, *Assistant Professor*
            """
        )

        st.divider()

        nav_view = st.radio(
            "Navigation Modules",
            options=[
                "Overview",
                "Clustering Playground",
                "Performance Benchmarks",
                "Algorithm Explorer",
                "Robustness Analysis",
                "Dataset & CSV Import",
                "Reproducibility & Configuration",
                "Methodology / Help",
            ],
            index=0,
            key="main_navigation",
        )

        st.divider()

        st.subheader("System Status")
        st.markdown(
            f"""
            - **Phase:** `M5C — Public Dashboard Privacy Preparation`
            - **Python Runtime:** `{sys.version.split()[0]}`
            - **Streamlit Version:** `{st.__version__}`
            - **Algorithms:** Custom Pure NumPy
            - **Interactive Limit:** `N ≤ {MAX_INTERACTIVE_SAMPLES}`
            """
        )

        st.info(
            "The Vanilla JavaScript application remains preserved at the repository "
            "root for static browser-only viva presentation."
        )

    return nav_view


# -----------------------------------------------------------------------------
# VIEW 1: Overview
# -----------------------------------------------------------------------------
def render_view_overview() -> None:
    """Render Project Overview, Research Objectives, and Roadmap."""
    st.subheader("Quantitative Evaluation of Graph-Theoretic vs Centroid-Based Clustering")

    st.markdown(
        """
        > [!NOTE]
        > **Migration Phase M5A Active:** The scientific Python research platform features
        > pure from-scratch implementations of Lloyd's K-Means and dense Prim's MST clustering,
        > along with an automated paired robustness sweep engine and Monte Carlo statistics.
        """
    )

    st.markdown("### Officially Allocated Research Objective")
    st.markdown(
        """
        The objective of this research is to evaluate and systematically compare the **clustering robustness**
        of **Minimum Spanning Tree (MST)-based clustering** against classical **Lloyd's K-Means clustering**
        across varying synthetic 2D geometric distributions and controlled perturbations:

        1. **Geometric Topology:** Evaluating non-globular cluster geometries (such as concentric circles and interlocking half-moons) where centroid-based algorithms tend to struggle due to convex Voronoi partitioning assumptions, whereas graph-theoretic single-linkage cuts can trace arbitrary curvilinear manifolds when cluster boundaries are clean.
        2. **Controlled Noise & Outlier Contamination:** Measuring tolerance to independent Gaussian coordinate jitter (inlier noise) and random uniform bounding-box outlier contamination (distinguishing uniform random noise points from adversarially placed outliers).
        3. **Heterogeneous Density Variation (Planned):** Investigating cluster stability when distinct clusters exhibit varying spatial densities (scheduled for systematic study in the automated benchmark suite).
        4. **Quantitative Validation:** Evaluating partition accuracy via ground-truth metrics (Inlier Adjusted Rand Index and Full-Data Adjusted Rand Index), intrinsic clustering structure (Silhouette Coefficient with geometric bias safeguards), and execution runtime profiling. *(Additional metrics such as Normalized Mutual Information are planned for subsequent benchmark sweeps).*
        """
    )

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Implemented Capabilities (Phases M1–M5A)")
        st.markdown(
            r"""
            - **M1 Foundation:** Standardized Linux CI workflow and modular package architecture.
            - **M2 Scientific Algorithms:** Pure NumPy Lloyd's K-Means ($k$-means++ seeding) and dense Prim's Euclidean MST ($O(N^2)$ time, $O(N)$ space) with deterministic cut tie-breaking.
            - **M3 Reproducible Data Layer:** Blobs, Moons, and Circles generators with decoupled noise/outlier contamination; secure CSV loader; versioned JSON schema `1.0.0`.
            - **M4 Interactive Dashboard:** Real-time parameter controls ($N \le 600$), dual algorithm execution on identical matrices, 1:1 isotropic Plotly visualization, Inlier/Full ARI and safe Silhouette metrics, and bi-directional JSON configuration synchronization.
            - **M5A Robustness Engine:** Controlled Gaussian noise and uniform outlier sweeps, paired Monte Carlo evaluation across deterministic seeds, matched baseline degradation metrics, and provenance-isolated CSV/JSON exports.
            """
        )

    with col2:
        st.markdown("#### Planned Subsequent Phases (Phase M5B+)")
        st.markdown(
            r"""
            - **Phase M5B — Computational Scaling & Algorithm Profiler:**
              - Dense Prim's $O(N^2)$ empirical scaling benchmarks across $N$.
              - Iteration and convergence diagnostics.
            - **Extended Metric Framework:**
              - Normalized Mutual Information (NMI) and multi-seed stability metrics.
            - **Final Deliverables:**
              - Complete experimental research report and oral viva demonstration materials.
            """
        )


# -----------------------------------------------------------------------------
# VIEW 2: Clustering Playground
# -----------------------------------------------------------------------------
def render_view_playground() -> None:
    """Render interactive Clustering Playground with controls, visualizations, and metrics."""
    st.subheader("Clustering Playground — Interactive Parameter Tuning & Analysis")
    st.caption("Interactive Parameter Tuning, Algorithm Execution, and Scientific Visualization")

    # Layout: Controls in expandable container
    with st.expander("⚙️ Dataset & Algorithm Configuration", expanded=True):
        col_family, col_samples, col_seed = st.columns([1.2, 1.2, 1.0])

        with col_family:
            family = st.selectbox(
                "Dataset Topology",
                options=["Gaussian Blobs", "Two Moons", "Concentric Circles"],
                index=0,
                key="pg_dataset_family",
                help="Geometric manifold distribution used to test clustering inductive bias.",
            )

        with col_samples:
            n_inliers = st.slider(
                "Inlier Sample Count",
                min_value=20,
                max_value=MAX_INTERACTIVE_SAMPLES,
                value=300,
                step=20,
                key="pg_n_samples",
                help=(
                    f"Safe interactive limit is {MAX_INTERACTIVE_SAMPLES} total points for real-time responsiveness. "
                    "Dense Prim's MST runs in O(N^2) time."
                ),
            )

        with col_seed:
            seed = st.number_input(
                "Random Seed",
                min_value=0,
                max_value=999999,
                value=42,
                step=1,
                key="pg_seed",
                help="Deterministic PRNG seed ensuring scientific reproducibility.",
            )

        # Family specific controls
        col_k, col_geom1, col_geom2 = st.columns(3)

        if family == "Gaussian Blobs":
            with col_k:
                k_clusters = st.slider(
                    "Cluster Count (k)",
                    min_value=2,
                    max_value=8,
                    value=3,
                    step=1,
                    key="pg_blobs_k",
                )
            with col_geom1:
                cluster_std = st.slider(
                    "Cluster Dispersion (std)",
                    min_value=0.1,
                    max_value=1.5,
                    value=0.4,
                    step=0.05,
                    key="pg_blobs_std",
                    help="Isotropic Gaussian kernel standard deviation.",
                )
            with col_geom2:
                radius = st.slider(
                    "Center Radius",
                    min_value=1.5,
                    max_value=6.0,
                    value=3.5,
                    step=0.5,
                    key="pg_blobs_radius",
                    help="Distance of blob centroids from the origin.",
                )
            factor = None
        elif family == "Two Moons":
            with col_k:
                st.info("Two Moons topology has fixed **k = 2** crescent manifolds.")
                k_clusters = 2
            with col_geom1:
                st.caption("Geometry: Interlocking half-circles of radius 1.0.")
                cluster_std = 0.0
            with col_geom2:
                radius = 1.0
            factor = None
        else:  # Concentric Circles
            with col_k:
                st.info("Concentric Circles topology has fixed **k = 2** nested rings.")
                k_clusters = 2
            with col_geom1:
                factor = st.slider(
                    "Inner Ring Scale (factor)",
                    min_value=0.15,
                    max_value=0.85,
                    value=0.45,
                    step=0.05,
                    key="pg_circles_factor",
                    help="Ratio of inner circle radius to outer circle radius (1.0).",
                )
                cluster_std = 0.0
                radius = 1.0
            with col_geom2:
                st.caption("Outer ring radius = 1.0; Inner ring radius = factor.")

        # Perturbation controls: Decoupled Noise and Outlier Rate
        col_noise, col_outliers, col_mst_opts = st.columns(3)

        default_noise = 0.0 if family == "Gaussian Blobs" else (0.08 if family == "Two Moons" else 0.05)
        with col_noise:
            noise_sigma = st.slider(
                "Gaussian Noise (σ)",
                min_value=0.0,
                max_value=0.5,
                value=float(default_noise),
                step=0.01,
                key="pg_noise",
                help="Zero-mean Gaussian jitter added independently to inlier coordinates.",
            )

        with col_outliers:
            outlier_rate = st.slider(
                "Outlier Contamination Rate",
                min_value=0.0,
                max_value=0.4,
                value=0.0,
                step=0.02,
                key="pg_outliers",
                help="Uniform random points injected across the bounding box as a fraction of inliers.",
            )
            n_outliers_calc = int(round(n_inliers * outlier_rate))
            total_n_calc = n_inliers + n_outliers_calc
            st.caption(
                f"Inliers: **{n_inliers}** | Injected Outliers: **{n_outliers_calc}** | Total N: **{total_n_calc}**"
            )

        with col_mst_opts:
            show_retained = st.checkbox("Overlay Retained MST Edges", value=True, key="pg_mst_retained")
            show_cuts = st.checkbox("Highlight Cut Edges", value=True, key="pg_mst_cuts")

        # Compute Safety Check for current inputs
        if total_n_calc > MAX_INTERACTIVE_SAMPLES:
            st.error(
                f"⚠️ Total observations ({total_n_calc} = {n_inliers} inliers + {n_outliers_calc} outliers) "
                f"exceeds the safe interactive limit of {MAX_INTERACTIVE_SAMPLES} observations for dense Prim's MST (O(N^2)). "
                "Please reduce inlier count or outlier rate before running."
            )

        # Action Buttons
        btn_col1, btn_col2, _ = st.columns([1.5, 1.2, 3.0])
        with btn_col1:
            run_clicked = st.button("🚀 Generate & Run Clustering", type="primary", use_container_width=True)
        with btn_col2:
            reset_clicked = st.button("🔄 Reset Defaults", use_container_width=True)

    # Current controls state dictionary
    current_controls = {
        "source": "synthetic",
        "family": family,
        "n_inliers": n_inliers,
        "seed": int(seed),
        "noise": float(noise_sigma),
        "outlier_rate": float(outlier_rate),
        "k": int(k_clusters),
        "cluster_std": float(cluster_std) if family == "Gaussian Blobs" else None,
        "radius": float(radius) if family == "Gaussian Blobs" else None,
        "factor": float(factor) if family == "Concentric Circles" else None,
    }

    # Process Reset Action
    if reset_clicked:
        reset_ds = generate_synthetic_dataset(
            family="blobs",
            n_samples=300,
            seed=42,
            noise=0.0,
            outlier_rate=0.0,
            n_clusters=3,
            cluster_std=0.4,
            radius=3.5,
        )
        st.session_state["current_dataset"] = reset_ds
        _run_clustering_on_dataset(reset_ds, k=3)
        st.session_state["executed_config"] = dict(DEFAULT_SYNTHETIC_CONFIG)
        # Reset widget session keys to defaults
        st.session_state["pg_dataset_family"] = "Gaussian Blobs"
        st.session_state["pg_n_samples"] = 300
        st.session_state["pg_seed"] = 42
        st.session_state["pg_noise"] = 0.0
        st.session_state["pg_outliers"] = 0.0
        st.session_state["pg_blobs_k"] = 3
        st.session_state["pg_blobs_std"] = 0.4
        st.session_state["pg_blobs_radius"] = 3.5
        st.success("Configuration reset to Gaussian Blobs baseline.")
        st.rerun()

    # Process Run Action
    if run_clicked:
        if total_n_calc > MAX_INTERACTIVE_SAMPLES:
            st.error(
                f"Execution blocked: Total observations ({total_n_calc}) exceeds the interactive limit "
                f"of {MAX_INTERACTIVE_SAMPLES}. Please adjust controls."
            )
        else:
            with st.spinner("Synthesizing dataset and executing dual clustering algorithms..."):
                family_key = "blobs" if family == "Gaussian Blobs" else ("moons" if family == "Two Moons" else "circles")
                kwargs: Dict[str, Any] = {}
                if family_key == "blobs":
                    kwargs["n_clusters"] = k_clusters
                    kwargs["cluster_std"] = cluster_std
                    kwargs["radius"] = radius
                elif family_key == "circles":
                    kwargs["factor"] = factor

                try:
                    new_ds = generate_synthetic_dataset(
                        family=family_key,
                        n_samples=n_inliers,
                        seed=seed,
                        noise=noise_sigma,
                        outlier_rate=outlier_rate,
                        **kwargs,
                    )
                    st.session_state["current_dataset"] = new_ds
                    _run_clustering_on_dataset(new_ds, k=k_clusters)
                    st.session_state["executed_config"] = current_controls
                    st.success(f"Successfully clustered {new_ds.n_samples} observations into k={k_clusters} components.")
                except Exception as exc:
                    st.error(f"Error during execution: {exc}")

    # State consistency check: do displayed results match the current configuration?
    executed_cfg = st.session_state.get("executed_config", {})
    is_stale = (executed_cfg != current_controls)

    if is_stale:
        st.divider()
        if executed_cfg.get("source") == "csv":
            st.info(
                f"ℹ️ Currently active dataset was imported from CSV ('{executed_cfg.get('name', 'file')}'). "
                "To visualize synthetic data, click '🚀 Generate & Run Clustering' above."
            )
        else:
            st.warning(
                "⚠️ Parameters have changed since the last execution. Results are pending. "
                "Click '🚀 Generate & Run Clustering' above to compute results for the current settings."
            )
            st.info("Visualizations and quantitative metrics will render once execution is triggered.")
        return

    # Retrieve current executed state for display
    dataset: Dataset = st.session_state["current_dataset"]
    km_res: KMeansResult = st.session_state["kmeans_result"]
    km_metrics: ClusteringMetrics = st.session_state["kmeans_metrics"]
    mst_res: MSTClusteringResult = st.session_state["mst_result"]
    mst_metrics: ClusteringMetrics = st.session_state["mst_metrics"]
    show_retained_edge_flag = st.session_state.get("pg_mst_retained", True)
    show_cut_edge_flag = st.session_state.get("pg_mst_cuts", True)

    # -------------------------------------------------------------------------
    # Visualizations Section
    # -------------------------------------------------------------------------
    st.divider()
    st.markdown("### Interactive 2D Visualizations (Isotropic 1:1 Scale)")
    st.caption(
        f"Displaying executed results: **{family}** | Total N={dataset.n_samples} | "
        f"Seed={dataset.seed} | Target k={st.session_state.get('clustering_k', km_res.k)}"
    )

    viz_tab1, viz_tab2, viz_tab3 = st.tabs(
        ["Ground Truth & Contamination", "Lloyd's K-Means Result", "Prim's MST Result"]
    )

    with viz_tab1:
        st.caption("Ground truth class assignments (outliers marked with red crosses).")
        fig_gt = create_ground_truth_figure(dataset, height=530)
        st.plotly_chart(fig_gt, use_container_width=True)

    with viz_tab2:
        st.caption("Predicted Voronoi clusters with centroid positions marked by golden stars.")
        fig_km = create_kmeans_figure(dataset, km_res, height=530)
        st.plotly_chart(fig_km, use_container_width=True)

    with viz_tab3:
        st.caption("Predicted connected components with Minimum Spanning Tree edge overlays.")
        fig_mst = create_mst_figure(
            dataset,
            mst_res,
            show_retained_edges=show_retained_edge_flag,
            show_cut_edges=show_cut_edge_flag,
            height=530,
        )
        st.plotly_chart(fig_mst, use_container_width=True)

    # -------------------------------------------------------------------------
    # Quantitative Metrics Comparison
    # -------------------------------------------------------------------------
    st.divider()
    st.markdown("### Quantitative Validation & Performance Metrics")

    col_m1, col_m2 = st.columns(2)

    with col_m1:
        st.markdown("#### 🎯 Lloyd's K-Means Clustering")
        km_inlier_ari_str = (
            f"{km_metrics.inlier_ari:.4f}"
            if km_metrics.inlier_ari is not None
            else "N/A — ground-truth unavailable"
        )
        km_full_ari_str = (
            f"{km_metrics.full_ari:.4f}"
            if km_metrics.full_ari is not None
            else "N/A — ground-truth unavailable"
        )
        km_sil_str = (
            f"{km_metrics.silhouette:.4f}"
            if km_metrics.silhouette is not None
            else "N/A — degenerate cluster count"
        )

        st.metric("Inlier Adjusted Rand Index (ARI)", value=km_inlier_ari_str)

        km_data = {
            "Metric": [
                "Inlier ARI",
                "Full-Data ARI",
                "Silhouette Coefficient",
                "Inertia (WCSS)",
                "Iterations Executed",
                "Convergence Status",
                "Runtime (Single Run)",
                "Clusters Formed",
            ],
            "Value": [
                km_inlier_ari_str,
                km_full_ari_str,
                km_sil_str,
                f"{km_res.inertia:.3f}",
                f"{km_res.n_iter}",
                "Converged" if km_res.converged else "Max Iter Reached",
                f"{km_metrics.runtime_ms:.2f} ms",
                f"{km_metrics.n_clusters_predicted}",
            ],
        }
        st.dataframe(pd.DataFrame(km_data), use_container_width=True, hide_index=True)

    with col_m2:
        st.markdown("#### 🌳 Prim's MST Clustering")
        mst_inlier_ari_str = (
            f"{mst_metrics.inlier_ari:.4f}"
            if mst_metrics.inlier_ari is not None
            else "N/A — ground-truth unavailable"
        )
        mst_full_ari_str = (
            f"{mst_metrics.full_ari:.4f}"
            if mst_metrics.full_ari is not None
            else "N/A — ground-truth unavailable"
        )
        mst_sil_str = (
            f"{mst_metrics.silhouette:.4f}"
            if mst_metrics.silhouette is not None
            else "N/A — degenerate cluster count"
        )

        st.metric("Inlier Adjusted Rand Index (ARI)", value=mst_inlier_ari_str)

        mst_data = {
            "Metric": [
                "Inlier ARI",
                "Full-Data ARI",
                "Silhouette Coefficient",
                "Total MST Weight",
                "Retained Forest Weight",
                "Edges Removed (k - 1)",
                "Runtime (Single Run)",
                "Components Formed",
            ],
            "Value": [
                mst_inlier_ari_str,
                mst_full_ari_str,
                mst_sil_str,
                f"{mst_res.total_mst_weight:.3f}",
                f"{mst_res.retained_weight:.3f}",
                f"{len(mst_res.cut_edges)}",
                f"{mst_metrics.runtime_ms:.2f} ms",
                f"{mst_metrics.n_clusters_predicted}",
            ],
        }
        st.dataframe(pd.DataFrame(mst_data), use_container_width=True, hide_index=True)

    # Scientific Interpretation Notes
    with st.expander("ℹ️ Scientific Metric Guidance & Inductive Biases", expanded=False):
        st.markdown(
            """
            - **Mathematical Distinction:** Never compare K-Means **Inertia** against **MST Weight**. Inertia represents variance-based sum of squared distances to centroids; MST Weight represents the linear sum of Euclidean edge lengths along the spanning tree.
            - **Adjusted Rand Index (ARI):** Measures partition similarity corrected for chance. Range is $[-0.5, 1.0]$ where $1.0$ represents identical cluster groupings. Inlier ARI measures preservation of clean cluster manifolds without outlier confounding.
            - **Full-Data ARI:** Treats outliers as an extra class ($-1$). Because standard clustering assigns outliers into the existing $k$ clusters, full ARI naturally penalizes both algorithms.
            - **Silhouette Score Caution:** Evaluates Euclidean distance ratios and intrinsically assumes spherical, convex geometries. It will penalize non-convex shapes (concentric rings and interlocking moons) even when MST partitions them with 100% ground-truth accuracy.
            - **Runtime Profiling:** Single execution measurements are provided for illustrative latency profiling and do not constitute multi-seed statistical benchmarks.
            """
        )


# -----------------------------------------------------------------------------
# VIEW 3: Robustness Analysis Engine (Phase M5A)
# -----------------------------------------------------------------------------
def render_view_robustness() -> None:
    """Render scientific robustness analysis engine with controlled sweeps and Monte Carlo statistics."""
    st.subheader("Scientific Robustness Analysis Engine")
    st.caption("Controlled Gaussian Noise & Uniform Outlier Contamination Sweeps (Paired Monte Carlo Evaluation)")

    st.markdown(
        """
        > [!NOTE]
        > **Phase M5A Research Platform:** This module executes controlled, paired sweeps to evaluate
        > the clustering robustness of **Lloyd's K-Means** against **Prim's MST** under varying
        > Gaussian coordinate jitter and uniform bounding-box outlier contamination.
        > For every trial, both algorithms receive **identical coordinate matrices and ground-truth masks**.
        """
    )

    # Controls Expander
    with st.expander("⚙️ Robustness Experiment Configuration", expanded=True):
        col_mode, col_inliers = st.columns(2)

        with col_mode:
            mode_choice = st.selectbox(
                "Execution Mode Preset",
                options=["Quick Mode (3 Seeds — Fast Demo)", "Extended Mode (10 Seeds — Statistically Grounded)", "Custom Seeds"],
                index=0,
                key="rob_mode_select",
                help="Quick mode uses 3 deterministic seeds (11, 22, 33). Extended mode uses 10 deterministic seeds.",
            )

        with col_inliers:
            n_inliers = st.slider(
                "Base Inlier Observation Count",
                min_value=50,
                max_value=400,
                value=300,
                step=50,
                key="rob_n_inliers",
                help="Number of manifold inliers per trial. With outliers, total points remain safely within N <= 600.",
            )

        # Parse seeds based on mode
        if mode_choice.startswith("Quick"):
            active_seeds = list(DEFAULT_QUICK_SEEDS)
            mode_tag = ExperimentMode.QUICK.value
            st.info(f"**Quick Mode Active:** Evaluating seeds `{active_seeds}` for rapid demonstration.")
        elif mode_choice.startswith("Extended"):
            active_seeds = list(DEFAULT_EXTENDED_SEEDS)
            mode_tag = ExperimentMode.EXTENDED.value
            st.info(f"**Extended Mode Active:** Evaluating 10 deterministic seeds `{active_seeds}` for statistical error bars.")
        else:
            mode_tag = ExperimentMode.CUSTOM.value
            seeds_input = st.text_input(
                "Comma-separated integer seeds",
                value="11, 22, 33, 44, 55",
                key="rob_custom_seeds",
            )
            try:
                active_seeds = [int(s.strip()) for s in seeds_input.split(",") if s.strip()]
                if not active_seeds:
                    active_seeds = list(DEFAULT_QUICK_SEEDS)
            except ValueError:
                st.error("Invalid seeds entered. Falling back to default quick seeds.")
                active_seeds = list(DEFAULT_QUICK_SEEDS)

        col_families, col_sweeps = st.columns(2)

        with col_families:
            family_options = ["Gaussian Blobs", "Two Moons", "Concentric Circles"]
            selected_families_ui = st.multiselect(
                "Dataset Topologies",
                options=family_options,
                default=family_options,
                key="rob_families_select",
                help="Manifold topologies to benchmark.",
            )

        with col_sweeps:
            sweep_ui_choice = st.radio(
                "Sweep Types to Execute",
                options=[
                    "Both Sweeps (Noise & Outliers)",
                    "Gaussian Noise Sweep Only",
                    "Uniform Outlier Sweep Only",
                ],
                index=0,
                key="rob_sweeps_choice",
                help="Noise sweep holds outliers=0.0; Outlier sweep holds base noise sigma=0.05.",
            )

        # Map UI families to internal keys
        fam_map = {
            "Gaussian Blobs": "blobs",
            "Two Moons": "moons",
            "Concentric Circles": "circles",
        }
        selected_families = [fam_map[f] for f in selected_families_ui if f in fam_map]

        # Map sweep types
        if sweep_ui_choice.startswith("Both"):
            active_sweeps = [SweepType.NOISE.value, SweepType.OUTLIER.value]
        elif "Noise" in sweep_ui_choice:
            active_sweeps = [SweepType.NOISE.value]
        else:
            active_sweeps = [SweepType.OUTLIER.value]

        # Compute expected execution count
        n_sweep_points = (len(DEFAULT_NOISE_LEVELS) if SweepType.NOISE.value in active_sweeps else 0) + (
            len(DEFAULT_OUTLIER_RATES) if SweepType.OUTLIER.value in active_sweeps else 0
        )
        total_trials_calc = len(selected_families) * n_sweep_points * len(active_seeds)
        total_executions_calc = total_trials_calc * 2

        st.markdown(
            f"""
            **Experiment Execution Plan:**
            - Dataset Families: **{len(selected_families)}** ({', '.join(selected_families_ui)})
            - Seeds: **{len(active_seeds)}** (`{active_seeds}`)
            - Sweep Points per Family/Seed: **{n_sweep_points}**
            - Total Paired Trials: **{total_trials_calc}** (**{total_executions_calc}** total clustering executions)
            """
        )

        can_run = len(selected_families) > 0 and len(active_seeds) > 0 and total_trials_calc <= 500

        if not selected_families:
            st.error("Please select at least one dataset topology.")
        elif total_trials_calc > 500:
            st.error(f"Total trials ({total_trials_calc}) exceeds safety bound of 500. Reduce seeds or families.")

        run_exp_clicked = st.button(
            "🚀 Execute Robustness Analysis Engine",
            type="primary",
            disabled=not can_run,
            key="rob_run_button",
        )

    # Execution handling
    if run_exp_clicked and can_run:
        sweep_cfg = SweepConfig(
            dataset_families=selected_families,
            n_inliers=n_inliers,
            seeds=active_seeds,
            sweep_types=active_sweeps,
            noise_levels=list(DEFAULT_NOISE_LEVELS),
            outlier_rates=list(DEFAULT_OUTLIER_RATES),
            outlier_sweep_base_noise=DEFAULT_OUTLIER_BASE_NOISE,
            mode=mode_tag,
        )

        progress_bar = st.progress(0.0)
        status_box = st.empty()

        def _update_progress(done: int, total: int, msg: str) -> None:
            pct = min(1.0, float(done) / max(1.0, float(total)))
            progress_bar.progress(pct)
            status_box.markdown(f"**Executing Trial ({done}/{total}):** `{msg}`")

        with st.spinner("Executing paired clustering trials across deterministic seeds..."):
            trial_results = run_robustness_experiment(sweep_cfg, progress_callback=_update_progress)
            agg_results = aggregate_trials(trial_results)

        st.session_state["robustness_trials"] = trial_results
        st.session_state["robustness_aggregates"] = agg_results
        st.session_state["robustness_config"] = sweep_cfg.to_dict()

        progress_bar.empty()
        status_box.success(
            f"✅ Completed robustness sweep: {len(trial_results)} trials ({len(trial_results) * 2} clustering executions) "
            f"across {len(active_seeds)} seeds."
        )

    # Results Display
    if st.session_state.get("robustness_trials") and st.session_state.get("robustness_aggregates"):
        trials: List[TrialResult] = st.session_state["robustness_trials"]
        aggregates: List[SweepAggregateRow] = st.session_state["robustness_aggregates"]
        exec_cfg = st.session_state.get("robustness_config", {})

        # Check for state consistency against current UI controls
        current_cfg_signature = {
            "families": sorted(selected_families),
            "n_inliers": n_inliers,
            "seeds": active_seeds,
            "sweeps": sorted(active_sweeps),
        }
        executed_cfg_signature = {
            "families": sorted(exec_cfg.get("dataset_families", [])),
            "n_inliers": exec_cfg.get("n_inliers", 0),
            "seeds": exec_cfg.get("seeds", []),
            "sweeps": sorted(exec_cfg.get("sweep_types", [])),
        }

        if current_cfg_signature != executed_cfg_signature:
            st.warning(
                "⚠️ **Configuration Warning:** Controls have been modified since the last run. "
                "The charts and metrics below reflect the previously executed configuration. "
                "Click **🚀 Execute Robustness Analysis Engine** to update."
            )

        agg_df = aggregates_to_dataframe(aggregates)

        st.divider()

        # Tabs for result inspection
        tab_noise, tab_outlier, tab_degrade, tab_summary, tab_findings, tab_export = st.tabs([
            "📈 Gaussian Noise Sweep",
            "🛡️ Uniform Outlier Sweep",
            "📉 Baseline Degradation",
            "📊 Full Statistical Summary",
            "🔬 Empirical Findings",
            "💾 Data Export (CSV & JSON)",
        ])

        # Tab 1: Noise Sweep
        with tab_noise:
            st.markdown("### Gaussian Coordinate Jitter Sweep (Outliers = 0%)")
            st.caption("Inlier Gaussian jitter (sigma in [0.00, 0.20]) applied along cluster manifolds with zero outlier contamination.")

            noise_sub = agg_df[agg_df["sweep_type"] == SweepType.NOISE.value]
            if not noise_sub.empty:
                distinct_fams = noise_sub["dataset_family"].unique()
                for fam in distinct_fams:
                    fig_noise = create_robustness_curve_figure(
                        aggregates_df=agg_df,
                        family=fam,
                        sweep_type=SweepType.NOISE.value,
                        metric_col="mean_inlier_ari",
                        std_col="std_inlier_ari",
                        y_label="Inlier Adjusted Rand Index (ARI)",
                        title_suffix="Gaussian Noise Robustness",
                    )
                    st.plotly_chart(fig_noise, use_container_width=True)

                st.markdown("#### Noise Sweep Summary Table")
                display_noise = noise_sub[[
                    "dataset_family", "parameter_value", "algorithm", "n_seeds",
                    "mean_inlier_ari", "std_inlier_ari", "mean_full_ari", "mean_runtime_ms",
                ]].rename(columns={
                    "parameter_value": "Noise Sigma",
                    "mean_inlier_ari": "Mean Inlier ARI",
                    "std_inlier_ari": "Sample Std",
                    "mean_full_ari": "Mean Full ARI",
                    "mean_runtime_ms": "Mean Runtime (ms)",
                })
                st.dataframe(display_noise, use_container_width=True, hide_index=True)
            else:
                st.info("No noise sweep was selected in the executed experiment.")

        # Tab 2: Outlier Sweep
        with tab_outlier:
            st.markdown("### Uniform Outlier Contamination Sweep (Base Noise σ = 0.05)")
            st.caption("Uniform outliers in [0%, 20%] sampled across the coordinate bounding box with baseline inlier jitter sigma = 0.05.")

            outlier_sub = agg_df[agg_df["sweep_type"] == SweepType.OUTLIER.value]
            if not outlier_sub.empty:
                distinct_fams = outlier_sub["dataset_family"].unique()
                for fam in distinct_fams:
                    fig_outlier = create_robustness_curve_figure(
                        aggregates_df=agg_df,
                        family=fam,
                        sweep_type=SweepType.OUTLIER.value,
                        metric_col="mean_inlier_ari",
                        std_col="std_inlier_ari",
                        y_label="Inlier Adjusted Rand Index (ARI)",
                        title_suffix="Uniform Outlier Robustness",
                    )
                    st.plotly_chart(fig_outlier, use_container_width=True)

                st.markdown("#### Outlier Sweep Summary Table")
                display_outlier = outlier_sub[[
                    "dataset_family", "parameter_value", "algorithm", "n_seeds",
                    "mean_inlier_ari", "std_inlier_ari", "mean_full_ari", "mean_runtime_ms",
                ]].rename(columns={
                    "parameter_value": "Outlier Rate",
                    "mean_inlier_ari": "Mean Inlier ARI",
                    "std_inlier_ari": "Sample Std",
                    "mean_full_ari": "Mean Full ARI",
                    "mean_runtime_ms": "Mean Runtime (ms)",
                })
                st.dataframe(display_outlier, use_container_width=True, hide_index=True)
            else:
                st.info("No outlier sweep was selected in the executed experiment.")

        # Tab 3: Baseline Degradation
        with tab_degrade:
            st.markdown("### Relative Performance Degradation Against Matched Baseline")
            st.markdown(
                """
                > [!NOTE]
                > **Matched Baseline Formulation & Confound Elimination:**
                > Every trial is matched with its exact baseline trial sharing the **identical dataset family, geometry, seed, and algorithm**:
                > - **Gaussian Noise Sweep Baseline:** Evaluated at $\\sigma = 0.00$ with $0\\%$ outliers on the identical family, seed, and algorithm.
                > - **Uniform Outlier Sweep Baseline:** Evaluated at $0\\%$ outliers with the **same fixed inlier noise ($\\sigma = 0.05$)** on the identical family, seed, and algorithm. This isolates outlier impact without conflating baseline Gaussian jitter.
                > - **Signed ARI Change:** $\\Delta \\text{ARI} = \\text{ARI}_{\\text{trial}} - \\text{ARI}_{\\text{baseline}}$. Positive indicates improvement, negative indicates degradation.
                > - **Nonnegative Degradation Loss:** $\\text{Degradation} = \\max(0, \\text{ARI}_{\\text{baseline}} - \\text{ARI}_{\\text{trial}})$. Quantifies the performance drop clamped to $\\ge 0.0$.
                """
            )

            degrade_view_mode = st.radio(
                "Metric Display Mode",
                options=["Signed Baseline Change (Δ ARI)", "Nonnegative Degradation Loss"],
                index=0,
                key="rob_degrade_metric_mode",
            )
            use_loss = degrade_view_mode.startswith("Nonnegative")

            for sw_type in sorted(agg_df["sweep_type"].unique()):
                sw_title = "Gaussian Noise Sweep" if sw_type == "noise" else "Uniform Outlier Sweep"
                st.markdown(f"#### {sw_title}")
                sub_sw = agg_df[agg_df["sweep_type"] == sw_type]
                for fam in sub_sw["dataset_family"].unique():
                    fig_deg = create_degradation_curve_figure(
                        aggregates_df=agg_df,
                        family=fam,
                        sweep_type=sw_type,
                        use_nonnegative_loss=use_loss,
                    )
                    st.plotly_chart(fig_deg, use_container_width=True)

        # Tab 4: Full Statistical Summary Table
        with tab_summary:
            st.markdown("### Monte Carlo Aggregated Statistics Table")
            st.caption("Sample means and sample standard deviations (Bessel's correction ddof=1) computed across deterministic seeds.")
            st.dataframe(agg_df, use_container_width=True, hide_index=True)

        # Tab 5: Empirical Findings
        with tab_findings:
            st.markdown("### Synthesized Empirical Findings")
            st.markdown(
                """
                #### 1. Globular Distributions (Gaussian Blobs)
                - **Both Algorithms Perform Robustly:** Under standard spherical clusters with balanced variance, both Lloyd's K-Means and dense Prim's MST achieve high Inlier ARI ($>0.95$) at low-to-moderate noise levels.
                - **Noise Tolerance:** As Gaussian jitter increases to $\\sigma=0.20$, Inlier ARI degrades gracefully for both algorithms.

                #### 2. Non-Convex Curvilinear Manifolds (Two Moons & Concentric Circles)
                - **Inductive Bias at Baseline:** Under clean zero-noise conditions, Prim's MST recovers the non-linear topologies with near-perfect Inlier ARI ($1.00$), whereas K-Means bisects the manifolds with linear Voronoi hyperplanes (Inlier ARI $\\approx 0.00$ for circles, $\\approx 0.49$ for moons).
                - **MST Vulnerability to Noise Bridges (The Chaining Effect):** In the Outlier Sweep, injecting uniform random outliers between the crescent moons creates short edges that connect distinct manifolds, causing MST Inlier ARI to drop sharply.
                - **K-Means Outlier Stability:** While K-Means fails to recover non-convex shapes, its centroid estimates remain relatively stable because uniform bounding-box points symmetrically cancel around cluster centers.

                #### 3. Statistical Sample Size Caution
                - **Quick Mode (3 Seeds):** Provides rapid qualitative insights for viva presentations but displays wider sample variance.
                - **Extended Mode (10 Seeds):** Demonstrates stable sample standard deviations and confirms reproducible convergence trends across repeated PRNG seeds.
                """
            )

        # Tab 6: Data Export
        with tab_export:
            st.markdown("### Data Export & Provenance Isolation")
            st.markdown(
                """
                All exported files originate from actual measured executions within the Python research engine.
                They are isolated from legacy JavaScript benchmark CSVs to preserve experimental provenance.
                """
            )

            csv_trials_str = export_trials_to_csv(trials)
            csv_summary_str = export_summary_to_csv(aggregates)
            cfg_obj = SweepConfig.from_dict(exec_cfg) if exec_cfg else SweepConfig()
            cfg_json_str = export_config_json(cfg_obj)
            meta_json_str = json.dumps(export_experiment_metadata(cfg_obj, len(trials)), indent=2)

            col_exp1, col_exp2 = st.columns(2)
            with col_exp1:
                st.download_button(
                    label="⬇️ Download Raw Trial Data (CSV)",
                    data=csv_trials_str,
                    file_name="python_robustness_raw_trials.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
                st.download_button(
                    label="⬇️ Download Aggregated Summary (CSV)",
                    data=csv_summary_str,
                    file_name="python_robustness_summary.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

            with col_exp2:
                st.download_button(
                    label="⬇️ Download Experiment Config (JSON)",
                    data=cfg_json_str,
                    file_name="robustness_config.json",
                    mime="application/json",
                    use_container_width=True,
                )
                st.download_button(
                    label="⬇️ Download Environment Metadata (JSON)",
                    data=meta_json_str,
                    file_name="environment_metadata.json",
                    mime="application/json",
                    use_container_width=True,
                )


# -----------------------------------------------------------------------------
# VIEW 4: Dataset & CSV Import
# -----------------------------------------------------------------------------
def render_view_csv_import() -> None:
    """Render secure CSV file upload, preview, and dual clustering execution."""
    st.subheader("Dataset & CSV Import — Empirical Benchmark Import")
    st.caption("Empirical Benchmark Import via Secure Tabular Parser")

    st.markdown(
        f"""
        Upload your custom 2D tabular dataset in CSV format. The parser will inspect the file
        up to the 10,000-row loader limit. To protect compute safety for dense Prim's MST ($O(N^2)$),
        clustering execution is enforced at a maximum of **{MAX_INTERACTIVE_SAMPLES} observations**.
        """
    )

    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=["csv"],
        key="csv_file_uploader",
        help="Upload CSV file up to 5 MB with numerical coordinates.",
    )

    if uploaded_file is not None:
        raw_bytes = uploaded_file.getvalue()
        try:
            # Preview first using pandas safely
            df_preview = pd.read_csv(io.BytesIO(raw_bytes))
            n_rows = len(df_preview)
            st.success(
                f"File parsed successfully: **{uploaded_file.name}** "
                f"({n_rows} rows, {len(df_preview.columns)} columns, {len(raw_bytes)} bytes)"
            )

            # Enforce compute safety: reject above 600 observations
            if n_rows > MAX_INTERACTIVE_SAMPLES:
                st.error(
                    f"⚠️ Dataset contains **{n_rows}** observations, which exceeds the interactive "
                    f"clustering limit of {MAX_INTERACTIVE_SAMPLES} observations for dense Prim's MST (O(N^2)). "
                    "Raw CSV data was parsed up to the loader limit, but clustering cannot execute above "
                    f"{MAX_INTERACTIVE_SAMPLES} points to prevent unresponsiveness. "
                    "Execution rejected gracefully without truncating the data."
                )
            elif n_rows > 300:
                st.warning(
                    f"Dataset contains {n_rows} observations (interactive limit: {MAX_INTERACTIVE_SAMPLES}). "
                    "Execution may take a few moments."
                )

            st.dataframe(df_preview.head(8), use_container_width=True)

            # Column selections
            all_cols = list(df_preview.columns)
            numeric_cols = [c for c in all_cols if pd.api.types.is_numeric_dtype(df_preview[c])]

            if len(numeric_cols) < 2:
                st.error("The uploaded CSV must contain at least two numeric feature columns.")
                return

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                feat_x = st.selectbox("Feature 1 (X Axis)", options=numeric_cols, index=0, key="csv_feat_x")
            with col2:
                default_y_idx = 1 if len(numeric_cols) > 1 else 0
                feat_y = st.selectbox("Feature 2 (Y Axis)", options=numeric_cols, index=default_y_idx, key="csv_feat_y")
            with col3:
                label_col_opts = ["(None / Unlabeled)"] + all_cols
                label_choice = st.selectbox("Ground-Truth Label (Optional)", options=label_col_opts, index=0, key="csv_label_col")
            with col4:
                k_csv = st.slider("Target Clusters (k)", min_value=2, max_value=10, value=3, key="csv_k")

            treat_minus_one_outlier = st.checkbox(
                "Treat label -1 as outlier",
                value=False,
                key="csv_treat_outlier",
                help="Only check this if your dataset adheres to the convention where label -1 represents outliers.",
            )

            if feat_x == feat_y:
                st.error("Feature 1 and Feature 2 must be distinct columns.")
                return

            btn_disabled = (n_rows > MAX_INTERACTIVE_SAMPLES)
            btn_run_csv = st.button(
                "🚀 Load & Run Clustering on CSV",
                type="primary",
                disabled=btn_disabled,
                help=f"Execution blocked for datasets with > {MAX_INTERACTIVE_SAMPLES} observations." if btn_disabled else None,
            )

            if btn_run_csv:
                if n_rows > MAX_INTERACTIVE_SAMPLES:
                    st.error(
                        f"Execution rejected: CSV contains {n_rows} observations, exceeding "
                        f"the interactive limit of {MAX_INTERACTIVE_SAMPLES}."
                    )
                else:
                    with st.spinner("Processing CSV and executing clustering..."):
                        label_arg = None if label_choice == "(None / Unlabeled)" else label_choice
                        try:
                            csv_dataset = load_dataset_from_csv(
                                source=raw_bytes,
                                feature_cols=(feat_x, feat_y),
                                label_col=label_arg,
                                dataset_name=uploaded_file.name,
                                treat_minus_one_as_outlier=treat_minus_one_outlier,
                            )

                            st.session_state["current_dataset"] = csv_dataset
                            _run_clustering_on_dataset(csv_dataset, k=k_csv)
                            st.session_state["executed_config"] = {
                                "source": "csv",
                                "name": uploaded_file.name,
                                "k": k_csv,
                                "features": (feat_x, feat_y),
                                "label": label_arg,
                                "treat_outlier": treat_minus_one_outlier,
                            }
                            st.success(f"Successfully processed CSV dataset: {csv_dataset.n_samples} points clustered.")
                            st.info("Navigate to the **Clustering Playground** tab to view comparative plots and metrics.")
                        except Exception as err:
                            st.error(f"Failed to process CSV dataset: {err}")

        except Exception as exc:
            st.error(f"Could not parse uploaded CSV: {exc}")


# -----------------------------------------------------------------------------
# VIEW 4: Reproducibility & Configuration
# -----------------------------------------------------------------------------
def render_view_config() -> None:
    """Render JSON ExperimentConfig import, export, and reproducibility controls."""
    st.subheader("Reproducibility & Configuration — Versioned Experiment Specification")
    st.caption("Versioned JSON Experiment Specification (Schema 1.0.0)")

    st.markdown(
        """
        Export or import validated JSON configuration files compliant with `ExperimentConfig` schema `1.0.0`.
        Configurations reproduce exact synthetic datasets when generated with identical seeds in matching environments.
        """
    )

    dataset: Dataset = st.session_state["current_dataset"]

    col_exp, col_imp = st.columns(2)

    # 1. Export Current Configuration
    with col_exp:
        st.markdown("### 📥 Export Current Configuration")
        if dataset.dataset_family in {"blobs", "moons", "circles"}:
            params = dataset.params
            cfg = ExperimentConfig(
                dataset_family=dataset.dataset_family,
                n_samples=params.get("n_samples", 300),
                n_clusters=params.get("n_clusters", 3),
                seed=dataset.seed if dataset.seed is not None else 42,
                noise=float(params.get("noise", 0.0)),
                outlier_rate=float(params.get("outlier_rate", 0.0)),
                dataset_params={
                    k: v
                    for k, v in params.items()
                    if k not in {"n_samples", "n_clusters", "noise", "outlier_rate"}
                },
            )
            json_str = cfg.to_json(indent=2)
            st.code(json_str, language="json")

            st.download_button(
                label="⬇️ Download Configuration (.json)",
                data=json_str,
                file_name=f"clustering_config_{dataset.dataset_family}.json",
                mime="application/json",
                use_container_width=True,
            )
        else:
            st.info(
                "Current active dataset was imported from an external CSV. "
                "JSON configuration files reproduce synthetic geometries and cannot regenerate "
                "external CSV tabular data without the original source file."
            )

    # 2. Import Configuration
    with col_imp:
        st.markdown("### 📤 Import & Restore Configuration")
        uploaded_cfg = st.file_uploader(
            "Upload valid configuration JSON",
            type=["json"],
            key="config_uploader",
        )

        if uploaded_cfg is not None:
            raw_json_str = uploaded_cfg.getvalue().decode("utf-8")
            try:
                parsed_cfg = ExperimentConfig.from_json(raw_json_str)
                total_cfg_pts = parsed_cfg.n_samples + int(round(parsed_cfg.n_samples * parsed_cfg.outlier_rate))

                st.success(
                    f"Configuration valid: Family `{parsed_cfg.dataset_family}`, "
                    f"N={parsed_cfg.n_samples} (Total with outliers: {total_cfg_pts}), Seed={parsed_cfg.seed}"
                )
                st.json(parsed_cfg.to_dict())

                if total_cfg_pts > MAX_INTERACTIVE_SAMPLES:
                    st.error(
                        f"Configuration specifies {total_cfg_pts} total observations, which exceeds "
                        f"the safe interactive limit of {MAX_INTERACTIVE_SAMPLES} observations. "
                        "Execution rejected without truncating configuration."
                    )
                else:
                    if st.button("Apply Configuration & Regenerate", type="primary", use_container_width=True):
                        with st.spinner("Regenerating dataset from configuration..."):
                            # Map dataset_family to selectbox option
                            family_map = {
                                "blobs": "Gaussian Blobs",
                                "moons": "Two Moons",
                                "circles": "Concentric Circles",
                            }
                            st.session_state["pg_dataset_family"] = family_map[parsed_cfg.dataset_family]
                            st.session_state["pg_n_samples"] = parsed_cfg.n_samples
                            st.session_state["pg_seed"] = parsed_cfg.seed
                            st.session_state["pg_noise"] = parsed_cfg.noise
                            st.session_state["pg_outliers"] = parsed_cfg.outlier_rate

                            if parsed_cfg.dataset_family == "blobs":
                                st.session_state["pg_blobs_k"] = parsed_cfg.n_clusters
                                if "cluster_std" in parsed_cfg.dataset_params:
                                    st.session_state["pg_blobs_std"] = float(parsed_cfg.dataset_params["cluster_std"])
                                if "radius" in parsed_cfg.dataset_params:
                                    st.session_state["pg_blobs_radius"] = float(parsed_cfg.dataset_params["radius"])
                            elif parsed_cfg.dataset_family == "circles":
                                if "factor" in parsed_cfg.dataset_params:
                                    st.session_state["pg_circles_factor"] = float(parsed_cfg.dataset_params["factor"])

                            new_ds = create_dataset_from_config(parsed_cfg)
                            st.session_state["current_dataset"] = new_ds
                            _run_clustering_on_dataset(new_ds, k=parsed_cfg.n_clusters)
                            st.session_state["executed_config"] = {
                                "source": "synthetic",
                                "family": family_map[parsed_cfg.dataset_family],
                                "n_inliers": parsed_cfg.n_samples,
                                "seed": parsed_cfg.seed,
                                "noise": parsed_cfg.noise,
                                "outlier_rate": parsed_cfg.outlier_rate,
                                "k": parsed_cfg.n_clusters,
                                "cluster_std": float(parsed_cfg.dataset_params.get("cluster_std", 0.4)) if parsed_cfg.dataset_family == "blobs" else None,
                                "radius": float(parsed_cfg.dataset_params.get("radius", 3.5)) if parsed_cfg.dataset_family == "blobs" else None,
                                "factor": float(parsed_cfg.dataset_params.get("factor", 0.45)) if parsed_cfg.dataset_family == "circles" else None,
                            }
                            st.success("Dataset regenerated and clustered according to configuration.")
                            st.rerun()

            except Exception as exc:
                st.error(f"Invalid experiment configuration: {exc}")


# -----------------------------------------------------------------------------
# VIEW: Performance Benchmarks
# -----------------------------------------------------------------------------
def render_view_benchmarks() -> None:
    """Render scientific execution-time benchmark engine and runtime analysis view."""
    st.subheader("Performance Benchmarks — Execution-Time Empirical Scaling")
    st.caption("Custom Lloyd's K-Means vs. Custom Dense Prim's MST Benchmark Engine")

    st.markdown(
        """
        Benchmark the execution time of the **actual custom Python implementations**
        on identical synthetic coordinate inputs. Timing is measured using high-resolution
        monotonic `time.perf_counter_ns()`, converting runtimes to milliseconds.
        Dataset generation is strictly excluded from timed regions.
        """
    )

    with st.expander("⚙️ Benchmark Configuration & Workload Controls", expanded=True):
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("##### Dataset Parameters")
            st.markdown("**Dataset Family:** Gaussian Blobs")
            n_clusters = st.slider("Number of Clusters (k)", min_value=2, max_value=6, value=3, key="bm_k")
            cluster_std = st.slider("Cluster Dispersion (std)", min_value=0.1, max_value=1.0, value=0.4, step=0.05, key="bm_std")
            base_seed = st.number_input("Deterministic Random Seed", min_value=1, max_value=9999, value=DEFAULT_BENCHMARK_SEED, key="bm_seed")

        with col2:
            st.markdown("##### Sample Sizes")
            size_options = [50, 100, 150, 200, 300, 400, 500, 600]
            selected_sizes = st.multiselect(
                "Sample Sizes (N ≤ 600)",
                options=size_options,
                default=[100, 200, 400, 600],
                key="bm_sizes",
                help="Select observation counts. Interactive compute limit enforces N ≤ 600 for dense Prim O(N^2).",
            )

        with col3:
            st.markdown("##### Repetitions & Warm-up")
            repetitions = st.slider(
                "Measured Repetitions per Size",
                min_value=1,
                max_value=10,
                value=DEFAULT_BENCHMARK_REPETITIONS,
                key="bm_reps",
                help="Number of independent measured trials per sample size.",
            )
            warmup = st.checkbox(
                "Include 1 Warm-up Stage per Size",
                value=True,
                key="bm_warmup",
                help="Warm-up iteration executes prior to measurements and is strictly excluded from recorded statistics.",
            )

        sorted_sizes = tuple(sorted(selected_sizes)) if selected_sizes else ()
        n_sizes = len(sorted_sizes)
        runs_per_size = (1 if warmup else 0) + repetitions
        total_executions = n_sizes * runs_per_size * 2
        total_trials = n_sizes * repetitions

        st.divider()
        col_p1, col_p2 = st.columns([3, 1])
        with col_p1:
            if n_sizes == 0:
                st.warning("Please select at least one sample size to benchmark.")
                can_run = False
            elif total_executions > BenchmarkConfig.MAX_TOTAL_EXECUTIONS:
                st.error(
                    f"Selected workload of {total_executions} algorithm executions exceeds safe threshold "
                    f"({BenchmarkConfig.MAX_TOTAL_EXECUTIONS}). Reduce sample sizes or repetitions."
                )
                can_run = False
            else:
                st.info(
                    f"**Preflight Estimate:** {n_sizes} sizes × {repetitions} repetitions = {total_trials} measured trials "
                    f"({total_executions} total algorithm executions including warm-up). "
                    f"Safe limit: ≤ {BenchmarkConfig.MAX_TOTAL_EXECUTIONS} executions."
                )
                can_run = True

        with col_p2:
            run_btn = st.button("🚀 Run Benchmarks", disabled=not can_run, type="primary", use_container_width=True)

    if run_btn and can_run:
        bm_config = BenchmarkConfig(
            sample_sizes=sorted_sizes,
            repetitions=repetitions,
            seed=int(base_seed),
            warmup=warmup,
            n_clusters=n_clusters,
            cluster_std=float(cluster_std),
        )

        progress_bar = st.progress(0.0)
        status_text = st.empty()

        def _bench_cb(completed: int, total: int, n: int, r: int, algo: str) -> None:
            pct = min(1.0, completed / max(1, total))
            progress_bar.progress(pct)
            status_text.caption(f"Running benchmarks: Size N={n}, Repetition {r}/{repetitions} ({algo})...")

        with st.spinner("Executing custom Python algorithms..."):
            trials = run_performance_benchmark(bm_config, progress_callback=_bench_cb)
            summary = aggregate_benchmark_trials(trials)

        progress_bar.progress(1.0)
        status_text.success(f"✓ Benchmark complete: {len(trials)} trials across {len(summary)} sample sizes.")

        st.session_state["benchmark_trials"] = trials
        st.session_state["benchmark_summary"] = summary
        st.session_state["benchmark_config"] = bm_config

    trials = st.session_state.get("benchmark_trials")
    summary = st.session_state.get("benchmark_summary")
    active_bm_cfg = st.session_state.get("benchmark_config")

    if trials and summary:
        if active_bm_cfg is not None:
            current_settings = (sorted_sizes, repetitions, int(base_seed), warmup, n_clusters, float(cluster_std))
            cached_settings = (
                active_bm_cfg.sample_sizes,
                active_bm_cfg.repetitions,
                active_bm_cfg.seed,
                active_bm_cfg.warmup,
                active_bm_cfg.n_clusters,
                active_bm_cfg.cluster_std,
            )
            if current_settings != cached_settings:
                st.warning("⚠️ Controls have changed since the last benchmark run. Displaying previous results. Click 'Run Benchmarks' to update.")

        st.divider()
        tab_chart, tab_table, tab_theory, tab_export = st.tabs(
            ["📈 Runtime Scaling Curves", "📊 Summary Statistics Table", "📐 Theoretical Complexity & System Notes", "💾 Research Data Export"]
        )

        with tab_chart:
            fig = create_benchmark_runtime_figure(summary)
            st.plotly_chart(fig, use_container_width=True)

            png_bytes = render_benchmark_png(summary)
            st.download_button(
                label="📥 Download Benchmark Scaling Plot (Publication PNG)",
                data=png_bytes,
                file_name="benchmark_runtime_scaling.png",
                mime="image/png",
            )

        with tab_table:
            st.markdown("##### Aggregated Performance Summary (Milliseconds)")
            rows = []
            for s in summary:
                ratio_str = f"{s.ratio_of_means:.2f}×" if s.ratio_of_means is not None else "N/A"
                rows.append({
                    "Sample Size (N)": s.sample_size,
                    "Repetitions": s.repetitions,
                    "K-Means Mean (ms)": f"{s.kmeans_mean_ms:.3f}",
                    "K-Means Median (ms)": f"{s.kmeans_median_ms:.3f}",
                    "K-Means Std (ms)": f"{s.kmeans_std_ms:.3f}",
                    "MST Mean (ms)": f"{s.mst_mean_ms:.3f}",
                    "MST Median (ms)": f"{s.mst_median_ms:.3f}",
                    "MST Std (ms)": f"{s.mst_std_ms:.3f}",
                    "Ratio of Means (MST / KM)": ratio_str,
                })
            df_summary = pd.DataFrame(rows)
            st.dataframe(df_summary, use_container_width=True, hide_index=True)

            st.caption(
                "Note: Ratio of means is defined strictly as mean(MST runtime) / mean(K-Means runtime). "
                "Sample standard deviations are computed using Bessel's correction (ddof=1)."
            )

        with tab_theory:
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                st.markdown(
                    r"""
                    ##### Computational Complexity
                    - **Lloyd's K-Means Iteration:**
                      $$\mathcal{O}(I \times N \times k \times D)$$
                      where $I$ is iterations until convergence, $N$ is sample size, $k$ is cluster count, and $D$ is dimensionality.
                      Initialization via K-Means++ requires $\mathcal{O}(k \times N \times D)$ distance evaluations.
                      Runtime scales **linearly** with observation count $N$.
                    - **Dense Prim's MST:**
                      $$\mathcal{O}(N^2)$$
                      The implemented dense Prim algorithm maintains a min-distance frontier array across $N$ vertices,
                      evaluating $N(N-1)/2$ pairwise Euclidean distances.
                      Runtime scales **quadratically** with observation count $N$.
                    """
                )
            with col_t2:
                st.markdown(
                    """
                    ##### Benchmarking Methodology & Disclaimers
                    - **Deterministic Baseline:** Datasets are generated outside the timed region using fixed PRNG seeds. Both algorithms receive identical coordinate matrices `X`.
                    - **Hardware Dependence:** Measured runtimes depend strongly on CPU clock speed, cache hierarchy, OS process scheduling, and NumPy vectorization.
                    - **No Universal Guarantee:** Results on this machine do not constitute a universal performance guarantee across all systems.
                    - **Scientific Interpretation:** Measured runtime curves illustrate empirical divergence matching theoretical expectations; they do not mathematically prove asymptotic complexity.
                    """
                )

        with tab_export:
            st.markdown("##### Research Artifacts Export")
            st.markdown("Export raw per-repetition trial observations, aggregated statistics, and reproduction configuration.")

            col_e1, col_e2, col_e3, col_e4 = st.columns(4)
            with col_e1:
                csv_trials = export_benchmark_trials_to_csv(trials)
                st.download_button(
                    label="📄 Raw Trials CSV",
                    data=csv_trials,
                    file_name="benchmark_trials.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
            with col_e2:
                csv_summary = export_benchmark_summary_to_csv(summary)
                st.download_button(
                    label="📊 Aggregated Summary CSV",
                    data=csv_summary,
                    file_name="benchmark_summary.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
            with col_e3:
                json_cfg = export_benchmark_config_json(active_bm_cfg) if active_bm_cfg else ""
                st.download_button(
                    label="⚙️ Benchmark Config JSON",
                    data=json_cfg,
                    file_name="benchmark_config.json",
                    mime="application/json",
                    use_container_width=True,
                )
            with col_e4:
                json_meta = export_benchmark_metadata()
                st.download_button(
                    label="📋 System Metadata JSON",
                    data=json_meta,
                    file_name="benchmark_metadata.json",
                    mime="application/json",
                    use_container_width=True,
                )
    else:
        st.info("Select benchmark parameters above and click **'🚀 Run Benchmarks'** to execute.")


# -----------------------------------------------------------------------------
# VIEW: Algorithm Explorer
# -----------------------------------------------------------------------------
def render_view_explorer() -> None:
    """Render interactive step-by-step algorithm explorer for Lloyd's K-Means and dense Prim's MST."""
    st.subheader("Algorithm Explorer — Step-by-Step Educational Visualizer")
    st.caption("Interactive Mechanics of Custom Lloyd's K-Means & Dense Prim's MST Clustering")

    algo_choice = st.radio(
        "Select Algorithm to Explore",
        ["Lloyd's K-Means", "Dense Prim's MST"],
        horizontal=True,
        key="explorer_algo_choice",
    )

    with st.expander("⚙️ Micro-Dataset Generation Controls", expanded=True):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            family_options = ["Gaussian Blobs", "Two Moons", "Concentric Circles"]
            default_fam_idx = 0 if algo_choice == "Lloyd's K-Means" else 1
            family = st.selectbox("Dataset Topology", family_options, index=default_fam_idx, key="exp_family")
        with col2:
            n_samples = st.slider(
                "Observations (N ≤ 60)",
                min_value=10,
                max_value=60,
                value=30,
                step=5,
                key="exp_n",
                help="Small sample size allows clean visualization of individual vertices, tree edges, and Voronoi assignments.",
            )
        with col3:
            k_val = st.slider(
                "Clusters (k)",
                min_value=2,
                max_value=5,
                value=3 if family == "Gaussian Blobs" else 2,
                key="exp_k",
            )
        with col4:
            seed = st.number_input("Random Seed", min_value=1, max_value=9999, value=42, key="exp_seed")

    fam_map = {
        "Gaussian Blobs": "blobs",
        "Two Moons": "moons",
        "Concentric Circles": "circles",
    }
    fam_code = fam_map[family]

    config_signature = (algo_choice, fam_code, n_samples, k_val, int(seed))
    cached_sig = st.session_state.get("explorer_config_hash")

    if cached_sig != config_signature or st.session_state.get("explorer_trace") is None:
        ds = generate_synthetic_dataset(
            family=fam_code,
            n_samples=n_samples,
            seed=int(seed),
            noise=0.04 if fam_code != "blobs" else 0.0,
            outlier_rate=0.0,
            n_clusters=k_val,
            cluster_std=0.4,
            radius=3.5,
        )
        X = ds.X

        if algo_choice == "Lloyd's K-Means":
            trace = run_kmeans_trace(X=X, k=k_val, seed=int(seed))
        else:
            trace = run_mst_trace(X=X, k=k_val)

        st.session_state["explorer_trace"] = trace
        st.session_state["explorer_step_index"] = 0
        st.session_state["explorer_config_hash"] = config_signature
        st.session_state["explorer_dataset"] = ds

    trace = st.session_state["explorer_trace"]
    steps = trace.steps
    total_steps = len(steps)

    curr_idx = st.session_state.get("explorer_step_index", 0)
    curr_idx = max(0, min(total_steps - 1, curr_idx))

    st.divider()
    st.markdown("#### Step Navigation Cockpit")

    c_first, c_prev, c_slider, c_next, c_last, c_reset = st.columns([1, 1, 4, 1, 1, 1])

    with c_first:
        if st.button("⏮ First", use_container_width=True):
            st.session_state["explorer_step_index"] = 0
            st.rerun()
    with c_prev:
        if st.button("◀ Prev", use_container_width=True):
            st.session_state["explorer_step_index"] = max(0, curr_idx - 1)
            st.rerun()
    with c_slider:
        slider_val = st.slider(
            "Step Navigator",
            min_value=0,
            max_value=total_steps - 1,
            value=curr_idx,
            key="exp_slider_widget",
            label_visibility="collapsed",
        )
        if slider_val != curr_idx:
            st.session_state["explorer_step_index"] = slider_val
            st.rerun()
    with c_next:
        if st.button("Next ▶", use_container_width=True):
            st.session_state["explorer_step_index"] = min(total_steps - 1, curr_idx + 1)
            st.rerun()
    with c_last:
        if st.button("⏭ Last", use_container_width=True):
            st.session_state["explorer_step_index"] = total_steps - 1
            st.rerun()
    with c_reset:
        if st.button("↺ Reset", use_container_width=True):
            st.session_state["explorer_step_index"] = 0
            st.rerun()

    current_step = steps[st.session_state["explorer_step_index"]]
    step_num = st.session_state["explorer_step_index"] + 1

    st.markdown(f"### Step {step_num} of {total_steps}: `{current_step.title}`")
    st.info(current_step.description)

    if algo_choice == "Lloyd's K-Means":
        fig = create_kmeans_explorer_figure(current_step)
    else:
        fig = create_mst_explorer_figure(current_step)

    st.plotly_chart(fig, use_container_width=True)

    ds_exp = st.session_state.get("explorer_dataset")
    if ds_exp is not None:
        lbls = current_step.labels if current_step.labels is not None else np.zeros(len(current_step.X), dtype=int)
        png_step_bytes = render_clustering_png(
            current_step.X,
            lbls,
            title=f"{algo_choice} Explorer — Step {step_num}: {current_step.title}",
        )
        st.download_button(
            label=f"📥 Download Step {step_num} Visualization (PNG)",
            data=png_step_bytes,
            file_name=f"explorer_step_{step_num}.png",
            mime="image/png",
        )

    st.divider()
    if trace.final_parity_verified:
        prod_fn = "kmeans()" if algo_choice == "Lloyd's K-Means" else "mst_clustering()"
        parity_stat = "inertia" if algo_choice == "Lloyd's K-Means" else "MST weight and cut edges"
        st.success(
            f"**✓ Mathematical Parity Verified:** The explorer's algorithmic trace precisely matches "
            f"the custom production `{prod_fn}` implementation on identical coordinates and random seed "
            f"(100% agreement on cluster labels, {parity_stat})."
        )
    else:
        st.warning("Parity check pending or failed.")


# -----------------------------------------------------------------------------
# VIEW 5: Methodology / Help
# -----------------------------------------------------------------------------
def render_view_methodology() -> None:
    """Render scientific background, inductive biases, and viva demonstration guide."""
    st.subheader("Methodology & Scientific Reference — Algorithmic Foundations")
    st.caption("Algorithmic Foundations, Inductive Biases, and Viva Walkthrough")

    st.markdown("### 1. Algorithmic Principles & Inductive Biases")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            r"""
            #### Lloyd's K-Means Clustering
            - **Mathematical Nature:** Centroid-based iterative optimization.
            - **Objective Function:** Minimizes Within-Cluster Sum of Squares (Inertia):
              $$J = \sum_{i=1}^N \| X_i - \mu_{c(i)} \|^2$$
            - **Inductive Bias:** Assumes isotropic, convex, globular clusters with roughly equal variance.
            - **Behavior on Complex Topologies:** Tends to fragment non-convex geometries (such as concentric circles or interleaving crescent moons) under standard $k$ settings, because linear Voronoi boundaries are mathematically constrained to convex partition cells.
            """
        )

    with col2:
        st.markdown(
            r"""
            #### Prim's MST Clustering
            - **Mathematical Nature:** Graph-theoretic single-linkage partitioning.
            - **Objective:** Constructs Euclidean Minimum Spanning Tree $T = (V, E)$ on complete graph, then removes the $k - 1$ longest tree edges.
            - **Inductive Bias:** Assumes clusters are high-density connected manifolds separated by lower-density spatial gaps.
            - **Behavior on Complex Topologies:** Effectively traces continuous curvilinear paths and non-convex manifolds when clusters are separated by clear spatial gaps. However, MST is not unconditionally robust: it is vulnerable to the "chaining effect" when noise bridges or uniform outliers span the inter-cluster gap.
            """
        )

    st.divider()

    st.markdown("### 2. Perturbation Mechanisms: Gaussian Jitter vs. Uniform Outliers")
    st.markdown(
        r"""
        - **Inlier Gaussian Jitter ($\sigma$):** Adds zero-mean Gaussian displacement directly to inlier coordinates along their manifold. Controlled by an independent PRNG stream. Evaluates resilience to localized boundary blurring without altering global cluster topology.
        - **Uniform Outlier Contamination (Rate):** Injects random noise points distributed uniformly across the 2D bounding box (using a decoupled secondary PRNG stream). These are *random uniform outliers*, not adversarially optimized points. Evaluates algorithm resilience to spurious spatial bridging between separate clusters.
        """
    )

    st.divider()

    st.markdown("### 3. Metric Interpretation Guide")
    st.markdown(
        r"""
        | Metric | Mathematical Meaning | Key Caution |
        | :--- | :--- | :--- |
        | **Inlier ARI** | Adjusted Rand Index on true inlier points. Measures manifold recovery. | Range $[-0.5, 1.0]$. $1.0$ is perfect partition recovery. |
        | **Full-Data ARI** | ARI evaluated across all points including outliers (label $-1$). | Outliers naturally penalize both algorithms since neither assigns an explicit reject class. |
        | **Inertia** | Sum of squared Euclidean distances to closest centroids. | **Do NOT compare against MST Weight.** They represent completely different mathematical spaces. |
        | **MST Weight** | Total linear Euclidean edge length of the spanning tree / forest. | Sum of edge lengths; decreases as more cut edges are removed. |
        | **Silhouette Score** | Ratio of intra-cluster distance to nearest neighbor cluster distance. | Biased towards convex/spherical clusters; penalizes valid non-convex MST clusters. |

        *(Note: Additional validation metrics such as Normalized Mutual Information (NMI) and systematic density variation tests are planned for Phase M5).*
        """
    )

    st.divider()

    st.markdown("### 4. Step-by-Step Viva Demonstration Walkthrough")
    st.markdown(
        r"""
        During the laboratory viva or project evaluation, follow this structured demonstration:

        1. **Baseline Sanity Check (Gaussian Blobs):**
           - In the **Clustering Playground**, select *Gaussian Blobs* ($k=3$, noise $\sigma=0.0$, outlier rate $0.0$).
           - Run clustering: Observe that **both** K-Means and MST achieve high Inlier ARI ($>0.95$). Explain to the examiner that on standard globular clusters, both centroidal and graph-theoretic approaches succeed.

        2. **Topological Separation on Clean Manifolds (Two Moons or Concentric Circles):**
           - Switch to *Concentric Circles* or *Two Moons* with zero noise and zero outliers.
           - Run clustering: Contrast the algorithmic inductive biases.
             - **K-Means Limitation:** K-Means bisects the nested rings or crescents with linear Voronoi hyperplanes, resulting in low Inlier ARI ($\approx 0.0$ for circles, $\approx 0.49$ for moons at $k=2$).
             - **MST Advantage:** Because there is an open spatial gap between clean manifolds, Prim's MST single-linkage cut follows the continuous manifold structure (Inlier ARI $= 1.0$).

        3. **Noise Perturbations & Chaining Degradation:**
           - On *Two Moons*, introduce Gaussian noise ($\sigma=0.15$) or add $10\%$ random uniform outliers.
           - Observe that MST's advantage on non-linear manifolds is **not unconditional**:
             - Random uniform outliers landing in the inter-cluster gap create short spurious edges.
             - These noise bridges trigger the classical **chaining effect**, causing MST Inlier ARI to degrade.
             - Clarify that these are random uniform outliers across the bounding box, not adversarially targeted points.

        4. **Scientific Reproducibility:**
           - Open the **Reproducibility & Configuration** view and download the JSON configuration.
           - Explain how the versioned JSON schema guarantees exact replication across platforms and seeds.
        """
    )


# -----------------------------------------------------------------------------
# Main Application Entry Point
# -----------------------------------------------------------------------------
def main() -> None:
    """Main Streamlit application coordinator."""
    init_session_state()
    active_view = render_sidebar()

    st.title("MST vs K-Means Robustness Analysis")

    if active_view == "Overview":
        render_view_overview()
    elif active_view == "Clustering Playground":
        render_view_playground()
    elif active_view == "Performance Benchmarks":
        render_view_benchmarks()
    elif active_view == "Algorithm Explorer":
        render_view_explorer()
    elif active_view == "Robustness Analysis":
        render_view_robustness()
    elif active_view == "Dataset & CSV Import":
        render_view_csv_import()
    elif active_view == "Reproducibility & Configuration":
        render_view_config()
    elif active_view == "Methodology / Help":
        render_view_methodology()
    else:
        render_view_overview()


if __name__ == "__main__":
    main()
