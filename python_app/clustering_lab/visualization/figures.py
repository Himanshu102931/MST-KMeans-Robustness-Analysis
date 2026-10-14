"""
clustering_lab.visualization.figures
====================================
Interactive, publication-quality Plotly 2D visualizations for clustering analysis:
1. Ground Truth / Input Dataset view (with distinct inlier classes and outlier markers).
2. K-Means clustering view (predicted Voronoi partitions + centroid overlays).
3. MST clustering view (connected components + single-linkage retained/cut tree edges).

All charts strictly preserve isotropic aspect ratios (1:1 Euclidean scale) to prevent
geometric distortion of concentric circles, crescent moons, or distances.
"""

from __future__ import annotations

from typing import Any, List, Optional
import numpy as np
import pandas as pd
import plotly.graph_objects as go

from clustering_lab.algorithms.kmeans import KMeansResult
from clustering_lab.algorithms.mst import MSTClusteringResult
from clustering_lab.data.dataset import Dataset

# Scientific color palette for clusters
CLUSTER_COLORS = [
    "#38bdf8",  # Sky Blue
    "#f43f5e",  # Rose Red
    "#10b981",  # Emerald Green
    "#f59e0b",  # Amber
    "#a855f7",  # Purple
    "#ec4899",  # Pink
    "#06b6d4",  # Cyan
    "#eab308",  # Yellow
    "#6366f1",  # Indigo
    "#14b8a6",  # Teal
]

OUTLIER_COLOR = "#ef4444"
CENTROID_COLOR = "#fbbf24"
RETAINED_EDGE_COLOR = "rgba(148, 163, 184, 0.45)"  # Slate-400 translucent
CUT_EDGE_COLOR = "#f43f5e"  # Rose-500 bold dashed


def _apply_standard_layout(
    fig: go.Figure,
    title: str,
    x_label: str = "Feature 1",
    y_label: str = "Feature 2",
    height: int = 520,
) -> None:
    """Apply consistent scientific theme, 1:1 aspect ratio, and typography."""
    fig.update_layout(
        title=dict(
            text=title,
            font=dict(size=15, color="#f8fafc", family="Inter, system-ui, sans-serif"),
            x=0.02,
            y=0.96,
        ),
        margin=dict(l=40, r=40, t=50, b=40),
        height=height,
        paper_bgcolor="#0f172a",  # Slate 900
        plot_bgcolor="#1e293b",   # Slate 800
        font=dict(color="#94a3b8", family="Inter, system-ui, sans-serif", size=12),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.22,
            xanchor="center",
            x=0.5,
            font=dict(size=11, color="#cbd5e1"),
            bgcolor="rgba(15, 23, 42, 0.8)",
            bordercolor="#334155",
            borderwidth=1,
        ),
        hoverlabel=dict(
            bgcolor="#1e293b",
            font_size=12,
            font_family="Inter, system-ui, sans-serif",
            font_color="#f8fafc",
            bordercolor="#475569",
        ),
    )
    # Ensure 1:1 aspect ratio: 1 Euclidean unit in x equals 1 Euclidean unit in y
    fig.update_xaxes(
        title=dict(text=x_label, font=dict(color="#cbd5e1", size=12)),
        gridcolor="#334155",
        zerolinecolor="#475569",
        showgrid=True,
    )
    fig.update_yaxes(
        title=dict(text=y_label, font=dict(color="#cbd5e1", size=12)),
        gridcolor="#334155",
        zerolinecolor="#475569",
        showgrid=True,
        scaleanchor="x",
        scaleratio=1,
    )


def create_ground_truth_figure(dataset: Dataset, height: int = 520) -> go.Figure:
    """Create 2D scatter plot of dataset showing true classes and distinct outliers."""
    fig = go.Figure()
    X = dataset.X

    # Resolve axis labels from metadata if available
    feat_cols = dataset.metadata.get("feature_columns", ["Feature 1", "Feature 2"])
    x_label = feat_cols[0] if len(feat_cols) > 0 else "Feature 1"
    y_label = feat_cols[1] if len(feat_cols) > 1 else "Feature 2"

    if dataset.labels is not None:
        labels = dataset.labels
        unique_labels = sorted([int(lbl) for lbl in np.unique(labels) if lbl != -1])

        # Plot each inlier class
        for i, class_id in enumerate(unique_labels):
            mask = labels == class_id
            pts = X[mask]
            color = CLUSTER_COLORS[i % len(CLUSTER_COLORS)]
            fig.add_trace(
                go.Scatter(
                    x=pts[:, 0],
                    y=pts[:, 1],
                    mode="markers",
                    name=f"Class {class_id} ({len(pts)} pts)",
                    marker=dict(size=7, color=color, opacity=0.88, line=dict(width=0.5, color="#0f172a")),
                    hovertemplate=(
                        f"<b>Class {class_id}</b><br>"
                        + f"{x_label}: %{{x:.3f}}<br>"
                        + f"{y_label}: %{{y:.3f}}<extra></extra>"
                    ),
                )
            )

        # Plot outliers if present
        outlier_mask = labels == -1
        if np.any(outlier_mask):
            outlier_pts = X[outlier_mask]
            fig.add_trace(
                go.Scatter(
                    x=outlier_pts[:, 0],
                    y=outlier_pts[:, 1],
                    mode="markers",
                    name=f"Outliers ({len(outlier_pts)} pts)",
                    marker=dict(
                        size=8,
                        color=OUTLIER_COLOR,
                        symbol="x",
                        opacity=0.95,
                        line=dict(width=1.5, color=OUTLIER_COLOR),
                    ),
                    hovertemplate=(
                        "<b>Outlier (Noise)</b><br>"
                        + f"{x_label}: %{{x:.3f}}<br>"
                        + f"{y_label}: %{{y:.3f}}<extra></extra>"
                    ),
                )
            )
    else:
        # Unlabeled observations
        fig.add_trace(
            go.Scatter(
                x=X[:, 0],
                y=X[:, 1],
                mode="markers",
                name=f"Unlabeled Observations ({len(X)} pts)",
                marker=dict(size=7, color="#38bdf8", opacity=0.85, line=dict(width=0.5, color="#0f172a")),
                hovertemplate=(
                    "<b>Observation</b><br>"
                    + f"{x_label}: %{{x:.3f}}<br>"
                    + f"{y_label}: %{{y:.3f}}<extra></extra>"
                ),
            )
        )

    title_text = f"Dataset Ground Truth ({dataset.dataset_family.capitalize()} — N={dataset.n_samples})"
    _apply_standard_layout(fig, title=title_text, x_label=x_label, y_label=y_label, height=height)
    return fig


def create_kmeans_figure(
    dataset: Dataset,
    result: KMeansResult,
    height: int = 520,
) -> go.Figure:
    """Create 2D scatter plot of K-Means clustering with Voronoi partitions and centroids."""
    fig = go.Figure()
    X = dataset.X
    labels = result.labels
    unique_clusters = sorted([int(lbl) for lbl in np.unique(labels)])

    feat_cols = dataset.metadata.get("feature_columns", ["Feature 1", "Feature 2"])
    x_label = feat_cols[0] if len(feat_cols) > 0 else "Feature 1"
    y_label = feat_cols[1] if len(feat_cols) > 1 else "Feature 2"

    # Plot sample points colored by predicted cluster
    for i, cluster_id in enumerate(unique_clusters):
        mask = labels == cluster_id
        pts = X[mask]
        color = CLUSTER_COLORS[i % len(CLUSTER_COLORS)]
        fig.add_trace(
            go.Scatter(
                x=pts[:, 0],
                y=pts[:, 1],
                mode="markers",
                name=f"Cluster {cluster_id} ({len(pts)} pts)",
                marker=dict(size=7, color=color, opacity=0.88, line=dict(width=0.5, color="#0f172a")),
                hovertemplate=(
                    f"<b>K-Means Cluster {cluster_id}</b><br>"
                    + f"{x_label}: %{{x:.3f}}<br>"
                    + f"{y_label}: %{{y:.3f}}<extra></extra>"
                ),
            )
        )

    # Plot computed centroids
    centers = result.cluster_centers
    fig.add_trace(
        go.Scatter(
            x=centers[:, 0],
            y=centers[:, 1],
            mode="markers",
            name="Centroids",
            marker=dict(
                size=14,
                color=CENTROID_COLOR,
                symbol="star",
                line=dict(width=1.5, color="#0f172a"),
            ),
            hovertemplate=(
                "<b>Centroid</b><br>"
                + f"{x_label}: %{{x:.3f}}<br>"
                + f"{y_label}: %{{y:.3f}}<extra></extra>"
            ),
        )
    )

    conv_str = "Converged" if result.converged else "Max Iterations Reached"
    title_text = f"K-Means Clustering (k={result.k}, Inertia={result.inertia:.2f}, {conv_str})"
    _apply_standard_layout(fig, title=title_text, x_label=x_label, y_label=y_label, height=height)
    return fig


def create_mst_figure(
    dataset: Dataset,
    result: MSTClusteringResult,
    show_retained_edges: bool = True,
    show_cut_edges: bool = True,
    height: int = 520,
) -> go.Figure:
    """Create 2D scatter plot of MST clustering with graph topology tree overlays."""
    fig = go.Figure()
    X = dataset.X
    labels = result.labels
    unique_components = sorted([int(lbl) for lbl in np.unique(labels)])

    feat_cols = dataset.metadata.get("feature_columns", ["Feature 1", "Feature 2"])
    x_label = feat_cols[0] if len(feat_cols) > 0 else "Feature 1"
    y_label = feat_cols[1] if len(feat_cols) > 1 else "Feature 2"

    # Retained edges trace (combined single trace with None separators for speed)
    if show_retained_edges and len(result.mst_edges) > 0:
        edge_x: List[Optional[float]] = []
        edge_y: List[Optional[float]] = []
        for edge in result.mst_edges:
            if not edge.is_cut:
                edge_x.extend([float(X[edge.u, 0]), float(X[edge.v, 0]), None])
                edge_y.extend([float(X[edge.u, 1]), float(X[edge.v, 1]), None])

        if len(edge_x) > 0:
            fig.add_trace(
                go.Scatter(
                    x=edge_x,
                    y=edge_y,
                    mode="lines",
                    name="Retained MST Edges",
                    line=dict(color=RETAINED_EDGE_COLOR, width=1.2),
                    hoverinfo="none",
                )
            )

    # Cut edges trace
    if show_cut_edges and len(result.cut_edges) > 0:
        cut_x: List[Optional[float]] = []
        cut_y: List[Optional[float]] = []
        for edge in result.cut_edges:
            cut_x.extend([float(X[edge.u, 0]), float(X[edge.v, 0]), None])
            cut_y.extend([float(X[edge.u, 1]), float(X[edge.v, 1]), None])

        if len(cut_x) > 0:
            fig.add_trace(
                go.Scatter(
                    x=cut_x,
                    y=cut_y,
                    mode="lines",
                    name=f"Cut Edges ({len(result.cut_edges)} cuts)",
                    line=dict(color=CUT_EDGE_COLOR, width=2.2, dash="dash"),
                    hoverinfo="none",
                )
            )

    # Plot sample points colored by predicted connected component
    for i, comp_id in enumerate(unique_components):
        mask = labels == comp_id
        pts = X[mask]
        color = CLUSTER_COLORS[i % len(CLUSTER_COLORS)]
        fig.add_trace(
            go.Scatter(
                x=pts[:, 0],
                y=pts[:, 1],
                mode="markers",
                name=f"Component {comp_id} ({len(pts)} pts)",
                marker=dict(size=7, color=color, opacity=0.88, line=dict(width=0.5, color="#0f172a")),
                hovertemplate=(
                    f"<b>MST Component {comp_id}</b><br>"
                    + f"{x_label}: %{{x:.3f}}<br>"
                    + f"{y_label}: %{{y:.3f}}<extra></extra>"
                ),
            )
        )

    title_text = (
        f"MST Clustering (k={result.k}, Total Weight={result.total_mst_weight:.2f}, "
        f"Retained={result.retained_weight:.2f})"
    )
    _apply_standard_layout(fig, title=title_text, x_label=x_label, y_label=y_label, height=height)
    return fig


def create_robustness_curve_figure(
    aggregates_df: pd.DataFrame,
    family: str,
    sweep_type: str,
    metric_col: str = "mean_inlier_ari",
    std_col: Optional[str] = "std_inlier_ari",
    y_label: str = "Inlier Adjusted Rand Index (ARI)",
    title_suffix: str = "Robustness Curve",
    height: int = 480,
) -> go.Figure:
    """Plot mean metric trajectory comparing K-Means and Prim's MST with sample std error bars.

    Args:
        aggregates_df: DataFrame containing SweepAggregateRow records.
        family: Selected dataset family ('blobs', 'moons', 'circles').
        sweep_type: Selected perturbation sweep ('noise' or 'outlier').
        metric_col: Name of column containing the mean metric to plot.
        std_col: Name of column containing sample standard deviation (or None).
        y_label: Y-axis title.
        title_suffix: Suffix for the chart title.
        height: Figure height in pixels.

    Returns:
        Plotly Figure with dual algorithm traces and error bars.
    """
    fig = go.Figure()

    sub = aggregates_df[
        (aggregates_df["dataset_family"] == family.lower())
        & (aggregates_df["sweep_type"] == sweep_type.lower())
    ].sort_values(by="parameter_value")

    if sub.empty:
        fig.add_annotation(
            text="No experiment data available for selected filter.",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=14, color="#94a3b8"),
        )
        return fig

    param_name = sub["parameter_name"].iloc[0] if not sub.empty else "Parameter"
    x_label = (
        "Gaussian Noise Standard Deviation (sigma)"
        if param_name == "noise_sigma"
        else "Uniform Outlier Contamination Rate"
    )

    algorithms = [
        ("Lloyd K-Means", "#38bdf8", "circle"),     # Sky blue
        ("Prim MST", "#10b981", "diamond"),          # Emerald green
    ]

    n_seeds_reported = 1
    for algo_name, color, symbol in algorithms:
        algo_sub = sub[sub["algorithm"] == algo_name].sort_values(by="parameter_value")
        if algo_sub.empty:
            continue

        x_vals = algo_sub["parameter_value"].values
        y_vals = algo_sub[metric_col].values
        n_seeds_reported = int(algo_sub["n_seeds"].iloc[0])

        error_dict = None
        if std_col and std_col in algo_sub.columns and n_seeds_reported > 1:
            std_vals = algo_sub[std_col].values
            error_dict = dict(
                type="data",
                array=std_vals,
                visible=True,
                thickness=1.5,
                width=4,
                color=color,
            )

        fig.add_trace(
            go.Scatter(
                x=x_vals,
                y=y_vals,
                error_y=error_dict,
                mode="lines+markers",
                name=f"{algo_name} (Mean ± Std)",
                line=dict(color=color, width=2.5),
                marker=dict(symbol=symbol, size=8, color=color),
                hovertemplate=(
                    f"<b>{algo_name}</b><br>"
                    + f"{param_name}: %{{x:.2f}}<br>"
                    + f"{y_label}: %{{y:.4f}}<br>"
                    + f"Seeds (N): {n_seeds_reported}<extra></extra>"
                ),
            )
        )

    family_title = family.capitalize()
    if family.lower() == "blobs":
        family_title = "Gaussian Blobs"
    elif family.lower() == "moons":
        family_title = "Two Moons"
    elif family.lower() == "circles":
        family_title = "Concentric Circles"

    seed_note = f"N = {n_seeds_reported} seeds"
    if n_seeds_reported <= 3:
        seed_note += " (Quick Mode — illustrative)"

    fig.update_layout(
        title=dict(
            text=f"{family_title} — {title_suffix} ({seed_note})",
            font=dict(size=14, color="#f8fafc", family="Inter, system-ui, sans-serif"),
            x=0.02,
            y=0.96,
        ),
        margin=dict(l=45, r=40, t=50, b=45),
        height=height,
        paper_bgcolor="#0f172a",
        plot_bgcolor="#1e293b",
        xaxis=dict(
            title=dict(text=x_label, font=dict(color="#cbd5e1", size=12)),
            tickfont=dict(color="#94a3b8", size=10),
            gridcolor="#334155",
            zerolinecolor="#475569",
        ),
        yaxis=dict(
            title=dict(text=y_label, font=dict(color="#cbd5e1", size=12)),
            tickfont=dict(color="#94a3b8", size=10),
            gridcolor="#334155",
            zerolinecolor="#475569",
        ),
        legend=dict(
            font=dict(color="#e2e8f0", size=11),
            bgcolor="rgba(15, 23, 42, 0.75)",
            bordercolor="#334155",
            borderwidth=1,
            x=0.02,
            y=0.08,
        ),
    )
    return fig


def create_degradation_curve_figure(
    aggregates_df: pd.DataFrame,
    family: str,
    sweep_type: str,
    use_nonnegative_loss: bool = False,
    height: int = 480,
) -> go.Figure:
    """Plot baseline degradation curves comparing K-Means and Prim's MST.

    Args:
        aggregates_df: DataFrame containing SweepAggregateRow records.
        family: Selected dataset family.
        sweep_type: Selected perturbation sweep ('noise' or 'outlier').
        use_nonnegative_loss: If True, plots nonnegative loss; if False, plots signed delta.
        height: Figure height in pixels.

    Returns:
        Plotly Figure showing degradation trajectory relative to matched baseline.
    """
    if use_nonnegative_loss:
        metric_col = "mean_degradation_inlier_ari"
        std_col = "std_degradation_inlier_ari"
        y_label = "ARI Degradation Loss [max(0, Base - Current)]"
        title_suffix = "Nonnegative ARI Degradation Loss"
    else:
        metric_col = "mean_delta_inlier_ari"
        std_col = "std_delta_inlier_ari"
        y_label = "Signed ARI Change Δ [Current - Base]"
        title_suffix = "Signed Baseline ARI Change (Δ)"

    fig = create_robustness_curve_figure(
        aggregates_df=aggregates_df,
        family=family,
        sweep_type=sweep_type,
        metric_col=metric_col,
        std_col=std_col,
        y_label=y_label,
        title_suffix=title_suffix,
        height=height,
    )

    # Add zero reference line
    fig.add_hline(
        y=0.0,
        line_dash="dot",
        line_color="#94a3b8",
        annotation_text="Matched Baseline Reference (0.0)",
        annotation_position="bottom right",
        annotation_font=dict(size=10, color="#94a3b8"),
    )
    return fig


def _normalize_benchmark_df(aggregates_df: Any) -> pd.DataFrame:
    """Normalize various benchmark summary container types to a standard DataFrame."""
    if aggregates_df is None:
        return pd.DataFrame()
    if isinstance(aggregates_df, pd.DataFrame):
        return aggregates_df.copy()
    if hasattr(aggregates_df, "to_dataframe"):
        return aggregates_df.to_dataframe()
    if isinstance(aggregates_df, (list, tuple)):
        rows = [s.to_dict() if hasattr(s, "to_dict") else dict(s) for s in aggregates_df]
        return pd.DataFrame(rows)
    return pd.DataFrame()


def create_benchmark_runtime_figure(
    aggregates_df: Any,
    height: int = 480,
) -> go.Figure:
    """Create interactive Plotly runtime comparison chart with sample std error bars.

    Supports both wide summaries (with kmeans_mean_ms, mst_mean_ms) and long aggregates.

    Args:
        aggregates_df: BenchmarkSummary, List of rows, or DataFrame.
        height: Figure height in pixels.

    Returns:
        Plotly Figure object.
    """
    fig = go.Figure()
    df = _normalize_benchmark_df(aggregates_df)

    if df.empty:
        fig.update_layout(title="No benchmark data available")
        return fig

    # Check for wide representation
    if "kmeans_mean_ms" in df.columns and "mst_mean_ms" in df.columns:
        df_sorted = df.sort_values("sample_size")
        fig.add_trace(
            go.Scatter(
                x=df_sorted["sample_size"],
                y=df_sorted["kmeans_mean_ms"],
                error_y=dict(
                    type="data",
                    array=df_sorted["kmeans_std_ms"] if "kmeans_std_ms" in df_sorted.columns else None,
                    visible=True,
                    thickness=1.5,
                    width=6,
                ),
                mode="lines+markers",
                name="Lloyd K-Means (O(I · N · k · D))",
                line=dict(color="#38bdf8", width=3),
                marker=dict(size=8, symbol="circle"),
                hovertemplate=(
                    "<b>Lloyd's K-Means</b><br>"
                    "N: %{x}<br>"
                    "Mean Runtime: %{y:.3f} ms<br>"
                    "<extra></extra>"
                ),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=df_sorted["sample_size"],
                y=df_sorted["mst_mean_ms"],
                error_y=dict(
                    type="data",
                    array=df_sorted["mst_std_ms"] if "mst_std_ms" in df_sorted.columns else None,
                    visible=True,
                    thickness=1.5,
                    width=6,
                ),
                mode="lines+markers",
                name="Prim's MST (O(N²))",
                line=dict(color="#10b981", width=3),
                marker=dict(size=8, symbol="diamond"),
                hovertemplate=(
                    "<b>Prim's MST</b><br>"
                    "N: %{x}<br>"
                    "Mean Runtime: %{y:.3f} ms<br>"
                    "<extra></extra>"
                ),
            )
        )
    elif "algorithm" in df.columns:
        km_sub = df[df["algorithm"] == "Lloyd K-Means"].sort_values("sample_size")
        if not km_sub.empty:
            fig.add_trace(
                go.Scatter(
                    x=km_sub["sample_size"],
                    y=km_sub["mean_ms"],
                    error_y=dict(
                        type="data",
                        array=km_sub["std_ms"],
                        visible=True,
                        thickness=1.5,
                        width=6,
                    ),
                    mode="lines+markers",
                    name="Lloyd K-Means (O(I · N · k · D))",
                    line=dict(color="#38bdf8", width=3),
                    marker=dict(size=8, symbol="circle"),
                    hovertemplate=(
                        "<b>Lloyd's K-Means</b><br>"
                        "N: %{x}<br>"
                        "Mean Runtime: %{y:.3f} ms<br>"
                        "<extra></extra>"
                    ),
                )
            )

        mst_sub = df[df["algorithm"] == "Prim MST"].sort_values("sample_size")
        if not mst_sub.empty:
            fig.add_trace(
                go.Scatter(
                    x=mst_sub["sample_size"],
                    y=mst_sub["mean_ms"],
                    error_y=dict(
                        type="data",
                        array=mst_sub["std_ms"],
                        visible=True,
                        thickness=1.5,
                        width=6,
                    ),
                    mode="lines+markers",
                    name="Prim's MST (O(N²))",
                    line=dict(color="#10b981", width=3),
                    marker=dict(size=8, symbol="diamond"),
                    hovertemplate=(
                        "<b>Prim's MST</b><br>"
                        "N: %{x}<br>"
                        "Mean Runtime: %{y:.3f} ms<br>"
                        "<extra></extra>"
                    ),
                )
            )

    fig.update_layout(
        title=dict(
            text="Empirical Runtime Scaling: Custom Lloyd's K-Means vs Dense Prim's MST",
            font=dict(size=15, color="#f8fafc", family="Inter, system-ui, sans-serif"),
            x=0.02,
            y=0.96,
        ),
        margin=dict(l=50, r=40, t=60, b=50),
        height=height,
        paper_bgcolor="#0f172a",
        plot_bgcolor="#1e293b",
        font=dict(color="#94a3b8"),
        xaxis=dict(
            title="Sample Size (N)",
            color="#94a3b8",
            gridcolor="#334155",
            zerolinecolor="#334155",
            tickmode="linear",
            dtick=100,
        ),
        yaxis=dict(
            title="Execution Time (ms)",
            color="#94a3b8",
            gridcolor="#334155",
            zerolinecolor="#334155",
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=12, color="#f8fafc"),
        ),
        hovermode="x unified",
    )
    return fig


def create_kmeans_explorer_figure(
    X_or_step: Any,
    step: Optional[Any] = None,
    height: int = 530,
) -> go.Figure:
    """Render interactive Plotly figure for a single K-Means algorithmic step.

    Accepts either (X, step) or just (step) if step contains attribute 'X'.
    """
    if step is None:
        actual_step = X_or_step
        actual_X = getattr(actual_step, "X", None)
        if actual_X is None:
            raise ValueError("Step object must contain attribute 'X' when X is not explicitly passed.")
    else:
        actual_X = X_or_step
        actual_step = step

    fig = go.Figure()
    n_samples = actual_X.shape[0]

    # Data points scatter
    is_init = actual_step.step_type == "init" or (
        actual_step.labels is not None and (actual_step.labels == -1).all()
    )
    if is_init:
        fig.add_trace(
            go.Scatter(
                x=actual_X[:, 0],
                y=actual_X[:, 1],
                mode="markers",
                name="Unassigned Points",
                marker=dict(size=7, color="#94a3b8", opacity=0.85),
                hovertemplate="Point %{pointNumber}<br>x: %{x:.2f}<br>y: %{y:.2f}<extra></extra>",
            )
        )
    else:
        unique_labels = np.unique(actual_step.labels)
        for label in unique_labels:
            if label == -1:
                mask = actual_step.labels == -1
                fig.add_trace(
                    go.Scatter(
                        x=actual_X[mask, 0],
                        y=actual_X[mask, 1],
                        mode="markers",
                        name="Unassigned",
                        marker=dict(size=7, color="#94a3b8", opacity=0.7),
                        hovertemplate="Unassigned<br>x: %{x:.2f}<br>y: %{y:.2f}<extra></extra>",
                    )
                )
            else:
                mask = actual_step.labels == label
                color = CLUSTER_COLORS[int(label) % len(CLUSTER_COLORS)]
                fig.add_trace(
                    go.Scatter(
                        x=actual_X[mask, 0],
                        y=actual_X[mask, 1],
                        mode="markers",
                        name=f"Cluster {label}",
                        marker=dict(size=8, color=color, opacity=0.9),
                        hovertemplate=f"Cluster {label}<br>x: %{{x:.2f}}<br>y: %{{y:.2f}}<extra></extra>",
                    )
                )

    # Centroid overlays
    if actual_step.centroids is not None and len(actual_step.centroids) > 0:
        c_x = actual_step.centroids[:, 0]
        c_y = actual_step.centroids[:, 1]
        fig.add_trace(
            go.Scatter(
                x=c_x,
                y=c_y,
                mode="markers+text",
                name="Centroids (μ)",
                text=[f"C{i}" for i in range(len(actual_step.centroids))],
                textposition="top center",
                textfont=dict(color="#fbbf24", size=12),
                marker=dict(
                    symbol="star",
                    size=18,
                    color="#f59e0b",
                    line=dict(color="#0f172a", width=2),
                ),
                hovertemplate="Centroid %{text}<br>x: %{x:.2f}<br>y: %{y:.2f}<extra></extra>",
            )
        )

    _apply_standard_layout(
        fig=fig,
        title=f"{actual_step.title} | N={n_samples}",
        x_label="Feature 1 (x₀)",
        y_label="Feature 2 (x₁)",
        height=height,
    )
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    return fig


def create_mst_explorer_figure(
    X_or_step: Any,
    step: Optional[Any] = None,
    height: int = 530,
) -> go.Figure:
    """Render interactive Plotly figure for a single Prim's MST algorithmic step.

    Accepts either (X, step) or just (step) if step contains attribute 'X'.
    """
    if step is None:
        actual_step = X_or_step
        actual_X = getattr(actual_step, "X", None)
        if actual_X is None:
            raise ValueError("Step object must contain attribute 'X' when X is not explicitly passed.")
    else:
        actual_X = X_or_step
        actual_step = step

    fig = go.Figure()
    n_samples = actual_X.shape[0]

    # Draw tree edges
    if actual_step.tree_edges:
        cut_edge_set = set(actual_step.cut_edges) if actual_step.cut_edges else set()

        for u, v, w in actual_step.tree_edges:
            is_cut = (u, v, w) in cut_edge_set or (v, u, w) in cut_edge_set
            if not is_cut:
                edge_cand = getattr(actual_step, "new_edge", None) or getattr(actual_step, "current_edge", None)
                is_current = edge_cand is not None and (u, v, w) == edge_cand
                line_color = "#f97316" if is_current else "#16a34a"
                line_width = 3.5 if is_current else 1.8
                fig.add_trace(
                    go.Scatter(
                        x=[actual_X[u, 0], actual_X[v, 0]],
                        y=[actual_X[u, 1], actual_X[v, 1]],
                        mode="lines",
                        line=dict(color=line_color, width=line_width),
                        hoverinfo="text",
                        hovertext=f"Edge ({u} - {v}) | Length: {w:.3f}",
                        showlegend=False,
                    )
                )

        for u, v, w in actual_step.cut_edges:
            fig.add_trace(
                go.Scatter(
                    x=[actual_X[u, 0], actual_X[v, 0]],
                    y=[actual_X[u, 1], actual_X[v, 1]],
                    mode="lines",
                    line=dict(color="#ef4444", width=3, dash="dash"),
                    hoverinfo="text",
                    hovertext=f"CUT Edge ({u} - {v}) | Length: {w:.3f}",
                    showlegend=False,
                )
            )

    # Points scatter
    if actual_step.step_type in ("final_clusters", "connected_components"):
        unique_labels = np.unique(actual_step.labels)
        for label in unique_labels:
            mask = actual_step.labels == label
            color = CLUSTER_COLORS[int(label) % len(CLUSTER_COLORS)]
            fig.add_trace(
                go.Scatter(
                    x=actual_X[mask, 0],
                    y=actual_X[mask, 1],
                    mode="markers",
                    name=f"Component {label}",
                    marker=dict(size=8, color=color, opacity=0.9),
                    hovertemplate=f"Component {label}<br>Point %{{pointNumber}}<br>x: %{{x:.2f}}<br>y: %{{y:.2f}}<extra></extra>",
                )
            )
    else:
        in_tree = actual_step.in_tree_mask
        unvisited = ~in_tree

        if np.any(unvisited):
            fig.add_trace(
                go.Scatter(
                    x=actual_X[unvisited, 0],
                    y=actual_X[unvisited, 1],
                    mode="markers",
                    name="Unvisited Vertices",
                    marker=dict(size=7, color="#94a3b8", opacity=0.7),
                    hovertemplate="Unvisited Vertex<br>x: %{x:.2f}<br>y: %{y:.2f}<extra></extra>",
                )
            )
        if np.any(in_tree):
            fig.add_trace(
                go.Scatter(
                    x=actual_X[in_tree, 0],
                    y=actual_X[in_tree, 1],
                    mode="markers",
                    name="Tree Vertices",
                    marker=dict(size=8, color="#10b981", opacity=0.95),
                    hovertemplate="Tree Vertex<br>x: %{x:.2f}<br>y: %{y:.2f}<extra></extra>",
                )
            )

    _apply_standard_layout(
        fig=fig,
        title=f"{actual_step.title} | N={n_samples}",
        x_label="Feature 1 (x₀)",
        y_label="Feature 2 (x₁)",
        height=height,
    )
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    return fig


def render_benchmark_png(
    aggregates_df: Any,
    width_in: float = 9.0,
    height_in: float = 5.5,
    dpi: int = 150,
) -> bytes:
    """Render publication-quality benchmark runtime chart to PNG bytes using Matplotlib."""
    import io
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(width_in, height_in), dpi=dpi)
    fig.patch.set_facecolor("#ffffff")
    ax.set_facecolor("#f8fafc")

    df = _normalize_benchmark_df(aggregates_df)

    if not df.empty:
        if "kmeans_mean_ms" in df.columns and "mst_mean_ms" in df.columns:
            df_sorted = df.sort_values("sample_size")
            ax.errorbar(
                df_sorted["sample_size"],
                df_sorted["kmeans_mean_ms"],
                yerr=df_sorted["kmeans_std_ms"] if "kmeans_std_ms" in df_sorted.columns else None,
                fmt="-o",
                color="#2563eb",
                capsize=4,
                linewidth=2,
                label="Lloyd K-Means (O(I · N · k · D))",
            )
            ax.errorbar(
                df_sorted["sample_size"],
                df_sorted["mst_mean_ms"],
                yerr=df_sorted["mst_std_ms"] if "mst_std_ms" in df_sorted.columns else None,
                fmt="-s",
                color="#16a34a",
                capsize=4,
                linewidth=2,
                label="Prim MST (O(N²))",
            )
        elif "algorithm" in df.columns:
            km_sub = df[df["algorithm"] == "Lloyd K-Means"].sort_values("sample_size")
            if not km_sub.empty:
                ax.errorbar(
                    km_sub["sample_size"],
                    km_sub["mean_ms"],
                    yerr=km_sub["std_ms"],
                    fmt="-o",
                    color="#2563eb",
                    capsize=4,
                    linewidth=2,
                    label="Lloyd K-Means (O(I · N · k · D))",
                )

            mst_sub = df[df["algorithm"] == "Prim MST"].sort_values("sample_size")
            if not mst_sub.empty:
                ax.errorbar(
                    mst_sub["sample_size"],
                    mst_sub["mean_ms"],
                    yerr=mst_sub["std_ms"],
                    fmt="-s",
                    color="#16a34a",
                    capsize=4,
                    linewidth=2,
                    label="Prim MST (O(N²))",
                )

    ax.set_title("Empirical Runtime Benchmark: K-Means vs Prim's MST", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Sample Size (N)", fontsize=11)
    ax.set_ylabel("Execution Time (ms)", fontsize=11)
    ax.grid(True, linestyle="--", alpha=0.5, color="#cbd5e1")
    ax.legend(frameon=True, facecolor="#ffffff", edgecolor="#cbd5e1")

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()


def render_clustering_png(
    X: np.ndarray,
    labels: np.ndarray,
    centroids: Optional[np.ndarray] = None,
    title: str = "Clustering Visualization",
    width_in: float = 7.0,
    height_in: float = 7.0,
    dpi: int = 150,
) -> bytes:
    """Render publication-quality 2D clustering scatter plot to PNG bytes using Matplotlib."""
    import io
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(width_in, height_in), dpi=dpi)
    fig.patch.set_facecolor("#ffffff")
    ax.set_facecolor("#f8fafc")

    unique_labels = np.unique(labels)
    mpl_colors = ["#38bdf8", "#f43f5e", "#10b981", "#f59e0b", "#a855f7", "#ec4899", "#06b6d4"]

    for lbl in unique_labels:
        mask = labels == lbl
        if lbl == -1:
            ax.scatter(X[mask, 0], X[mask, 1], c="#ef4444", marker="x", s=35, label="Outliers (-1)")
        else:
            col = mpl_colors[int(lbl) % len(mpl_colors)]
            ax.scatter(X[mask, 0], X[mask, 1], c=col, s=30, alpha=0.85, label=f"Cluster {lbl}")

    if centroids is not None and len(centroids) > 0:
        ax.scatter(
            centroids[:, 0],
            centroids[:, 1],
            c="#f59e0b",
            marker="*",
            s=180,
            edgecolors="#0f172a",
            linewidths=1.5,
            label="Centroids",
            zorder=10,
        )

    ax.set_aspect("equal", adjustable="box")
    ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    ax.set_xlabel("Feature 1 (x₀)", fontsize=10)
    ax.set_ylabel("Feature 2 (x₁)", fontsize=10)
    ax.grid(True, linestyle="--", alpha=0.5, color="#cbd5e1")
    ax.legend(frameon=True, facecolor="#ffffff", edgecolor="#cbd5e1", fontsize=9)

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()
