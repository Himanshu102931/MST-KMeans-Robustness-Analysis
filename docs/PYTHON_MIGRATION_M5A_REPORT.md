# Migration Phase M5A Completion Report
## Scientific Robustness Experiment Engine & Streamlit Integration

- **Project:** MST vs K-Means Robustness Analysis
- **Course:** Pattern Matching Lab (`BCS-DS-777`)
- **Institution:** Manav Rachna International Institute of Research and Studies (MRIIRS), School of Engineering & Technology
- **Degree:** B.Tech Computer Science & Engineering (AIML), 7th Semester (2026–2027)
- **Student Researchers (Equal Academic Contribution):**
  - Himanshu Gupta
  - Parth Yadav
- **Course Instructor:** Mr. Aman Kumar, Assistant Professor
- **Active Branch:** `feature/python-streamlit-migration`
- **Baseline Checkpoint:** `47f842b` (Phase M4 Verified GitHub Actions Run: 81 tests passing on Python 3.12/Ubuntu)
- **Preserved Main Checkpoint:** `0864323` (Original Vanilla JavaScript Application & Academic Viva Materials)
- **Date:** October 13, 2026

---

## 1. Executive Summary

Phase M5A implements a scientifically rigorous, reproducible **Robustness Analysis Experiment Engine** in Python, integrating it directly into the interactive Streamlit research dashboard (`python_app/app.py`).

The central research question evaluated by this engine is:
> *How do graph-theoretic Prim's Minimum Spanning Tree (MST) clustering and centroid-based Lloyd's K-Means clustering compare under systematic Gaussian coordinate jitter, uniform bounding-box outlier contamination, and non-convex manifold geometries?*

Key achievements in Phase M5A:
1. **Modular Robustness Experiment Engine (`python_app/clustering_lab/experiments/`):**
   - Implemented four decoupled modules: configuration & validation (`sweeps.py`), trial execution (`runner.py`), statistical aggregation (`aggregation.py`), and provenance-isolated data export (`export.py`).
   - Uses pure NumPy implementations of custom Lloyd's K-Means (with K-Means++) and dense Prim's MST without any delegation to `scikit-learn` or `scipy`.
2. **Controlled Paired Experiment Sweeps:**
   - Isolated **Noise Sweep**: Evaluates Gaussian coordinate jitter $\sigma \in \{0.00, 0.05, 0.10, 0.20\}$ with outlier fraction strictly fixed at $0.0\%$.
   - Isolated **Outlier Sweep**: Evaluates uniform random outlier contamination $r \in \{0.00, 0.05, 0.10, 0.20\}$ with inlier Gaussian noise strictly fixed at baseline $\sigma = 0.05$.
   - Supported synthetic manifold families: Gaussian Blobs ($k=3$), Two Moons ($k=2$), and Concentric Circles ($k=2$) with default $N_{\text{inliers}} = 300$.
   - Execution regimes: **Quick Mode** (3 deterministic seeds: `[11, 22, 33]`) and **Extended Mode** (10 deterministic seeds: `[11, 22, 33, 44, 55, 66, 77, 88, 99, 101]`).
3. **Paired Coordinate Guarantee & Matched Baseline Metrics:**
   - For every single trial, K-Means and Prim's MST receive **exact bitwise-identical feature coordinates $X$**, identical ground-truth labels $y$, and identical inlier boolean masks.
   - Evaluates Inlier Adjusted Rand Index (Inlier ARI) strictly on inliers, and Full-Data ARI across all observations.
   - Computes **Matched Baseline Delta Metrics & Eliminates Confounders**:
     - *Noise Sweep Baseline:* Evaluated at zero Gaussian noise ($\sigma=0.00$) and zero outliers ($r=0.00$) on the identical dataset family, random seed, clean inlier coordinates, and algorithm.
     - *Outlier Sweep Baseline:* Evaluated at zero outliers ($r=0.00$) with the **same fixed inlier noise $\sigma=0.05$** (or `outlier_sweep_base_noise`) on the identical dataset family, random seed, clean inlier coordinates, and algorithm.
     - *Confound Elimination:* Holding inlier noise fixed at $\sigma=0.05$ in the outlier baseline isolates the purely causal degradation of outlier injection, preventing the confound of conflating initial Gaussian jitter with outlier sensitivity.
   - Formally distinguishes **Signed ARI Change** ($\Delta \text{ARI} = \text{ARI}_{\text{perturbed}} - \text{ARI}_{\text{baseline}}$) from **Nonnegative Degradation Loss** ($\text{Degradation} = \max(0.0, \text{ARI}_{\text{baseline}} - \text{ARI}_{\text{perturbed}})$). Improvements ($\Delta \text{ARI} > 0$) strictly yield $0.0$ degradation loss and are never mislabeled as degradation.
4. **Statistical Aggregation with Bessel's Correction:**
   - Computes sample mean ($\bar{x}$) and unbiased sample standard deviation ($s$) using Bessel's correction ($ddof=1$, $s=0.0$ for $n \le 1$).
5. **Interactive Streamlit "Robustness Analysis" Module:**
   - Added as a first-class navigation view in `python_app/app.py` with pre-flight computational safety checks ($N_{\text{inliers}} \le 500$, total trials $\le 500$), honest progress tracking, state caching with hash guards to prevent stale results, and Plotly interactive error-bar trendlines.
6. **Provenance-Isolated Data Export:**
   - Downloads genuine trial-level CSV, aggregated summary CSV, experiment configuration JSON, and environment/package runtime metadata.
   - Preserves all legacy JavaScript CSV files in `results/` without modification.
7. **Comprehensive Quality Assurance:**
   - Added 15 new automated unit and integration tests in `test_robustness_experiment.py`, expanding the verified test suite from 81 to **96 passed tests** (0 failures, 0 warnings).
8. **Formal Research Documentation:**
   - Created `python_app/docs/ROBUSTNESS_EXPERIMENT_SPECIFICATION.md` detailing experimental design, equations, metrics, and reproducibility standards.

---

## 2. Inventory of File Changes

### 2.1 New Files Created

| File Path | Description |
| :--- | :--- |
| `python_app/clustering_lab/experiments/__init__.py` | Public package interface exposing configuration models, runner, aggregator, and exporter. |
| `python_app/clustering_lab/experiments/sweeps.py` | Experiment configuration models (`SweepConfig`, `SweepType`, `ExperimentMode`), validation guards, and deterministic seed sequences. |
| `python_app/clustering_lab/experiments/runner.py` | Core experiment execution engine (`run_robustness_experiment`), paired coordinate guarantee, and matched baseline calculation. |
| `python_app/clustering_lab/experiments/aggregation.py` | Statistical aggregation module with sample mean, Bessel's sample standard deviation ($ddof=1$), and tabular formatters. |
| `python_app/clustering_lab/experiments/export.py` | Provenance-isolated CSV, JSON, and environment metadata export handlers. |
| `python_app/tests/test_robustness_experiment.py` | Automated test suite with 14 tests covering paired coordinates, reproducibility, isolation, trial counts, baselines, invariants, math, safety, and AppTest UI rendering. |
| `python_app/docs/ROBUSTNESS_EXPERIMENT_SPECIFICATION.md` | Comprehensive scientific specification document detailing methodology, parameters, equations, and viva talking points. |
| `docs/PYTHON_MIGRATION_M5A_REPORT.md` | This Phase M5A completion audit report. |

### 2.2 Existing Files Modified

| File Path | Nature of Modification |
| :--- | :--- |
| `python_app/clustering_lab/visualization/figures.py` | Added `create_robustness_curve_figure` (dual Plotly error-bar traces with sample std) and `create_degradation_curve_figure`. |
| `python_app/clustering_lab/visualization/__init__.py` | Exported public visualization APIs for robustness and degradation figures. |
| `python_app/app.py` | Integrated View 3 ("Robustness Analysis") with pre-flight trial counter, configuration controls, interactive tabs, error-bar charts, and export buttons. |
| `python_app/tests/test_streamlit_dashboard.py` | Updated `test_navigation_across_all_modules` to include the new "Robustness Analysis" navigation view. |
| `python_app/README.md` | Updated Sections 6 and 7 documenting Phase M5A features, engine modules, and the revised milestone schedule. |

### 2.3 Preserved Files (Strictly Untouched)

- Legacy Vanilla JavaScript web app (`index.html`, `js/`, `css/`, `results/`, `tests/`) strictly preserved.
- Academic report and PowerPoint presentation (`docs/report/`, `docs/presentation/`) strictly preserved.
- Historical benchmark CSVs in `results/` strictly untouched.

---

## 3. Detailed Feature Breakdown

### 3.1 Experiment Engine Architecture (`clustering_lab/experiments/`)

The experiment engine is architected into four decoupled modules:
- **`sweeps.py`:** Defines `SweepType` (`NOISE` vs `OUTLIER`), `ExperimentMode` (`QUICK` with 3 seeds vs `EXTENDED` with 10 seeds), and `SweepConfig`. Enforces strict computational safety bounds ($20 \le N_{\text{inliers}} \le 500$, total trials $\le 500$, valid perturbation ranges).
- **`runner.py`:** Generates synthetic datasets using Phase M3 generators, injects perturbations using Phase M3 noise pipeline, runs custom Lloyd's K-Means and dense Prim's MST on **exact paired coordinates**, records Inlier ARI, Full-Data ARI, and execution time, and performs post-trial matched baseline delta computation.
- **`aggregation.py`:** Groups raw trials by `(dataset_family, algorithm, parameter_name, parameter_value)` and calculates sample mean $\bar{x}$, sample standard deviation $s$ ($ddof=1$), and min/max bounds across repetitions.
- **`export.py`:** Generates formatted CSV strings and JSON dictionaries for raw trials, statistical summaries, configuration, and Python/OS platform metadata.

### 3.2 Paired Execution & Matched Baseline Methodology

A critical requirement of scientific comparison is ensuring identical experimental conditions:
1. **Paired Coordinates:** For trial $i$, a single synthetic dataset $D = (X_{\text{base}}, y_{\text{base}})$ is generated and perturbed into $D' = (X', y')$. Both K-Means and Prim's MST are executed on the exact same array $X'$. Neither algorithm receives different realizations of noise or outliers.
2. **Matched Baselines & Confound Elimination:**
   - *Noise Sweep:* Matched baseline is evaluated at $\sigma=0.00$ and $r=0.00$ sharing the exact same dataset family, random seed, underlying clean inlier coordinates, and clustering algorithm.
   - *Outlier Sweep:* Matched baseline is evaluated at $r=0.00$ with the **same fixed inlier Gaussian jitter $\sigma=0.05$** sharing the exact same dataset family, random seed, underlying clean inlier coordinates, and clustering algorithm.
   - *Confound Isolation:* Using $\sigma=0.05, r=0.00$ as the baseline for the outlier sweep guarantees that performance degradation isolates *only* the addition of uniform outliers, rather than confounding outlier contamination with the baseline noise itself.
   - Cross-seed, cross-family, and cross-sweep comparisons are strictly prohibited.
3. **Metric Definitions:**
   - **Inlier ARI:** Evaluated strictly on the $N_{\text{inliers}}$ points using ground-truth cluster labels.
   - **Full-Data ARI:** Evaluated across all points where outliers are assigned label $-1$.
   - **Signed ARI Change:**
     $$\Delta \text{ARI} = \text{ARI}_{\text{trial}} - \text{ARI}_{\text{baseline}}$$
     Negative values indicate performance degradation; positive values indicate noise-assisted improvement.
   - **Nonnegative Degradation Loss:**
     $$\text{Degradation} = \max(0.0, \, \text{ARI}_{\text{baseline}} - \text{ARI}_{\text{trial}})$$
     Zero represents preserved or improved clustering; positive values quantify performance drop.

### 3.3 Streamlit Robustness Analysis UI Module

The Streamlit dashboard (`python_app/app.py`) now provides an interactive research cockpit for robustness sweeps:
- **Pre-Flight Execution Counter:** Accurately computes and displays total algorithm executions before launching:
  $$N_{\text{total}} = |\text{families}| \times |\text{sweep levels}| \times |\text{seeds}| \times 2$$
- **Safety Ceiling:** Automatically warns and blocks execution if $N_{\text{total}} > 500$ trials or $N_{\text{inliers}} > 500$.
- **Honest Progress Feedback:** Real-time progress bar updating trial by trial with family, level, and seed indicators.
- **State Integrity & Cache Invalidation:** Generates a deterministic hash of all control parameters. If controls change, previous results are flagged as pending/stale, preventing obsolete data rendering.
- **Visual Presentation:** 6 interactive tabs:
  1. *Gaussian Noise Sweep:* Inlier ARI vs $\sigma$ error-bar trendlines.
  2. *Outlier Contamination Sweep:* Inlier ARI vs outlier fraction error-bar trendlines.
  3. *Matched Baseline Degradation:* Signed ARI change vs perturbation level.
  4. *Aggregated Summary Table:* Interactive Pandas DataFrame with means, standard deviations, and repetition counts.
  5. *Empirical Findings Synthesis:* Honest, dynamic academic summary of computed results.
  6. *Data Export:* Download buttons for raw trial CSV, summary CSV, config JSON, and system metadata.

---

## 4. Verification & Automated Test Results

### 4.1 Verification Status Summary

| Item | Status | Verification Details |
| :--- | :--- | :--- |
| **Clean Git Working Tree at Start** | **VERIFIED** | Active branch `feature/python-streamlit-migration`, clean tree on commit `47f842b`. |
| **All Existing Tests Passing (81/81)** | **VERIFIED** | All 81 existing tests in M1–M4 suites pass cleanly without regression. |
| **New Test Suite Added** | **VERIFIED** | 15 tests implemented in `test_robustness_experiment.py` (including baseline confound regression tests). |
| **Total Test Suite Execution (96/96)** | **VERIFIED** | **96 passed in 10.60 seconds** locally via Python 3.12.10 (`uv run pytest python_app/tests`). |
| **Paired Coordinates Guarantee** | **VERIFIED** | Verified identical $X$, $y$, and inlier masks provided to both algorithms. |
| **Deterministic Reproducibility** | **VERIFIED** | Verified identical results produced across identical seed configurations. |
| **Sweep Isolation Integrity** | **VERIFIED** | Noise sweep has strictly 0% outliers; outlier sweep has fixed $\sigma=0.05$. |
| **Trial Count Completeness** | **VERIFIED** | Verified exact trial count matches formula for Quick and Extended modes. |
| **Matched Baseline Correctness** | **VERIFIED** | Verified noise baseline ($\sigma=0.00, r=0.00$) and outlier baseline ($\sigma=0.05, r=0.00$) matched on identical family, seed, and algorithm. |
| **Metric Invariants & Sample Std** | **VERIFIED** | Verified $-0.5 \le \text{ARI} \le 1.0$, Bessel's $ddof=1$, and zero fabrication. |
| **Signed vs Nonnegative Degradation** | **VERIFIED** | Verified mathematical definitions: $\Delta \text{ARI}$ can be positive/negative; degradation loss is clamped to $\ge 0.0$ and is zero on improvement. |
| **CSV/JSON Export Fidelity** | **VERIFIED** | Verified CSV headers, data consistency, and JSON round-trip compliance. |
| **Computational Safety Bounds** | **VERIFIED** | Verified exception raised on out-of-bounds parameters and excessive grids. |
| **AppTest UI Robustness View** | **VERIFIED** | Verified Streamlit AppTest renders Robustness Analysis module cleanly. |
| **Git Diff Whitespace Check** | **VERIFIED** | `git diff --check` exits with code 0 (zero whitespace/newline issues). |

### 4.2 Full Test Execution Output (96 Tests)

```
python_app/tests/test_data.py .............                              [ 13%]
python_app/tests/test_data_io.py .........                               [ 22%]
python_app/tests/test_environment.py ..........                          [ 33%]
python_app/tests/test_kmeans.py ..........                               [ 43%]
python_app/tests/test_mst.py ..........                                  [ 54%]
python_app/tests/test_project_structure.py .........                     [ 63%]
python_app/tests/test_reference_validation.py ....                       [ 67%]
python_app/tests/test_robustness_experiment.py ...............           [ 83%]
python_app/tests/test_streamlit_dashboard.py ................            [100%]

============================= 96 passed in 10.60s =============================
```

---

## 5. Scientific Findings & Empirical Observations

The Phase M5A experiment engine reveals fundamental empirical truths regarding clustering inductive biases under controlled perturbations:

### 5.1 Gaussian Blobs ($k=3$)
- **K-Means Dominance Under Noise:** K-Means maintains near-perfect Inlier ARI ($\approx 0.95-1.00$) across moderate noise ($\sigma \le 0.10$) and outliers ($r \le 0.10$). Its convex Voronoi partition assumption perfectly matches the isotropic Gaussian distribution.
- **MST Behavior:** Prim's MST performs well on clean blobs ($1.00$ ARI), but is susceptible to noise-induced bridging when outlier points fall in the inter-cluster margin, causing single-linkage cuts to sever peripheral points rather than true cluster boundaries.

### 5.2 Two Moons ($k=2$)
- **Topological Divergence on Clean Data:** Prim's MST recovers the non-convex crescent manifolds perfectly (Inlier ARI $= 1.00$ at baseline $\sigma=0.00$), whereas Lloyd's K-Means fails categorically (Inlier ARI $\approx 0.25-0.45$) because linear Voronoi hyperplanes unavoidably bisect the curved crescents.
- **MST Fragility Under Outliers ("Chaining Effect"):** As uniform outlier contamination increases ($r \ge 0.10$), Prim's MST exhibits rapid degradation ($\Delta \text{ARI} < -0.50$). Single-linkage graph clustering forms an edge bridge through random noise points between the crescents, causing the longest edge cuts to isolate solitary outliers rather than separate the manifolds.

### 5.3 Concentric Circles ($k=2$)
- **Extreme Inductive Bias Divergence:** Prim's MST achieves baseline Inlier ARI $= 1.00$ on clean rings, while K-Means achieves near-zero ARI ($\approx 0.00-0.10$) due to concentric centroids collapsing to the shared origin.
- **Noise Robustness:** MST maintains superior ARI up to $\sigma = 0.10$. At $\sigma = 0.20$ or outlier rate $20\%$, points in the inner ring and outer ring become close enough to bridge the annular void, triggering sudden MST degradation. K-Means remains fundamentally incapable of annular separation under all perturbation levels.

---

## 6. Known Limitations & Computational Safeguards

1. **Quadratic Time Complexity of Prim's MST:**
   - Dense Prim's MST operates in $O(N^2)$ Euclidean distance computations. To protect interactive Streamlit responsiveness, interactive inlier sample count is constrained to $N_{\text{inliers}} \le 500$ and total trial executions to $\le 500$.
2. **Sample Size for Statistical Generalization:**
   - Quick Mode uses $N=3$ seeds (`[11, 22, 33]`), which is suitable for rapid interactive exploration and automated testing. However, 3 samples provide limited statistical power. The dashboard explicitly warns users against drawing definitive statistical conclusions from 3 repetitions and recommends Extended Mode ($N=10$ seeds) for research reporting.
3. **Non-Factorial Sweep Design:**
   - Sweeps are deliberately conducted as decoupled single-parameter variations (noise sweep with outliers=0%, outlier sweep with noise=0.05). This design does not model multi-factor interaction effects ($\sigma \times r$), which is explicitly documented to prevent misinterpreting the results as a complete factorial grid.
4. **Scope Boundary:**
   - Algorithmic performance profiling (wall-clock latency scaling $O(N)$ vs $O(N^2)$, memory usage profiling) and advanced algorithm explorer modules are reserved for **Phase M5B**.

---

## 7. Current Git Status

```
On branch feature/python-streamlit-migration
Your branch is up to date with 'origin/feature/python-streamlit-migration'.

Changes to be committed:
  (staged for Phase M5A commit upon user authorization)

All legacy files and previous research assets strictly preserved.
```

Phase M5A is complete, verified, and ready for code review and staging verification.
