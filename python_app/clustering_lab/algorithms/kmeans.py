"""
clustering_lab.algorithms.kmeans
================================
Independent, from-scratch implementation of Lloyd's K-Means clustering algorithm
with K-Means++ initialization and deterministic tie-breaking.

Academic Context:
    Course: Pattern Matching Lab (BCS-DS-777)
    Project: MST vs K-Means Robustness Analysis
    Authors: Himanshu Gupta & Parth Yadav (Equal Academic Contribution)
    Institution: MRIIRS, School of Engineering & Technology (2026–2027)

Design & Implementation Principles:
    - Pure Python and NumPy implementation (no runtime dependency on scikit-learn).
    - Finite numerical input validation (strictly rejects NaN, Inf, non-2D arrays).
    - Deterministic K-Means++ initialization with configurable NumPy PRNG seed.
    - Deterministic tie-breaking: distance ties break towards the lowest cluster index.
    - Explicit empty-cluster handling: reseeds empty centroids to the observation
      with maximum squared distance to its assigned centroid.
    - Preserves input immutability: copies feature arrays before processing.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple
import numpy as np


@dataclass(frozen=True)
class KMeansResult:
    """Immutable result object produced by K-Means clustering.

    Attributes:
        labels: 1D array of shape (N,) containing integer cluster assignments in [0, k-1].
        cluster_centers: 2D array of shape (k, D) with computed centroid coordinates.
        inertia: Sum of squared Euclidean distances of samples to their closest centroid (WCSS).
        n_iter: Total number of Lloyd iterations executed until convergence or max_iter.
        converged: Boolean indicating whether centroid shifts fell below tolerance.
        k: Number of clusters requested.
    """

    labels: np.ndarray
    cluster_centers: np.ndarray
    inertia: float
    n_iter: int
    converged: bool
    k: int

    @property
    def centroids(self) -> np.ndarray:
        """Alias for cluster_centers."""
        return self.cluster_centers


def _validate_input_data(X: np.ndarray, k: int, max_iter: int, tol: float) -> Tuple[np.ndarray, int]:
    """Validate numerical data and hyperparameters.

    Raises:
        TypeError: If input types are invalid.
        ValueError: If array dimensions, values, or hyperparameters violate constraints.
    """
    if not isinstance(k, (int, np.integer)):
        raise TypeError(f"Number of clusters 'k' must be an integer, got {type(k).__name__}.")
    k = int(k)

    if not isinstance(max_iter, (int, np.integer)):
        raise TypeError(f"'max_iter' must be an integer, got {type(max_iter).__name__}.")
    max_iter = int(max_iter)

    if not isinstance(tol, (int, float, np.floating)):
        raise TypeError(f"'tol' must be a real number, got {type(tol).__name__}.")
    tol = float(tol)

    if max_iter < 1:
        raise ValueError(f"'max_iter' must be at least 1, got {max_iter}.")
    if tol < 0.0:
        raise ValueError(f"'tol' must be non-negative, got {tol}.")

    try:
        X_arr = np.asarray(X, dtype=np.float64)
    except (ValueError, TypeError) as exc:
        raise ValueError(f"Input X could not be converted to float64 array: {exc}") from exc

    if X_arr.ndim != 2:
        raise ValueError(f"Input X must be a 2D array of shape (N, D), got {X_arr.ndim}D shape {X_arr.shape}.")

    n_samples, n_features = X_arr.shape
    if n_samples < 1:
        raise ValueError(f"Input array X must contain at least 1 sample, got shape {X_arr.shape}.")
    if n_features < 1:
        raise ValueError(f"Input array X must contain at least 1 feature dimension, got shape {X_arr.shape}.")

    if not np.isfinite(X_arr).all():
        raise ValueError("Input array X contains non-finite values (NaN or Inf). Only finite numerical values are permitted.")

    if k < 1:
        raise ValueError(f"Number of clusters 'k' must be at least 1, got {k}.")
    if k > n_samples:
        raise ValueError(f"Number of clusters 'k' ({k}) cannot exceed number of samples N ({n_samples}).")

    return X_arr.copy(), k


def _init_kmeans_plus_plus(X: np.ndarray, k: int, rng: np.random.Generator) -> np.ndarray:
    """Initialize centroids using the K-Means++ algorithm.

    Theoretical Guarantee:
        Chooses initial cluster centers such that expected clustering cost (inertia)
        is within an O(log k) competitive ratio of optimal clustering. Note: O(log k)
        refers to the cost approximation ratio, not the computational time complexity.

    Args:
        X: Feature array of shape (N, D).
        k: Number of centroids to initialize.
        rng: Seeded NumPy random Generator.

    Returns:
        Initial centroids array of shape (k, D).
    """
    n_samples, n_features = X.shape
    centers = np.empty((k, n_features), dtype=np.float64)

    # 1. Choose first center uniformly at random from X
    first_idx = int(rng.integers(0, n_samples))
    centers[0] = X[first_idx]

    if k == 1:
        return centers

    # Distance squared to closest center chosen so far
    min_dist_sq = np.sum((X - centers[0]) ** 2, axis=1)

    # 2. Iteratively choose remaining k - 1 centers
    for c in range(1, k):
        total_dist_sq = np.sum(min_dist_sq)

        if total_dist_sq <= 1e-12:
            # Degenerate case: all remaining points coincide with existing centers.
            # Choose uniformly at random from remaining samples to complete initialization.
            fallback_idx = int(rng.integers(0, n_samples))
            centers[c] = X[fallback_idx]
        else:
            probs = min_dist_sq / total_dist_sq
            # Avoid minor precision drift causing sum(probs) != 1.0
            probs = probs / np.sum(probs)
            selected_idx = int(rng.choice(n_samples, p=probs))
            centers[c] = X[selected_idx]

        # Update shortest squared distance to closest center
        new_dist_sq = np.sum((X - centers[c]) ** 2, axis=1)
        min_dist_sq = np.minimum(min_dist_sq, new_dist_sq)

    return centers


def kmeans(
    X: np.ndarray,
    k: int,
    max_iter: int = 300,
    tol: float = 1e-4,
    seed: Optional[int] = 42,
) -> KMeansResult:
    """Fit Lloyd's K-Means clustering algorithm on dataset X.

    Mathematical Formulation:
        Minimizes the Within-Cluster Sum of Squares (Inertia):
            J = sum_{i=1}^N || X_i - mu_{c(i)} ||^2
        where mu_c is the centroid of cluster c, and c(i) is the cluster assigned to sample i.

    Tie-breaking:
        When a sample is equidistant to multiple centroids, it is deterministically
        assigned to the centroid with the lowest index (argmin convention).

    Degeneracy & Empty Clusters:
        If a cluster becomes empty during an iteration, the algorithm reseeds that
        centroid at the sample currently exhibiting the largest squared distance
        to its assigned centroid.
        Note: If a dataset contains fewer than k distinct coordinate values (U < k),
        it is mathematically impossible to partition the samples into k non-empty
        separated clusters. In this degenerate regime, redundant centroids will coincide
        with existing sample coordinates.

    Args:
        X: Array-like of shape (N, D) containing numerical observations.
        k: Number of clusters (1 <= k <= N).
        max_iter: Maximum number of Lloyd iterations.
        tol: Convergence tolerance for centroid coordinate shifts.
        seed: Random seed for reproducible K-Means++ initialization.

    Returns:
        KMeansResult containing labels, centroids, inertia, iterations, and convergence flag.
    """
    X_clean, k_val = _validate_input_data(X, k, max_iter, tol)
    n_samples, n_features = X_clean.shape

    # Fast path: single cluster
    if k_val == 1:
        center = np.mean(X_clean, axis=0, keepdims=True)
        inertia = float(np.sum((X_clean - center) ** 2))
        return KMeansResult(
            labels=np.zeros(n_samples, dtype=np.int32),
            cluster_centers=center,
            inertia=inertia,
            n_iter=1,
            converged=True,
            k=1,
        )

    # Fast path: k equals n_samples (each sample is its own centroid)
    if k_val == n_samples:
        return KMeansResult(
            labels=np.arange(n_samples, dtype=np.int32),
            cluster_centers=X_clean.copy(),
            inertia=0.0,
            n_iter=1,
            converged=True,
            k=k_val,
        )

    rng = np.random.default_rng(seed)
    centers = _init_kmeans_plus_plus(X_clean, k_val, rng)

    converged = False
    iteration = 0
    labels = np.zeros(n_samples, dtype=np.int32)

    while iteration < max_iter and not converged:
        iteration += 1

        # 1. Assignment step: squared Euclidean distance matrix of shape (N, k)
        # Using expanded dimensions: (N, 1, D) - (1, k, D) -> (N, k, D)
        diff = X_clean[:, np.newaxis, :] - centers[np.newaxis, :, :]
        dist_sq_matrix = np.sum(diff ** 2, axis=2)

        # Deterministic assignment: argmin selects lowest cluster index in case of ties
        new_labels = np.argmin(dist_sq_matrix, axis=1).astype(np.int32)

        # 2. Update step: recompute centroid positions as arithmetic means
        new_centers = np.empty_like(centers)
        reseeded_indices: set[int] = set()
        force_continue = False

        for c in range(k_val):
            mask = new_labels == c
            cluster_size = int(np.sum(mask))

            if cluster_size > 0:
                new_centers[c] = np.mean(X_clean[mask], axis=0)
            else:
                # Handle empty cluster: reseed at sample with maximum distance to its assigned centroid
                assigned_dists = dist_sq_matrix[np.arange(n_samples), new_labels]

                # Find candidate index not already reseeded in this iteration
                sorted_candidate_indices = np.argsort(-assigned_dists)
                farthest_idx = -1
                for idx in sorted_candidate_indices:
                    if int(idx) not in reseeded_indices:
                        farthest_idx = int(idx)
                        break

                if farthest_idx == -1:
                    farthest_idx = c % n_samples

                reseeded_indices.add(farthest_idx)
                new_centers[c] = X_clean[farthest_idx].copy()
                force_continue = True

        # Check convergence via maximum centroid Euclidean displacement
        shift_vector = np.linalg.norm(new_centers - centers, axis=1)
        max_shift = float(np.max(shift_vector))

        centers = new_centers
        labels = new_labels

        if not force_continue and max_shift < tol:
            converged = True

    # Final pass to compute exact inertia and final labels
    final_diff = X_clean[:, np.newaxis, :] - centers[np.newaxis, :, :]
    final_dist_sq = np.sum(final_diff ** 2, axis=2)
    final_labels = np.argmin(final_dist_sq, axis=1).astype(np.int32)
    final_inertia = float(np.sum(final_dist_sq[np.arange(n_samples), final_labels]))

    return KMeansResult(
        labels=final_labels,
        cluster_centers=centers,
        inertia=final_inertia,
        n_iter=iteration,
        converged=converged,
        k=k_val,
    )


class KMeans:
    """Object-oriented estimator interface for Lloyd's K-Means clustering algorithm.

    Conforms to standard estimator patterns (fit, predict, fit_predict).
    """

    def __init__(
        self,
        n_clusters: int = 2,
        max_iter: int = 300,
        tol: float = 1e-4,
        seed: Optional[int] = 42,
    ) -> None:
        self.n_clusters = n_clusters
        self.max_iter = max_iter
        self.tol = tol
        self.seed = seed

        # Fitted attributes
        self.labels_: Optional[np.ndarray] = None
        self.cluster_centers_: Optional[np.ndarray] = None
        self.inertia_: Optional[float] = None
        self.n_iter_: Optional[int] = None
        self.converged_: Optional[bool] = None

    def fit(self, X: np.ndarray) -> "KMeans":
        """Fit the K-Means clustering model to feature array X."""
        result = kmeans(
            X=X,
            k=self.n_clusters,
            max_iter=self.max_iter,
            tol=self.tol,
            seed=self.seed,
        )
        self.labels_ = result.labels
        self.cluster_centers_ = result.cluster_centers
        self.inertia_ = result.inertia
        self.n_iter_ = result.n_iter
        self.converged_ = result.converged
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict the closest cluster center for each sample in X."""
        if self.cluster_centers_ is None:
            raise RuntimeError("Estimator is not fitted yet. Call 'fit' before 'predict'.")

        X_clean, _ = _validate_input_data(X, k=1, max_iter=self.max_iter, tol=self.tol)
        n_features = self.cluster_centers_.shape[1]
        if X_clean.shape[1] != n_features:
            raise ValueError(
                f"Feature dimension mismatch: model was fitted on {n_features} "
                f"features, but input X has {X_clean.shape[1]} features."
            )

        diff = X_clean[:, np.newaxis, :] - self.cluster_centers_[np.newaxis, :, :]
        dist_sq = np.sum(diff ** 2, axis=2)
        return np.argmin(dist_sq, axis=1).astype(np.int32)

    def fit_predict(self, X: np.ndarray) -> np.ndarray:
        """Fit model and return cluster assignments."""
        return self.fit(X).labels_
