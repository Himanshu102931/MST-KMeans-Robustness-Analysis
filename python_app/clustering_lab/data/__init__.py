"""
clustering_lab.data
===================
Reproducible synthetic dataset generators, noise/outlier contamination pipelines,
CSV loader, and versioned configuration schemas.
"""

from clustering_lab.data.config import (
    SCHEMA_VERSION,
    ExperimentConfig,
    create_dataset_from_config,
)
from clustering_lab.data.csv_loader import load_dataset_from_csv
from clustering_lab.data.dataset import Dataset, create_dataset
from clustering_lab.data.noise import (
    apply_gaussian_noise,
    contaminate_dataset,
    generate_uniform_outliers,
)
from clustering_lab.data.synthetic import (
    generate_blobs,
    generate_circles,
    generate_moons,
    generate_synthetic_dataset,
)

__all__ = [
    "Dataset",
    "create_dataset",
    "generate_blobs",
    "generate_moons",
    "generate_circles",
    "generate_synthetic_dataset",
    "apply_gaussian_noise",
    "generate_uniform_outliers",
    "contaminate_dataset",
    "load_dataset_from_csv",
    "ExperimentConfig",
    "create_dataset_from_config",
    "SCHEMA_VERSION",
]
