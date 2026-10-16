# Performance Benchmark Specification
## Empirical Execution-Time Scaling Analysis & Algorithmic Complexity

### Academic Project Information
- **Course:** Pattern Matching Lab (`BCS-DS-777`)
- **Institution:** Manav Rachna International Institute of Research and Studies (MRIIRS), School of Engineering & Technology
- **Degree:** B.Tech Computer Science & Engineering (AIML), 7th Semester (2026–2027)
- **Student Researchers (Equal Academic Contribution):**
  - Himanshu Gupta
  - Parth Yadav
- **Course Instructor:** Mr. Aman Kumar, Assistant Professor
- **Active Branch:** `feature/python-streamlit-migration`
- **Module Path:** `python_app/clustering_lab/experiments/benchmarks.py`

---

## 1. Scientific Motivation & Objective

While Phase M5A evaluated topological and noise robustness (clustering quality measured via Adjusted Rand Index), Phase M5B investigates the **computational trade-off** between centroid-based geometric optimization and graph-theoretic single-linkage partitioning.

The objective of the Python Performance Benchmark Engine is to measure, statistically aggregate, and compare the execution time of:
1. **Custom Lloyd's K-Means** (with K-Means++ initialization).
2. **Custom Dense Prim's MST** clustering.

The benchmark engine operates on actual custom from-scratch pure NumPy implementations, strictly avoiding third-party library calls (such as `scipy.spatial.distance` or `sklearn.cluster.KMeans`) within the measured regions.

---

## 2. Benchmark Methodology

### 2.1 Controlled Dataset Baseline
- **Distribution:** Synthetic Gaussian Blobs ($k=3$, cluster dispersion $\sigma=0.4$, radius $r=3.5$).
- **Observation Counts ($N$):** Default evaluation grid $N \in \{100, 200, 400, 600\}$.
- **Repetitions ($R$):** Default 5 measured repetitions per observation count.
- **Deterministic Seed Sequence:** Dataset generation for repetition $r$ at size $N$ uses seed $s = \text{seed} + (r \times 1000) + N$, guaranteeing exact cross-platform replication.

### 2.2 Measurement Isolation Protocol
To guarantee scientific validity:
1. **Data Generation Outside Timed Region:** Dataset generation, cluster centering, label generation, and coordinate array copying are performed strictly *before* the timer starts.
2. **Identical Memory Copies:** Both algorithms receive an exact duplicate of the identical 2D feature matrix `X = ds.X.copy()`.
3. **High-Resolution Monotonic Clock:** Elapsed execution time is captured via `time.perf_counter_ns()`, measuring the monotonic clock with nanosecond resolution, and converted to milliseconds ($t_{\text{ms}} = \Delta t_{\text{ns}} / 10^6$).
4. **Rendering & Export Exclusion:** Neither Plotly/Matplotlib rendering, Streamlit widget execution, nor metrics computation is included in the recorded algorithm runtimes.
5. **Pre-Benchmark Warm-Up:** An optional, separately labeled warm-up execution runs before measured repetitions to prime CPU caches and NumPy internal buffer pools; warm-up measurements are strictly excluded from statistical results.

---

## 3. Statistical Formulations

For a given observation count $N$ across $R$ independent repetitions, runtimes $t_1, t_2, \dots, t_R$ are aggregated as follows:

### 3.1 Arithmetic Mean
$$\bar{t} = \frac{1}{R} \sum_{r=1}^R t_r$$

### 3.2 Median
$$\tilde{t} = \begin{cases} t_{((R+1)/2)} & \text{if } R \text{ is odd} \\ \frac{1}{2}\left(t_{(R/2)} + t_{(R/2 + 1)}\right) & \text{if } R \text{ is even} \end{cases}$$

### 3.3 Sample Standard Deviation (Bessel's Correction)
$$s = \sqrt{\frac{1}{R - 1} \sum_{r=1}^R (t_r - \bar{t})^2} \quad (\text{for } R > 1; \quad s = 0.0 \text{ for } R = 1)$$

> [!NOTE]
> **Statistical Precision (Unbiased Sample Variance vs. Sample Standard Deviation):**
> Dividing the sum of squared deviations by $R - 1$ (Bessel's correction, $ddof=1$) yields an **unbiased estimator of population variance** ($s^2$, satisfying $\mathbb{E}[s^2] = \sigma^2$).
> However, because the square root function is strictly concave, Jensen's inequality implies $\mathbb{E}[s] = \mathbb{E}[\sqrt{s^2}] \le \sqrt{\mathbb{E}[s^2]} = \sigma$.
> Thus, the sample standard deviation $s = \sqrt{s^2}$ is **not** strictly an unbiased estimator of population standard deviation $\sigma$ (it slightly underestimates $\sigma$ for finite samples). Applying Bessel's correction ($ddof=1$) is standard scientific practice to reduce small-sample bias, but it must not be conflated with the exact unbiasedness of sample variance $s^2$.

### 3.4 Comparison Ratio: Ratio of Means
The comparative scaling ratio is defined strictly as the **ratio of sample means**:
$$\text{Ratio of Means} = \frac{\bar{t}_{\text{MST}}}{\bar{t}_{\text{K-Means}}}$$

> [!IMPORTANT]
> **Mathematical Distinction:** The ratio of means ($\bar{t}_{\text{MST}} / \bar{t}_{\text{KM}}$) is mathematically distinct from the mean of paired ratios ($\frac{1}{R}\sum (t_{\text{MST}, r} / t_{\text{KM}, r})$). The ratio of means represents the expected aggregate relative workload and avoids non-linear distortions from individual tiny denominators. If the denominator is zero or below machine precision ($\le 10^{-12}$ ms), the ratio reports `None` / `N/A`.

---

## 4. Theoretical Complexity vs. Empirical Behavior

| Property | Lloyd's K-Means (Custom) | Dense Prim's MST (Custom) |
| :--- | :--- | :--- |
| **Algorithmic Nature** | Iterative centroid relocation | Graph-theoretic spanning tree growth |
| **Initialization Complexity** | $\mathcal{O}(k \cdot N \cdot D)$ (K-Means++ sampling) | $\mathcal{O}(N)$ (Root vertex selection) |
| **Iterative / Main Loop** | $\mathcal{O}(I \cdot N \cdot k \cdot D)$ ($I$ iterations) | $\mathcal{O}(N^2)$ (Dense vector distance relaxation) |
| **Cutting / Partitioning** | $\mathcal{O}(1)$ (Voronoi partitions implicit) | $\mathcal{O}(N \log N)$ (Sorting tree edges + DSU) |
| **Overall Asymptotic Complexity** | $\mathcal{O}(I \cdot N \cdot k \cdot D)$ (Linear in $N$) | $\mathcal{O}(N^2)$ (Quadratic in $N$) |
| **Empirical Growth Pattern** | Near-linear scaling curve | Parabolic (quadratic) scaling curve |

### Asymptotic Scaling Divergence
As sample size $N$ increases from 100 to 600:
- K-Means distance calculations scale as $2 \cdot N \cdot k$ per iteration.
- Dense Prim's MST evaluates all $\frac{N(N - 1)}{2}$ pairwise Euclidean distances across the complete graph.
- Consequently, the ratio of means ($\bar{t}_{\text{MST}} / \bar{t}_{\text{KM}}$) increases monotonically as $N$ grows, empirically demonstrating the asymptotic divergence between $\mathcal{O}(N)$ and $\mathcal{O}(N^2)$.

---

## 5. System and Environmental Dependencies

Empirical benchmarks depend directly on the execution environment:
1. **CPU Architecture:** Clock speed, instruction pipeline, SIMD vector extensions (AVX2/AVX-512), and L1/L2/L3 cache capacities directly impact vectorized distance computations.
2. **Operating System Scheduling:** Process priority, background tasks, and thermal throttling introduce variance across trials.
3. **NumPy Vectorization:** Array operations in `kmeans.py` and `mst.py` leverage compiled BLAS/C primitives, which run orders of magnitude faster than pure Python loops.
4. **No Universal Guarantee:** Results measured on a university lab workstation or cloud runner illustrate the empirical divergence of the implementations; they do not constitute a universal absolute execution speed guarantee across all platforms.
5. **Scientific Rigor:** Measured runtime curves illustrate empirical divergence consistent with theoretical complexity; they do not mathematically prove asymptotic bounds.

---

## 6. Safety Workload Limits

To guarantee that interactive benchmarks complete reliably in Streamlit Community Cloud and academic demonstration environments without memory exhaustion:
- **Maximum Observation Count:** $N \le 600$.
- **Maximum Repetitions:** $R \le 10$.
- **Maximum Total Executions:** $\text{Total Executions} \le 200$.
$$\text{Total Executions} = \left[(\text{warmup} ? 1 : 0) + R\right] \times |\{N\}| \times 2 \le 200$$

Workloads exceeding these bounds are rejected prior to execution.

---

## 7. Viva Demonstration Walkthrough

### Examiner Questions & Model Answers

**Q1: Why does Prim's MST scale quadratically $\mathcal{O}(N^2)$ while K-Means scales linearly $\mathcal{O}(N)$?**
> **Model Answer:** Custom Prim's MST operates on the complete Euclidean graph $G=(V, E)$ where $|V|=N$ and $|E|=\frac{N(N-1)}{2}$. Each of the $N$ steps updates a minimum-distance frontier across all remaining unvisited vertices, yielding $\mathcal{O}(N^2)$ total distance checks. Lloyd's K-Means calculates distances from $N$ points to only $k$ centroids per iteration, totaling $\mathcal{O}(I \cdot N \cdot k \cdot D)$. For fixed $k=3$ and small $D=2$, this scales strictly linearly with $N$.

**Q2: Why are dataset generation times excluded from the benchmark timer?**
> **Model Answer:** Including dataset generation would contaminate the measurement with PRNG sampling and NumPy array allocation overheads that have nothing to do with the clustering algorithms themselves. The goal is to measure the algorithmic throughput of Lloyd's iteration versus Prim's tree relaxation in isolation.

**Q3: Why report both the mean, median, and sample standard deviation?**
> **Model Answer:** In empirical computing, execution times are subject to OS interrupts, CPU context switches, and cache misses. The arithmetic mean measures expected overall workload; the median provides a robust central tendency resistant to transient CPU spikes; and the sample standard deviation (computed with Bessel's correction $ddof=1$) quantifies measurement dispersion across independent runs.

---

## 8. Export Integrity and Scientific Reproducibility

The platform supports exporting genuine trial records (`.csv`), aggregated summaries (`.csv`), runtime environment metadata (`.json`), and benchmark configuration (`.json`).

> [!IMPORTANT]
> **Reproducibility Scope of Benchmark JSON:**
> The exported `benchmark_config_*.json` serializes the benchmark configuration parameters (`BenchmarkConfig`), including dataset topology, sample sizes, repetition counts, geometric parameters, and the master random PRNG seed.
> Restoring this JSON file deterministically reproduces the **identical synthetic datasets, cluster centers, and trial execution order**.
> However, because execution time is an empirical physical measurement influenced by hardware architecture, operating system thread scheduling, CPU frequency scaling, and background memory activity, the benchmark JSON **does not and cannot guarantee reproduction of exact execution times (milliseconds)** across different runs or test machines. Scientific claims must report empirical scaling trends rather than machine-specific wall-clock latencies.
