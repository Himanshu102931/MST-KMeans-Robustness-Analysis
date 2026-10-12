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
│   └── DATASET_AND_REPRODUCIBILITY_SPECIFICATION.md # Dataset topologies, noise decoupling & CSV specs
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
│   ├── experiments/            # Automated noise sweeps & parameter sweep runners (Phase M4)
│   │   └── __init__.py
│   ├── evaluation/             # Quantitative validation metrics (Phase M4)
│   │   └── __init__.py
│   ├── visualization/          # Static and interactive charting utilities (Phase M5)
│   │   └── __init__.py
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
    └── test_data_io.py         # CSV importing, validation bounds, and JSON config round-trip
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

## 6. Streamlit Dashboard Entry Point & Cloud Deployment

### Entry Point
The primary application entry point is:
```bash
streamlit run python_app/app.py
```

### Cloud Deployment (Future Phase)
Upon completion of the algorithm migration and experimental dashboards:
- The app will be deployed on **Streamlit Community Cloud** (or Linux cloud container) connected to the GitHub repository.
- Configuration will point to the `python_app/app.py` script with `python_app/requirements.txt` for automatic build and hosting.

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
  - GitHub Actions upgraded to Node 24 actions (`checkout@v5`, `setup-python@v7`).
- **Completed in Phase M3:**
  - Standardized immutable `Dataset` container with boundary validation (`dataset.py`).
  - Decoupled Gaussian noise and uniform outlier contamination pipeline (`noise.py`).
  - Synthetic generators: Gaussian Blobs, Two Moons, and Concentric Circles (`synthetic.py`).
  - Secure, UI-independent CSV dataset parser with categorical label encoding (`csv_loader.py`).
  - Versioned JSON experiment configuration schema `1.0.0` with round-trip fidelity (`config.py`).
  - Dataset and reproducibility specification (`docs/DATASET_AND_REPRODUCIBILITY_SPECIFICATION.md`).
  - Refined mathematical definitions in `ALGORITHM_SPECIFICATION.md`.
  - Comprehensive unit test suites (`test_data.py`, `test_data_io.py`).
- **Scheduled for Subsequent Phases:**
  - Phase M4: Robustness experiment engine, Monte Carlo sweep runners, and quantitative evaluation metrics (ARI, NMI, Silhouette).
  - Phase M5: Interactive Streamlit UI and visualization dashboard.
