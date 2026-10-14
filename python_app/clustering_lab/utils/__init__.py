"""
clustering_lab.utils
====================
Scientific helper functions and common utilities:
- Canonical sample standard deviation with Bessel's correction
- Random seed initialization for experiment reproducibility
- Pairwise Euclidean distance computations
- Input validation and schema assertions
"""

from clustering_lab.utils.math_helpers import compute_sample_std

__all__ = ["compute_sample_std"]
