# Migration Phase M5B Completion Report
## Python Performance Benchmarks, Algorithm Explorers & Research Exports

- **Project:** MST vs K-Means Robustness Analysis
- **Course:** Pattern Matching Lab (`BCS-DS-777`)
- **Institution:** Manav Rachna International Institute of Research and Studies (MRIIRS), School of Engineering & Technology (SET)
- **Degree:** B.Tech Computer Science & Engineering (AIML), 7th Semester (Academic Session: 2026–2027)
- **Student Researchers (Equal Academic Contribution):**
  - Himanshu Gupta
  - Parth Yadav
- **Course Instructor:** Mr. Aman Kumar, Assistant Professor
- **Active Git Branch:** `feature/python-streamlit-migration`
- **Baseline Verified Checkpoint:** `06582d6` (Phase M5A verified commit; 96 tests passed in 4.34s on Python 3.12 / Ubuntu CI)
- **Preserved Main Checkpoint:** `0864323` (Original Vanilla JavaScript Application & Historical Research Artifacts)
- **Date:** October 13, 2026

---

## 1. Executive Summary

Phase M5B advances the scientific capabilities of the Python research platform by introducing:
1. **A Rigorous Python Performance Benchmark Engine:** Execution-time measurement of the actual custom Lloyd's K-Means and dense Prim's MST clustering implementations across systematic sample sizes ($N \in \{100, 200, 400, 600\}$) with paired inputs, nanosecond monotonic timing, warm-up exclusion, and Bessel-corrected sample statistics.
2. **Interactive Algorithm Explorers:** Step-by-step visual pedagogical traces for both Lloyd's K-Means (K-Means++ initialization, Voronoi assignment, centroid relocation, inertia) and dense Prim's MST (root vertex, greedy minimum cut edge selection, cut of $k-1$ longest edges, connected component partition), with guaranteed 100% mathematical parity against production algorithms.
3. **Scientific Figure & Data Export Engine:** Provenance-isolated CSV exports (raw trials, aggregated summaries), configuration/metadata JSON exports, and verified in-memory Matplotlib PNG chart generation (yielding valid `b'\x89PNG'` binary payloads without filesystem pollution).
4. **Interactive Streamlit Integration:** Integrated two dedicated first-class views ("Performance Benchmarks" and "Algorithm Explorer") in `python_app/app.py` with preflight safety limit enforcement ($\le 200$ executions, $N \le 60$ for explorer), state-caching hash guards, responsive 1:1 Plotly visualizations, and comprehensive theoretical complexity explanations.
5. **Comprehensive Automated Test Coverage:** Implemented 27 new unit and integration tests across `test_benchmarks.py` and `test_algorithm_explorer.py`, expanding the verified test suite from 96 to **123 tests passing with 0 failures** in ~15 seconds.

---

## 2. Inventory of File Changes

### 2.1 New Files Created

| File Path | Description |
| :--- | :--- |
| `python_app/clustering_lab/experiments/benchmarks.py` | Benchmark configuration dataclass (`BenchmarkConfig`), trial recorder (`BenchmarkTrialResult`), statistical summary aggregator (`BenchmarkSummary`), and execution engine (`run_performance_benchmark`). |
| `python_app/clustering_lab/algorithms/explorer.py` | Step-by-step educational trace generators (`run_kmeans_trace`, `run_mst_trace`), immutable step containers (`KMeansTraceStep`, `MSTTraceStep`), and mathematical parity verifier against production implementations. |
| `python_app/tests/test_benchmarks.py` | Automated test suite for benchmarks: trial counts, paired coordinates, monotonic non-negative timings, sample statistics, ratio formulas, export integrity, and Streamlit UI rendering. |
| `python_app/tests/test_algorithm_explorer.py` | Automated test suite for algorithm explorers: trace step chronology, initialization invariants, centroid updates, MST edge counts, cut edge counts, component partitions, and production parity verification. |
| `python_app/docs/PERFORMANCE_BENCHMARK_SPECIFICATION.md` | Formal specification document detailing benchmarking methodology, monotonic timing, statistical definitions, complexity analysis, and hardware dependencies. |
| `python_app/docs/ALGORITHM_EXPLORER_GUIDE.md` | Comprehensive educational guide explaining the step-by-step tracing logic, mathematical invariants, viva demonstration script, and FAQ. |
| `docs/PYTHON_MIGRATION_M5B_REPORT.md` | This Phase M5B completion audit report. |

### 2.2 Existing Files Modified

| File Path | Nature of Modification |
| :--- | :--- |
| `python_app/app.py` | Integrated View 3 ("Algorithm Explorer") and View 4 ("Performance Benchmarks"), expanded navigation router to 8 views, implemented preflight execution limits, state invalidation guards, and export controls. |
| `python_app/clustering_lab/algorithms/kmeans.py` | Added `@property def centroids` to `KMeansResult` for unified access with explorer trace representations. |
| `python_app/clustering_lab/algorithms/mst.py` | Added `@property def total_weight` to `MSTClusteringResult` for unified access with explorer trace representations. |
| `python_app/clustering_lab/algorithms/__init__.py` | Exported `run_kmeans_trace`, `run_mst_trace`, `KMeansTraceStep`, `KMeansTraceResult`, `MSTTraceStep`, and `MSTTraceResult`. |
| `python_app/clustering_lab/data/synthetic.py` | Filtered kwargs in `generate_synthetic_dataset` for non-convex geometries (moons, circles) so passing `n_clusters` avoids `TypeError`. |
| `python_app/clustering_lab/experiments/export.py` | Implemented benchmark export functions (`export_benchmark_trials_to_csv`, `export_benchmark_summary_to_csv`, `export_benchmark_config_json`, `export_benchmark_metadata`). |
| `python_app/clustering_lab/experiments/__init__.py` | Exported benchmark public models, execution functions, and export routines. |
| `python_app/clustering_lab/visualization/figures.py` | Added Plotly visualizers (`create_benchmark_runtime_figure`, `create_kmeans_explorer_figure`, `create_mst_explorer_figure`) and in-memory Matplotlib PNG exporters (`render_benchmark_png`, `render_clustering_png`). |
| `python_app/clustering_lab/visualization/__init__.py` | Exported public visualization routines for explorer and benchmark figures. |
| `python_app/README.md` | Updated Section 3 directory tree, Section 6 navigation module organization (8 modules), and Section 7 implementation status. |

### 2.3 Strictly Preserved Files (Untouched)

- Legacy Vanilla JavaScript web app (`index.html`, `js/`, `css/`, `results/`, `tests/`) strictly preserved.
- Academic report and PowerPoint presentation (`docs/report/`, `docs/presentation/`) strictly preserved (the academic report remains ON HOLD).
- Historical JavaScript benchmark CSVs in `results/` strictly untouched.

---

## 3. Performance Benchmark Engine Methodology

### 3.1 High-Resolution Monotonic Timing
Execution time is measured using `time.perf_counter_ns()`, the highest-resolution monotonic clock available in Python. Monotonic timing ensures immunity against system clock adjustments, NTP updates, or daylight saving time shifts. Nanosecond integers are converted to floating-point milliseconds:
$$\text{latency (ms)} = \frac{\text{elapsed\_ns}}{1{,}000{,}000.0}$$

### 3.2 Paired Execution & Overhead Decoupling
To eliminate experimental confounds:
1. **Dataset Synthesis Outside Timed Region:** Synthetic Gaussian Blobs datasets are generated prior to starting the timer. Coordinate synthesis, memory allocation for ground-truth arrays, and random jitter addition are strictly excluded from algorithm runtime.
2. **Identical Coordinated Input Arrays:** For each repetition, the identical bitwise coordinate matrix $X \in \mathbb{R}^{N \times 2}$ is passed to both custom algorithms.
3. **No UI or Rendering Overhead:** Streamlit widget lifecycles, DOM updates, and Plotly figure serialization are measured separately and never incorporated into algorithm runtime.
4. **Separate Warm-up Stage:** An optional small warm-up run ($N=50$) is executed prior to measurement to trigger Python bytecode compilation, CPU branch predictor warming, and dynamic memory suballocations. Warm-up measurements are strictly excluded from all reported trial statistics.
5. **No Delegation to External Libraries:** Custom NumPy implementations of Lloyd's K-Means (`kmeans()`) and dense Prim's MST (`mst_clustering()`) are benchmarked directly. No calls to `sklearn.cluster.KMeans` or `scipy.sparse.csgraph` are made.

### 3.3 Default Benchmark Matrix & Preflight Safety Guards
- **Dataset Family:** Gaussian Blobs with $k=3$, cluster dispersion $\sigma=0.08$, bounded in $[-2, 2]^2$.
- **Sample Sizes ($N$):** $N \in \{100, 200, 400, 600\}$.
- **Repetitions:** Default 5 measured repetitions per sample size across distinct deterministic seeds ($[42, 43, 44, 45, 46]$).
- **Preflight Workload Enforcement:**
  $$\text{Total Executions} = |N_{\text{sizes}}| \times \text{repetitions} \times 2 \le 200$$
  If user controls exceed 200 total executions, the engine halts preflight with a clear scientific safety error to prevent resource exhaustion on Streamlit Community Cloud.

---

## 4. Benchmark Statistics & Theoretical Complexity

### 4.1 Statistical Formulas
For $R$ repetitions of an algorithm on sample size $N$:
1. **Sample Mean Runtime:**
   $$\bar{t} = \frac{1}{R} \sum_{r=1}^{R} t_r$$
2. **Sample Median Runtime:**
   $$\tilde{t} = \begin{cases} t_{(\frac{R+1}{2})}, & R \text{ odd} \\ \frac{1}{2}\left(t_{(\frac{R}{2})} + t_{(\frac{R}{2}+1)}\right), & R \text{ even} \end{cases}$$
3. **Sample Standard Deviation with Bessel's Correction ($ddof=1$):**
   $$s = \sqrt{\frac{1}{R-1} \sum_{r=1}^{R} (t_r - \bar{t})^2} \quad (s = 0.0 \text{ for } R \le 1)$$
   *Mathematical Distinction (Unbiased Variance vs. Sample Standard Deviation):* Dividing the sum of squared deviations by $R-1$ (Bessel's correction, $ddof=1$) yields an **unbiased estimator of population variance** ($s^2$, satisfying $\mathbb{E}[s^2] = \sigma^2$). However, because the square root is strictly concave, Jensen's inequality implies $\mathbb{E}[s] = \mathbb{E}[\sqrt{s^2}] \le \sqrt{\mathbb{E}[s^2]} = \sigma$. Thus, the sample standard deviation $s = \sqrt{s^2}$ is **not** strictly an unbiased estimator of population standard deviation $\sigma$ (it slightly underestimates $\sigma$ in finite samples). Bessel's correction reduces small-sample bias and is standard scientific convention, but should not be conflated with the exact unbiasedness of sample variance $s^2$.
4. **Ratio of Means:**
   $$\text{ratio\_of\_means} = \frac{\bar{t}_{\text{MST}}}{\bar{t}_{\text{K-Means}}}$$
   *Zero-Denominator Guard:* If $\bar{t}_{\text{K-Means}} \le 0$ or invalid, the ratio yields `None` / `N/A` rather than an invented or infinite quantity.
   *Methodological Precision:* We explicitly distinguish the **ratio of means** ($\bar{t}_{\text{MST}} / \bar{t}_{\text{KM}}$) from the **mean of paired ratios** ($\frac{1}{R} \sum \frac{t_{\text{MST},r}}{t_{\text{KM},r}}$) and the **ratio of medians** ($\tilde{t}_{\text{MST}} / \tilde{t}_{\text{KM}}$).

### 4.2 Asymptotic Complexity Analysis
| Algorithm | Theoretical Time Complexity | Working Space Complexity | Dominant Computational Operation |
| :--- | :--- | :--- | :--- |
| **Lloyd's K-Means** | $\mathcal{O}(I \cdot N \cdot k \cdot D)$ | $\mathcal{O}(N \cdot D + k \cdot D)$ | Iterative pairwise Voronoi distance matrix broadcasting and centroid arithmetic updates. |
| **Dense Prim's MST** | $\mathcal{O}(N^2)$ | $\mathcal{O}(N)$ distance tracking vectors | Greedy linear relaxation of unvisited vertex distances via vectorized Euclidean vector evaluation. |

*Academic Caveat:* Measured runtime curves reflect hardware architecture, cache locality, Python bytecode overhead, and NumPy C-vectorization efficiency. Measured runtime curves illustrate empirical execution behavior on the test host and do not mathematically prove asymptotic bounds.

---

## 5. Algorithm Explorers & Mathematical Parity

### 5.1 Lloyd's K-Means Algorithm Explorer
The K-Means explorer provides an interactive step-by-step trace of Lloyd's iteration:
- **Step 0:** Initial state displaying clean unassigned coordinates (labels set to $-1$).
- **Steps $1 \dots k$:** K-Means++ initialization phase. Centroid 1 is placed deterministically, and centroids $2 \dots k$ are selected sequentially with probability proportional to squared Euclidean distances $D(x)^2$.
- **Subsequent Iterations ($i = 1 \dots I$):**
  - **Assignment Substep:** Each observation $x_i$ is mapped to its nearest centroid $c_j$ under Euclidean metric ($z_i = \arg\min_j \|x_i - c_j\|_2^2$), forming Voronoi partition cells.
  - **Update Substep:** Centroids are relocated to the arithmetic centroid mean of their assigned points ($c_j = \frac{1}{|S_j|} \sum_{x \in S_j} x$).
  - **Convergence & Inertia:** Tracks Within-Cluster Sum of Squares (Inertia / WCSS). Iteration halts when centroid relocation shift falls below convergence tolerance $\varepsilon = 10^{-4}$ or maximum iterations are exhausted.

### 5.2 Dense Prim's MST Algorithm Explorer
The MST explorer traces greedy Euclidean minimum spanning tree growth:
- **Step 0:** Root vertex selection (vertex index 0 is added to tree set $V_{\text{tree}}$).
- **Steps $1 \dots N-1$:** Spanning tree growth. At each step, the greedy minimum-weight cut edge connecting an in-tree vertex to an unvisited vertex is added:
  $$e^* = \arg\min_{u \in V_{\text{tree}},\, v \notin V_{\text{tree}}} \|x_u - x_v\|_2$$
- **Completed Spanning Tree:** Displays all $N-1$ selected MST edges with edge lengths.
- **Cutting Longest Edges ($k-1$ steps):** The $k-1$ edges with largest Euclidean weights are identified and severed.
- **Final Connected Components:** Disjoint Set Union (DSU / Union-Find) traverses remaining edges to assign discrete cluster partition labels $0 \dots k-1$.

### 5.3 Exact Parity Verification Proof
To guarantee pedagogical integrity, the explorer trace engines do not approximate or alter clustering behavior:
- `run_kmeans_trace()` matches production `kmeans()` to machine precision on final cluster labels, final centroids, iteration count, and inertia invariant.
- `run_mst_trace()` matches production `mst_clustering()` exactly on total MST weight, selected $N-1$ tree edges, cut $k-1$ edges, and final component labels.
- Verified automatically by automated tests in `test_algorithm_explorer.py` across Blobs, Moons, and Circles geometries.

---

## 6. Scientific Data & Figure Exports

The platform enables direct download of genuine research artifacts without writing temporary files to the host server disk:
1. **Raw Benchmark Trials CSV (`benchmark_trials_*.csv`):** Per-trial observations containing trial ID, sample size $N$, repetition index, random seed, K-Means runtime (ms), MST runtime (ms), paired runtime ratio, K-Means inertia, and total MST weight.
2. **Aggregated Summary CSV (`benchmark_summary_*.csv`):** Sample size, repetition count, mean, median, sample std ($ddof=1$), min, max for both algorithms, and ratio of means.
3. **Benchmark Configuration JSON (`benchmark_config_*.json`):** Complete serializable parameter state enabling exact benchmark replay. *Reproducibility Scope:* Serializes configuration parameters and random seeds, guaranteeing deterministic recreation of identical synthetic datasets and execution sequences, but **not exact execution times**, which naturally vary across different hardware architectures, operating systems, and CPU load conditions.
4. **Environment & Package Metadata JSON (`benchmark_env_*.json`):** Documents OS platform, Python runtime version, NumPy/Pandas/SciPy/Streamlit package versions, high-resolution timer (`time.perf_counter_ns`), and academic provenance.
5. **Publication-Ready Matplotlib PNG Charts:** In-memory BytesIO generation of 2D clustering scatter plots and benchmark scaling curves. Headers start strictly with `b'\x89PNG\r\n\x1a\n'`, avoiding dependencies on external headless browser utilities (e.g. `kaleido`).

---

## 7. Automated Test Suite Results

All tests were executed locally against Python 3.12 via `uv`:
```bash
uv run --python "C:\Users\himan\AppData\Local\Python\pythoncore-3.12-64\python.exe" --with-requirements python_app/requirements-dev.txt pytest python_app/tests -v
```

### 7.1 Test Execution Summary
- **Baseline Tests (M1 to M5A):** 96 passed
- **New Benchmark Tests (`test_benchmarks.py`):** 11 passed
- **New Explorer Tests (`test_algorithm_explorer.py`):** 16 passed
- **Total Tests Passed:** **123 passed in 15.90 seconds** (100% pass rate, 0 failures, 0 warnings, 0 regressions)

### 7.2 Breakdown of New Test Suites
1. **`python_app/tests/test_benchmarks.py` (11 tests):**
   - `test_benchmark_config_defaults_and_validation`: verifies default sample sizes, repetition limits, and safety bound rejection.
   - `test_paired_benchmark_receives_identical_coordinate_arrays`: confirms identical feature coordinates passed to both algorithms.
   - `test_runtimes_are_finite_and_nonnegative`: validates monotonic clock outputs.
   - `test_warmup_excluded_from_trial_statistics`: ensures warm-up does not inflate measured trial counts.
   - `test_sample_statistics_and_bessel_correction`: verifies mean, median, min, max, and sample std ($ddof=1$).
   - `test_ratio_of_means_formula_and_zero_division_guard`: validates ratio equation and zero-denominator safety.
   - `test_benchmark_exports_integrity`: checks CSV formatting, column presence, and JSON round-trip fidelity.
   - `test_environment_metadata_provenance`: verifies metadata structure and package version reporting.
   - `test_deterministic_reproducibility_with_fixed_seeds`: checks dataset coordinate determinism.
   - `test_in_memory_benchmark_png_render`: verifies valid PNG magic byte signature `b'\x89PNG'`.
   - `test_streamlit_benchmark_view_apptest`: validates UI rendering and preflight counter updates via Streamlit `AppTest`.
2. **`python_app/tests/test_algorithm_explorer.py` (16 tests):**
   - `test_kmeans_trace_step_chronology_and_invariants`: validates Step 0 unassigned coordinates through convergence.
   - `test_kmeans_trace_exact_parity_with_production`: verifies 100% label and centroid parity with `kmeans()`.
   - `test_kmeans_trace_fixed_seed_determinism`: confirms reproducible traces under fixed seeds.
   - `test_kmeans_trace_inertia_monotonicity_or_bound`: verifies final inertia invariant.
   - `test_kmeans_trace_handles_small_and_boundary_datasets`: verifies $k=1$ and small $N$ edge cases.
   - `test_mst_trace_step_chronology_and_edge_growth`: verifies greedy single-edge addition per step.
   - `test_mst_trace_exact_n_minus_one_edges_and_weight`: checks tree edge count and total weight.
   - `test_mst_trace_k_minus_one_cuts_and_components`: verifies exactly $k-1$ cuts and $k$ discrete clusters.
   - `test_mst_trace_exact_parity_with_production`: proves 100% edge and partition parity with `mst_clustering()`.
   - `test_mst_trace_deterministic_tie_breaking`: verifies deterministic edge selection for equidistant points.
   - `test_mst_trace_on_non_convex_geometries`: tests Moons and Circles non-convex manifold tracing.
   - `test_explorer_dataset_size_guard`: validates safety ceiling ($N \le 60$) for interactive tracing.
   - `test_in_memory_clustering_png_render`: checks valid PNG header generation.
   - `test_streamlit_algorithm_explorer_view_apptest`: validates UI controls, step slider, and parity cards via `AppTest`.
   - `test_explorer_reset_and_state_consistency`: verifies parameter changes invalidate stale traces.
   - `test_explorer_parity_card_displays_verified`: confirms UI displays mathematical parity badge.

---

## 8. Manual Verification & Demonstration Guide

To launch and inspect the application:
```bash
streamlit run python_app/app.py
```

### 8.1 Performance Benchmarks Demonstration
1. Navigate to **"Performance Benchmarks"** in the sidebar.
2. Review the preflight workload estimate (e.g., "4 sample sizes x 5 repetitions x 2 algorithms = 40 executions (Well within limit of 200)").
3. Click **"Run Performance Benchmarks"**.
4. Observe the live progress bar and execution status updates.
5. Inspect the resulting Plotly dual-line runtime scaling curves with sample standard deviation error bars.
6. Review the summary statistics table showing Mean, Median, Std Dev, Min, Max, and Ratio of Means ($\bar{t}_{\text{MST}} / \bar{t}_{\text{KM}}$).
7. Download and inspect the exported trial CSV, summary CSV, and configuration JSON.

### 8.2 Algorithm Explorer Demonstration
1. Navigate to **"Algorithm Explorer"** in the sidebar.
2. Select **"Lloyd's K-Means"**, choose Gaussian Blobs ($N=30$, $k=3$, Seed=42), and generate the trace.
3. Step through using **"Next Step >"** or the step slider:
   - Observe Step 0 (gray unassigned observations).
   - Observe Steps 1 to 3 ($k$ initial centroids placed via K-Means++ $D(x)^2$ sampling).
   - Observe assignment and update iterations with Voronoi colors and red centroid markers.
   - Note the mathematical parity confirmation badge matching production results.
4. Switch to **"Prim's MST"**, select Two Moons ($N=30$, $k=2$, Seed=42), and generate the trace.
5. Step through:
   - Observe root vertex initialization.
   - Watch tree edges grow one by one across the manifold without crossing cluster gaps.
   - Observe the final $k-1=1$ longest edge cut highlighted in dashed red.
   - Observe final single-linkage cluster recovery matching the ground-truth manifold geometry.

---

## 9. Known Limitations & Academic Caveats

1. **Host-Specific Execution Timings:** Runtimes are sensitive to CPU thermal throttling, OS background processes, and Python virtual environment performance. Timing results should be interpreted as empirical comparative trends rather than universal hardware guarantees.
2. **Interactive Explorer Data Limits:** The explorer traces are capped at $N \le 60$ observations. Tracing larger datasets produces visual edge clutter and degrades browser canvas responsiveness without pedagogical benefit.
3. **No Dynamic Autoplay Timer:** Manual step navigation (First, Prev, Slider, Next, Last, Reset) is intentionally employed over timer-based autoplay loops to prevent Streamlit session state race conditions and UI flickering.

---

## 10. Git Status & Strict Stop Conditions

- **Active Branch:** `feature/python-streamlit-migration`
- **Working Tree Cleanliness:** `git diff --check` executed with **0 whitespace errors and 0 EOF warnings**.
- **Report Status:** Completed without modifying legacy JavaScript code or existing academic report/presentation files.
- **Strict Stop Condition:** Stopped cleanly after Phase M5B completion. Awaiting user instruction before staging, committing, pushing, or proceeding to Phase M5C.
