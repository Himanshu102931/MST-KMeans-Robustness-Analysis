"""
clustering_lab.experiments
==========================
Experiment execution and robustness benchmarking workflows:
- Controlled Gaussian noise and uniform outlier sweeps
- Paired dual-algorithm execution engine (Lloyd's K-Means vs Prim's MST)
- Monte Carlo statistical aggregation across deterministic seeds
- Provenance-isolated CSV/JSON data export
"""

from __future__ import annotations

from clustering_lab.experiments.aggregation import (
    SweepAggregateRow,
    aggregate_trials,
    aggregates_to_dataframe,
    compute_sample_std,
    trials_to_dataframe,
)
from clustering_lab.experiments.export import (
    export_config_json,
    export_experiment_metadata,
    export_summary_to_csv,
    export_trials_to_csv,
)
from clustering_lab.experiments.runner import (
    TrialResult,
    run_robustness_experiment,
)
from clustering_lab.experiments.sweeps import (
    DEFAULT_EXTENDED_SEEDS,
    DEFAULT_NOISE_LEVELS,
    DEFAULT_OUTLIER_BASE_NOISE,
    DEFAULT_OUTLIER_RATES,
    DEFAULT_QUICK_SEEDS,
    ExperimentMode,
    SweepConfig,
    SweepType,
)

__all__ = [
    "SweepType",
    "ExperimentMode",
    "SweepConfig",
    "DEFAULT_QUICK_SEEDS",
    "DEFAULT_EXTENDED_SEEDS",
    "DEFAULT_NOISE_LEVELS",
    "DEFAULT_OUTLIER_RATES",
    "DEFAULT_OUTLIER_BASE_NOISE",
    "TrialResult",
    "run_robustness_experiment",
    "SweepAggregateRow",
    "compute_sample_std",
    "aggregate_trials",
    "trials_to_dataframe",
    "aggregates_to_dataframe",
    "export_trials_to_csv",
    "export_summary_to_csv",
    "export_config_json",
    "export_experiment_metadata",
]
