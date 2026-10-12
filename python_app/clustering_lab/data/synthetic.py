"""
clustering_lab.data.synthetic
=============================
Reproducible synthetic 2D dataset generators for clustering robustness benchmarks:
1. Gaussian Blobs (isotropic Gaussian clusters with configurable separation)
2. Two Moons (interlocking non-convex crescent manifolds)
3. Concentric Circles (nested non-convex rings with separation factor)

All generators return standardized, immutable Dataset objects with decoupled
Gaussian noise and uniform outlier injection.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import numpy as np
from sklearn.datasets import make_blobs, make_circles, make_moons

from clustering_lab.data.dataset import Dataset, create_dataset
from clustering_lab.data.noise import contaminate_dataset


def generate_blobs(
    n_samples: int = 300,
    n_clusters: int = 3,
    cluster_std: float = 0.4,
    radius: float = 3.5,
    noise: float = 0.0,
    outlier_rate: float = 0.0,
    seed: Optional[int] = 42,
) -> Dataset:
    """Generate Gaussian Blobs dataset with balanced cluster sizes.

    Geometry:
        Cluster centroids are positioned symmetrically around a circle of given radius:
            center_i = (radius * cos(2*pi*i / k), radius * sin(2*pi*i / k))
        Observations within each cluster are drawn from an isotropic Gaussian with
        standard deviation cluster_std.

    Decoupled Perturbation:
        - Inlier points are generated from the base Gaussian distributions.
        - Additional independent Gaussian jitter of standard deviation 'noise' can be applied.
        - Uniform outliers are injected across the padded bounding box at fraction 'outlier_rate'.

    Args:
        n_samples: Number of inlier observations (>= 3).
        n_clusters: Number of distinct clusters k (>= 1, default 3).
        cluster_std: Standard deviation of each cluster's Gaussian kernel.
        radius: Distance of cluster centers from the origin.
        noise: Additional Gaussian jitter sigma added to inliers (>= 0.0).
        outlier_rate: Outlier fraction in [0.0, 1.0).
        seed: Random seed for deterministic reproducibility.

    Returns:
        Dataset object containing feature matrix X, ground-truth labels, and metadata.
    """
    if n_samples < n_clusters:
        raise ValueError(f"Sample count n_samples ({n_samples}) must be >= n_clusters ({n_clusters}).")
    if n_clusters < 1:
        raise ValueError(f"n_clusters must be >= 1, got {n_clusters}.")
    if cluster_std <= 0.0:
        raise ValueError(f"cluster_std must be positive, got {cluster_std}.")

    # Generate symmetric cluster centers around origin
    angles = np.linspace(0, 2 * np.pi, n_clusters, endpoint=False)
    centers = np.column_stack([radius * np.cos(angles), radius * np.sin(angles)])

    # Generate base clean inliers
    X_clean, labels_clean = make_blobs(
        n_samples=n_samples,
        n_features=2,
        centers=centers,
        cluster_std=cluster_std,
        shuffle=False,
        random_state=seed,
    )
    labels_clean = labels_clean.astype(np.int32)

    # Apply decoupled noise and outliers
    X_comb, labels_comb, inlier_mask, n_in, n_out = contaminate_dataset(
        X_clean=X_clean,
        labels_clean=labels_clean,
        noise_sigma=noise,
        outlier_rate=outlier_rate,
        seed=seed,
    )

    params: Dict[str, Any] = {
        "n_samples": n_samples,
        "n_clusters": n_clusters,
        "cluster_std": cluster_std,
        "radius": radius,
        "noise": noise,
        "outlier_rate": outlier_rate,
    }

    metadata: Dict[str, Any] = {
        "centers": centers.tolist(),
        "cluster_counts": {int(c): int(np.sum(labels_clean == c)) for c in range(n_clusters)},
    }

    return create_dataset(
        X=X_comb,
        labels=labels_comb,
        inlier_mask=inlier_mask,
        dataset_family="blobs",
        seed=seed,
        params=params,
        clean_X=X_clean,
        metadata=metadata,
    )


def generate_moons(
    n_samples: int = 300,
    noise: float = 0.08,
    outlier_rate: float = 0.0,
    seed: Optional[int] = 42,
) -> Dataset:
    """Generate Two Moons dataset: two interlocking crescent manifolds (k=2).

    Geometry:
        Constructs two interleaving half-circles of radius 1.0.
        Upper moon: centered at origin (y >= 0).
        Lower moon: translated to (1.0, -0.5).

    Decoupled Perturbation:
        - Base inliers are generated on the clean crescent curves.
        - Gaussian noise with standard deviation 'noise' is applied via decoupled stream.
        - Uniform outliers are injected across the bounding box at fraction 'outlier_rate'.

    Args:
        n_samples: Number of inlier observations (>= 2).
        noise: Standard deviation of Gaussian jitter (>= 0.0).
        outlier_rate: Outlier fraction in [0.0, 1.0).
        seed: Random seed for deterministic reproducibility.

    Returns:
        Dataset object with k=2 ground-truth labels in {0, 1} and outliers as -1.
    """
    if n_samples < 2:
        raise ValueError(f"Sample count n_samples ({n_samples}) must be >= 2.")

    # Generate clean base geometry with zero internal jitter
    X_clean, labels_clean = make_moons(
        n_samples=n_samples,
        shuffle=False,
        noise=None,  # Clean curve
        random_state=seed,
    )
    labels_clean = labels_clean.astype(np.int32)

    # Apply decoupled noise and outliers
    X_comb, labels_comb, inlier_mask, n_in, n_out = contaminate_dataset(
        X_clean=X_clean,
        labels_clean=labels_clean,
        noise_sigma=noise,
        outlier_rate=outlier_rate,
        seed=seed,
    )

    params: Dict[str, Any] = {
        "n_samples": n_samples,
        "n_clusters": 2,
        "noise": noise,
        "outlier_rate": outlier_rate,
    }

    metadata: Dict[str, Any] = {
        "cluster_counts": {0: int(np.sum(labels_clean == 0)), 1: int(np.sum(labels_clean == 1))},
    }

    return create_dataset(
        X=X_comb,
        labels=labels_comb,
        inlier_mask=inlier_mask,
        dataset_family="moons",
        seed=seed,
        params=params,
        clean_X=X_clean,
        metadata=metadata,
    )


def generate_circles(
    n_samples: int = 300,
    factor: float = 0.45,
    noise: float = 0.05,
    outlier_rate: float = 0.0,
    seed: Optional[int] = 42,
) -> Dataset:
    """Generate Concentric Circles dataset: two nested circular rings (k=2).

    Geometry:
        Outer ring: circle of radius 1.0 centered at origin (cluster 0).
        Inner ring: circle of radius 'factor' centered at origin (cluster 1).

    Decoupled Perturbation:
        - Base inliers are sampled uniformly along both circle perimeters.
        - Gaussian noise with standard deviation 'noise' is applied via decoupled stream.
        - Uniform outliers are injected across the bounding box at fraction 'outlier_rate'.

    Args:
        n_samples: Number of inlier observations (>= 2).
        factor: Scale factor between inner and outer ring radius (0.0 < factor < 1.0).
        noise: Standard deviation of Gaussian jitter (>= 0.0).
        outlier_rate: Outlier fraction in [0.0, 1.0).
        seed: Random seed for deterministic reproducibility.

    Returns:
        Dataset object with k=2 ground-truth labels in {0, 1} and outliers as -1.
    """
    if n_samples < 2:
        raise ValueError(f"Sample count n_samples ({n_samples}) must be >= 2.")
    if not (0.0 < factor < 1.0):
        raise ValueError(f"Circle separation factor must be in (0.0, 1.0), got {factor}.")

    # Generate clean base rings with zero internal jitter
    X_clean, labels_clean = make_circles(
        n_samples=n_samples,
        shuffle=False,
        factor=factor,
        noise=None,  # Clean curve
        random_state=seed,
    )
    labels_clean = labels_clean.astype(np.int32)

    # Apply decoupled noise and outliers
    X_comb, labels_comb, inlier_mask, n_in, n_out = contaminate_dataset(
        X_clean=X_clean,
        labels_clean=labels_clean,
        noise_sigma=noise,
        outlier_rate=outlier_rate,
        seed=seed,
    )

    params: Dict[str, Any] = {
        "n_samples": n_samples,
        "n_clusters": 2,
        "factor": factor,
        "noise": noise,
        "outlier_rate": outlier_rate,
    }

    metadata: Dict[str, Any] = {
        "factor": factor,
        "cluster_counts": {0: int(np.sum(labels_clean == 0)), 1: int(np.sum(labels_clean == 1))},
    }

    return create_dataset(
        X=X_comb,
        labels=labels_comb,
        inlier_mask=inlier_mask,
        dataset_family="circles",
        seed=seed,
        params=params,
        clean_X=X_clean,
        metadata=metadata,
    )


def generate_synthetic_dataset(
    family: str,
    n_samples: int = 300,
    seed: Optional[int] = 42,
    noise: float = 0.0,
    outlier_rate: float = 0.0,
    **kwargs: Any,
) -> Dataset:
    """Unified dispatcher to synthesize benchmark clustering datasets.

    Args:
        family: One of 'blobs', 'moons', 'circles'.
        n_samples: Inlier sample count.
        seed: Random seed.
        noise: Gaussian noise standard deviation.
        outlier_rate: Contamination fraction.
        **kwargs: Family-specific hyperparameters (e.g. n_clusters, factor, cluster_std).

    Returns:
        Validated Dataset object.
    """
    family_lower = str(family).strip().lower()
    if family_lower == "blobs":
        return generate_blobs(
            n_samples=n_samples,
            noise=noise,
            outlier_rate=outlier_rate,
            seed=seed,
            **kwargs,
        )
    elif family_lower == "moons":
        return generate_moons(
            n_samples=n_samples,
            noise=noise,
            outlier_rate=outlier_rate,
            seed=seed,
            **kwargs,
        )
    elif family_lower == "circles":
        return generate_circles(
            n_samples=n_samples,
            noise=noise,
            outlier_rate=outlier_rate,
            seed=seed,
            **kwargs,
        )
    else:
        raise ValueError(
            f"Unsupported dataset family '{family}'. Must be one of: 'blobs', 'moons', 'circles'."
        )
