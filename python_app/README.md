# Python Clustering Laboratory (`python_app`)
## MST vs K-Means Robustness Analysis — Stage 07: Academic Handoff
### Status: Stage 07 — Release Candidate Under Verification (Draft)

### Academic Information
- **Course:** Pattern Matching Lab (`BCS-DS-777`)
- **Institution:** Manav Rachna International Institute of Research and Studies (MRIIRS), School of Engineering & Technology
- **Degree:** B.Tech Computer Science & Engineering (AIML), 7th Semester (2026–2027)
- **Student Researchers (Equal Academic Contribution):**
  - Himanshu Gupta
  - Parth Yadav
- **Faculty Guide / Course Instructor:** Mr. Aman Kumar, Assistant Professor
- **Repository Branch:** `feature/python-streamlit-migration`
- **Preserved Main Checkpoint:** `0864323`
- **Draft Release Notes:** [docs/RELEASE_NOTES.md](../docs/RELEASE_NOTES.md)

---

## 1. Purpose of the Python Migration

This subproject (`python_app/`) establishes the scientific Python implementation for the **MST vs K-Means Robustness Analysis** project. 

The primary objectives of the Python migration are:
1. **Industry-Standard Scientific Tooling:** Transition from a purely clientside JavaScript execution model to the Python data science and machine learning ecosystem (`numpy`, `scipy`, `scikit-learn`, `pandas`).
2. **Interactive Cloud-Deployable Web Dashboard:** Utilize [Streamlit](https://streamlit.io) to deliver an intuitive, clean graphical user interface for real-time parameter tweaking and visualization without client-side browser performance throttling.
3. **Rigorous Automated Quality Assurance:** Implement continuous integration via GitHub Actions on standard Linux containers with automated `pytest` suites to guarantee scientific code correctness and dependency integrity.

---

## 2. Preservation of the Existing JavaScript Application

The existing Vanilla JavaScript web application located at the repository root (`index.html`, `js/`, `css/`, `results/`, `tests/`) is **strictly preserved and remains fully functional**:
- **Zero-Dependency Viva Fallback:** The JavaScript application requires zero installation, running directly in any modern web browser via file or static web server.
- **Academic Independence:** All existing viva materials, presentation slides (`docs/presentation/`), and experimental artifacts remain anchored to the preserved main-branch checkpoint (`0864323`).
- **Parallel Evolution:** The Python application evolves cleanly inside `python_app/` on the `feature/python-streamlit-migration` branch without modifying or overwriting any legacy JavaScript code or report files.

---

## 3. Directory Structure

```
python_app/
├── app.py                      # Main Streamlit dashboard entry point
├── requirements.txt            # Production application dependencies (Python 3.12)
├── requirements-dev.txt        # QA and development testing dependencies (-r requirements.txt + pytest)
├── README.md                   # This documentation guide
├── docs/
│   ├── ALGORITHM_SPECIFICATION.md # Formal mathematical definitions, complexities, and biases
│   ├── DATASET_AND_REPRODUCIBILITY_SPECIFICATION.md # Dataset topologies, noise decoupling & CSV specs
│   ├── STREAMLIT_DASHBOARD_GUIDE.md # Viva demonstration script and dashboard manual
│   ├── ROBUSTNESS_EXPERIMENT_SPECIFICATION.md # Phase M5A robustness sweeps, metrics & statistical design
│   ├── PERFORMANCE_BENCHMARK_SPECIFICATION.md # Phase M5B execution-time benchmark methodology
│   └── ALGORITHM_EXPLORER_GUIDE.md # Phase M5B educational step-by-step algorithm explorer guide
├── clustering_lab/             # Core scientific Python research package
│   ├── __init__.py             # Package metadata and version definition
│   ├── algorithms/             # Clustering algorithm implementations
│   │   ├── __init__.py         # Package exports (KMeans, MSTClustering)
│   │   ├── kmeans.py           # Lloyd's K-Means with K-Means++ and deterministic tie-breaking
│   │   ├── mst.py              # Dense Prim's MST with single-linkage cut and DSU
│   │   └── explorer.py         # Step-by-step trace generators for K-Means and dense Prim's MST
│   ├── data/                   # Synthetic dataset generation, contamination & CSV loader
│   │   ├── __init__.py         # Data layer public API exports
│   │   ├── dataset.py          # Standardized immutable Dataset container and validation
│   │   ├── noise.py            # Decoupled Gaussian jitter and uniform outlier pipeline
│   │   ├── synthetic.py        # Blobs, Moons, and Circles synthetic generators
│   │   ├── csv_loader.py       # Secure, UI-independent CSV parser with categorical encoding
│   │   └── config.py           # Versioned JSON experiment configuration schema (1.0.0)
│   ├── experiments/            # Robustness sweeps & performance benchmark runners
│   │   ├── __init__.py         # Public exports (benchmarks, sweeps, runners, etc.)
│   │   ├── benchmarks.py       # High-resolution monotonic runtime benchmarks & statistics
│   │   ├── sweeps.py           # SweepConfig, sweep types, presets (Quick/Extended) and validation
│   │   ├── runner.py           # Paired execution engine with matched baseline association
│   │   ├── aggregation.py      # Monte Carlo statistical aggregation (mean, sample std dev ddof=1)
│   │   └── export.py           # Provenance-isolated CSV and JSON serialization
│   ├── evaluation/             # Quantitative validation metrics (Phase M4)
│   │   ├── __init__.py
│   │   └── metrics.py          # Inlier ARI, Full ARI, safe Silhouette, runtime
│   ├── visualization/          # Static and interactive charting utilities
│   │   ├── __init__.py
│   │   └── figures.py          # 2D scatter plots, 1:1 scaling, sweep curves, explorer & benchmark charts
│   └── utils/                  # Mathematical helpers and seed management
│       └── __init__.py
└── tests/                      # Automated test suite (pytest)
    ├── __init__.py
    ├── test_environment.py     # Runtime Python version & dependency import assertions
    ├── test_project_structure.py # Package layout, internal imports & Streamlit AppTest smoke
    ├── test_kmeans.py          # Mathematical, boundary, and convergence tests for K-Means
    ├── test_mst.py             # Graph invariants, 3-4-5 triangle, cuts, and DSU tests for MST
    ├── test_reference_validation.py # Reference validation against SciPy and scikit-learn
    ├── test_data.py            # Synthetic generators, shapes, noise/outliers, and invariants
    ├── test_data_io.py         # CSV importing, validation bounds, and JSON config round-trip
    ├── test_streamlit_dashboard.py # Interactive dashboard AppTest smoke and regressions
    ├── test_robustness_experiment.py # Phase M5A paired sweeps, statistical aggregation, and safety bounds
    ├── test_benchmarks.py      # Phase M5B execution-time benchmark engine and statistics tests
    └── test_algorithm_explorer.py # Phase M5B educational trace invariants and parity tests
```

---

## 4. Python Runtime & Scientific Dependency Specifications

The project targets **Python 3.12 (64-bit)** on standard Linux x86_64 environments.

### Core Dependencies and Their Roles

| Package | Version Bound | Role in Research Lab |
| :--- | :--- | :--- |
| **Streamlit** | `>=1.35.0, <2.0.0` | Powers the web user interface, parameter sliders, dataset controls, and dynamic charts. |
| **NumPy** | `>=1.26.4, <2.0.0` | Vectorized coordinate representations, Euclidean distance calculations, and fast array operations. Bound to `<2.0.0` for maximum binary compatibility with compiled ecosystem libraries. |
| **Pandas** | `>=2.2.0, <3.0.0` | Structured DataFrame handling for benchmark experiment runs, noise sweep tables, and metric reporting. |
| **SciPy** | `>=1.12.0, <2.0.0` | Pairwise spatial distance matrix computation (`scipy.spatial.distance`) and minimum spanning tree routines (`scipy.sparse.csgraph`). |
| **scikit-learn** | `>=1.4.0, <2.0.0` | Standardized clustering metrics (`adjusted_rand_score`, `normalized_mutual_info_score`, `silhouette_score`) and baseline algorithms. |
| **Matplotlib** | `>=3.8.0, <4.0.0` | Publication-ready 2D clustering figures and diagnostic plots. |
| **Plotly** | `>=5.20.0, <6.0.0` | Interactive WebGL-accelerated 2D scatter plots and dynamic MST tree edge overlays. |
| **pytest** | `>=8.0.0, <9.0.0` | Automated test runner used in continuous integration. |

---

## 5. Automated CI Testing (GitHub Actions)

Because native C-extensions (NumPy/SciPy DLLs) may face execution restrictions in locked-down Windows student environments, **all dependency installation and automated tests are verified on cloud-hosted Linux**:

- **Workflow File:** `.github/workflows/python-ci.yml`
- **Target OS:** `ubuntu-latest`
- **Target Python:** `3.12`
- **Workflow Triggers:**
  - Push to `feature/python-streamlit-migration`
  - Pull requests targeting `main` or `feature/python-streamlit-migration`
  - Manual trigger via `workflow_dispatch`
- **Execution Pipeline:**
  1. Checks out repository (`actions/checkout@v5`).
  2. Sets up Python 3.12 (`actions/setup-python@v7`) with pip caching.
  3. Upgrades pip and installs `requirements-dev.txt`.
  4. Runs explicit inline import check across all scientific packages.
  5. Executes `pytest python_app/tests -v` with `PYTHONPATH=python_app`.

---

## 6. Streamlit Dashboard Usage & Features

### Running the Application Locally
Launch the interactive research dashboard with:
```bash
streamlit run python_app/app.py
```

### Module Organization
The dashboard is partitioned into 8 core navigation modules:
1. **Overview:** Official research objective, project metadata, student details, and migration status.
2. **Clustering Playground:** Interactive parameter controls, simultaneous execution of Lloyd's K-Means and Prim's MST on the same feature matrix $X$, 2D Plotly visualizations with equal 1:1 scaling, and side-by-side quantitative metrics.
3. **Algorithm Explorer (Phase M5B):** Step-by-step interactive educational visualizations for Lloyd's K-Means (K-Means++ initialization, Voronoi assignment, centroid relocation, inertia) and dense Prim's MST (root vertex, greedy minimum cut edge selection, cut of $k-1$ longest edges, connected component partition), with guaranteed 100% final parity with production algorithms.
4. **Performance Benchmarks (Phase M5B):** Scientifically valid monotonic execution-time benchmarks ($N \in [100, 200, 400, 600]$, 5 repetitions), preflight safety limits ($\le 200$ executions), sample statistics (mean, median, Bessel-corrected sample std, ratio of means), asymptotic complexity discussion ($\mathcal{O}(I \cdot N \cdot k \cdot D)$ vs $\mathcal{O}(N^2)$), and data/figure exports.
5. **Robustness Analysis (Phase M5A):** Automated paired perturbation sweeps (Gaussian noise and uniform outliers), Monte Carlo statistical aggregation across deterministic seeds, matched baseline degradation curves, and provenance-isolated CSV/JSON exports.
6. **Dataset & CSV Import:** Secure upload of custom 2D tabular CSV datasets with automatic numeric column detection, optional ground-truth label mapping, and validation guards.
7. **Reproducibility & Configuration:** Export and import of versioned JSON configuration files compliant with `ExperimentConfig` schema `1.0.0`.
8. **Methodology / Help:** Algorithmic inductive biases, mathematical definitions of metrics, and a step-by-step viva demonstration walkthrough.

### Meaning of Controls & Hyperparameters
- **Dataset Topology:** Choose between `Gaussian Blobs` (globular/convex), `Two Moons` (non-convex crescent manifolds), or `Concentric Circles` (nested non-convex rings).
- **Inlier Sample Count ($N_{inliers}$):** Number of clean or noisy manifold observations ($20 \le N_{inliers} \le 600$). Enforced interactive ceiling is $\le 600$ total points ($N_{total} = N_{inliers} + N_{outliers}$) to ensure dense Prim's $O(N^2)$ responsiveness.
- **Random Seed:** Master PRNG seed ensuring deterministic generation and reproducibility.
- **Gaussian Noise ($\sigma$):** Standard deviation of zero-mean Gaussian jitter added independently to inliers.
- **Outlier Contamination Rate:** Fraction of uniform random noise points injected across the bounding box ($N_{outliers} = \text{round}(N_{inliers} \times \text{rate})$). Total observation count is $N = N_{inliers} + N_{outliers}$.
- **Cluster Count ($k$):** Number of target partitions. Configurable for Blobs ($2 \le k \le 8$); fixed at $k=2$ for Moons and Circles.
- **Overlay Retained MST Edges / Highlight Cut Edges:** Toggle visual graph overlays to inspect the Euclidean tree structure and removed partition boundaries.

### Quantitative Metrics Interpretation
- **Inlier Adjusted Rand Index (Inlier ARI):** Measures clustering agreement strictly on true inliers. Evaluates how well the algorithm recovers intrinsic cluster topology despite surrounding contamination. Range $[-0.5, 1.0]$ ($1.0$ is perfect partition recovery).
- **Full-Data ARI:** Evaluated across all points including outliers (label $-1$). Outliers naturally penalize both algorithms since neither assigns an explicit reject class.
- **Inertia (WCSS):** Within-cluster sum of squared Euclidean distances to centroids. *Cannot be compared against MST weight.*
- **Total MST Weight:** Sum of Euclidean edge lengths in the uncut minimum spanning tree.
- **Retained Forest Weight:** Sum of edge lengths remaining after cutting the $k-1$ longest edges.
- **Silhouette Coefficient:** Intrinsic quality metric measuring cluster tightness vs separation. *Warning: intrinsically favors convex spherical clusters and penalizes non-convex shapes (circles, moons) even when perfectly clustered by MST.*
- **Runtime (Single Run):** Illustrative wall-clock latency measurement in milliseconds.

### CSV Format Requirements
- **File Format:** Standard comma-separated values (`.csv`), UTF-8 encoded.
- **Size Bounds:** $\le 5\text{ MB}$ raw file size, $\le 10,000$ rows.
- **Feature Columns:** At least two distinct numerical columns containing finite coordinates (no NaN/Inf).
- **Label Column (Optional):** Optional column containing integer or categorical class identifiers. If omitted, data is treated as unlabeled and ARI is reported as `N/A` (never fabricated).
- **Interactive Scalability Ceiling:** Datasets exceeding 600 total observations gracefully reject interactive clustering execution to protect dense Prim's $O(N^2)$ responsiveness without truncating input data.

### JSON Configuration Import/Export
- Complies with `ExperimentConfig` schema `1.0.0`.
- Serializes `dataset_family`, `n_samples`, `n_clusters`, `seed`, `noise`, `outlier_rate`, and geometric hyperparameters.
- Restoring a JSON configuration deterministically reproduces the identical dataset and clustering result.
- *Notice:* JSON configuration alone cannot regenerate external CSV datasets without the source CSV file.

### Cloud Deployment Instructions
To deploy the Streamlit dashboard on **Streamlit Community Cloud**:
1. Connect the GitHub repository `Himanshu102931/MST-KMeans-Robustness-Analysis`.
2. Set the target branch to `feature/python-streamlit-migration` (or merged production branch).
3. Set the Main file path to `python_app/app.py`.
4. The deployment environment automatically installs dependencies from `python_app/requirements.txt`.

---

## 7. Implementation Status

- **Completed in Phase M1:**
  - Python 3.12 project architecture established.
  - Package namespaces created (`clustering_lab.*`).
  - Production and development requirement specifications defined.
  - Minimal foundation Streamlit application (`app.py`) deployed with project metadata and research goals.
  - Automated foundation tests (`test_environment.py`, `test_project_structure.py`).
  - GitHub Actions CI workflow implemented.
- **Completed in Phase M2:**
  - Pure NumPy implementation of Lloyd's K-Means with K-Means++ initialization (`kmeans.py`).
  - Pure NumPy dense Prim's MST clustering with deterministic cuts and DSU (`mst.py`).
  - Mathematical unit test suite for K-Means (`test_kmeans.py`).
  - Graph-theoretic unit test suite for MST (`test_mst.py`).
  - Reference validation suite against SciPy and scikit-learn (`test_reference_validation.py`).
  - Formal algorithm specifications documentation (`docs/ALGORITHM_SPECIFICATION.md`).
- **Completed in Phase M3:**
  - Standardized immutable `Dataset` container with boundary validation (`dataset.py`).
  - Decoupled Gaussian noise and uniform outlier contamination pipeline (`noise.py`).
  - Synthetic generators: Gaussian Blobs, Two Moons, and Concentric Circles (`synthetic.py`).
  - Secure, UI-independent CSV dataset parser with categorical label encoding (`csv_loader.py`).
  - Versioned JSON experiment configuration schema `1.0.0` with round-trip fidelity (`config.py`).
  - Dataset and reproducibility specification (`docs/DATASET_AND_REPRODUCIBILITY_SPECIFICATION.md`).
  - Refined mathematical definitions in `ALGORITHM_SPECIFICATION.md`.
  - Comprehensive unit test suites (`test_data.py`, `test_data_io.py`).
- **Completed in Phase M4:**
  - Interactive Python Streamlit dashboard (`app.py`) with 5 core views.
  - Dual algorithm execution on identical feature arrays with real-time runtime profiling.
  - Quantitative metrics evaluation module (`metrics.py`) with Inlier ARI, Full ARI, and safe Silhouette score.
  - Interactive 2D Plotly visualizers (`figures.py`) with 1:1 isotropic scaling, centroid markers, and MST tree edge overlays.
  - Tabular CSV upload workflow with numeric column mapping and boundary guards.
  - Versioned JSON configuration import/export with instant regeneration.
  - Automated Streamlit test suite (`test_streamlit_dashboard.py`) covering AppTest smoke, metadata, invariants, and bias benchmarks.
- **Completed in Phase M5B:**
  - Scientific performance benchmark engine (`clustering_lab/experiments/benchmarks.py`):
    - Custom Lloyd's K-Means vs custom dense Prim's MST on Gaussian Blobs baseline ($N \in [100, 200, 400, 600]$, 5 measured repetitions per size).
    - Monotonic nanosecond timer (`time.perf_counter_ns()`), converting runtimes to float milliseconds.
    - Dataset generation strictly outside timed region, passing identical coordinate array to both algorithms.
    - Pre-benchmark warm-up excluded from measured statistics.
    - Statistical aggregation: sample mean, median, sample std ($ddof=1$, Bessel's correction), min, max, ratio of means (`mean(MST)/mean(KM)` with zero-division safety).
  - Step-by-step interactive educational algorithm explorers (`clustering_lab/algorithms/explorer.py`):
    - Lloyd's K-Means explorer: Step 0 unassigned points -> K-Means++ $D(x)^2$ centroid placement -> Lloyd Voronoi assignment -> Centroid arithmetic mean update -> Convergence and inertia invariants.
    - Dense Prim's MST explorer: Step 0 root vertex -> $N-1$ minimum cut edge additions -> completed spanning tree -> cutting $k-1$ longest tree edges -> connected component partition via DSU.
    - Guaranteed 100% final mathematical parity with production custom implementations on identical coordinates and seeds.
  - Research data and figure exports (`clustering_lab/experiments/export.py`, `clustering_lab/visualization/figures.py`):
    - Raw trials CSV, summary statistics CSV, benchmark configuration JSON, environment metadata JSON.
    - In-memory Matplotlib publication-quality PNG rendering (`render_benchmark_png`, `render_clustering_png`) with verified `b'\x89PNG'` headers without filesystem writes.
  - Streamlit UI integration (`app.py`):
    - Dedicated "Performance Benchmarks" view with preflight workload estimate (enforcing safety bound of $\le 200$ executions), live progress bar, scaling curves with sample std error bars, and theoretical complexity discussion ($\mathcal{O}(I \cdot N \cdot k \cdot D)$ vs $\mathcal{O}(N^2)$).
    - Dedicated "Algorithm Explorer" view with topology controls ($N \le 60$), interactive step cockpit (First, Prev, Slider, Next, Last, Reset), step descriptions with LaTeX math, isotropic 1:1 Plotly figure, and production parity verification card.
  - Automated test suite:
    - 168 passing automated tests across 12 Pytest modules verified on Python 3.12 (0 failures, 0 skips).
    - Measured statement coverage: 86.0% overall application line coverage (2,711 statements) and ~90.92% scientific core library coverage (1,995 statements).
  - Formal documentation specifications:
    - Performance Benchmark Specification (`docs/PERFORMANCE_BENCHMARK_SPECIFICATION.md`).
    - Algorithm Explorer Guide (`docs/ALGORITHM_EXPLORER_GUIDE.md`).
- **Completed in Stage 06:**
  - Comprehensive user-led manual acceptance testing campaign across all eight application modules.
  - Successfully verified in Brave browser on Windows 11; formally approved and accepted by project owner on October 15, 2026.
- **Stage 07: Final Release & Academic Handoff (In Progress):**
  - Read-only release readiness audit completed (Prompt 1).
  - Documentation synchronization, privacy remediation, and draft release notes preparation under way (Prompt 2).
  - Final QA validation and release packaging in progress (Prompt 3). Release tagging (`v1.0.0-final`) and GitHub push pending explicit owner authorization.
