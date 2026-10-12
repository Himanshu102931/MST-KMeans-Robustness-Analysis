"""
clustering_lab.data.dataset
===========================
Standard scientific data container for 2D clustering benchmarks,
supporting ground-truth labels, outlier masks, and validation metadata.

Academic Context:
    Course: Pattern Matching Lab (BCS-DS-777)
    Project: MST vs K-Means Robustness Analysis
    Authors: Himanshu Gupta ([REDACTED_STUDENT_IDENTIFIER]) & Parth Yadav ([REDACTED_STUDENT_IDENTIFIER])
    Institution: MRIIRS, School of Engineering & Technology (2026–2027)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Tuple
import numpy as np

# Safe upper bound on observation count to prevent unbounded O(N^2) memory consumption
MAX_SAFE_SAMPLES: int = 10000


@dataclass(frozen=True)
class Dataset:
    """Immutable standardized container for 2D clustering benchmark datasets.

    Attributes:
        X: Feature matrix of shape (N, 2) containing finite numerical coordinates.
        labels: 1D array of shape (N,) containing integer ground-truth cluster labels
            (0, 1, ..., k-1) for inliers, and -1 for outliers; or None if unlabeled.
        inlier_mask: Boolean 1D array of shape (N,) where True denotes an inlier and
            False denotes an injected or identified outlier.
        dataset_family: Origin identifier ('blobs', 'moons', 'circles', 'csv').
        seed: Random seed used to synthesize the dataset, or None if external.
        params: Dictionary recording generation and perturbation hyperparameters.
        n_inliers: Count of clean or noisy inlier observations.
        n_outliers: Count of uniform outlier observations.
        n_samples: Total number of observations (n_inliers + n_outliers == N).
        clean_X: Optional coordinates of inliers before noise addition, shape (n_inliers, 2).
        metadata: Additional diagnostic info (column names, class balance, etc.).
    """

    X: np.ndarray
    labels: Optional[np.ndarray]
    inlier_mask: np.ndarray
    dataset_family: str
    seed: Optional[int]
    params: Dict[str, Any]
    n_inliers: int
    n_outliers: int
    n_samples: int
    clean_X: Optional[np.ndarray] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate structural and numerical invariants."""
        # Validate X
        if not isinstance(self.X, np.ndarray):
            raise TypeError(f"Feature matrix 'X' must be a numpy.ndarray, got {type(self.X).__name__}.")
        if self.X.ndim != 2 or self.X.shape[1] != 2:
            raise ValueError(f"Feature matrix 'X' must have shape (N, 2), got {self.X.shape}.")
        if not np.issubdtype(self.X.dtype, np.floating) and not np.issubdtype(self.X.dtype, np.integer):
            raise TypeError(f"Feature matrix 'X' must contain numerical data, got dtype {self.X.dtype}.")
        if not np.isfinite(self.X).all():
            raise ValueError("Feature matrix 'X' contains non-finite values (NaN or Inf).")

        n = self.X.shape[0]
        if n < 1:
            raise ValueError("Feature matrix 'X' cannot be empty (must have N >= 1).")
        if n > MAX_SAFE_SAMPLES:
            raise ValueError(
                f"Sample count {n} exceeds safe dashboard limit of {MAX_SAFE_SAMPLES}. "
                "Large datasets require excessive O(N^2) pairwise distance memory."
            )

        # Validate inlier_mask
        if not isinstance(self.inlier_mask, np.ndarray) or self.inlier_mask.dtype != bool:
            raise TypeError("Attribute 'inlier_mask' must be a boolean numpy.ndarray.")
        if self.inlier_mask.shape != (n,):
            raise ValueError(f"'inlier_mask' shape {self.inlier_mask.shape} does not match X rows {n}.")

        # Validate counts
        actual_inliers = int(np.sum(self.inlier_mask))
        actual_outliers = int(np.sum(~self.inlier_mask))
        if actual_inliers != self.n_inliers:
            raise ValueError(f"Declared n_inliers ({self.n_inliers}) != mask sum ({actual_inliers}).")
        if actual_outliers != self.n_outliers:
            raise ValueError(f"Declared n_outliers ({self.n_outliers}) != mask sum ({actual_outliers}).")
        if self.n_samples != n or (self.n_inliers + self.n_outliers != n):
            raise ValueError(f"Inconsistent sample counts: n_samples={self.n_samples}, sum={self.n_inliers + self.n_outliers}, N={n}.")

        # Validate labels if present
        if self.labels is not None:
            if not isinstance(self.labels, np.ndarray):
                raise TypeError(f"'labels' must be a numpy.ndarray, got {type(self.labels).__name__}.")
            if self.labels.shape != (n,):
                raise ValueError(f"'labels' shape {self.labels.shape} does not match X rows {n}.")
            if not np.issubdtype(self.labels.dtype, np.integer):
                raise TypeError(f"'labels' must have integer dtype, got {self.labels.dtype}.")
            # Outliers must have label -1
            if actual_outliers > 0:
                outlier_labels = self.labels[~self.inlier_mask]
                if not np.all(outlier_labels == -1):
                    raise ValueError("All outlier observations (inlier_mask=False) must have ground-truth label -1.")

        # Validate clean_X if present
        if self.clean_X is not None:
            if not isinstance(self.clean_X, np.ndarray) or self.clean_X.ndim != 2 or self.clean_X.shape[1] != 2:
                raise ValueError("Attribute 'clean_X' must be a 2D numpy array with 2 columns.")
            if self.clean_X.shape[0] != self.n_inliers:
                raise ValueError(f"'clean_X' row count ({self.clean_X.shape[0]}) must equal n_inliers ({self.n_inliers}).")


def create_dataset(
    X: np.ndarray,
    labels: Optional[np.ndarray],
    inlier_mask: np.ndarray,
    dataset_family: str,
    seed: Optional[int] = None,
    params: Optional[Dict[str, Any]] = None,
    clean_X: Optional[np.ndarray] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dataset:
    """Factory helper to construct a validated, immutable Dataset instance."""
    X_arr = np.asarray(X, dtype=np.float64).copy()
    mask_arr = np.asarray(inlier_mask, dtype=bool).copy()
    labels_arr = np.asarray(labels, dtype=np.int32).copy() if labels is not None else None
    clean_X_arr = np.asarray(clean_X, dtype=np.float64).copy() if clean_X is not None else None

    n_samples = X_arr.shape[0]
    n_inliers = int(np.sum(mask_arr))
    n_outliers = int(np.sum(~mask_arr))

    return Dataset(
        X=X_arr,
        labels=labels_arr,
        inlier_mask=mask_arr,
        dataset_family=str(dataset_family),
        seed=int(seed) if seed is not None else None,
        params=dict(params) if params is not None else {},
        n_inliers=n_inliers,
        n_outliers=n_outliers,
        n_samples=n_samples,
        clean_X=clean_X_arr,
        metadata=dict(metadata) if metadata is not None else {},
    )
