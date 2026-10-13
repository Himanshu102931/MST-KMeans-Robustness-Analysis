"""
clustering_lab.experiments.export
=================================
Data export, serialization, and provenance isolation for robustness analysis.

Academic Context:
    Course: Pattern Matching Lab (BCS-DS-777)
    Project: MST vs K-Means Robustness Analysis
    Authors: Himanshu Gupta ([REDACTED_STUDENT_IDENTIFIER]) & Parth Yadav ([REDACTED_STUDENT_IDENTIFIER])
    Instructor: Mr. Aman Kumar, Assistant Professor
    Institution: MRIIRS, School of Engineering & Technology (2026–2027)

Provenance Separation:
    All exported CSV and JSON artifacts strictly maintain independent Python laboratory
    provenance and never overwrite legacy JavaScript benchmarks in the results/ directory.
"""

from __future__ import annotations

import datetime
import io
import json
import platform
import sys
from typing import Any, Dict, List
import numpy as np
import pandas as pd

from clustering_lab.experiments.aggregation import SweepAggregateRow, aggregates_to_dataframe, trials_to_dataframe
from clustering_lab.experiments.runner import TrialResult
from clustering_lab.experiments.sweeps import SweepConfig


def export_trials_to_csv(trials: List[TrialResult]) -> str:
    """Serialize raw trial results to a CSV string.

    Columns:
        dataset_family, sweep_type, parameter_name, parameter_value, seed,
        n_inliers, n_outliers, n_total, k, algorithm, inlier_ari, full_ari,
        runtime_ms, baseline_inlier_ari, delta_inlier_ari, degradation_inlier_ari
    """
    df = trials_to_dataframe(trials)
    if df.empty:
        return ""
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    return buf.getvalue()


def export_summary_to_csv(aggregates: List[SweepAggregateRow]) -> str:
    """Serialize aggregated sweep summary records to a CSV string.

    Columns:
        dataset_family, sweep_type, parameter_name, parameter_value, algorithm,
        n_seeds, mean_inlier_ari, std_inlier_ari, mean_full_ari, std_full_ari,
        mean_delta_inlier_ari, std_delta_inlier_ari, mean_degradation_inlier_ari,
        std_degradation_inlier_ari, mean_runtime_ms, std_runtime_ms
    """
    df = aggregates_to_dataframe(aggregates)
    if df.empty:
        return ""
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    return buf.getvalue()


def export_config_json(config: SweepConfig) -> str:
    """Serialize experiment SweepConfig to formatted JSON string."""
    return json.dumps(config.to_dict(), indent=2)


def export_experiment_metadata(
    config: SweepConfig,
    n_trials: int,
) -> Dict[str, Any]:
    """Compile comprehensive runtime environment and provenance metadata.

    Captures:
        - Engine version & ISO 8601 timestamp
        - Python interpreter version & platform
        - Scientific ecosystem library versions
        - Git branch context
        - Experiment configuration parameters
        - Provenance statement distinguishing Python lab from legacy JS assets
    """
    # Extract package versions safely
    pkg_versions: Dict[str, str] = {}
    for pkg_name in ["numpy", "scipy", "sklearn", "pandas", "streamlit", "plotly", "pytest"]:
        try:
            mod = __import__(pkg_name)
            pkg_versions[pkg_name] = getattr(mod, "__version__", "unknown")
        except ImportError:
            pkg_versions[pkg_name] = "not_installed"

    return {
        "engine": "Python Clustering Laboratory Robustness Engine",
        "phase": "M5A — Scientific Robustness Experiment Engine",
        "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "academic_context": {
            "course": "Pattern Matching Lab (BCS-DS-777)",
            "institution": "Manav Rachna International Institute of Research and Studies (MRIIRS)",
            "degree": "B.Tech CSE (AIML), 7th Semester (2026–2027)",
            "students": [
                {"name": "Himanshu Gupta", "roll_no": "[REDACTED_STUDENT_IDENTIFIER]"},
                {"name": "Parth Yadav", "roll_no": "[REDACTED_STUDENT_IDENTIFIER]"},
            ],
            "instructor": "Mr. Aman Kumar, Assistant Professor",
        },
        "git": {
            "branch": "feature/python-streamlit-migration",
            "repository": "Himanshu102931/MST-KMeans-Robustness-Analysis",
        },
        "environment": {
            "python_version": sys.version,
            "platform": platform.platform(),
            "machine": platform.machine(),
            "packages": pkg_versions,
        },
        "provenance_statement": (
            "This experiment was generated exclusively by the Python Clustering Laboratory "
            "engine in python_app/. It is strictly independent from the legacy JavaScript "
            "research benchmark files preserved in results/."
        ),
        "execution_summary": {
            "n_trials_executed": n_trials,
            "n_clustering_executions": n_trials * 2,
            "config": config.to_dict(),
        },
    }


def export_benchmark_trials_to_csv(trials: Any) -> str:
    """Serialize raw benchmark trials to a CSV string.

    Columns:
        sample_size, repetition_index, seed, algorithm, runtime_ns, runtime_ms,
        k, n_clusters_predicted, inertia_or_weight, converged
    """
    if not trials:
        return ""
    df = pd.DataFrame([t.to_dict() for t in trials])
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    return buf.getvalue()


def export_benchmark_summary_to_csv(summary: Any) -> str:
    """Serialize aggregated benchmark summary to a CSV string.

    Supports BenchmarkSummary objects, lists of rows, or pandas DataFrames.
    """
    if summary is None:
        return ""
    if isinstance(summary, pd.DataFrame):
        df = summary
    elif hasattr(summary, "to_dataframe"):
        df = summary.to_dataframe()
    elif isinstance(summary, (list, tuple)):
        rows = []
        for item in summary:
            if hasattr(item, "to_dict"):
                rows.append(item.to_dict())
            elif hasattr(item, "to_dataframe"):
                sub_df = item.to_dataframe()
                rows.extend(sub_df.to_dict(orient="records"))
            elif isinstance(item, dict):
                rows.append(item)
            else:
                try:
                    rows.append(dict(item))
                except Exception:
                    pass
        df = pd.DataFrame(rows)
    else:
        return ""

    if df.empty:
        return ""
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    return buf.getvalue()


def export_benchmark_config_json(config: Any) -> str:
    """Serialize BenchmarkConfig to formatted JSON string."""
    return json.dumps(config.to_dict(), indent=2)


def export_benchmark_metadata(
    config: Optional[Any] = None,
    n_trials: int = 0,
) -> str:
    """Compile comprehensive runtime environment and provenance metadata for benchmarks as a JSON string."""
    pkg_versions: Dict[str, str] = {}
    for pkg_name in ["numpy", "scipy", "sklearn", "pandas", "streamlit", "plotly", "pytest", "matplotlib"]:
        try:
            mod = __import__(pkg_name)
            pkg_versions[pkg_name] = getattr(mod, "__version__", "unknown")
        except ImportError:
            pkg_versions[pkg_name] = "not_installed"

    meta_dict = {
        "engine": "Python Clustering Laboratory Performance Benchmark Engine",
        "phase": "M5B — Python Performance Benchmarks, Algorithm Explorers & Research Exports",
        "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "academic_context": {
            "course": "Pattern Matching Lab (BCS-DS-777)",
            "institution": "Manav Rachna International Institute of Research and Studies (MRIIRS)",
            "school": "School of Engineering & Technology (SET)",
            "degree": "B.Tech CSE (AIML), 7th Semester (2026–2027)",
            "students": [
                {"name": "Himanshu Gupta", "roll_no": "[REDACTED_STUDENT_IDENTIFIER]"},
                {"name": "Parth Yadav", "roll_no": "[REDACTED_STUDENT_IDENTIFIER]"},
            ],
            "instructor": "Mr. Aman Kumar, Assistant Professor",
        },
        "institution": "MRIIRS, School of Engineering & Technology",
        "git": {
            "branch": "feature/python-streamlit-migration",
            "repository": "Himanshu102931/MST-KMeans-Robustness-Analysis",
        },
        "environment": {
            "python_version": sys.version,
            "platform": platform.platform(),
            "machine": platform.machine(),
            "packages": pkg_versions,
        },
        "python_version": sys.version.split()[0],
        "platform": platform.platform(),
        "numpy_version": np.__version__,
        "timer": "time.perf_counter_ns",
        "implementation": "Custom Pure NumPy (kmeans.py, mst.py)",
        "provenance_statement": (
            "These benchmark results were measured natively in the Python environment using "
            "time.perf_counter_ns() on pure NumPy custom clustering implementations. "
            "They are strictly independent from legacy JavaScript timing results."
        ),
        "execution_summary": {
            "n_trials_measured": n_trials,
            "n_clustering_executions": n_trials * 2,
            "config": config.to_dict() if config is not None and hasattr(config, "to_dict") else {},
        },
    }
    return json.dumps(meta_dict, indent=2)
