# Python Clustering Laboratory (`python_app`)
## MST vs K-Means Robustness Analysis — Phase M1: Foundation

### Academic Information
- **Course:** Pattern Matching Lab (`BCS-DS-777`)
- **Institution:** Manav Rachna International Institute of Research and Studies (MRIIRS), School of Engineering & Technology
- **Degree:** B.Tech Computer Science & Engineering (AIML), 7th Semester (2026–2027)
- **Student Researchers:**
  - Himanshu Gupta (Roll No: `[REDACTED_STUDENT_IDENTIFIER]`)
  - Parth Yadav (Roll No: `[REDACTED_STUDENT_IDENTIFIER]`)
- **Repository Branch:** `feature/python-streamlit-migration`
- **Preserved Main Checkpoint:** `0864323`

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
├── app.py                      # Main Streamlit dashboard entry point (foundation stage)
├── requirements.txt            # Production application dependencies (Python 3.12)
├── requirements-dev.txt        # QA and development testing dependencies (-r requirements.txt + pytest)
├── README.md                   # This documentation guide
├── docs/
│   ├── ALGORITHM_SPECIFICATION.md # Formal mathematical definitions, complexities, and biases
│   ├── DATASET_AND_REPRODUCIBILITY_SPECIFICATION.md # Dataset topologies, noise decoupling & CSV specs
│   ├── STREAMLIT_DASHBOARD_GUIDE.md # Viva demonstration script and dashboard manual
│   └── ROBUSTNESS_EXPERIMENT_SPECIFICATION.md # Phase M5A robustness sweeps, metrics & statistical design
├── clustering_lab/             # Core scientific Python research package
│   ├── __init__.py             # Package metadata and version definition
│   ├── algorithms/             # Clustering algorithm implementations
│   │   ├── __init__.py         # Package exports (KMeans, MSTClustering)
│   │   ├── kmeans.py           # Lloyd's K-Means with K-Means++ and deterministic tie-breaking
│   │   └── mst.py              # Dense Prim's MST with single-linkage cut and DSU
│   ├── data/                   # Synthetic dataset generation, contamination & CSV loader
│   │   ├── __init__.py         # Data layer public API exports
│   │   ├── dataset.py          # Standardized immutable Dataset container and validation
│   │   ├── noise.py            # Decoupled Gaussian jitter and uniform outlier pipeline
│   │   ├── synthetic.py        # Blobs, Moons, and Circles synthetic generators
│   │   ├── csv_loader.py       # Secure, UI-independent CSV parser with categorical encoding
│   │   └── config.py           # Versioned JSON experiment configuration schema (1.0.0)
│   ├── experiments/            # Automated noise sweeps & parameter sweep runners (Phase M5A)
│   │   ├── __init__.py         # Public exports (SweepConfig, run_robustness_experiment, etc.)
│   │   ├── sweeps.py           # SweepConfig, sweep types, presets (Quick/Extended) and validation
│   │   ├── runner.py           # Paired execution engine with matched baseline association
│   │   ├── aggregation.py      # Monte Carlo statistical aggregation (mean, sample std dev ddof=1)
│   │   └── export.py           # Provenance-isolated CSV and JSON serialization
│   ├── evaluation/             # Quantitative validation metrics (Phase M4)
│   │   ├── __init__.py
│   │   └── metrics.py          # Inlier ARI, Full ARI, safe Silhouette, runtime
│   ├── visualization/          # Static and interactive charting utilities (Phase M4/M5A)
│   │   ├── __init__.py
│   │   └── figures.py          # 2D scatter plots, 1:1 scaling, and robustness sweep curves
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
    └── test_robustness_experiment.py # Phase M5A paired sweeps, statistical aggregation, and safety bounds
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

## 6. Streamlit Dashboard Usage & Features (Phase M4)

### Running the Application Locally
Launch the interactive research dashboard with:
```bash
streamlit run python_app/app.py
```

### Module Organization
The dashboard is partitioned into 6 core navigation modules:
1. **Overview:** Official research objective, project metadata, student details, and migration status.
2. **Clustering Playground:** Interactive parameter controls, simultaneous execution of Lloyd's K-Means and Prim's MST on the same feature matrix $X$, 2D Plotly visualizations with equal 1:1 scaling, and side-by-side quantitative metrics.
3. **Robustness Analysis (Phase M5A):** Automated paired perturbation sweeps (Gaussian noise and uniform outliers), Monte Carlo statistical aggregation across deterministic seeds, matched baseline degradation curves, and provenance-isolated CSV/JSON exports.
4. **Dataset & CSV Import:** Secure upload of custom 2D tabular CSV datasets with automatic numeric column detection, optional ground-truth label mapping, and validation guards.
5. **Reproducibility & Configuration:** Export and import of versioned JSON configuration files compliant with `ExperimentConfig` schema `1.0.0`.
6. **Methodology / Help:** Algorithmic inductive biases, mathematical definitions of metrics, and a step-by-step viva demonstration walkthrough.

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
- **Completed in Phase M5A:**
  - Scientific robustness experiment engine (`clustering_lab/experiments/` with `sweeps.py`, `runner.py`, `aggregation.py`, `export.py`).
  - Controlled perturbation sweeps: isolated Gaussian noise sweep ($\sigma \in [0.00, 0.20]$, outlier rate 0%) and isolated uniform outlier sweep ($r \in [0\%, 20\%]$, baseline $\sigma=0.05$).
  - Dual execution regimes: Quick mode (seeds 11, 22, 33; 3 trials/level) and Extended mode (10 deterministic seeds: 11, 22, 33, 44, 55, 66, 77, 88, 99, 101; 10 trials/level).
  - Paired identical coordinates and ground-truth guarantee: Lloyd's K-Means and Prim's MST evaluated on exact bitwise-identical feature matrices and inlier masks.
  - Matched baseline delta metrics: signed ARI change ($\Delta \text{ARI}$) and non-negative degradation loss ($\max(0, \text{ARI}_{\text{base}} - \text{ARI}_{\text{curr}})$) paired strictly by dataset family, seed, and algorithm (noise baseline at $\sigma=0.00, r=0.00$; outlier baseline at $\sigma=0.05, r=0.00$ to eliminate noise confounders).
  - Rigorous statistical aggregation: Sample mean ($\bar{x}$) and sample standard deviation ($s$) computed using Bessel's correction ($ddof=1$, $s=0.0$ for $n \le 1$).
  - Dedicated "Robustness Analysis" Streamlit navigation module with pre-flight trial computation bounds ($N_{\text{inliers}} \le 500$, max 500 trials), Plotly error-bar trendlines, matched degradation curves, and honest findings synthesis.
  - Provenance-isolated CSV/JSON data export: raw trial records, aggregated summaries, experiment configuration, and runtime environment/package metadata.
  - Automated scientific test suite (`test_robustness_experiment.py`) with 15 tests verifying invariants, isolation, baseline matching, and AppTest UI rendering (96 total tests passing).
  - Formal experiment specification (`docs/ROBUSTNESS_EXPERIMENT_SPECIFICATION.md`).
- **Scheduled for Subsequent Phases:**
  - Phase M5B: Algorithmic performance benchmarking, empirical runtime complexity scaling ($O(N)$ vs $O(N^2)$), memory footprint profiling, and advanced algorithm explorer modules.
