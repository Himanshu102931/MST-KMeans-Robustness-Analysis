"""
clustering_lab.data.noise
=========================
Scientific noise and outlier contamination pipeline for clustering robustness benchmarks.

Provides independently controllable:
1. Zero-mean Gaussian coordinate jitter applied to inlier observations.
2. Uniform random outlier injection sampled across a padded bounding region.

Deterministic Independence:
    Uses NumPy SeedSequence to spawn decoupled PRNG streams for noise and outliers,
    guaranteeing that adjusting the outlier rate never alters the noise coordinates,
    and vice-versa.
"""

from __future__ import annotations

from typing import Optional, Tuple
import numpy as np


def compute_bounding_box(
    X: np.ndarray,
    padding_fraction: float = 0.15,
    min_padding: float = 0.5,
) -> Tuple[float, float, float, float]:
    """Compute 2D bounding box with proportional padding.

    Args:
        X: Feature array of shape (N, 2).
        padding_fraction: Fraction of range to pad on each boundary (default 0.15).
        min_padding: Absolute minimum padding distance when range is small.

    Returns:
        Tuple of (x_min, x_max, y_min, y_max) representing padded bounds.
    """
    if X.shape[0] == 0:
        return (-1.0, 1.0, -1.0, 1.0)

    min_x, max_x = float(np.min(X[:, 0])), float(np.max(X[:, 0]))
    min_y, max_y = float(np.min(X[:, 1])), float(np.max(X[:, 1]))

    range_x = max_x - min_x
    range_y = max_y - min_y

    pad_x = max(range_x * padding_fraction, min_padding)
    pad_y = max(range_y * padding_fraction, min_padding)

    return (min_x - pad_x, max_x + pad_x, min_y - pad_y, max_y + pad_y)


def apply_gaussian_noise(
    X_inliers: np.ndarray,
    noise_sigma: float,
    rng: np.random.Generator,
) -> np.ndarray:
    """Add independently sampled zero-mean Gaussian jitter to inlier coordinates.

    Mathematical Formulation:
        For each inlier x_i in R^2:
            x_i^{noisy} = x_i + delta_i,   delta_i ~ N(0, sigma^2 * I_2)

    Scale Convention:
        'noise_sigma' represents the absolute coordinate standard deviation.
        When noise_sigma == 0.0, the input array is returned unmodified as a fresh copy.

    Args:
        X_inliers: Feature array of shape (N_inliers, 2).
        noise_sigma: Absolute standard deviation of Gaussian perturbation (>= 0.0).
        rng: Seeded NumPy random Generator.

    Returns:
        Perturbed coordinates of shape (N_inliers, 2).
    """
    if noise_sigma < 0.0:
        raise ValueError(f"Noise standard deviation 'noise_sigma' must be >= 0.0, got {noise_sigma}.")

    X_copy = np.asarray(X_inliers, dtype=np.float64).copy()
    if noise_sigma == 0.0 or X_copy.shape[0] == 0:
        return X_copy

    jitter = rng.normal(loc=0.0, scale=noise_sigma, size=X_copy.shape)
    return X_copy + jitter


def generate_uniform_outliers(
    X_inliers: np.ndarray,
    outlier_rate: float,
    rng: np.random.Generator,
    padding_fraction: float = 0.15,
) -> Tuple[np.ndarray, np.ndarray]:
    """Generate uniform random outlier coordinates across the padded bounding box.

    Outlier Rate Convention:
        The outlier count is defined strictly as a fraction of the inlier sample count:
            n_outliers = int(round(n_inliers * outlier_rate))
        Standard supported levels include 0.0 (0%), 0.05 (5%), 0.10 (10%), and 0.20 (20%),
        as well as arbitrary validated user rates in [0.0, 1.0).

    Label Convention:
        Outliers are assigned ground-truth label -1.

    Args:
        X_inliers: Base inlier observations of shape (N_inliers, 2).
        outlier_rate: Contamination fraction in [0.0, 1.0).
        rng: Seeded NumPy random Generator.
        padding_fraction: Relative padding on the bounding box (default 0.15).

    Returns:
        Tuple of (X_outliers, labels_outliers) where X_outliers has shape (N_outliers, 2)
        and labels_outliers has shape (N_outliers,) with all elements equal to -1.
    """
    if outlier_rate < 0.0 or outlier_rate >= 1.0:
        raise ValueError(f"Outlier rate must be in the interval [0.0, 1.0), got {outlier_rate}.")

    n_inliers = X_inliers.shape[0]
    n_outliers = int(round(n_inliers * outlier_rate))

    if n_outliers == 0:
        return (
            np.empty((0, 2), dtype=np.float64),
            np.empty((0,), dtype=np.int32),
        )

    x_min, x_max, y_min, y_max = compute_bounding_box(X_inliers, padding_fraction=padding_fraction)

    outliers_x = rng.uniform(low=x_min, high=x_max, size=n_outliers)
    outliers_y = rng.uniform(low=y_min, high=y_max, size=n_outliers)

    X_outliers = np.column_stack([outliers_x, outliers_y])
    labels_outliers = np.full(n_outliers, -1, dtype=np.int32)

    return X_outliers, labels_outliers


def contaminate_dataset(
    X_clean: np.ndarray,
    labels_clean: Optional[np.ndarray],
    noise_sigma: float = 0.0,
    outlier_rate: float = 0.0,
    seed: Optional[int] = 42,
    padding_fraction: float = 0.15,
) -> Tuple[np.ndarray, Optional[np.ndarray], np.ndarray, int, int]:
    """Apply decoupled Gaussian noise and uniform outliers to a clean dataset.

    Decoupling Mechanism:
        When a master seed is provided, NumPy's SeedSequence spawns two independent,
        non-overlapping PRNG streams:
        1. stream_noise: dedicated exclusively to Gaussian jitter.
        2. stream_outliers: dedicated exclusively to uniform outlier placement.
        This guarantees that varying the outlier rate leaves the inlier noise jitter
        completely identical, enabling scientific paired comparisons.

    Args:
        X_clean: Base clean coordinates, shape (N_inliers, 2).
        labels_clean: Base clean integer labels, shape (N_inliers,), or None.
        noise_sigma: Gaussian noise standard deviation (>= 0.0).
        outlier_rate: Outlier fraction in [0.0, 1.0).
        seed: Master random seed.
        padding_fraction: Bounding box padding fraction.

    Returns:
        Tuple of (X_combined, labels_combined, inlier_mask, n_inliers, n_outliers).
    """
    n_inliers = X_clean.shape[0]

    # Spawn decoupled PRNG streams
    if seed is not None:
        sq = np.random.SeedSequence(seed)
        spawned = sq.spawn(2)
        rng_noise = np.random.default_rng(spawned[0])
        rng_outliers = np.random.default_rng(spawned[1])
    else:
        rng_noise = np.random.default_rng()
        rng_outliers = np.random.default_rng()

    # 1. Apply Gaussian jitter to inlier coordinates
    X_noisy = apply_gaussian_noise(X_clean, noise_sigma=noise_sigma, rng=rng_noise)

    # 2. Generate uniform outliers using bounding box derived from clean inliers
    X_outliers, labels_outliers = generate_uniform_outliers(
        X_clean,
        outlier_rate=outlier_rate,
        rng=rng_outliers,
        padding_fraction=padding_fraction,
    )
    n_outliers = X_outliers.shape[0]

    # 3. Stack combined observation matrix
    if n_outliers > 0:
        X_combined = np.vstack([X_noisy, X_outliers])
        inlier_mask = np.concatenate([
            np.ones(n_inliers, dtype=bool),
            np.zeros(n_outliers, dtype=bool),
        ])
        if labels_clean is not None:
            labels_combined = np.concatenate([labels_clean, labels_outliers])
        else:
            labels_combined = None
    else:
        X_combined = X_noisy
        inlier_mask = np.ones(n_inliers, dtype=bool)
        labels_combined = labels_clean.copy() if labels_clean is not None else None

    return X_combined, labels_combined, inlier_mask, n_inliers, n_outliers
