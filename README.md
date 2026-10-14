# Quantitative Evaluation of Graph-Theoretic vs Centroid-Based Clustering Under Geometric and Contamination Perturbations

**A Comparative Robustness and Inductive Bias Laboratory**

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Streamlit Cloud](https://img.shields.io/badge/Streamlit-Live%20Application-FF4B4B.svg)](https://mst-kmeans-robustness-analysis.streamlit.app/)

---

## 1. Project Overview & Research Objectives

In unsupervised pattern recognition and machine learning, clustering algorithms exhibit distinct **inductive biases**—implicit mathematical assumptions regarding cluster geometry, density distributions, and separation boundaries:

- **Centroid-Based Clustering (Lloyd's K-Means with K-Means++):**
  Partitions feature space into $k$ convex Voronoi polyhedra by minimizing the within-cluster sum of squared Euclidean distances (inertia):
  $$\arg\min_S \sum_{i=1}^k \sum_{x \in S_i} \|x - \mu_i\|_2^2$$
  *Inductive Bias:* Assumes compact, convex, isotropic, linearly separable clusters.
  *Expected Failure Mode:* Cannot partition non-convex, manifold-based topologies (such as interlocking crescents or concentric rings), necessarily cutting across manifolds with linear hyperplanes regardless of iteration budget.

- **Graph-Theoretic Clustering (Dense Prim's Euclidean Minimum Spanning Tree):**
  Constructs an exact Minimum Spanning Tree across all observations and deletes the $k-1$ longest edges to yield $k$ connected components via Disjoint Set Union (DSU):
  $$\text{Cut } k-1 \text{ edges minimizing single-linkage boundary distance}$$
  *Inductive Bias:* Assumes arbitrary manifold connectivity based on local geometric proximity.
  *Expected Failure Mode:* Highly vulnerable to single-linkage chaining and uniform outlier contamination, where isolated noise observations consume edge cuts or bridge distinct clusters.

### Research Questions
1. How do topological manifold non-convexities affect partition fidelity between hyperplane and graph-based models?
2. Under what rate of uniform bounding-box outlier contamination ($\epsilon$) does graph-theoretic connectivity experience catastrophic breakdown?
3. How does continuous Gaussian coordinate jitter ($\sigma$) compare to discrete contamination when evaluated on inliers versus the full dataset?

---

## 2. Interactive Web Platform

The primary research platform is deployed as an interactive multi-module Streamlit laboratory:

**Live Application URL:** [https://mst-kmeans-robustness-analysis.streamlit.app/](https://mst-kmeans-robustness-analysis.streamlit.app/)

The application provides real-time dual-algorithm clustering, parameter manipulation, wall-clock performance benchmarking, step-by-step educational trace visualizers, paired robustness sweeps, and CSV/JSON provenance exports.

---

## 3. Academic Attribution

This project is developed as part of the academic curriculum for:

- **Course:** Pattern Matching Lab (`BCS-DS-777`)
- **Degree:** B.Tech Computer Science & Engineering (Artificial Intelligence & Machine Learning)
- **Semester:** 7th Semester (Academic Year 2026–2027)
- **Institution:** School of Engineering & Technology, Manav Rachna International Institute of Research and Studies (MRIIRS), Faridabad, India
- **Faculty Guide / Instructor:** **Mr. Aman Kumar**, Assistant Professor
- **Student Researchers (Equal Academic Contribution):**
  - **Himanshu Gupta**
  - **Parth Yadav**

*Note on Privacy Compliance:* Institutional student registration identifiers are strictly excluded from public web dashboards, figures, and exported datasets.

---

## 4. Implemented Streamlit Modules

The platform is organized into eight specialized views accessible via the sidebar navigation:

1. **Overview:**
   Introduces the research abstract, comparative inductive bias foundations, system status badges, and interactive topology preview.
2. **Clustering Playground:**
   Side-by-side dual clustering on Gaussian Blobs, Two Moons, Concentric Circles, or user-uploaded datasets. Visualizes decision boundaries (Voronoi overlays for K-Means; tree edges and cut boundaries for Prim MST) with locked 1:1 isotropic scaling and metrics tables. Features non-collapsing state persistence when parameters are modified.
3. **Performance Benchmarks:**
   High-resolution monotonic execution-time profiling (`time.perf_counter`) comparing $O(N^2)$ Prim distance relaxation against $O(N \cdot k \cdot I)$ Lloyd iterations. Evaluates the ratio of means ($\bar{t}_{\text{MST}} / \bar{t}_{\text{KM}}$) and exports benchmark CSVs.
4. **Algorithm Explorer:**
   Educational trace generator stepping through individual algorithm iterations on micro-datasets ($N \le 60$). Traces centroid migrations and active Prim edge candidate relaxations.
5. **Robustness Analysis:**
   Paired Monte Carlo sweeps across Gaussian noise ($\sigma \in [0.00, 0.20]$) and uniform outliers ($\epsilon \in [0.00, 0.20]$). Generates multi-series charts with shaded $\pm 1\sigma$ sample standard deviation error bands, tracking Inlier ARI and Full ARI degradation.
6. **Dataset & CSV Import:**
   Tabular CSV ingestion tool supporting user datasets up to 5MB and 10,000 observations. Features automated delimiter detection, column mapping, distribution histograms, and direct handoff to the Playground.
7. **Reproducibility & Configuration:**
   Versioned JSON configuration management (schema v1.0.0). Allows researchers to export and import exact experiment states for reproducible replication.
8. **Methodology / Help:**
   Formal mathematical definitions, computational complexities, objective functions, Disjoint Set Union mechanics, and academic viva defense questions.

---

## 5. Technology Stack & Scientific Architecture

The core algorithms in this repository are **custom, pure NumPy implementations** built from first mathematical principles. External machine learning libraries are utilized strictly for reference validation and baseline testing.

- **Language & Runtime:** Python 3.12 (64-bit)
- **Web Framework:** Streamlit ($\ge 1.35.0, < 2.0.0$)
- **Numerical Computing:** NumPy ($\ge 1.26.4, < 2.0.0$), Pandas ($\ge 2.2.0, < 3.0.0$), SciPy ($\ge 1.12.0, < 2.0.0$), PyArrow ($\ge 14.0.0, < 26.0.0$)
- **Machine Learning Reference:** scikit-learn ($\ge 1.4.0, < 2.0.0$) — reference parity checks and evaluation metrics
- **Interactive Visualization:** Plotly ($\ge 5.20.0, < 6.0.0$) — 1:1 isotropic 2D scatter plots and multi-series curves
- **Static Graphics:** Matplotlib ($\ge 3.8.0, < 4.0.0$) — publication-ready PNG export figures
- **Testing & Quality Assurance:** Pytest ($\ge 8.0.0, < 9.0.0$) with automated GitHub Actions CI

---

## 6. Repository Layout

```
MST-KMeans-Robustness-Analysis/
├── .devcontainer/
│   └── devcontainer.json          # Standardized Python 3.12 Dev Container configuration
├── .github/
│   └── workflows/
│       └── python-ci.yml          # GitHub Actions CI workflow (Python 3.12 / Ubuntu)
├── README.md                      # This primary repository landing page
├── index.html                     # Preserved legacy Vanilla JS entrypoint
├── css/                           # Preserved Vanilla JS styling
├── js/                            # Preserved Vanilla JS algorithms and Canvas renderers
├── tests/                         # Preserved Vanilla JS client-side test runner
├── docs/                          # Comprehensive Academic Reports, Audits & Blueprints
│   ├── FINALIZATION_MASTER_AUDIT.md      # Comprehensive scientific and code audit
│   └── FINALIZATION_MASTER_BLUEPRINT.md  # Definitive 8-stage finalization roadmap
└── python_app/                    # Core Python Research Platform
    ├── app.py                     # Streamlit multi-module application entrypoint
    ├── requirements.txt           # Pinned production dependencies
    ├── requirements-dev.txt       # Development & QA testing dependencies
    ├── README.md                  # Detailed Python technical documentation
    ├── docs/                      # Scientific algorithm & experiment specifications
    ├── tests/                     # 12 Pytest test modules (129 unit/integration/UI tests)
    └── clustering_lab/            # Modular Scientific Python Package
        ├── algorithms/            # Pure NumPy K-Means, Prim MST, and Explorer tracers
        ├── data/                  # Synthetic generators, noise pipelines, CSV parser, config
        ├── evaluation/            # Inlier ARI, Full ARI, and Silhouette metrics
        ├── experiments/           # Paired robustness sweeps, benchmarks, and export engines
        ├── utils/                 # Mathematical helpers and sample standard deviation
        └── visualization/         # Plotly isotropic renderers and Matplotlib dark exporter
```

---

## 7. Local Installation & Quickstart

### Prerequisites
- Python 3.12 (64-bit) installed locally, **or** [uv](https://docs.astral.sh/uv/) (recommended for fast virtual environment management).

### Option A: Using `uv` (Recommended)

From the repository root:

```bash
# Verify Python version
uv run --python 3.12 python --version

# Run the complete test suite (129 passing tests)
uv run --python 3.12 --with-requirements python_app/requirements-dev.txt pytest python_app/tests -v

# Launch the interactive Streamlit dashboard
uv run --python 3.12 --with-requirements python_app/requirements-dev.txt streamlit run python_app/app.py
```

### Option B: Using Standard Python Virtual Environment

#### On Windows (PowerShell):
```powershell
# Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install development and production dependencies
pip install --upgrade pip
pip install -r python_app/requirements-dev.txt

# Run automated tests
$env:PYTHONPATH='python_app'
pytest python_app/tests -v

# Launch Streamlit dashboard
streamlit run python_app/app.py
```

#### On Linux / macOS (Bash):
```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install development and production dependencies
pip install --upgrade pip
pip install -r python_app/requirements-dev.txt

# Run automated tests
PYTHONPATH=python_app pytest python_app/tests -v

# Launch Streamlit dashboard
streamlit run python_app/app.py
```

The application will be accessible locally at `http://localhost:8501`.

### Option C: Using VS Code Dev Containers or GitHub Codespaces

1. Open this repository in VS Code with the **Dev Containers** extension installed, or launch directly in **GitHub Codespaces**.
2. Select **Reopen in Container** when prompted. The container environment builds automatically using `mcr.microsoft.com/devcontainers/python:1-3.12-bookworm` and installs all dependencies from `python_app/requirements-dev.txt`.
3. From the terminal at the repository root, launch the Streamlit dashboard:
   ```bash
   python3 -m streamlit run python_app/app.py --server.address 0.0.0.0 --server.port 8501
   ```
4. Once the server starts listening, Codespaces and Dev Containers automatically forward port `8501` and open the application preview (or access directly at `http://localhost:8501`).

---

## 8. Reproducibility & Research Transparency

The platform is designed around strict scientific reproducibility principles:

1. **Deterministic PRNG Seeding:**
   All stochastic operations (K-Means++ initialization, Gaussian coordinate jitter, uniform outlier injection) utilize `np.random.default_rng(seed)`. Supplying the same integer seed guarantees identical datasets, partitions, and metrics.
2. **Paired Comparisons:**
   In both interactive Playground and Robustness Sweeps, K-Means and Prim MST are evaluated on the exact same feature matrix instance $X$.
3. **Inlier Isolation:**
   When uniform outliers are added, ground-truth inliers are tagged in an immutable boolean `inlier_mask`. Adjusted Rand Index is evaluated both on the entire dataset (Full ARI) and strictly on genuine manifold inliers (Inlier ARI) to isolate structural degradation.
4. **Versioned Configuration Payloads:**
   Experiment setups can be exported and imported as JSON conforming to `ExperimentConfig` schema version 1.0.0.

---

## 9. Scientific Limitations

While the platform achieves strong mathematical rigor, the following scientific boundaries are acknowledged:

- **Convexity Boundary of K-Means:**
  K-Means clusters by minimizing squared Euclidean distance to arithmetic centroids, which mathematically mandates linear hyperplane boundaries. It cannot learn concentric or spiral structures regardless of iteration count.
- **Single-Linkage Vulnerability of MST:**
  Prim's MST with longest-edge cuts is mathematically equivalent to single-linkage hierarchical clustering cut at $k$ components. It is susceptible to "chaining" when even a single noise point falls between distinct clusters, and to "outlier isolation" when distant outliers consume the $k-1$ cuts.
- **Hardware & Multi-Tasking Jitter:**
  Wall-clock benchmark timings are subject to CPU thermal states, background operating system task scheduling, and interpreter overhead. Benchmarks report sample mean $\pm$ standard deviation across repetitions ($R \ge 5$) rather than deterministic timing guarantees.
- **Monte Carlo Sample Budget:**
  Quick Mode (3 seeds, 72 paired trials) offers rapid interactive feedback. For academic publication data, Extended Mode (10 seeds, 240 paired trials) or custom sweeps should be used to minimize standard error.

---

## 10. Preserved Legacy JavaScript Implementation

The original client-side Vanilla JavaScript and HTML5 Canvas implementation created for initial viva presentation remains fully preserved in the repository root:

- **Entrypoint:** [index.html](file:///d:/7th%20Sem/PM/Mini%20project/MST-KMeans-Robustness-Analysis/index.html)
- **Zero Installation:** Can be opened directly in any web browser (`file:///.../index.html`) without a backend server or dependencies.
- **Algorithms:** Independent JavaScript implementations of Lloyd's K-Means and Prim's MST with canvas-based visual step progression.

---

## 11. Project Status & Documentation

The laboratory platform is deployed and currently undergoing structured finalization according to the approved engineering roadmap:

- **Master Audit Report:** [docs/FINALIZATION_MASTER_AUDIT.md](docs/FINALIZATION_MASTER_AUDIT.md) — Comprehensive code, scientific, security, and UI/UX audit.
- **Finalization Blueprint:** [docs/FINALIZATION_MASTER_BLUEPRINT.md](docs/FINALIZATION_MASTER_BLUEPRINT.md) — Approved 8-stage finalization work breakdown structure.
- **Python Technical Guide:** [python_app/README.md](python_app/README.md) — Deep-dive architecture and API specifications for the scientific engine.
- **Formal Specifications:** [python_app/docs/](python_app/docs/) — Algorithm, dataset, benchmark, and robustness sweep mathematical specs.
