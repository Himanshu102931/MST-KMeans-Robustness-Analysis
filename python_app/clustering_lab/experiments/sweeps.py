"""
clustering_lab.experiments.sweeps
=================================
Controlled experiment design and configuration schema for clustering robustness sweeps.

Academic Context:
    Course: Pattern Matching Lab (BCS-DS-777)
    Project: MST vs K-Means Robustness Analysis
    Authors: Himanshu Gupta ([REDACTED_STUDENT_IDENTIFIER]) & Parth Yadav ([REDACTED_STUDENT_IDENTIFIER])
    Instructor: Mr. Aman Kumar, Assistant Professor
    Institution: MRIIRS, School of Engineering & Technology (2026–2027)

Research Design:
    Investigates how graph-theoretic Prim's MST and centroid-based Lloyd's K-Means
    perform under controlled perturbations across three geometric manifolds:
    1. Gaussian Blobs (convex globular baseline, default k=3)
    2. Two Moons (interlocking non-convex crescents, default k=2)
    3. Concentric Circles (nested non-convex rings, default k=2)

    Two separate controlled univariate sweeps around well-defined baselines:
    - Noise sweep: vary Gaussian jitter sigma in {0.00, 0.05, 0.10, 0.20} at 0% outliers.
    - Outlier sweep: vary uniform outlier rate in {0.00, 0.05, 0.10, 0.20} at baseline sigma=0.05.

    (Note: These are two separate univariate sweeps, NOT a complete factorial grid).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Sequence


class SweepType(str, Enum):
    """Supported univariate perturbation sweep types."""

    NOISE = "noise"
    OUTLIER = "outlier"


class ExperimentMode(str, Enum):
    """Execution preset modes for robustness analysis."""

    QUICK = "quick"
    EXTENDED = "extended"
    CUSTOM = "custom"


# Deterministic seed lists
DEFAULT_QUICK_SEEDS: List[int] = [11, 22, 33]
DEFAULT_EXTENDED_SEEDS: List[int] = [11, 22, 33, 44, 55, 66, 77, 88, 99, 101]

# Default sweep levels
DEFAULT_NOISE_LEVELS: List[float] = [0.00, 0.05, 0.10, 0.20]
DEFAULT_OUTLIER_RATES: List[float] = [0.00, 0.05, 0.10, 0.20]
DEFAULT_OUTLIER_BASE_NOISE: float = 0.05

# Default dataset geometry constants
DEFAULT_FAMILIES: List[str] = ["blobs", "moons", "circles"]
DEFAULT_N_INLIERS: int = 300

# Computational safety bounds
MIN_INLIERS: int = 20
MAX_INLIERS: int = 500
MAX_OUTLIER_RATE: float = 0.30
MAX_SEEDS: int = 20
MAX_TOTAL_TRIALS: int = 500  # 500 trials = 1000 clustering executions


@dataclass
class SweepConfig:
    """Configuration container for scientific robustness benchmark sweeps.

    Attributes:
        dataset_families: List of dataset families in {'blobs', 'moons', 'circles'}.
        n_inliers: Base number of clean manifold inliers (default 300).
        seeds: List of deterministic PRNG seeds to repeat for statistical averaging.
        sweep_types: List of sweep types to run ('noise', 'outlier', or both).
        noise_levels: Gaussian jitter standard deviation levels for the noise sweep.
        outlier_rates: Uniform outlier fraction levels for the outlier sweep.
        outlier_sweep_base_noise: Fixed baseline Gaussian jitter during the outlier sweep (default 0.05).
        blobs_k: Cluster count for Gaussian Blobs (default 3).
        blobs_cluster_std: Cluster dispersion standard deviation for Gaussian Blobs (default 0.4).
        blobs_radius: Radial distance of blob centers from origin (default 3.5).
        moons_k: Cluster count for Two Moons (fixed 2).
        circles_k: Cluster count for Concentric Circles (fixed 2).
        circles_factor: Scale factor between inner and outer ring radius (default 0.45).
        mode: Preset execution mode identifier ('quick', 'extended', 'custom').
    """

    dataset_families: List[str] = field(default_factory=lambda: list(DEFAULT_FAMILIES))
    n_inliers: int = DEFAULT_N_INLIERS
    seeds: List[int] = field(default_factory=lambda: list(DEFAULT_QUICK_SEEDS))
    sweep_types: List[str] = field(default_factory=lambda: [SweepType.NOISE.value, SweepType.OUTLIER.value])
    noise_levels: List[float] = field(default_factory=lambda: list(DEFAULT_NOISE_LEVELS))
    outlier_rates: List[float] = field(default_factory=lambda: list(DEFAULT_OUTLIER_RATES))
    outlier_sweep_base_noise: float = DEFAULT_OUTLIER_BASE_NOISE
    blobs_k: int = 3
    blobs_cluster_std: float = 0.4
    blobs_radius: float = 3.5
    moons_k: int = 2
    circles_k: int = 2
    circles_factor: float = 0.45
    mode: str = ExperimentMode.QUICK.value

    def validate(self) -> None:
        """Validate configuration parameters against scientific and computational constraints.

        Raises:
            ValueError: If any parameter violates bounds or limits.
        """
        # Validate sample counts
        if not (MIN_INLIERS <= self.n_inliers <= MAX_INLIERS):
            raise ValueError(
                f"n_inliers must be in [{MIN_INLIERS}, {MAX_INLIERS}], got {self.n_inliers}."
            )

        # Validate dataset families
        if not self.dataset_families:
            raise ValueError("At least one dataset family must be selected.")
        valid_families = {"blobs", "moons", "circles"}
        for fam in self.dataset_families:
            if fam.lower() not in valid_families:
                raise ValueError(
                    f"Unsupported dataset family '{fam}'. Must be one of {valid_families}."
                )

        # Validate seeds
        if not self.seeds:
            raise ValueError("At least one random seed must be specified.")
        if len(self.seeds) > MAX_SEEDS:
            raise ValueError(
                f"Maximum allowed seeds is {MAX_SEEDS}, got {len(self.seeds)}."
            )
        for s in self.seeds:
            if not isinstance(s, int) or s < 0:
                raise ValueError(f"Seeds must be non-negative integers, got {s}.")

        # Validate sweep types
        if not self.sweep_types:
            raise ValueError("At least one sweep type must be selected ('noise' or 'outlier').")
        valid_sweeps = {SweepType.NOISE.value, SweepType.OUTLIER.value}
        for st_name in self.sweep_types:
            if st_name.lower() not in valid_sweeps:
                raise ValueError(
                    f"Unsupported sweep type '{st_name}'. Must be in {valid_sweeps}."
                )

        # Validate noise levels
        if SweepType.NOISE.value in self.sweep_types:
            if not self.noise_levels:
                raise ValueError("noise_levels cannot be empty when noise sweep is selected.")
            for n in self.noise_levels:
                if n < 0.0:
                    raise ValueError(f"Noise sigma must be >= 0.0, got {n}.")

        # Validate outlier rates
        if SweepType.OUTLIER.value in self.sweep_types:
            if not self.outlier_rates:
                raise ValueError("outlier_rates cannot be empty when outlier sweep is selected.")
            for r in self.outlier_rates:
                if not (0.0 <= r <= MAX_OUTLIER_RATE):
                    raise ValueError(
                        f"Outlier rate must be in [0.0, {MAX_OUTLIER_RATE}], got {r}."
                    )
            if self.outlier_sweep_base_noise < 0.0:
                raise ValueError(
                    f"outlier_sweep_base_noise must be >= 0.0, got {self.outlier_sweep_base_noise}."
                )

        # Validate geometric hyperparameters
        if self.blobs_k < 1:
            raise ValueError(f"blobs_k must be >= 1, got {self.blobs_k}.")
        if self.blobs_cluster_std <= 0.0:
            raise ValueError(f"blobs_cluster_std must be > 0.0, got {self.blobs_cluster_std}.")
        if self.blobs_radius <= 0.0:
            raise ValueError(f"blobs_radius must be > 0.0, got {self.blobs_radius}.")
        if not (0.0 < self.circles_factor < 1.0):
            raise ValueError(f"circles_factor must be in (0.0, 1.0), got {self.circles_factor}.")

        # Computational safety check on total trial count
        total_trials = self.total_expected_trials()
        if total_trials > MAX_TOTAL_TRIALS:
            raise ValueError(
                f"Total expected trials ({total_trials}) exceeds computational safety limit of "
                f"{MAX_TOTAL_TRIALS} ({MAX_TOTAL_TRIALS * 2} algorithm executions). "
                f"Reduce the number of seeds, families, or sweep points."
            )

    def total_expected_trials(self) -> int:
        """Calculate total number of dataset trial runs across all selected sweeps and seeds."""
        n_families = len(self.dataset_families)
        n_seeds = len(self.seeds)
        trials = 0

        if SweepType.NOISE.value in self.sweep_types:
            trials += n_families * len(self.noise_levels) * n_seeds

        if SweepType.OUTLIER.value in self.sweep_types:
            trials += n_families * len(self.outlier_rates) * n_seeds

        return trials

    def total_expected_executions(self) -> int:
        """Calculate total number of clustering executions (2 per trial: K-Means and MST)."""
        return self.total_expected_trials() * 2

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary format."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> SweepConfig:
        """Construct a validated SweepConfig from dictionary data."""
        # Filter keys matching dataclass fields
        valid_keys = {
            "dataset_families",
            "n_inliers",
            "seeds",
            "sweep_types",
            "noise_levels",
            "outlier_rates",
            "outlier_sweep_base_noise",
            "blobs_k",
            "blobs_cluster_std",
            "blobs_radius",
            "moons_k",
            "circles_k",
            "circles_factor",
            "mode",
        }
        filtered = {k: v for k, v in data.items() if k in valid_keys}
        cfg = cls(**filtered)
        cfg.validate()
        return cfg
