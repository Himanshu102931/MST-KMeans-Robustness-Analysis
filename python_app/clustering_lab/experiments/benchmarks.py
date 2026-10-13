"""
clustering_lab.experiments.benchmarks
=====================================
Scientifically rigorous execution-time benchmark engine for comparing custom
Lloyd's K-Means and dense Prim's Minimum Spanning Tree (MST) clustering.

Academic Context:
    Course: Pattern Matching Lab (BCS-DS-777)
    Project: MST vs K-Means Robustness Analysis
    Authors: Himanshu Gupta ([REDACTED_STUDENT_IDENTIFIER]) & Parth Yadav ([REDACTED_STUDENT_IDENTIFIER])
    Instructor: Mr. Aman Kumar, Assistant Professor
    Institution: MRIIRS, School of Engineering & Technology (2026–2027)

Methodological Guarantees:
    1. Evaluates the ACTUAL from-scratch pure NumPy implementations:
       - Lloyd's K-Means with K-Means++ initialization (O(I * N * k * D))
       - Dense Prim's Euclidean MST clustering (O(N^2))
    2. Measures algorithm runtime strictly in isolation:
       - Dataset synthesis occurs OUTSIDE the timed measurement block.
       - Both algorithms receive the exact same coordinate array copy of feature matrix X.
       - Rendering, plotting, and metric evaluation are excluded from timing.
    3. High-resolution monotonic timer:
       - Uses time.perf_counter_ns() for nanosecond precision, converted to float ms.
    4. Optional warm-up trial:
       - Prevents cold-start caching bias; warm-up runs are excluded from metrics.
    5. Statistical Rigor:
       - Computes mean, median, sample standard deviation (Bessel's ddof=1), min, and max.
       - Defines comparison ratio strictly as ratio_of_means = mean(MST) / mean(K-Means).
       - Explicitly notes machine, OS, and CPU dependencies.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import platform
import sys
import time
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple, Union
import numpy as np
import pandas as pd

from clustering_lab.algorithms.kmeans import KMeansResult, kmeans
from clustering_lab.algorithms.mst import MSTClusteringResult, mst_clustering
from clustering_lab.data.synthetic import generate_blobs


# Benchmark defaults and safety constraints
DEFAULT_BENCHMARK_SIZES: Tuple[int, ...] = (100, 200, 400, 600)
DEFAULT_BENCHMARK_REPETITIONS: int = 5
DEFAULT_BENCHMARK_SEED: int = 42
DEFAULT_BLOBS_K: int = 3
DEFAULT_BLOBS_STD: float = 0.4
DEFAULT_BLOBS_RADIUS: float = 3.5

MAX_BENCHMARK_SAMPLE_SIZE: int = 600
MIN_BENCHMARK_SAMPLE_SIZE: int = 10
MAX_BENCHMARK_REPETITIONS: int = 10
MAX_TOTAL_BENCHMARK_EXECUTIONS: int = 200


@dataclass
class BenchmarkConfig:
    """Validated configuration container for performance benchmarking sweeps.

    Attributes:
        dataset_family: Dataset topology (strictly 'blobs' for controlled spherical baseline).
        sample_sizes: Sequence of observation counts N to benchmark (each <= 600).
        n_repetitions: Number of measured repetitions per sample size (1 to 10).
        seed: Master random seed for deterministic dataset generation.
        blobs_k: Target cluster count k (default 3).
        blobs_cluster_std: Standard deviation of cluster Gaussian dispersion (default 0.4).
        blobs_radius: Distance of cluster centers from origin (default 3.5).
        warmup: If True, executes one unmeasured warm-up run per algorithm before timing.
    """

    MAX_TOTAL_EXECUTIONS: int = MAX_TOTAL_BENCHMARK_EXECUTIONS

    dataset_family: str = "blobs"
    sample_sizes: Tuple[int, ...] = DEFAULT_BENCHMARK_SIZES
    n_repetitions: int = DEFAULT_BENCHMARK_REPETITIONS
    seed: int = DEFAULT_BENCHMARK_SEED
    blobs_k: int = DEFAULT_BLOBS_K
    blobs_cluster_std: float = DEFAULT_BLOBS_STD
    blobs_radius: float = DEFAULT_BLOBS_RADIUS
    warmup: bool = True

    def __init__(
        self,
        dataset_family: str = "blobs",
        sample_sizes: Optional[Sequence[int]] = None,
        n_repetitions: Optional[int] = None,
        repetitions: Optional[int] = None,
        seed: int = DEFAULT_BENCHMARK_SEED,
        blobs_k: Optional[int] = None,
        n_clusters: Optional[int] = None,
        blobs_cluster_std: Optional[float] = None,
        cluster_std: Optional[float] = None,
        blobs_radius: Optional[float] = None,
        radius: Optional[float] = None,
        warmup: bool = True,
        **kwargs: Any,
    ) -> None:
        self.dataset_family = dataset_family
        if sample_sizes is None:
            self.sample_sizes = DEFAULT_BENCHMARK_SIZES
        else:
            self.sample_sizes = tuple(int(x) for x in sample_sizes)

        # Repetition alias handling
        if n_repetitions is not None:
            self.n_repetitions = int(n_repetitions)
        elif repetitions is not None:
            self.n_repetitions = int(repetitions)
        else:
            self.n_repetitions = DEFAULT_BENCHMARK_REPETITIONS

        self.seed = int(seed)

        # k alias handling
        if blobs_k is not None:
            self.blobs_k = int(blobs_k)
        elif n_clusters is not None:
            self.blobs_k = int(n_clusters)
        else:
            self.blobs_k = DEFAULT_BLOBS_K

        # cluster_std alias handling
        if blobs_cluster_std is not None:
            self.blobs_cluster_std = float(blobs_cluster_std)
        elif cluster_std is not None:
            self.blobs_cluster_std = float(cluster_std)
        else:
            self.blobs_cluster_std = DEFAULT_BLOBS_STD

        # radius alias handling
        if blobs_radius is not None:
            self.blobs_radius = float(blobs_radius)
        elif radius is not None:
            self.blobs_radius = float(radius)
        else:
            self.blobs_radius = DEFAULT_BLOBS_RADIUS

        self.warmup = bool(warmup)
        self.validate()

    @property
    def repetitions(self) -> int:
        """Alias for n_repetitions."""
        return self.n_repetitions

    @property
    def n_clusters(self) -> int:
        """Alias for blobs_k."""
        return self.blobs_k

    @property
    def cluster_std(self) -> float:
        """Alias for blobs_cluster_std."""
        return self.blobs_cluster_std

    @property
    def radius(self) -> float:
        """Alias for blobs_radius."""
        return self.blobs_radius

    def validate(self) -> None:
        """Validate configuration parameters against safety and scientific bounds.

        Raises:
            ValueError: If any parameter violates scientific or computational limits.
        """
        if self.dataset_family.lower() != "blobs":
            raise ValueError(f"Performance benchmark requires 'blobs' family, got '{self.dataset_family}'.")

        if not self.sample_sizes or len(self.sample_sizes) == 0:
            raise ValueError("At least one sample size must be provided; sample_sizes sequence cannot be empty.")

        for n in self.sample_sizes:
            if not isinstance(n, (int, np.integer)) or n < MIN_BENCHMARK_SAMPLE_SIZE:
                raise ValueError(
                    f"Sample size {n} is below minimum interactive limit of {MIN_BENCHMARK_SAMPLE_SIZE}."
                )
            if n > MAX_BENCHMARK_SAMPLE_SIZE:
                raise ValueError(
                    f"Sample size {n} exceeds safe limit of {MAX_BENCHMARK_SAMPLE_SIZE}."
                )

        if not (1 <= self.n_repetitions <= MAX_BENCHMARK_REPETITIONS):
            raise ValueError(
                f"n_repetitions must be between 1 and {MAX_BENCHMARK_REPETITIONS}, got {self.n_repetitions}."
            )

        if self.seed < 0:
            raise ValueError(f"Seed must be non-negative, got {self.seed}.")

        if self.blobs_k < 1:
            raise ValueError(f"blobs_k must be >= 1, got {self.blobs_k}.")
        if self.blobs_cluster_std <= 0.0:
            raise ValueError(f"blobs_cluster_std must be > 0.0, got {self.blobs_cluster_std}.")
        if self.blobs_radius <= 0.0:
            raise ValueError(f"blobs_radius must be > 0.0, got {self.blobs_radius}.")

        total_execs = self.total_expected_executions()
        if total_execs > MAX_TOTAL_BENCHMARK_EXECUTIONS:
            raise ValueError(
                f"Total expected algorithm executions ({total_execs}) exceeds maximum safe workload of "
                f"{MAX_TOTAL_BENCHMARK_EXECUTIONS}. Reduce sample sizes or repetitions."
            )

    def total_expected_trials(self) -> int:
        """Return total number of dataset configurations evaluated across repetitions."""
        return len(self.sample_sizes) * self.n_repetitions

    def total_expected_executions(self) -> int:
        """Return total number of algorithm executions (2 algorithms per trial, plus warmup)."""
        warmup_runs = (len(self.sample_sizes) * 2) if self.warmup else 0
        return (self.total_expected_trials() * 2) + warmup_runs

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "schema": "benchmark_config",
            "version": "1.0.0",
            "dataset_family": self.dataset_family,
            "sample_sizes": list(self.sample_sizes),
            "n_repetitions": self.n_repetitions,
            "repetitions": self.n_repetitions,
            "seed": self.seed,
            "blobs_k": self.blobs_k,
            "n_clusters": self.blobs_k,
            "blobs_cluster_std": self.blobs_cluster_std,
            "cluster_std": self.blobs_cluster_std,
            "blobs_radius": self.blobs_radius,
            "radius": self.blobs_radius,
            "warmup": self.warmup,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> BenchmarkConfig:
        """Construct validated BenchmarkConfig from dictionary."""
        return cls(**data)


@dataclass
class BenchmarkTrialResult:
    """Record of an individual timed algorithm execution trial.

    Stores both individual and paired measurements for complete flexibility.
    """

    sample_size: int
    repetition_index: int
    seed: int = 42
    kmeans_runtime_ms: float = 0.0
    mst_runtime_ms: float = 0.0
    kmeans_inertia: float = 0.0
    mst_total_weight: float = 0.0
    kmeans_iterations: int = 0
    mst_edges_count: int = 0
    algorithm: str = "Paired Benchmark"
    runtime_ms: float = 0.0
    runtime_ns: int = 0

    def __init__(
        self,
        sample_size: int,
        repetition_index: int,
        seed: int = 42,
        algorithm: Optional[str] = None,
        runtime_ns: int = 0,
        runtime_ms: Optional[float] = None,
        k: int = 3,
        n_clusters_predicted: int = 3,
        inertia_or_weight: float = 0.0,
        converged: bool = True,
        kmeans_runtime_ms: Optional[float] = None,
        mst_runtime_ms: Optional[float] = None,
        kmeans_inertia: Optional[float] = None,
        mst_total_weight: Optional[float] = None,
        kmeans_iterations: int = 0,
        mst_edges_count: int = 0,
        **kwargs: Any,
    ) -> None:
        self.sample_size = sample_size
        self.repetition_index = repetition_index
        self.seed = seed

        # Paired execution fields
        self.kmeans_runtime_ms = kmeans_runtime_ms if kmeans_runtime_ms is not None else (runtime_ms or 0.0)
        self.mst_runtime_ms = mst_runtime_ms if mst_runtime_ms is not None else (runtime_ms or 0.0)
        self.kmeans_inertia = kmeans_inertia if kmeans_inertia is not None else inertia_or_weight
        self.mst_total_weight = mst_total_weight if mst_total_weight is not None else inertia_or_weight
        self.kmeans_iterations = kmeans_iterations
        self.mst_edges_count = mst_edges_count or max(1, sample_size - 1)

        # Backward compatibility fields
        self.algorithm = algorithm or "Paired Benchmark"
        self.runtime_ns = runtime_ns
        self.runtime_ms = runtime_ms if runtime_ms is not None else self.kmeans_runtime_ms

    def to_dict(self) -> Dict[str, Any]:
        """Convert trial result to dictionary."""
        return {
            "sample_size": self.sample_size,
            "repetition_index": self.repetition_index,
            "seed": self.seed,
            "kmeans_runtime_ms": self.kmeans_runtime_ms,
            "mst_runtime_ms": self.mst_runtime_ms,
            "kmeans_inertia": self.kmeans_inertia,
            "mst_total_weight": self.mst_total_weight,
            "kmeans_iterations": self.kmeans_iterations,
            "mst_edges_count": self.mst_edges_count,
        }


@dataclass
class BenchmarkAggregateRow:
    """Statistical summary of benchmark repetitions for a specific (sample_size, algorithm) pair."""

    sample_size: int
    algorithm: str
    n_runs: int
    mean_ms: float
    median_ms: float
    std_ms: float
    min_ms: float
    max_ms: float

    def to_dict(self) -> Dict[str, Any]:
        """Convert aggregated row to dictionary."""
        return asdict(self)


@dataclass
class BenchmarkSummaryRow:
    """Comprehensive summary row per sample size comparing K-Means and MST."""

    sample_size: int
    repetitions: int
    kmeans_mean_ms: float
    kmeans_median_ms: float
    kmeans_std_ms: float
    kmeans_min_ms: float
    kmeans_max_ms: float
    mst_mean_ms: float
    mst_median_ms: float
    mst_std_ms: float
    mst_min_ms: float
    mst_max_ms: float
    ratio_of_means: Optional[float]
    ratio_of_medians: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert summary row to dictionary."""
        return asdict(self)


class BenchmarkSummary:
    """Aggregated benchmark report container supporting both per-size rows and tabular representations."""

    rows: List[BenchmarkSummaryRow]
    aggregates: List[BenchmarkAggregateRow]
    ratio_of_means_dict: Dict[int, Optional[float]]
    ratio_of_medians_dict: Dict[int, Optional[float]]
    platform_info: Dict[str, str]

    # Row attribute proxies for single-item construction in tests
    sample_size: int = 0
    repetitions: int = 0
    kmeans_mean_ms: float = 0.0
    kmeans_median_ms: float = 0.0
    kmeans_std_ms: float = 0.0
    kmeans_min_ms: float = 0.0
    kmeans_max_ms: float = 0.0
    mst_mean_ms: float = 0.0
    mst_median_ms: float = 0.0
    mst_std_ms: float = 0.0
    mst_min_ms: float = 0.0
    mst_max_ms: float = 0.0
    ratio_of_means: Optional[float] = None

    def __init__(
        self,
        rows: Optional[List[BenchmarkSummaryRow]] = None,
        aggregates: Optional[List[BenchmarkAggregateRow]] = None,
        ratio_of_means: Optional[Union[Dict[int, Optional[float]], float]] = None,
        ratio_of_medians: Optional[Dict[int, Optional[float]]] = None,
        platform_info: Optional[Dict[str, str]] = None,
        # Direct keyword arguments for single-item instantiation
        sample_size: Optional[int] = None,
        repetitions: Optional[int] = None,
        kmeans_mean_ms: Optional[float] = None,
        kmeans_median_ms: Optional[float] = None,
        kmeans_std_ms: Optional[float] = None,
        kmeans_min_ms: Optional[float] = None,
        kmeans_max_ms: Optional[float] = None,
        mst_mean_ms: Optional[float] = None,
        mst_median_ms: Optional[float] = None,
        mst_std_ms: Optional[float] = None,
        mst_min_ms: Optional[float] = None,
        mst_max_ms: Optional[float] = None,
        **kwargs: Any,
    ) -> None:
        if sample_size is not None and kmeans_mean_ms is not None:
            # Single-item constructor mode
            r_ratio = ratio_of_means if isinstance(ratio_of_means, (int, float)) else None
            single_row = BenchmarkSummaryRow(
                sample_size=sample_size,
                repetitions=repetitions or 1,
                kmeans_mean_ms=kmeans_mean_ms,
                kmeans_median_ms=kmeans_median_ms if kmeans_median_ms is not None else kmeans_mean_ms,
                kmeans_std_ms=kmeans_std_ms if kmeans_std_ms is not None else 0.0,
                kmeans_min_ms=kmeans_min_ms if kmeans_min_ms is not None else kmeans_mean_ms,
                kmeans_max_ms=kmeans_max_ms if kmeans_max_ms is not None else kmeans_mean_ms,
                mst_mean_ms=mst_mean_ms if mst_mean_ms is not None else 0.0,
                mst_median_ms=mst_median_ms if mst_median_ms is not None else (mst_mean_ms or 0.0),
                mst_std_ms=mst_std_ms if mst_std_ms is not None else 0.0,
                mst_min_ms=mst_min_ms if mst_min_ms is not None else (mst_mean_ms or 0.0),
                mst_max_ms=mst_max_ms if mst_max_ms is not None else (mst_mean_ms or 0.0),
                ratio_of_means=r_ratio,
            )
            self.rows = [single_row]
            self.sample_size = sample_size
            self.repetitions = repetitions or 1
            self.kmeans_mean_ms = kmeans_mean_ms
            self.kmeans_median_ms = single_row.kmeans_median_ms
            self.kmeans_std_ms = single_row.kmeans_std_ms
            self.kmeans_min_ms = single_row.kmeans_min_ms
            self.kmeans_max_ms = single_row.kmeans_max_ms
            self.mst_mean_ms = single_row.mst_mean_ms
            self.mst_median_ms = single_row.mst_median_ms
            self.mst_std_ms = single_row.mst_std_ms
            self.mst_min_ms = single_row.mst_min_ms
            self.mst_max_ms = single_row.mst_max_ms
            self.ratio_of_means = r_ratio
            self.aggregates = aggregates or []
            self.ratio_of_means_dict = {sample_size: r_ratio}
            self.ratio_of_medians_dict = {}
            self.platform_info = platform_info or {}
        else:
            self.rows = rows or []
            self.aggregates = aggregates or []
            self.ratio_of_means_dict = ratio_of_means if isinstance(ratio_of_means, dict) else {}
            self.ratio_of_medians_dict = ratio_of_medians or {}
            self.platform_info = platform_info or {}
            if self.rows:
                first = self.rows[0]
                self.sample_size = first.sample_size
                self.repetitions = first.repetitions
                self.kmeans_mean_ms = first.kmeans_mean_ms
                self.kmeans_median_ms = first.kmeans_median_ms
                self.kmeans_std_ms = first.kmeans_std_ms
                self.kmeans_min_ms = first.kmeans_min_ms
                self.kmeans_max_ms = first.kmeans_max_ms
                self.mst_mean_ms = first.mst_mean_ms
                self.mst_median_ms = first.mst_median_ms
                self.mst_std_ms = first.mst_std_ms
                self.mst_min_ms = first.mst_min_ms
                self.mst_max_ms = first.mst_max_ms
                self.ratio_of_means = first.ratio_of_means

    def __iter__(self):
        return iter(self.rows)

    def __len__(self) -> int:
        return len(self.rows)

    def __getitem__(self, index: int) -> BenchmarkSummaryRow:
        return self.rows[index]

    def to_dict(self) -> Dict[str, Any]:
        """Convert summary row to dictionary."""
        if self.rows:
            return self.rows[0].to_dict()
        return {
            "sample_size": self.sample_size,
            "repetitions": self.repetitions,
            "kmeans_mean_ms": self.kmeans_mean_ms,
            "kmeans_median_ms": self.kmeans_median_ms,
            "kmeans_std_ms": self.kmeans_std_ms,
            "kmeans_min_ms": self.kmeans_min_ms,
            "kmeans_max_ms": self.kmeans_max_ms,
            "mst_mean_ms": self.mst_mean_ms,
            "mst_median_ms": self.mst_median_ms,
            "mst_std_ms": self.mst_std_ms,
            "mst_min_ms": self.mst_min_ms,
            "mst_max_ms": self.mst_max_ms,
            "ratio_of_means": self.ratio_of_means,
        }

    def to_dataframe(self) -> pd.DataFrame:
        """Convert summary rows to a formatted pandas DataFrame."""
        if not self.rows:
            return pd.DataFrame()
        return pd.DataFrame([r.to_dict() for r in self.rows])


def compute_sample_std(values: Sequence[float]) -> float:
    """Calculate sample standard deviation with Bessel's correction (ddof=1).

    Note on statistical terminology:
        Dividing the sum of squared deviations by (N - 1) via Bessel's correction
        (ddof=1) yields an unbiased estimator of population variance (s^2).
        The sample standard deviation s = sqrt(s^2) applies Bessel's correction
        to reduce small-sample bias, but due to Jensen's inequality (concavity
        of the square root function, E[s] <= sigma), s is not strictly an
        unbiased estimator of population standard deviation sigma.

    Args:
        values: Sequence of numeric measurements.

    Returns:
        Sample standard deviation as float. Returns 0.0 if len(values) <= 1.
    """
    n = len(values)
    if n <= 1:
        return 0.0
    arr = np.asarray(values, dtype=np.float64)
    return float(np.std(arr, ddof=1))


def run_performance_benchmark(
    config: BenchmarkConfig,
    progress_callback: Optional[Callable[[int, int, int, int, str], None]] = None,
) -> List[BenchmarkTrialResult]:
    """Execute a controlled, paired execution-time benchmark across configured sample sizes.

    Methodological Invariants:
        1. Both algorithms receive an exact memory copy of identical feature matrix X.
        2. Execution times are captured using monotonic time.perf_counter_ns().
        3. Data generation occurs strictly OUTSIDE the timed regions.
        4. Optional warm-up run executes prior to measured repetitions to prime CPU caches.

    Args:
        config: Validated BenchmarkConfig object.
        progress_callback: Optional callback reporting (completed, total, sample_size, rep, algo).

    Returns:
        List of BenchmarkTrialResult records.
    """
    config.validate()
    total_execs = config.total_expected_executions()
    completed_execs = 0

    results: List[BenchmarkTrialResult] = []

    # Optional warm-up stage (excluded from results)
    if config.warmup:
        for size in config.sample_sizes:
            ds_warmup = generate_blobs(
                n_samples=size,
                n_clusters=config.blobs_k,
                cluster_std=config.blobs_cluster_std,
                radius=config.blobs_radius,
                seed=config.seed + 9999 + size,
            )
            X_warmup = ds_warmup.X.copy()
            # Warmup K-Means
            _ = kmeans(X=X_warmup, k=config.blobs_k, seed=config.seed)
            completed_execs += 1
            # Warmup MST
            _ = mst_clustering(X=X_warmup, k=config.blobs_k)
            completed_execs += 1

    # Measured Trials
    for size in config.sample_sizes:
        for rep in range(1, config.n_repetitions + 1):
            trial_seed = config.seed + (rep * 1000) + size

            # 1. Synthesize dataset strictly outside timed blocks
            ds = generate_blobs(
                n_samples=size,
                n_clusters=config.blobs_k,
                cluster_std=config.blobs_cluster_std,
                radius=config.blobs_radius,
                seed=trial_seed,
            )
            X = ds.X.copy()

            # 2. Time custom Lloyd's K-Means
            if progress_callback is not None:
                progress_callback(completed_execs, total_execs, size, rep, "Lloyd K-Means")

            t0_km = time.perf_counter_ns()
            km_res: KMeansResult = kmeans(
                X=X,
                k=config.blobs_k,
                max_iter=300,
                tol=1e-4,
                seed=trial_seed,
            )
            t1_km = time.perf_counter_ns()
            km_ns = t1_km - t0_km
            km_ms = km_ns / 1_000_000.0
            completed_execs += 1

            # 3. Time custom dense Prim's MST on the exact same array
            if progress_callback is not None:
                progress_callback(completed_execs, total_execs, size, rep, "Prim MST")

            t0_mst = time.perf_counter_ns()
            mst_res: MSTClusteringResult = mst_clustering(
                X=X,
                k=config.blobs_k,
            )
            t1_mst = time.perf_counter_ns()
            mst_ns = t1_mst - t0_mst
            mst_ms = mst_ns / 1_000_000.0
            completed_execs += 1

            results.append(
                BenchmarkTrialResult(
                    sample_size=size,
                    repetition_index=rep,
                    seed=trial_seed,
                    kmeans_runtime_ms=km_ms,
                    mst_runtime_ms=mst_ms,
                    kmeans_inertia=float(km_res.inertia),
                    mst_total_weight=float(mst_res.total_mst_weight),
                    kmeans_iterations=int(km_res.n_iter),
                    mst_edges_count=len(mst_res.mst_edges),
                    runtime_ns=km_ns,
                    runtime_ms=km_ms,
                )
            )

    if progress_callback is not None:
        progress_callback(total_execs, total_execs, config.sample_sizes[-1], config.n_repetitions, "Completed")

    return results


def aggregate_benchmark_trials(trials: List[BenchmarkTrialResult]) -> BenchmarkSummary:
    """Aggregate individual benchmark trials into summary statistics and comparative ratios.

    Statistical Definitions:
        - Mean: (1 / n) * sum(x_i)
        - Median: Middle value of sorted runtimes
        - Sample Standard Deviation: sqrt((1 / (n - 1)) * sum((x_i - mean)^2)) (Bessel's correction ddof=1)
        - Ratio of Means: mean(MST runtime) / mean(K-Means runtime)
          (Zero-denominator returns None rather than an invalid value).

    Args:
        trials: List of BenchmarkTrialResult records.

    Returns:
        BenchmarkSummary containing aggregated statistics and scaling ratios.
    """
    if not trials:
        return BenchmarkSummary(rows=[], aggregates=[], ratio_of_means={}, platform_info={})

    # Group trials by sample_size
    grouped: Dict[int, List[BenchmarkTrialResult]] = {}
    for t in trials:
        if t.sample_size not in grouped:
            grouped[t.sample_size] = []
        grouped[t.sample_size].append(t)

    rows: List[BenchmarkSummaryRow] = []
    ratio_of_means: Dict[int, Optional[float]] = {}
    ratio_of_medians: Dict[int, Optional[float]] = {}

    for size in sorted(grouped.keys()):
        size_trials = grouped[size]
        km_times = [t.kmeans_runtime_ms for t in size_trials]
        mst_times = [t.mst_runtime_ms for t in size_trials]

        km_arr = np.asarray(km_times, dtype=np.float64)
        mst_arr = np.asarray(mst_times, dtype=np.float64)

        km_mean = float(np.mean(km_arr))
        km_median = float(np.median(km_arr))
        km_std = compute_sample_std(km_times)
        km_min = float(np.min(km_arr))
        km_max = float(np.max(km_arr))

        mst_mean = float(np.mean(mst_arr))
        mst_median = float(np.median(mst_arr))
        mst_std = compute_sample_std(mst_times)
        mst_min = float(np.min(mst_arr))
        mst_max = float(np.max(mst_arr))

        # Comparison ratio: mean(MST) / mean(KM)
        if km_mean > 1e-12:
            r_means = mst_mean / km_mean
        else:
            r_means = None

        if km_median > 1e-12:
            r_medians = mst_median / km_median
        else:
            r_medians = None

        ratio_of_means[size] = r_means
        ratio_of_medians[size] = r_medians

        rows.append(
            BenchmarkSummaryRow(
                sample_size=size,
                repetitions=len(size_trials),
                kmeans_mean_ms=km_mean,
                kmeans_median_ms=km_median,
                kmeans_std_ms=km_std,
                kmeans_min_ms=km_min,
                kmeans_max_ms=km_max,
                mst_mean_ms=mst_mean,
                mst_median_ms=mst_median,
                mst_std_ms=mst_std,
                mst_min_ms=mst_min,
                mst_max_ms=mst_max,
                ratio_of_means=r_means,
                ratio_of_medians=r_medians,
            )
        )

    platform_info = {
        "python_version": sys.version.split()[0],
        "numpy_version": np.__version__,
        "os_system": platform.system(),
        "os_release": platform.release(),
        "processor": platform.processor() or "Generic x86_64",
    }

    return BenchmarkSummary(
        rows=rows,
        ratio_of_means=ratio_of_means,
        ratio_of_medians=ratio_of_medians,
        platform_info=platform_info,
    )
