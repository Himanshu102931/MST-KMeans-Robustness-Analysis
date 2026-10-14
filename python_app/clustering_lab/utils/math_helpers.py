"""
clustering_lab.utils.math_helpers
=================================
Canonical mathematical and statistical helper utilities for clustering experiments.

Academic Context:
    Course: Pattern Matching Lab (BCS-DS-777)
    Project: MST vs K-Means Robustness Analysis
    Authors: Himanshu Gupta & Parth Yadav (Equal Academic Contribution)
    Instructor: Mr. Aman Kumar, Assistant Professor
    Institution: MRIIRS, School of Engineering & Technology (2026–2027)

Mathematical Formulation:
    Sample Standard Deviation with Bessel's Correction (ddof=1):
        Given a sample X = [x_1, x_2, ..., x_n] of n observations:
            x_bar = (1 / n) * sum_{i=1}^n x_i
            s = sqrt( (1 / (n - ddof)) * sum_{i=1}^n (x_i - x_bar)^2 )

    Boundary Conditions:
        - If n <= ddof (e.g. n <= 1 when ddof=1, or empty collection n=0):
          Degrees of freedom are non-positive (n - ddof <= 0).
          The sample standard deviation is defined as 0.0 to prevent division by zero.
        - For constant observations (all x_i equal):
          Variance is 0.0, yielding standard deviation 0.0.
"""

from __future__ import annotations

from typing import Sequence, Union
import numpy as np


def compute_sample_std(
    values: Union[Sequence[float], np.ndarray],
    ddof: int = 1,
) -> float:
    """Calculate sample standard deviation with Bessel's correction (ddof=1).

    Applies Bessel's correction (dividing by N - ddof) to compute an unbiased
    estimate of sample variance before taking the square root.

    Args:
        values: Sequence or 1D array of numerical observations.
        ddof: Delta degrees of freedom for Bessel's correction (default: 1).

    Returns:
        Sample standard deviation as a Python float.
        Returns 0.0 if len(values) <= ddof or if input is empty.

    Raises:
        TypeError: If ddof is not an integer.
        ValueError: If ddof is negative.
    """
    if not isinstance(ddof, (int, np.integer)):
        raise TypeError(f"ddof must be an integer, got {type(ddof).__name__}.")
    ddof_val = int(ddof)
    if ddof_val < 0:
        raise ValueError(f"ddof must be non-negative, got {ddof_val}.")

    n = len(values)
    if n <= ddof_val:
        return 0.0

    arr = np.asarray(values, dtype=np.float64)
    if arr.size == 0:
        return 0.0
    if arr.ndim != 1:
        arr = arr.ravel()
        if arr.size <= ddof_val:
            return 0.0

    return float(np.std(arr, ddof=ddof_val))
