"""
clustering_lab.experiments.aggregation
======================================
Statistical aggregation and summary modeling across repeated Monte Carlo experiment trials.

Academic Context:
    Course: Pattern Matching Lab (BCS-DS-777)
    Project: MST vs K-Means Robustness Analysis
    Authors: Himanshu Gupta ([REDACTED_STUDENT_IDENTIFIER]) & Parth Yadav ([REDACTED_STUDENT_IDENTIFIER])
    Instructor: Mr. Aman Kumar, Assistant Professor
    Institution: MRIIRS, School of Engineering & Technology (2026–2027)

Statistical Formulations:
    - Sample Mean:
        x_bar = (1 / n) * sum_{i=1}^n x_i
    - Sample Standard Deviation (Bessel's Correction ddof=1):
        s = sqrt( (1 / (n - 1)) * sum_{i=1}^n (x_i - x_bar)^2 )  for n >= 2
        For n = 1, s is defined as 0.0 (zero degrees of freedom).
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Sequence, Tuple
import numpy as np
import pandas as pd

from clustering_lab.experiments.runner import TrialResult


def compute_sample_std(values: Sequence[float]) -> float:
    """Calculate sample standard deviation with Bessel's correction (ddof=1).

    Args:
        values: Sequence of numeric values.

    Returns:
        Sample standard deviation as float. Returns 0.0 if len(values) <= 1.
    """
    n = len(values)
    if n <= 1:
        return 0.0
    arr = np.asarray(values, dtype=np.float64)
    return float(np.std(arr, ddof=1))


@dataclass
class SweepAggregateRow:
    """Aggregated statistical record for a specific sweep parameter configuration.

    Attributes:
        dataset_family: Dataset topology ('blobs', 'moons', 'circles').
        sweep_type: Perturbation sweep ('noise' or 'outlier').
        parameter_name: Name of varied hyperparameter ('noise_sigma' or 'outlier_rate').
        parameter_value: Numeric value of the varied parameter.
        algorithm: Algorithm identifier ('Lloyd K-Means' or 'Prim MST').
        n_seeds: Number of repeated deterministic seed trials aggregated.
        mean_inlier_ari: Mean Inlier ARI across seeds.
        std_inlier_ari: Sample standard deviation of Inlier ARI across seeds.
        mean_full_ari: Mean Full-Data ARI across seeds.
        std_full_ari: Sample standard deviation of Full-Data ARI across seeds.
        mean_delta_inlier_ari: Mean signed change relative to matched baseline.
        std_delta_inlier_ari: Sample standard deviation of signed ARI change.
        mean_degradation_inlier_ari: Mean nonnegative degradation loss.
        std_degradation_inlier_ari: Sample standard deviation of degradation loss.
        mean_runtime_ms: Mean execution time in milliseconds.
        std_runtime_ms: Sample standard deviation of execution time.
    """

    dataset_family: str
    sweep_type: str
    parameter_name: str
    parameter_value: float
    algorithm: str
    n_seeds: int
    mean_inlier_ari: float
    std_inlier_ari: float
    mean_full_ari: float
    std_full_ari: float
    mean_delta_inlier_ari: float
    std_delta_inlier_ari: float
    mean_degradation_inlier_ari: float
    std_degradation_inlier_ari: float
    mean_runtime_ms: float
    std_runtime_ms: float

    def to_dict(self) -> Dict[str, Any]:
        """Convert aggregated row to dictionary."""
        return asdict(self)


def aggregate_trials(trials: List[TrialResult]) -> List[SweepAggregateRow]:
    """Aggregate individual trial results across seeds by (family, sweep, param, algorithm).

    Args:
        trials: List of TrialResult records from run_robustness_experiment.

    Returns:
        List of SweepAggregateRow records sorted deterministically.
    """
    if not trials:
        return []

    # Group trials by (dataset_family, sweep_type, parameter_name, parameter_value, algorithm)
    grouped: Dict[
        Tuple[str, str, str, float, str],
        Dict[str, List[float]],
    ] = defaultdict(lambda: {
        "inlier_ari": [],
        "full_ari": [],
        "delta_inlier_ari": [],
        "degradation_inlier_ari": [],
        "runtime_ms": [],
    })

    for t in trials:
        key = (
            t.dataset_family,
            t.sweep_type,
            t.parameter_name,
            float(t.parameter_value),
            t.algorithm,
        )
        grouped[key]["inlier_ari"].append(float(t.inlier_ari))
        grouped[key]["full_ari"].append(float(t.full_ari))
        grouped[key]["delta_inlier_ari"].append(
            float(t.delta_inlier_ari) if t.delta_inlier_ari is not None else 0.0
        )
        grouped[key]["degradation_inlier_ari"].append(
            float(t.degradation_inlier_ari) if t.degradation_inlier_ari is not None else 0.0
        )
        grouped[key]["runtime_ms"].append(float(t.runtime_ms))

    rows: List[SweepAggregateRow] = []

    # Sort keys deterministically: sweep_type, family, parameter_value, algorithm
    sorted_keys = sorted(
        grouped.keys(),
        key=lambda k: (k[1], k[0], k[3], k[4]),
    )

    for key in sorted_keys:
        fam, sw_type, param_name, param_val, algo = key
        data = grouped[key]
        n_seeds = len(data["inlier_ari"])

        in_ari_vals = data["inlier_ari"]
        fl_ari_vals = data["full_ari"]
        delta_vals = data["delta_inlier_ari"]
        deg_vals = data["degradation_inlier_ari"]
        time_vals = data["runtime_ms"]

        rows.append(
            SweepAggregateRow(
                dataset_family=fam,
                sweep_type=sw_type,
                parameter_name=param_name,
                parameter_value=param_val,
                algorithm=algo,
                n_seeds=n_seeds,
                mean_inlier_ari=float(np.mean(in_ari_vals)),
                std_inlier_ari=compute_sample_std(in_ari_vals),
                mean_full_ari=float(np.mean(fl_ari_vals)),
                std_full_ari=compute_sample_std(fl_ari_vals),
                mean_delta_inlier_ari=float(np.mean(delta_vals)),
                std_delta_inlier_ari=compute_sample_std(delta_vals),
                mean_degradation_inlier_ari=float(np.mean(deg_vals)),
                std_degradation_inlier_ari=compute_sample_std(deg_vals),
                mean_runtime_ms=float(np.mean(time_vals)),
                std_runtime_ms=compute_sample_std(time_vals),
            )
        )

    return rows


def trials_to_dataframe(trials: List[TrialResult]) -> pd.DataFrame:
    """Convert list of TrialResult records to a structured Pandas DataFrame."""
    if not trials:
        return pd.DataFrame()
    return pd.DataFrame([t.to_dict() for t in trials])


def aggregates_to_dataframe(aggregates: List[SweepAggregateRow]) -> pd.DataFrame:
    """Convert list of SweepAggregateRow records to a structured Pandas DataFrame."""
    if not aggregates:
        return pd.DataFrame()
    return pd.DataFrame([a.to_dict() for a in aggregates])
