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

from typing import List, Optional
import numpy as np
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
