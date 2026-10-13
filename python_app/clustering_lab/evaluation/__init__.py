"""
clustering_lab.evaluation
=========================
Quantitative evaluation metrics and benchmarking:
- Adjusted Rand Index (ARI) — Ground truth clustering recovery (inlier & full)
- Silhouette Coefficient — Intra-cluster compactness vs inter-cluster separation
- Execution time profiling
"""

from clustering_lab.evaluation.metrics import (
    ClusteringMetrics,
    compute_full_ari,
    compute_inlier_ari,
    compute_silhouette_safe,
    evaluate_clustering,
)

__all__ = [
    "ClusteringMetrics",
    "compute_inlier_ari",
    "compute_full_ari",
    "compute_silhouette_safe",
    "evaluate_clustering",
]
