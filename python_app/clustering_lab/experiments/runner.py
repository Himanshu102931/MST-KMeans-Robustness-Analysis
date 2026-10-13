"""
clustering_lab.experiments.runner
=================================
Scientific experiment runner for paired clustering robustness benchmarking.

Academic Context:
    Course: Pattern Matching Lab (BCS-DS-777)
    Project: MST vs K-Means Robustness Analysis
    Authors: Himanshu Gupta ([REDACTED_STUDENT_IDENTIFIER]) & Parth Yadav ([REDACTED_STUDENT_IDENTIFIER])
    Instructor: Mr. Aman Kumar, Assistant Professor
    Institution: MRIIRS, School of Engineering & Technology (2026–2027)

Core Scientific Guarantees:
    1. Identical Paired Input Guarantee:
       Both Lloyd's K-Means and dense Prim's MST execute on the IDENTICAL feature
       array X for every single trial.
    2. Zero Delegation:
       Clustering is executed strictly by the from-scratch pure NumPy implementations
       (`kmeans` and `mst_clustering`), never by sklearn or scipy black-box clusterers.
    3. Matched Baselines:
       Relative degradation is evaluated exclusively against the matched baseline
       sharing the exact same dataset family, geometry, and random seed.
    4. Metric Invariants:
       Signed change (delta) is preserved without clamping, while nonnegative degradation
       loss is explicitly defined and recorded in separate fields.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import time
from typing import Any, Callable, Dict, List, Optional, Tuple
import numpy as np

from clustering_lab.algorithms.kmeans import kmeans
from clustering_lab.algorithms.mst import mst_clustering
from clustering_lab.data.dataset import Dataset
from clustering_lab.data.synthetic import generate_synthetic_dataset
from clustering_lab.evaluation.metrics import compute_full_ari, compute_inlier_ari
from clustering_lab.experiments.sweeps import SweepConfig, SweepType


@dataclass
class TrialResult:
    """Record of a single clustering algorithm execution on a benchmark dataset.

    Attributes:
        dataset_family: Dataset topology ('blobs', 'moons', 'circles').
        sweep_type: Type of perturbation sweep ('noise' or 'outlier').
        parameter_name: Name of varied hyperparameter ('noise_sigma' or 'outlier_rate').
        parameter_value: Numeric value of the varied parameter.
        seed: Random seed used to generate the dataset and contamination streams.
        n_inliers: Base manifold inlier observation count.
        n_outliers: Injected uniform outlier observation count.
        n_total: Total observation count (n_inliers + n_outliers).
        k: Number of clusters partitioned.
        algorithm: Algorithm identifier ('Lloyd K-Means' or 'Prim MST').
        inlier_ari: Adjusted Rand Index evaluated strictly on verified inliers.
        full_ari: Adjusted Rand Index evaluated across all points including outliers (-1).
        runtime_ms: Measured wall-clock execution time in milliseconds.
        baseline_inlier_ari: Matched baseline Inlier ARI (same family, seed, algorithm at level 0.0).
        delta_inlier_ari: Signed change relative to matched baseline (inlier_ari - baseline).
        degradation_inlier_ari: Nonnegative loss relative to matched baseline (max(0.0, baseline - inlier_ari)).
    """

    dataset_family: str
    sweep_type: str
    parameter_name: str
    parameter_value: float
    seed: int
    n_inliers: int
    n_outliers: int
    n_total: int
    k: int
    algorithm: str
    inlier_ari: float
    full_ari: float
    runtime_ms: float
    baseline_inlier_ari: Optional[float] = None
    delta_inlier_ari: Optional[float] = None
    degradation_inlier_ari: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to a plain dictionary representation."""
        return asdict(self)


def _get_family_hyperparams(config: SweepConfig, family: str) -> Dict[str, Any]:
    """Retrieve family-specific geometry arguments from SweepConfig."""
    fam = family.lower()
    if fam == "blobs":
        return {
            "n_clusters": config.blobs_k,
            "cluster_std": config.blobs_cluster_std,
            "radius": config.blobs_radius,
        }
    elif fam == "moons":
        return {}
    elif fam == "circles":
        return {
            "factor": config.circles_factor,
        }
    return {}


def _get_cluster_count(config: SweepConfig, family: str) -> int:
    """Return target cluster count k for the given dataset family."""
    fam = family.lower()
    if fam == "blobs":
        return config.blobs_k
    elif fam == "moons":
        return config.moons_k
    elif fam == "circles":
        return config.circles_k
    return 2


def _run_dual_clustering_on_dataset(
    dataset: Dataset,
    k: int,
    seed: int,
) -> Tuple[float, float, float, float, float, float]:
    """Execute both Lloyd's K-Means and Prim's MST on identical feature array X.

    Returns:
        Tuple of:
        (km_inlier_ari, km_full_ari, km_time_ms,
         mst_inlier_ari, mst_full_ari, mst_time_ms)
    """
    X = dataset.X
    y_true = dataset.labels
    inlier_mask = dataset.inlier_mask

    # 1. Lloyd's K-Means execution (Pure NumPy)
    t0_km = time.perf_counter()
    km_result = kmeans(X=X, k=k, seed=seed)
    km_time_ms = (time.perf_counter() - t0_km) * 1000.0

    km_inlier_ari = compute_inlier_ari(
        y_true=y_true,
        y_pred=km_result.labels,
        inlier_mask=inlier_mask,
    )
    km_full_ari = compute_full_ari(
        y_true=y_true,
        y_pred=km_result.labels,
    )

    # 2. Prim's MST execution (Pure NumPy)
    t0_mst = time.perf_counter()
    mst_result = mst_clustering(X=X, k=k)
    mst_time_ms = (time.perf_counter() - t0_mst) * 1000.0

    mst_inlier_ari = compute_inlier_ari(
        y_true=y_true,
        y_pred=mst_result.labels,
        inlier_mask=inlier_mask,
    )
    mst_full_ari = compute_full_ari(
        y_true=y_true,
        y_pred=mst_result.labels,
    )

    return (
        km_inlier_ari,
        km_full_ari,
        km_time_ms,
        mst_inlier_ari,
        mst_full_ari,
        mst_time_ms,
    )


def run_robustness_experiment(
    config: SweepConfig,
    progress_callback: Optional[Callable[[int, int, str], None]] = None,
) -> List[TrialResult]:
    """Execute a fully controlled, paired robustness experiment across configured sweeps.

    Args:
        config: Validated SweepConfig specifying families, sweeps, levels, and seeds.
        progress_callback: Optional callback reporting (completed_trials, total_trials, status_message).

    Returns:
        List of TrialResult records with computed ARI, runtimes, and matched-baseline metrics.
    """
    config.validate()
    total_trials = config.total_expected_trials()
    completed = 0

    results: List[TrialResult] = []

    # Map to store matched baseline Inlier ARIs:
    # Key: (sweep_type, family, seed, algorithm_name) -> inlier_ari
    baseline_map: Dict[Tuple[str, str, int, str], float] = {}

    # -------------------------------------------------------------------------
    # Helper to generate dataset and record trials
    # -------------------------------------------------------------------------
    def _execute_sweep_level(
        sweep_type: str,
        param_name: str,
        param_value: float,
        family: str,
        seed: int,
        noise_sigma: float,
        outlier_rate: float,
    ) -> Tuple[TrialResult, TrialResult]:
        nonlocal completed

        k = _get_cluster_count(config, family)
        geom_kwargs = _get_family_hyperparams(config, family)

        # Generate dataset with decoupled contamination streams
        dataset = generate_synthetic_dataset(
            family=family,
            n_samples=config.n_inliers,
            seed=seed,
            noise=noise_sigma,
            outlier_rate=outlier_rate,
            **geom_kwargs,
        )

        # Execute dual clustering on IDENTICAL coordinates
        (
            km_in_ari,
            km_fl_ari,
            km_time,
            mst_in_ari,
            mst_fl_ari,
            mst_time,
        ) = _run_dual_clustering_on_dataset(dataset=dataset, k=k, seed=seed)

        completed += 1
        if progress_callback is not None:
            msg = f"{family.capitalize()} | {sweep_type} ({param_name}={param_value:.2f}) | seed={seed}"
            progress_callback(completed, total_trials, msg)

        km_trial = TrialResult(
            dataset_family=family,
            sweep_type=sweep_type,
            parameter_name=param_name,
            parameter_value=param_value,
            seed=seed,
            n_inliers=dataset.n_inliers,
            n_outliers=dataset.n_outliers,
            n_total=dataset.n_samples,
            k=k,
            algorithm="Lloyd K-Means",
            inlier_ari=km_in_ari,
            full_ari=km_fl_ari,
            runtime_ms=km_time,
        )

        mst_trial = TrialResult(
            dataset_family=family,
            sweep_type=sweep_type,
            parameter_name=param_name,
            parameter_value=param_value,
            seed=seed,
            n_inliers=dataset.n_inliers,
            n_outliers=dataset.n_outliers,
            n_total=dataset.n_samples,
            k=k,
            algorithm="Prim MST",
            inlier_ari=mst_in_ari,
            full_ari=mst_fl_ari,
            runtime_ms=mst_time,
        )

        return km_trial, mst_trial

    # -------------------------------------------------------------------------
    # Pre-compute matched baselines if not explicitly in configured levels
    # -------------------------------------------------------------------------
    for family in config.dataset_families:
        k = _get_cluster_count(config, family)
        geom_kwargs = _get_family_hyperparams(config, family)

        for seed in config.seeds:
            # Noise sweep baseline: noise=0.00, outlier=0.0
            if SweepType.NOISE.value in config.sweep_types:
                ds_noise_base = generate_synthetic_dataset(
                    family=family,
                    n_samples=config.n_inliers,
                    seed=seed,
                    noise=0.0,
                    outlier_rate=0.0,
                    **geom_kwargs,
                )
                km_ari, _, _, mst_ari, _, _ = _run_dual_clustering_on_dataset(
                    dataset=ds_noise_base, k=k, seed=seed
                )
                baseline_map[(SweepType.NOISE.value, family, seed, "Lloyd K-Means")] = km_ari
                baseline_map[(SweepType.NOISE.value, family, seed, "Prim MST")] = mst_ari

            # Outlier sweep baseline: noise=outlier_sweep_base_noise, outlier=0.0
            if SweepType.OUTLIER.value in config.sweep_types:
                ds_outlier_base = generate_synthetic_dataset(
                    family=family,
                    n_samples=config.n_inliers,
                    seed=seed,
                    noise=config.outlier_sweep_base_noise,
                    outlier_rate=0.0,
                    **geom_kwargs,
                )
                km_ari, _, _, mst_ari, _, _ = _run_dual_clustering_on_dataset(
                    dataset=ds_outlier_base, k=k, seed=seed
                )
                baseline_map[(SweepType.OUTLIER.value, family, seed, "Lloyd K-Means")] = km_ari
                baseline_map[(SweepType.OUTLIER.value, family, seed, "Prim MST")] = mst_ari

    # -------------------------------------------------------------------------
    # 1. Execute Noise Sweep (Vary sigma, outlier_rate = 0.0)
    # -------------------------------------------------------------------------
    if SweepType.NOISE.value in config.sweep_types:
        for family in config.dataset_families:
            for sigma in config.noise_levels:
                for seed in config.seeds:
                    km_trial, mst_trial = _execute_sweep_level(
                        sweep_type=SweepType.NOISE.value,
                        param_name="noise_sigma",
                        param_value=float(sigma),
                        family=family,
                        seed=seed,
                        noise_sigma=float(sigma),
                        outlier_rate=0.0,
                    )
                    results.extend([km_trial, mst_trial])

    # -------------------------------------------------------------------------
    # 2. Execute Outlier Sweep (Vary rate, noise = outlier_sweep_base_noise)
    # -------------------------------------------------------------------------
    if SweepType.OUTLIER.value in config.sweep_types:
        for family in config.dataset_families:
            for rate in config.outlier_rates:
                for seed in config.seeds:
                    km_trial, mst_trial = _execute_sweep_level(
                        sweep_type=SweepType.OUTLIER.value,
                        param_name="outlier_rate",
                        param_value=float(rate),
                        family=family,
                        seed=seed,
                        noise_sigma=float(config.outlier_sweep_base_noise),
                        outlier_rate=float(rate),
                    )
                    results.extend([km_trial, mst_trial])

    # -------------------------------------------------------------------------
    # 3. Associate Matched Baselines and Compute Relative Metrics
    # -------------------------------------------------------------------------
    for trial in results:
        base_key = (trial.sweep_type, trial.dataset_family, trial.seed, trial.algorithm)
        base_ari = baseline_map.get(base_key, trial.inlier_ari)
        trial.baseline_inlier_ari = base_ari
        # Signed change (can be positive, negative, or zero; unconstrained)
        trial.delta_inlier_ari = trial.inlier_ari - base_ari
        # Nonnegative degradation loss (clamped to >= 0.0)
        trial.degradation_inlier_ari = max(0.0, base_ari - trial.inlier_ari)

    return results
