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
        - Himanshu Gupta (Roll No: [REDACTED_STUDENT_IDENTIFIER])
        - Parth Yadav (Roll No: [REDACTED_STUDENT_IDENTIFIER])
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

from clustering_lab.algorithms.kmeans import KMeansResult, kmeans
from clustering_lab.algorithms.mst import MSTClusteringResult, mst_clustering
from clustering_lab.data.config import ExperimentConfig, create_dataset_from_config
from clustering_lab.data.csv_loader import load_dataset_from_csv
from clustering_lab.data.dataset import Dataset
from clustering_lab.data.synthetic import generate_synthetic_dataset
from clustering_lab.evaluation.metrics import ClusteringMetrics, evaluate_clustering
from clustering_lab.visualization.figures import (
    create_ground_truth_figure,
    create_kmeans_figure,
    create_mst_figure,
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
            - **Himanshu Gupta** (`[REDACTED_STUDENT_IDENTIFIER]`)
            - **Parth Yadav** (`[REDACTED_STUDENT_IDENTIFIER]`)

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
            - **Phase:** `M4 — Streamlit Dashboard`
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
        > **Migration Phase M4 Active:** The interactive Python Streamlit research platform
        > executes **pure from-scratch implementations** of Lloyd's K-Means and dense Prim's MST clustering.
        > SciPy and scikit-learn are employed solely as independent test references and metric calculators.
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
        st.markdown("#### Implemented Dashboard Capabilities (Phases M1–M4)")
        st.markdown(
            r"""
            - **M1 Foundation:** Standardized Linux CI workflow and modular package architecture.
            - **M2 Scientific Algorithms:** Pure NumPy Lloyd's K-Means ($k$-means++ seeding) and dense Prim's Euclidean MST ($O(N^2)$ time, $O(N)$ space) with deterministic cut tie-breaking.
            - **M3 Reproducible Data Layer:** Blobs, Moons, and Circles generators with decoupled noise/outlier contamination; secure CSV loader; versioned JSON schema `1.0.0`.
            - **M4 Interactive Dashboard:** Real-time parameter controls ($N \le 600$), dual algorithm execution on identical matrices, 1:1 isotropic Plotly visualization, Inlier/Full ARI and safe Silhouette metrics, and bi-directional JSON configuration synchronization.
            """
        )

    with col2:
        st.markdown("#### Planned Subsequent Phases (Phase M5+)")
        st.markdown(
            r"""
            - **Phase M5 — Automated Robustness Experiment Engine:**
              - Multi-seed Monte Carlo sweep execution across hundreds of PRNG seeds.
              - Parameter degradation curves ($\sigma$ noise sweeps, outlier ratio curves).
              - Automated CSV benchmark reporting across varied spatial densities.
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
# VIEW 3: Dataset & CSV Import
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
