"""
clustering_lab.data.config
==========================
Versioned JSON experiment configuration schema for reproducible clustering benchmarks.

Key Features:
    - Strict schema validation with explicit schema_version check (1.0.0).
    - Bi-directional JSON serialization and deserialization with round-trip stability.
    - Comprehensive hyperparameter range and type enforcement.
    - Factory helper to instantiate Dataset objects directly from ExperimentConfig.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import json
from typing import Any, Dict, Optional
import numpy as np

from clustering_lab.data.dataset import Dataset
from clustering_lab.data.synthetic import (
    generate_blobs,
    generate_circles,
    generate_moons,
)

SCHEMA_VERSION: str = "1.0.0"
MAX_CONFIG_JSON_BYTES: int = 100 * 1024  # 100 KB


@dataclass
class ExperimentConfig:
    """Versioned specification of a synthetic clustering experiment dataset.

    Attributes:
        dataset_family: Family identifier ('blobs', 'moons', 'circles').
        n_samples: Inlier observation count (10 <= n_samples <= 5000).
        n_clusters: Cluster count k (must be 2 for moons and circles).
        seed: Master random seed (>= 0).
        noise: Gaussian jitter standard deviation (>= 0.0).
        outlier_rate: Contamination fraction in [0.0, 0.5].
        dataset_params: Additional family-specific parameters (e.g. cluster_std, factor).
        schema_version: Semantic schema version (default '1.0.0').
    """

    dataset_family: str
    n_samples: int = 300
    n_clusters: int = 3
    seed: int = 42
    noise: float = 0.0
    outlier_rate: float = 0.0
    dataset_params: Dict[str, Any] = field(default_factory=dict)
    schema_version: str = SCHEMA_VERSION

    def __post_init__(self) -> None:
        """Validate all configuration attributes strictly."""
        # Schema version check
        if not isinstance(self.schema_version, str):
            raise TypeError(f"'schema_version' must be str, got {type(self.schema_version).__name__}.")
        major_version = self.schema_version.split(".")[0]
        if major_version != SCHEMA_VERSION.split(".")[0]:
            raise ValueError(
                f"Unsupported schema_version '{self.schema_version}'. "
                f"This environment requires major version {SCHEMA_VERSION.split('.')[0]}.x.x."
            )

        # Family check
        family = str(self.dataset_family).strip().lower()
        if family not in {"blobs", "moons", "circles"}:
            raise ValueError(f"Unknown dataset_family '{self.dataset_family}'. Supported: 'blobs', 'moons', 'circles'.")
        self.dataset_family = family

        # Sample count check
        if not isinstance(self.n_samples, (int, np.integer)) or isinstance(self.n_samples, bool):
            raise TypeError(f"'n_samples' must be an integer, got {type(self.n_samples).__name__}.")
        self.n_samples = int(self.n_samples)
        if self.n_samples < 10 or self.n_samples > 5000:
            raise ValueError(f"'n_samples' must be in [10, 5000], got {self.n_samples}.")

        # Cluster count check
        if not isinstance(self.n_clusters, (int, np.integer)) or isinstance(self.n_clusters, bool):
            raise TypeError(f"'n_clusters' must be an integer, got {type(self.n_clusters).__name__}.")
        self.n_clusters = int(self.n_clusters)
        if self.dataset_family in {"moons", "circles"} and self.n_clusters != 2:
            raise ValueError(f"Dataset family '{self.dataset_family}' strictly requires n_clusters=2, got {self.n_clusters}.")
        if self.n_clusters < 1 or self.n_clusters > 20:
            raise ValueError(f"'n_clusters' must be in [1, 20], got {self.n_clusters}.")

        # Seed check
        if not isinstance(self.seed, (int, np.integer)) or isinstance(self.seed, bool):
            raise TypeError(f"'seed' must be an integer, got {type(self.seed).__name__}.")
        self.seed = int(self.seed)
        if self.seed < 0:
            raise ValueError(f"'seed' must be non-negative, got {self.seed}.")

        # Noise check
        if not isinstance(self.noise, (int, float, np.floating)):
            raise TypeError(f"'noise' must be a float, got {type(self.noise).__name__}.")
        self.noise = float(self.noise)
        if self.noise < 0.0 or not np.isfinite(self.noise):
            raise ValueError(f"'noise' must be a finite non-negative real number, got {self.noise}.")

        # Outlier rate check
        if not isinstance(self.outlier_rate, (int, float, np.floating)):
            raise TypeError(f"'outlier_rate' must be a float, got {type(self.outlier_rate).__name__}.")
        self.outlier_rate = float(self.outlier_rate)
        if self.outlier_rate < 0.0 or self.outlier_rate > 0.5 or not np.isfinite(self.outlier_rate):
            raise ValueError(f"'outlier_rate' must be in [0.0, 0.5], got {self.outlier_rate}.")

        # Dataset params check
        if not isinstance(self.dataset_params, dict):
            raise TypeError(f"'dataset_params' must be a dictionary, got {type(self.dataset_params).__name__}.")

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to a standard dictionary."""
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        """Serialize configuration to a JSON string."""
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ExperimentConfig:
        """Construct and validate ExperimentConfig from a dictionary."""
        if not isinstance(data, dict):
            raise TypeError(f"Config data must be a dictionary, got {type(data).__name__}.")

        required_keys = {"dataset_family"}
        missing = required_keys - set(data.keys())
        if missing:
            raise ValueError(f"Missing required configuration key(s): {missing}.")

        return cls(
            dataset_family=data["dataset_family"],
            n_samples=data.get("n_samples", 300),
            n_clusters=data.get("n_clusters", 3 if data["dataset_family"] == "blobs" else 2),
            seed=data.get("seed", 42),
            noise=data.get("noise", 0.0),
            outlier_rate=data.get("outlier_rate", 0.0),
            dataset_params=data.get("dataset_params", {}),
            schema_version=data.get("schema_version", SCHEMA_VERSION),
        )

    @classmethod
    def from_json(cls, json_str: str) -> ExperimentConfig:
        """Parse, deserialize, and validate ExperimentConfig from a JSON string."""
        if not isinstance(json_str, str):
            raise TypeError(f"Input must be a JSON string, got {type(json_str).__name__}.")
        if len(json_str.strip()) == 0:
            raise ValueError("Configuration JSON string is empty.")
        if len(json_str.encode("utf-8")) > MAX_CONFIG_JSON_BYTES:
            raise ValueError(f"Configuration JSON exceeds maximum size limit of {MAX_CONFIG_JSON_BYTES} bytes.")

        try:
            parsed = json.loads(json_str)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Malformed configuration JSON: {exc}") from exc

        return cls.from_dict(parsed)


def create_dataset_from_config(config: ExperimentConfig) -> Dataset:
    """Generate a reproducible Dataset from an ExperimentConfig."""
    family = config.dataset_family
    params = config.dataset_params

    if family == "blobs":
        return generate_blobs(
            n_samples=config.n_samples,
            n_clusters=config.n_clusters,
            cluster_std=float(params.get("cluster_std", 0.4)),
            radius=float(params.get("radius", 3.5)),
            noise=config.noise,
            outlier_rate=config.outlier_rate,
            seed=config.seed,
        )
    elif family == "moons":
        return generate_moons(
            n_samples=config.n_samples,
            noise=config.noise,
            outlier_rate=config.outlier_rate,
            seed=config.seed,
        )
    elif family == "circles":
        return generate_circles(
            n_samples=config.n_samples,
            factor=float(params.get("factor", 0.45)),
            noise=config.noise,
            outlier_rate=config.outlier_rate,
            seed=config.seed,
        )
    else:
        raise ValueError(f"Cannot generate dataset for unsupported family '{family}'.")
