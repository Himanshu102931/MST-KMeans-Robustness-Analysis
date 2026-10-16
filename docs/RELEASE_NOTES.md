# MST vs K-Means Robustness Analysis — v1.0.0-final Release Candidate
## Comprehensive Release Notes and Academic Technical Handoff Guide

> [!WARNING]
> **DRAFT — NOT YET TAGGED OR DEPLOYED AS FINAL RELEASE**
> This document represents the Stage 07 candidate release documentation and academic handoff package. Release version tag `v1.0.0-final`, remote push to GitHub, and live production deployment synchronization remain **PENDING EXPLICIT PROJECT OWNER AUTHORIZATION**.

---

## 1. Project Identity and Academic Attribution

- **Project Title:** Quantitative Evaluation of Graph-Theoretic vs Centroid-Based Clustering Under Geometric and Contamination Perturbations
- **Academic Course:** Pattern Matching Lab (`BCS-DS-777`)
- **Degree Program:** B.Tech Computer Science & Engineering (Artificial Intelligence & Machine Learning)
- **Academic Year / Semester:** 7th Semester (Academic Year 2026–2027)
- **Institution:** School of Engineering & Technology, Manav Rachna International Institute of Research and Studies (MRIIRS), Faridabad, India
- **Faculty Guide / Course Instructor:** **Mr. Aman Kumar**, Assistant Professor
- **Student Researchers (Equal Academic Contribution):**
  - **Himanshu Gupta**
  - **Parth Yadav**
- **Repository:** [https://github.com/Himanshu102931/MST-KMeans-Robustness-Analysis](https://github.com/Himanshu102931/MST-KMeans-Robustness-Analysis)
- **Development Branch:** `feature/python-streamlit-migration`
- **Preserved Main Baseline:** Commit `0864323` (`Phase 6C: Final presentation, viva and demo materials`)
- **Target Release Version:** `v1.0.0-final` (Candidate)
- **Document Date:** October 16, 2026

*Privacy Compliance Notice:* Institutional student registration numbers and allocation identifiers are strictly excluded from all public-facing dashboards, figures, exported datasets, and publication release documentation.

---

## 2. Release Purpose and Scientific Research Objectives

This release candidate consolidates the complete migration of the **MST vs K-Means Robustness Analysis Laboratory** into a production-grade Python research platform. The platform is designed to investigate the fundamental theoretical and empirical divergence between two canonical clustering paradigms:

1. **Centroid-Based Inductive Bias (Lloyd's K-Means with K-Means++):**
   Implicitly assumes compact, convex, isotropic, and linearly separable clusters. Evaluates partition boundaries via Euclidean distance minimization to arithmetic cluster centroids (Voronoi partitioning).
2. **Graph-Theoretic Inductive Bias (Dense Prim's Euclidean Minimum Spanning Tree):**
   Implicitly assumes manifold connectivity based on local geometric proximity. Identifies natural topological clusters by deleting the $k-1$ longest edges in the Euclidean spanning tree (single-linkage graph partitioning).

### Scientific Research Questions Investigated
- **Topological Manifold Curvature:** How do non-convex geometric structures (interlocking Two Moons crescents, concentric rings) expose the intrinsic failure modes of linear hyperplane partitioning?
- **Outlier Contamination Stress:** At what contamination rate ($\epsilon$) of uniform bounding-box noise does single-linkage graph connectivity experience catastrophic breakdown ("chaining" and "outlier isolation")?
- **Continuous Gaussian Jitter:** How does continuous coordinate perturbation ($\sigma$) affect centroid stability versus spanning tree topology when evaluated on genuine inliers versus the contaminated dataset?
- **Computational Scaling:** How does dense Prim distance array relaxation ($\mathcal{O}(N^2)$) compare to Lloyd's iterations ($\mathcal{O}(N \cdot k \cdot I \cdot D)$) under empirical CPU execution?

---

## 3. Platform Architecture and Supported Modules

The platform is deployed as an interactive multi-module Streamlit research laboratory structured into eight specialized views accessible from the sidebar navigation:

```
+----------------------------------------------------------------------------------------------------+
|                                    STREAMLIT WEB DASHBOARD (python_app/app.py)                     |
+----------------------------------------------------------------------------------------------------+
| 1. Overview             | Research abstract, inductive bias comparison cards, interactive preview  |
| 2. Playground           | Dual clustering, isotropic Plotly charts, Voronoi/MST overlays, metrics  |
| 3. Benchmarks           | Monotonic wall-clock profiling, ratio of means, scaling curves, CSV      |
| 4. Algorithm Explorer   | Step-by-step educational trace visualizer for K-Means and Prim's MST     |
| 5. Robustness Analysis  | Paired Monte Carlo sweeps across noise (sigma) and outliers (epsilon)    |
| 6. CSV Import           | Tabular CSV parser, column mapping, 2D preview, playground handoff       |
| 7. Reproducibility      | Versioned JSON configuration (schema 1.0.0) export, import & restoration |
| 8. Methodology / Help   | Mathematical formulations, viva defense model questions, and help cards  |
+----------------------------------------------------------------------------------------------------+
```

All scientific computations are executed by the modular `clustering_lab` Python package:
- `clustering_lab.algorithms`: Pure NumPy Lloyd's K-Means and dense Prim's MST with deterministic tie-breaking and educational tracers.
- `clustering_lab.data`: Synthetic generators (Blobs, Moons, Circles), decoupled noise injection, CSV parser, versioned configuration schemas.
- `clustering_lab.evaluation`: Inlier ARI, Full-Data ARI, and safe Silhouette coefficient calculations.
- `clustering_lab.experiments`: Paired sweep runner, Monte Carlo statistical aggregation, runtime benchmarking, provenance CSV/JSON exporters.
- `clustering_lab.utils`: Canonical sample standard deviation helper with Bessel's correction ($ddof=1$).
- `clustering_lab.visualization`: Isotropic Plotly figures (1:1 Euclidean scale) and publication-quality dark-themed Matplotlib PNG exporters.

---

## 4. Scientific Methods and Computational Formulations

### 4.1 Lloyd's K-Means with K-Means++ Initialization
- **Optimization Objective:** Minimizes the within-cluster sum of squared Euclidean distances (inertia):
  $$\arg\min_S \sum_{j=1}^k \sum_{x \in S_j} \|x - \mu_j\|_2^2$$
- **Initialization:** Arthur & Vassilvitskii (2007) K-Means++ algorithm. Samples subsequent initial centroids with probability proportional to squared Euclidean distance to the nearest existing center:
  $$P(x) = \frac{D(x)^2}{\sum_{x' \in X} D(x')^2}$$
  Probabilities are explicitly normalized to sum to $1.0$ to eliminate floating-point drift.
- **Assignment & Centroid Update:** Pairwise distances are computed via vectorized NumPy broadcasting. Ties are broken deterministically by selecting the smallest cluster index $j$. Centroids are relocated to the arithmetic mean of assigned points.
- **Convergence Criterion:** Iteration terminates when the maximum centroid shift across all clusters satisfies $\max_j \|\mu_j^{(t)} - \mu_j^{(t-1)}\|_2 < \text{tol}$ (default $\text{tol} = 10^{-4}$) or when `max_iter` (default 300) is reached.
- **Empty-Cluster Reseeding:** If a cluster loses all assignments, it is reseeded to the point exhibiting the maximum distance to its current centroid. If all candidates are claimed, deterministic modulo fallback ($c \pmod{n_{\text{samples}}}$) is applied.
- **Memory & Time Complexity:** Time complexity is $\mathcal{O}(N \cdot k \cdot I \cdot D)$, where $N$ is sample count, $k$ is number of clusters, $I$ is iterations to convergence, and $D$ is feature dimensionality ($D=2$ in this lab). Memory complexity is qualified across lifecycle stages:
  - *Persistent Clustering State:* $\mathcal{O}(N + k \cdot D)$ auxiliary memory storing integer cluster assignment labels of shape $(N,)$ and centroid coordinate array of shape $(k, D)$.
  - *Temporary Vectorized NumPy Arrays:* In the assignment step, pairwise Euclidean distance vectorization broadcasts coordinate differences `(N, 1, D) - (1, k, D)` to shape $(N, k, D)$ and calculates `dist_sq_matrix` of shape $(N, k)$, temporarily allocating $\mathcal{O}(N \cdot k \cdot D)$ and $\mathcal{O}(N \cdot k)$ array memory during execution before deallocation.
  - *Empty-Cluster Handling:* Reseeding computes assigned distances of shape $(N,)$ and candidate sort indices of shape $(N,)$ when triggered.

### 4.2 Dense Prim's Minimum Spanning Tree Clustering
- **Spanning Tree Construction:** Evaluates the exact Euclidean Minimum Spanning Tree across all $N$ vertices using dense Prim's algorithm with distance array relaxation.
- **Memory & Time Complexity:** Dense Prim's algorithm runs in quadratic time $\mathcal{O}(N^2)$ and linear auxiliary space $\mathcal{O}(N)$. It operates directly on coordinate points without materializing a dense $N \times N$ adjacency distance matrix in memory. It maintains three 1D arrays of length $N$ (`min_dist` of type float64, `parent` of type int32, and `in_tree` of type bool), dynamically relaxing minimum edge distances across $N$ outer iterations. Output tree edges occupy $\mathcal{O}(N)$ memory ($N-1$ edge tuples).
- **Deterministic Edge Cut Sorting:** Tree edges are sorted in descending order of Euclidean length using a deterministic multi-key sort tuple:
  $$\text{sort\_key} = (-w, \min(u, v), \max(u, v), \text{edge\_id})$$
- **Single-Linkage Partitioning:** Cutting the $k-1$ longest edges partitions the spanning tree into exactly $k$ connected components. Component memberships are evaluated via Disjoint Set Union (DSU) with path compression and rank optimization.
- **Mathematical Equivalence:** Longest-edge removal from an MST is strictly equivalent to single-linkage hierarchical agglomerative clustering cut at $k$ components.

### 4.3 Data Generation and Decoupled Perturbations
- **Synthetic Manifolds:**
  - `Gaussian Blobs`: $k$ well-separated spherical clusters generated around equidistant angular centers.
  - `Two Moons`: Interlocking non-convex crescent manifolds with controllable vertical separation and radius.
  - `Concentric Circles`: Non-convex inner and outer concentric rings with radius ratio $0.5$.
- **Decoupled Noise Injection:** Zero-mean isotropic Gaussian coordinate jitter $X_{\text{noisy}} = X + \mathcal{N}(0, \sigma^2 I)$ is added exclusively to inliers, preserving ground-truth cluster associations.
- **Uniform Outlier Contamination:** Injects uniform bounding-box noise across the expanded coordinate range $[\min(X) - 0.2\Delta, \max(X) + 0.2\Delta]$. Outliers are assigned ground-truth label $-1$ and tracked via an immutable boolean `inlier_mask`. Observation count is:
  $$N_{\text{outliers}} = \lfloor N_{\text{clean}} \times \frac{\epsilon}{1 - \epsilon} \rfloor$$

### 4.4 Evaluation Metrics and Mathematical Nuances
- **Inlier Adjusted Rand Index (Inlier ARI):** Evaluated strictly on genuine manifold inliers ($y \neq -1$). Isolates whether the intrinsic topological partition survived perturbation without conflating outlier contamination.
- **Full-Data ARI:** Evaluated across all $N$ observations, treating outliers as cluster label $-1$. Penalizes algorithms for grouping outliers into genuine clusters.
- **Silhouette Coefficient:** Evaluates cluster compactness versus separation:
  $$s(i) = \frac{b(i) - a(i)}{\max(a(i), b(i))}$$
  *Scientific Caveat:* The Silhouette Coefficient has an intrinsic mathematical bias favoring convex spherical clusters; it intrinsically penalizes non-convex crescent or ring clusters even when an algorithm achieves 100% ground-truth topological recovery.
- **Sample Standard Deviation ($ddof=1$):** All Monte Carlo sweep aggregations and benchmark timings report Bessel-corrected sample standard deviation:
  $$s = \sqrt{\frac{1}{n - 1} \sum_{i=1}^n (x_i - \bar{x})^2}$$
  Boundary condition $n \le 1$ returns $0.0$ to prevent division by zero.

---

## 5. Consolidated Issue Resolution Register

All 15 issues cataloged during project finalization are reconciled below based on verified repository evidence:

| Issue ID | Severity | Category | Description | Final Classification | Exact Implementation & Verification Evidence |
| :--- | :---: | :--- | :--- | :---: | :--- |
| **ISSUE-01** | **P1** | Algorithmic / Visual | $N=1$ MST Explorer Figure Dataclass Bug | **Fully Resolved** | Resolved in commit `50b2ae6`. Regression tests `test_mst_trace_single_observation_mathematical_properties` and `test_create_mst_explorer_figure_single_observation` pass. |
| **ISSUE-02** | **P2** | Algorithmic / Parity | Convergence tolerance condition disparity (`< tol` vs `<= tol`) | **Fully Resolved** | Resolved in `kmeans.py:276` and `explorer.py:403`. Both engines enforce strict `if not force_continue and max_shift < tol:` verified by automated parity tests. |
| **ISSUE-03** | **P2** | Algorithmic / Parity | Empty-cluster fallback reseeding divergence | **Fully Resolved** | Resolved in `kmeans.py:263` and `explorer.py:394`. Both engines apply deterministic modulo reseeding `c % n_samples`. |
| **ISSUE-04** | **P2** | Algorithmic / Validation | `KMeans.predict()` missing feature dimension check | **Fully Resolved** | Resolved in `kmeans.py:343-347`. Explicit domain `ValueError` raised on dimension mismatch with descriptive diagnostic message. |
| **ISSUE-05** | **P2** | Streamlit / State | Algorithm Explorer slider widget key collision & step desync | **Fully Resolved** | Resolved via unified session state callback on `explorer_step_index`. Verified in `test_algorithm_explorer_navigation_synchronization` and Stage 06 Protocol M5. |
| **ISSUE-06** | **P2** | Streamlit / UX | Playground stale-state visualizer unmounting | **Fully Resolved** | Resolved in `app.py`. Implemented non-collapsing state machine retaining previous Plotly figures with amber stale warning banner and recompute action. |
| **ISSUE-07** | **P2** | Code Hygiene | `compute_sample_std` code duplication across modules | **Fully Resolved** | Canonical implementation established in `clustering_lab/utils/math_helpers.py` with Bessel's correction ($ddof=1$). Verified by `test_canonical_math_helper_sample_std_properties`. |
| **ISSUE-08** | **P3** | Maintainability | Dual-signature constructor overload in `BenchmarkSummary` | **Resolved with Trade-off** | Preserved backward-compatible keyword arguments in `BenchmarkTrialResult` and `BenchmarkSummary` to support legacy call signatures without runtime impact. |
| **ISSUE-09** | **P3** | Scientific / Scope | Uniform cluster dispersions in `generate_blobs` | **Intentionally Deferred** | Deferred per Blueprint Section 1.1. Scalar cluster dispersion $\sigma$ provides a scientifically controlled baseline. Heterogeneous variance is cataloged for future research. |
| **ISSUE-10** | **P3** | Scientific / Scope | Unimplemented Normalized Mutual Information (NMI) | **Intentionally Deferred** | Deferred per Blueprint Section 1.1. Inlier ARI and Full ARI provide comprehensive evaluation under equal class priors. NMI remains cataloged for future research. |
| **ISSUE-11** | **P3** | UI / Theming | Matplotlib PNG export theme vs Plotly dark theme divergence | **Fully Resolved** | Resolved in `figures.py:938-943, 1034-1039`. Matplotlib exporters now use `SURFACE_INSET`, `SURFACE_HOVER`, and `BORDER_STRONG` design tokens. |
| **ISSUE-12** | **P3** | Cloud / Performance | Extended sweep latency under product bounds ($N=500$) | **Mitigated** | Capped at $N \le 500$ in `sweeps.py`; trial progress bar in UI; Quick Mode default; verified in Stage 06 Protocol M6. |
| **ISSUE-13** | **P1** | Security / DevOps | Dev Container security & configuration breakdown | **Fully Resolved** | Resolved in `.devcontainer/devcontainer.json`: Python 3.12 image, pinned `requirements-dev.txt`, removed `apt upgrade`, restored browser CORS/XSRF guards. |
| **ISSUE-14** | **P2** | Documentation | Missing repository root `README.md` entrypoint | **Fully Resolved** | Created comprehensive root `README.md` in Stage 01 with architecture, quickstart, live links, and academic attribution. |
| **ISSUE-15** | **P3** | UX Polish | Missing micro-spinner progress indicator during Prim computation | **Fully Resolved** | Integrated `st.spinner("Computing dense Prim MST and Voronoi partitions...")` across Playground and Benchmarks. |

---

## 6. Stage 06 Manual Acceptance Testing Summary

On October 15, 2026, the project owner conducted a comprehensive, user-led manual acceptance testing campaign on Windows 11 using the Brave browser against `http://localhost:8501`.

The campaign verified all eight application modules across eight primary protocols (M1–M8), eight supplementary quality gates (S1–S8), and two verified defect fixes:

### Primary Manual Protocols (M1–M8)
- **Protocol M1 (Overview & Academic Identity):** Verified dark theme, course badges, equal attribution (**Himanshu Gupta & Parth Yadav**), and absence of private roll numbers.
- **Protocol M2 & M2-R1 (Playground Dual Execution & Topological Inductive Bias):** Confirmed K-Means hyperplane bisection failure on Two Moons ($ARI \approx 0.25$) versus Prim MST perfect topological recovery ($ARI = 1.000$). Verified `Reset Defaults` recovery from defect `S06-DEFECT-001`.
- **Protocol M3 (Playground Stale-State Persistence):** Confirmed previous Plotly charts, Voronoi boundaries, and metric tables remain in the DOM when sliders change, displaying an amber warning banner.
- **Protocol M4 (Performance Benchmarks & Scaling Trends):** Confirmed wall-clock execution time profiling, ratio of means table ($\bar{t}_{\text{MST}} / \bar{t}_{\text{KM}}$), monotonic scaling curves, and CSV export.
- **Protocol M5 (Algorithm Explorer Synchronization):** Confirmed step-by-step navigation across K-Means iterations and Prim edge cuts without double reruns, step skips, or index crashes (verifying fix for `S06-DEFECT-002`).
- **Protocol M6 (Robustness Analysis Sweeps):** Confirmed paired sweeps across noise and outliers; verified the MST "cliff drop" failure mode under uniform outliers versus K-Means resilience under Gaussian noise.
- **Protocol M7 (CSV Ingestion Workflow):** Tested valid 2D labeled, unlabeled, and whitespace-padded CSV fixtures; confirmed clean error rejection on corrupted non-numeric fixtures (`05_invalid_nonnumeric.csv`).
- **Protocol M8 (Configuration Round-Trip):** Verified JSON export, parameter tweaking, and 100% session state restoration from saved JSON configuration payloads.

### Supplementary Checks (S1–S8) and Defect Verification
- **Supplementary Checks S1–S8:** Covered dark-mode contrast tokens, responsive layouts, CSV delimiter handling, mathematical boundary conditions ($N=1$, collinear points), Bessel $ddof=1$ variance checks, clean error boundaries, and uncorrupted file export downloads.
- **Defects Resolved & Formally Verified:**
  - `S06-DEFECT-001` (P2): `StreamlitWidgetAlreadyInstantiatedError` on Playground default reset — resolved via safe pre-render callback `on_click=_on_reset_playground_defaults` executing prior to widget instantiation, re-verified in Protocol M2-R1.
  - `S06-DEFECT-002` (P1): `TypeError: unexpected keyword argument 'radius'` on Algorithm Explorer dataset generation for Concentric Circles and Two Moons — resolved via topology-specific keyword argument dispatch and filtering, re-verified in Protocol M5.
- **Distinction Notice:** The 8 manual acceptance protocols (M1–M8) and 8 supplementary checks (S1–S8) are distinct from the 10 engineering blueprint milestones that comprised Stage 06 execution. All 8 protocols and 8 checks received unconditional sign-off.

*Acceptance Record:* Formally signed off and documented in [docs/STAGE_06_MANUAL_ACCEPTANCE.md](STAGE_06_MANUAL_ACCEPTANCE.md).

---

## 7. Automated Test Suite and Quality Verification

The automated test suite consists of **169 passing tests** (168 tests historical baseline established in Stage 06 + 1 generalized privacy fixture test added in Stage 07) across 11 test modules, verified locally and in continuous integration on Python 3.12:

```text
============================= test session starts =============================
platform win32 -- Python 3.12, pytest-8.4.2
collected 169 items

python_app/tests/test_algorithm_explorer.py ........ [ 11%]
python_app/tests/test_benchmarks.py ................ [ 20%]
python_app/tests/test_data.py .............          [ 28%]
python_app/tests/test_data_io.py .........           [ 33%]
python_app/tests/test_environment.py ..........      [ 39%]
python_app/tests/test_kmeans.py ..........           [ 45%]
python_app/tests/test_mst.py ..........              [ 51%]
python_app/tests/test_project_structure.py ......... [ 56%]
python_app/tests/test_reference_validation.py ....   [ 59%]
python_app/tests/test_robustness_experiment.py ..... [ 79%]
python_app/tests/test_streamlit_dashboard.py ....... [100%]

======================= 169 passed in 61.02s (0:01:01) ========================
Exit Code: 0
```

### Module Breakdown
- `test_algorithm_explorer.py` (14 tests): Step progression, Voronoi updates, MST edge commits, $N=1$ invariants, AppTest navigation synchronization.
- `test_benchmarks.py` (16 tests): Monotonic timing, warmup exclusion, ratio of means, repetition statistics, CSV export, generalized privacy assertion.
- `test_data.py` (13 tests): Blobs, Moons, Circles generation, noise injection, outlier contamination, immutability.
- `test_data_io.py` (9 tests): CSV loading, integer/categorical labels, missing coordinates, JSON round-trip serialization.
- `test_environment.py` (10 tests): Python 3.12 runtime assertions, required library imports.
- `test_kmeans.py` (10 tests): K-Means++ initialization, convergence tolerance, empty-cluster reseeding, inertia, estimator interface.
- `test_mst.py` (10 tests): Dense Prim construction, edge cutting, DSU components, $N=1$ single point, collinear ties.
- `test_project_structure.py` (9 tests): Package importability, directory layout, Streamlit AppTest smoke, canonical math helper exports.
- `test_reference_validation.py` (4 tests): Parity against `scipy.sparse.csgraph.minimum_spanning_tree` and `sklearn.cluster.KMeans`.
- `test_robustness_experiment.py` (16 tests): Matched-seed pairing, baseline isolation, Inlier vs Full ARI degradation, trial accounting, generalized privacy assertion.
- `test_streamlit_dashboard.py` (48 tests): AppTest execution across all 8 views, generalized privacy compliance across routes and exports, synthetic ID regex fixture verification, trial reconciliation, stale state lifecycle, reset recovery.

---

## 8. Statement Coverage Baseline

Authoritative statement coverage measured locally in a single unified `pytest-cov` invocation on Python 3.12:

- **Overall Application Line Coverage:** **86.0%** across all 2,711 executable statements.
- **Scientific Core Library Coverage (`clustering_lab`):** **~90.92%** across 1,995 library statements.
- **Streamlit Web Application (`app.py`):** **~63.4%** across 716 statements (covering core routing, state initialization, and component rendering via headless `AppTest`).

---

## 9. Local Installation and Startup Instructions

### Prerequisites
- Python 3.12 (64-bit) installed locally, **or** [uv](https://docs.astral.sh/uv/) (recommended).

### Option A: Using `uv` (Fastest, Self-Contained)
```powershell
# From the repository root:
$env:PYTHONPATH="python_app"

# Verify Python version:
uv run --python 3.12 python --version

# Run the complete test suite (169 tests):
uv run --python 3.12 --with-requirements python_app/requirements-dev.txt pytest python_app/tests -v

# Launch the interactive Streamlit dashboard:
uv run --python 3.12 --with-requirements python_app/requirements-dev.txt streamlit run python_app/app.py
```

### Option B: Using Standard Python Virtual Environment
```powershell
# On Windows PowerShell:
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r python_app/requirements-dev.txt

$env:PYTHONPATH="python_app"
pytest python_app/tests -v
streamlit run python_app/app.py
```

```bash
# On Linux / macOS (Bash):
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r python_app/requirements-dev.txt

PYTHONPATH=python_app pytest python_app/tests -v
streamlit run python_app/app.py
```

The application opens locally in your web browser at: `http://localhost:8501`.

---

## 10. Supported Import and Export Workflows

### 10.1 Tabular CSV Ingestion
- **Format:** Standard comma-separated (`.csv`), semicolon (`;`), or tab-delimited (`\t`).
- **Guards:** Maximum file size 5MB, maximum rows 10,000.
- **Coordinates:** At least two finite numeric columns required.
- **Labels:** Optional ground-truth label column. Categorical labels are automatically encoded to sequential integers; label `-1` is treated as uniform outlier noise. If labels are absent, ARI is cleanly reported as `N/A` (never fabricated).
- **Interactive Cap:** Enforces hard cap of $\le 600$ total observations for interactive clustering to protect dense Prim's $\mathcal{O}(N^2)$ responsiveness.

### 10.2 Versioned JSON Experiment Configuration (Schema 1.0.0)
- Serializes full experiment state: topology, sample sizes, noise levels, outlier rates, cluster counts, and random seed.
- Validates uploaded JSON against strict bounds; malformed payloads are rejected with clear error banners.
- Restoring a JSON configuration updates UI session state and re-executes dual clustering deterministically.

### 10.3 Provenance-Preserving Exports
- **Raw Trials CSV:** Exports every individual paired trial with seed, topology, perturbation parameter, Inlier ARI, Full ARI, and runtime.
- **Summary Statistics CSV:** Exports aggregated mean and sample standard deviation ($ddof=1$) per sweep condition.
- **Publication-Quality PNGs:** In-memory Matplotlib dark-themed figures exported with 150 DPI without temporary filesystem writes.

---

## 11. Scientific Limitations and Research Boundaries

To maintain scientific integrity during academic defense, the following boundaries are formally acknowledged:

1. **Convex Partitioning Constraint of K-Means:**
   Lloyd's K-Means mathematically minimizes squared Euclidean distance to centroids, mandating linear Voronoi hyperplane boundaries. It is fundamentally incapable of partitioning non-convex topologies (Two Moons, Concentric Circles) regardless of sample size or iteration budget.
2. **Single-Linkage Vulnerability of Prim's MST:**
   Longest-edge removal from an MST is equivalent to single-linkage hierarchical clustering. While it naturally follows non-convex manifolds, it is susceptible to "chaining" when uniform noise bridges distinct clusters, and to "outlier isolation" when distant outliers consume edge cuts.
3. **Wall-Clock Benchmarking Caveat:**
   Empirical execution timings measured via `time.perf_counter` reflect real-world operating system scheduling, interpreter overhead, and CPU thermal throttling. Timings across small sample sets ($N \in \{100, 200, 400, 600\}$) illustrate general growth trends but do not mathematically prove asymptotic bounds.
4. **ARI vs. NMI Evaluation Nuance:**
   Adjusted Rand Index adjusts for chance and penalizes cluster fragmentation effectively under equal class priors. Normalized Mutual Information (NMI) remains an alternative information-theoretic metric that is cataloged for post-course research.
5. **Cross-Platform Floating-Point Determinism:**
   While `np.random.default_rng(seed)` ensures identical random sequences, bit-identical floating-point results across different OS platforms (Linux vs Windows) or different CPU architectures (x86 vs ARM) are subject to compiler-specific BLAS/LAPACK vectorization optimizations.

---

## 12. Academic Demonstration and Offline Viva Checklist

This checklist is provided for the lead student researchers (**Himanshu Gupta & Parth Yadav**) during in-person academic defense:

### Pre-Viva Setup (Internet Connected)
- [ ] Laptop provisioned with Python 3.12 and dependencies pre-installed (`pip install -r python_app/requirements-dev.txt`).
- [ ] Repository located at `D:\7th Sem\PM\Mini project\MST-KMeans-Robustness-Analysis`.
- [ ] Local Git status clean on branch `feature/python-streamlit-migration`.

### Physical Airgap Offline Demonstration (Airplane Mode ON)
- [ ] **Step 1 (Physical Airgap):** Disconnect Wi-Fi and Ethernet. Enable Airplane Mode.
- [ ] **Step 2 (Legacy JS Verification):** Double-click `index.html` to open in browser via `file:///`. Demonstrate client-side HTML5 Canvas visualizers with zero internet or server dependencies.
- [ ] **Step 3 (Launch Python Dashboard):** In PowerShell, run `$env:PYTHONPATH="python_app"; streamlit run python_app/app.py`.
- [ ] **Step 4 (Overview & Identity):** Open `http://localhost:8501`. Demonstrate academic badges, instructor credit (*Mr. Aman Kumar*), and equal attribution without roll numbers.
- [ ] **Step 5 (Topological Inductive Bias):** In Playground, select `Two Moons`, $N=300$, noise $0.05$. Show K-Means linear bisection failure ($ARI \approx 0.25$) versus Prim MST manifold recovery ($ARI = 1.000$).
- [ ] **Step 6 (Stale-State Persistence):** Adjust noise slider without clicking Generate. Show that previous figures persist with an amber warning banner.
- [ ] **Step 7 (Algorithm Explorer):** In Explorer, select Prim's MST, $N=20$. Step through tree growth from root vertex to final $k-1$ edge cuts.
- [ ] **Step 8 (Robustness Sweep):** In Robustness Analysis, run Quick Preset across all 3 manifolds. Show MST performance drop under uniform outliers versus K-Means stability under Gaussian noise.
- [ ] **Step 9 (Artifact Export):** Download a high-res PNG and summary CSV, verifying clean in-memory export.

*Airgap Status:* Verified zero-network code architecture and 169 in-memory tests. Physical airgap execution by project owner: **PENDING AT VIVA TIME**.

---

## 13. Public Cloud Deployment Verification Limitations

The public Streamlit Community Cloud application is deployed at:
[https://mst-kmeans-robustness-analysis.streamlit.app/](https://mst-kmeans-robustness-analysis.streamlit.app/)

### Current Cloud Verification State
- **Public URL Reachable:** Confirmed reachable.
- **Main Dashboard Rendered:** Confirmed clean rendering in dark theme.
- **Module Navigation Tested:** Confirmed all eight views load without Python exceptions.
- **Deployment Repository & Branch:** Associated with `Himanshu102931/MST-KMeans-Robustness-Analysis` on branch `feature/python-streamlit-migration`.
- **Exact Deployed Commit Verification:** **UNKNOWN** (Standard Streamlit Community Cloud security prevents public viewers from inspecting private deployment build logs or commit hashes. The exact deployed commit must be verified by the project owner via the authenticated Streamlit admin dashboard at `share.streamlit.io`).

---

## 14. Release Approval and Version-Tagging Status

- **Candidate Tag:** `v1.0.0-final`
- **Release Status:** **DRAFT / CANDIDATE ONLY**
- **Git Actions Taken in Batch 1:**
  - Prompt 1/3: Read-only release readiness audit (ZERO commits, ZERO pushes, ZERO tags).
  - Prompt 2/3: Privacy remediation and draft release notes preparation (ZERO commits, ZERO pushes, ZERO tags).
  - Prompt 3/3: Consolidated QA and single local commit (Commit 2 of 3 in current push cycle).
- **Formal Release Publication:**
  - Creation of Git release tag `v1.0.0-final` is **STRICTLY ON HOLD** pending final QA review and explicit written authorization from the project owner.
  - No remote pushes to GitHub origin, merges to `main`, or cloud deployment triggers will be performed without explicit project owner instructions.

> [!NOTE]
> **Historical Git Privacy Notice:** Active-source sanitization ensures the current working tree and candidate release snapshot contain zero personal student registration identifiers. Historical Git commit objects prior to commit `4adbc8c` remain preserved in repository history per non-destructive Git governance, and do not compromise active runtime or release package privacy.

---

*Draft Release Notes finalized for Stage 07 Batch 2, Prompt 3 of 3. Historical milestone privacy sanitized; quality gates validated.*
