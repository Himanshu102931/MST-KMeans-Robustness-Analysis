"""
clustering_lab.visualization
============================
Interactive and publication-quality scientific visualization:
- Interactive Plotly 2D scatter plots
- Ground truth and outlier views
- K-Means Voronoi partitions and centroid overlays
- MST graph topology tree edge overlays (retained vs cut edges)
"""

from clustering_lab.visualization.figures import (
    CLUSTER_COLORS,
    create_degradation_curve_figure,
    create_ground_truth_figure,
    create_kmeans_figure,
    create_mst_figure,
    create_robustness_curve_figure,
)

__all__ = [
    "CLUSTER_COLORS",
    "create_ground_truth_figure",
    "create_kmeans_figure",
    "create_mst_figure",
    "create_robustness_curve_figure",
    "create_degradation_curve_figure",
]
