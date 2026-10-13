"""
clustering_lab.evaluation.metrics
=================================
Scientifically sound quantitative evaluation metrics for clustering benchmarks:
1. Adjusted Rand Index (ARI):
   - Inlier ARI: evaluated strictly on true inlier points.
   - Optional Full ARI: evaluated on all points including outliers (with documented caveats).
2. Silhouette Coefficient:
   - Evaluates intra-cluster tightness vs nearest-neighbor cluster separation.
   - Handled with explicit guardrails for degenerate cluster counts (k < 2 or k >= N).
3. Runtime Profiling:
   - High-resolution wall-clock execution time (labeled as single-execution measurement).

Academic Context:
    Course: Pattern Matching Lab (BCS-DS-777)
    Project: MST vs K-Means Robustness Analysis
    Authors: Himanshu Gupta ([REDACTED_STUDENT_IDENTIFIER]) & Parth Yadav ([REDACTED_STUDENT_IDENTIFIER])
    Institution: MRIIRS, School of Engineering & Technology (2026–2027)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional
import numpy as np
from sklearn.metrics import adjusted_rand_score, silhouette_score


@dataclass(frozen=True)
class ClusteringMetrics:
    """Standardized quantitative metrics container for clustering validation.

    Attributes:
        n_clusters_predicted: Number of unique non-empty clusters formed.
        runtime_ms: Wall-clock execution time in milliseconds (single execution measurement).
        inlier_ari: Adjusted Rand Index evaluated strictly on ground-truth inliers (None if unlabeled).
        full_ari: Adjusted Rand Index evaluated across all observations including outliers (None if unlabeled).
        silhouette: Intrinsic silhouette score in [-1.0, 1.0] (None if k < 2 or k >= N).
        metadata: Diagnostic annotations and caveats explaining metric interpretation.
    """

    n_clusters_predicted: int
    runtime_ms: float
    inlier_ari: Optional[float] = None
    full_ari: Optional[float] = None
    silhouette: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


def compute_inlier_ari(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    inlier_mask: Optional[np.ndarray] = None,
) -> float:
    """Compute Adjusted Rand Index strictly on verified inlier observations.

    Rationale:
        Standard synthetic generators inject uniform random outliers with label -1.
        Neither Lloyd's K-Means nor single-linkage MST has a designated outlier reject
        class in this phase. Measuring ARI exclusively on known inliers quantifies
        how robustly the internal manifold / cluster topology was preserved despite
        the surrounding contamination.

    Args:
        y_true: Ground-truth class labels, shape (N,).
        y_pred: Predicted cluster assignments, shape (N,).
        inlier_mask: Boolean mask of shape (N,) indicating inliers. If None, all points are used.

    Returns:
        Adjusted Rand Index as a float in [-0.5, 1.0].
    """
    y_true_arr = np.asarray(y_true, dtype=np.int32)
    y_pred_arr = np.asarray(y_pred, dtype=np.int32)

    if y_true_arr.shape != y_pred_arr.shape:
        raise ValueError(
            f"Shape mismatch: y_true shape {y_true_arr.shape} != y_pred shape {y_pred_arr.shape}."
        )

    if inlier_mask is not None:
        mask_arr = np.asarray(inlier_mask, dtype=bool)
        if mask_arr.shape != y_true_arr.shape:
            raise ValueError(
                f"Shape mismatch: inlier_mask shape {mask_arr.shape} != y_true shape {y_true_arr.shape}."
            )
        y_true_eval = y_true_arr[mask_arr]
        y_pred_eval = y_pred_arr[mask_arr]
    else:
        # Exclude points with ground-truth label -1 (outliers) if present
        valid_mask = y_true_arr != -1
        y_true_eval = y_true_arr[valid_mask]
        y_pred_eval = y_pred_arr[valid_mask]

    if len(y_true_eval) < 2:
        return 0.0

    return float(adjusted_rand_score(y_true_eval, y_pred_eval))


def compute_full_ari(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Compute Adjusted Rand Index over all observations including injected outliers.

    Note on Interpretation:
        Outliers are encoded as label -1 in y_true, effectively forming an artificial
        extra cluster. Because standard K-Means and MST assign every outlier to one of
        their k clusters, full ARI naturally incurs a penalty proportional to the outlier
        rate.

    Args:
        y_true: Ground-truth class labels, shape (N,).
        y_pred: Predicted cluster assignments, shape (N,).

    Returns:
        Adjusted Rand Index as a float in [-0.5, 1.0].
    """
    y_true_arr = np.asarray(y_true, dtype=np.int32)
    y_pred_arr = np.asarray(y_pred, dtype=np.int32)

    if y_true_arr.shape != y_pred_arr.shape:
        raise ValueError(
            f"Shape mismatch: y_true shape {y_true_arr.shape} != y_pred shape {y_pred_arr.shape}."
        )

    if len(y_true_arr) < 2:
        return 0.0

    return float(adjusted_rand_score(y_true_arr, y_pred_arr))


def compute_silhouette_safe(
    X: np.ndarray,
    labels: np.ndarray,
) -> Optional[float]:
    """Compute the Mean Silhouette Coefficient with safety guards against degenerate configurations.

    Theoretical Conditions:
        Silhouette Coefficient requires:
        1. Number of unique clusters k must be in [2, N - 1].
        2. At least two distinct clusters must contain >= 1 observation.
        3. Feature array X must be 2D numerical matrix.

    Geometric Bias Warning:
        Silhouette score measures Euclidean distance ratios assuming convex, spherical
        clusters. It intrinsically favors K-Means style globular clusters and strongly
        penalizes non-convex manifolds (e.g., concentric rings or interleaving moons)
        even when perfectly partitioned by MST. It is an auxiliary internal metric,
        never a replacement for ground-truth ARI.

    Args:
        X: Feature matrix of shape (N, D).
        labels: Predicted cluster labels of shape (N,).

    Returns:
        Float silhouette score in [-1.0, 1.0], or None if computation is mathematically invalid.
    """
    X_arr = np.asarray(X, dtype=np.float64)
    labels_arr = np.asarray(labels, dtype=np.int32)

    n_samples = X_arr.shape[0]
    unique_labels = np.unique(labels_arr)
    n_unique = len(unique_labels)

    if n_unique < 2 or n_unique >= n_samples or n_samples < 3:
        return None

    try:
        score = float(silhouette_score(X_arr, labels_arr, metric="euclidean"))
        return score
    except Exception:
        return None


def evaluate_clustering(
    y_pred: np.ndarray,
    y_true: Optional[np.ndarray] = None,
    inlier_mask: Optional[np.ndarray] = None,
    X: Optional[np.ndarray] = None,
    runtime_sec: float = 0.0,
) -> ClusteringMetrics:
    """Evaluate comprehensive clustering metrics for a single algorithm run.

    Args:
        y_pred: 1D array of predicted cluster IDs, shape (N,).
        y_true: Optional 1D array of ground-truth class labels, shape (N,).
        inlier_mask: Optional boolean 1D array where True denotes inlier, shape (N,).
        X: Optional feature coordinates of shape (N, 2) for silhouette evaluation.
        runtime_sec: Elapsed execution time in seconds.

    Returns:
        Immutable ClusteringMetrics instance.
    """
    y_pred_arr = np.asarray(y_pred, dtype=np.int32)
    n_unique_pred = int(len(np.unique(y_pred_arr)))
    runtime_ms = float(runtime_sec * 1000.0)

    inlier_ari_val: Optional[float] = None
    full_ari_val: Optional[float] = None
    silhouette_val: Optional[float] = None
    meta: Dict[str, Any] = {
        "has_ground_truth": y_true is not None,
        "runtime_nature": "single execution measurement (illustrative, not multi-trial benchmark)",
    }

    if y_true is not None:
        y_true_arr = np.asarray(y_true, dtype=np.int32)
        inlier_ari_val = compute_inlier_ari(y_true_arr, y_pred_arr, inlier_mask)
        full_ari_val = compute_full_ari(y_true_arr, y_pred_arr)
        meta["inlier_ari_interpretation"] = "Evaluated exclusively on known inliers."
        meta["full_ari_interpretation"] = (
            "Evaluated across all points; outliers (label -1) penalize both algorithms."
        )

    if X is not None:
        silhouette_val = compute_silhouette_safe(X, y_pred_arr)
        if silhouette_val is not None:
            meta["silhouette_bias_warning"] = (
                "Silhouette assumes spherical geometry; non-convex shapes may receive low scores despite valid recovery."
            )
        else:
            meta["silhouette_status"] = "N/A — requires 2 <= k <= N-1 clusters."

    return ClusteringMetrics(
        n_clusters_predicted=n_unique_pred,
        runtime_ms=runtime_ms,
        inlier_ari=inlier_ari_val,
        full_ari=full_ari_val,
        silhouette=silhouette_val,
        metadata=meta,
    )
