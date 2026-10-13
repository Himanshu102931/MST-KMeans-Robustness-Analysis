# Streamlit Dashboard User & Viva Demonstration Guide
## MST vs K-Means Robustness Analysis

### Academic Project Details
- **Course:** Pattern Matching Lab (`BCS-DS-777`)
- **Institution:** Manav Rachna International Institute of Research and Studies (MRIIRS), School of Engineering & Technology
- **Degree:** B.Tech Computer Science & Engineering (AIML), 7th Semester (2026–2027)
- **Student Researchers:**
  - Himanshu Gupta (Roll No: `[REDACTED_STUDENT_IDENTIFIER]`)
  - Parth Yadav (Roll No: `[REDACTED_STUDENT_IDENTIFIER]`)
- **Course Instructor:** Mr. Aman Kumar, Assistant Professor
- **Branch:** `feature/python-streamlit-migration`

---

## 1. Quick Start: Launching the Application

Ensure your Python 3.12 environment has dependencies installed from `python_app/requirements.txt`:
```bash
streamlit run python_app/app.py
```
Streamlit will automatically open the dashboard in your default browser at `http://localhost:8501`.

---

## 2. Dashboard Architecture & Navigation

The dashboard is structured into five cohesive academic modules accessible via the sidebar:

| Module | Purpose |
| :--- | :--- |
| **Overview** | Official research objective, university metadata, student information, and project roadmap. |
| **Clustering Playground** | Interactive parameter tweaking, simultaneous dual-algorithm execution on identical feature arrays, 2D Plotly scatter plots with 1:1 isotropic scaling, and side-by-side metric tables. |
| **Dataset & CSV Import** | Secure parser for external 2D tabular CSV benchmarks with column mapping and boundary validation guards. |
| **Reproducibility & Configuration** | Bi-directional JSON configuration import and export adhering to `ExperimentConfig` version `1.0.0`. |
| **Methodology / Help** | Algorithmic fundamentals, inductive biases, metric glossary, and oral examination walkthrough. |

---

## 3. Step-by-Step Viva Demonstration Script

Follow this structured, 5-minute walkthrough during your viva or project presentation.

### Stage 1: State the Research Question
> *"Good morning, sir. Our project investigates the clustering robustness of graph-theoretic Minimum Spanning Tree (MST) clustering against centroid-based Lloyd's K-Means clustering. Specifically, we test their resilience under non-convex geometric topologies, inlier Gaussian jitter, and random uniform outlier contamination."*

Navigate to the **Overview** tab to display the official research objective and academic credentials.

---

### Stage 2: The Baseline Experiment (Gaussian Blobs)
1. In the sidebar, select **Clustering Playground**.
2. Select **Gaussian Blobs** ($k=3$, Inliers: $300$, Noise: $0.0$, Outliers: $0\%$).
3. Click **🚀 Generate & Run Clustering**.
4. Point out the results:
   - **Visualizations:** Both algorithms correctly isolate the 3 circular clusters.
   - **Metrics:** Both algorithms achieve **Inlier ARI $> 0.95$**.
5. **Viva Talking Point:**
   > *"When clusters are globular, convex, and well-separated, both K-Means and Prim's MST clustering perform exceptionally well. K-Means finds optimal centroids minimizing within-cluster variance, while MST connects intra-cluster neighbors with short edges and removes the long inter-cluster edges."*

---

### Stage 3: The Topological Stress Test (Concentric Circles & Two Moons)
1. Change **Dataset Topology** to **Concentric Circles** (fixed $k=2$, factor: $0.45$, Noise: $0.0$, Outliers: $0\%$).
2. Click **🚀 Generate & Run Clustering**.
3. Direct the examiner's attention to the contrast under clean baseline conditions:
   - **Lloyd's K-Means:** Struggles with nested rings (**Inlier ARI $\approx 0.0$**). It cuts across the concentric rings with a linear Voronoi hyperplane because it cannot form non-convex partition boundaries.
   - **Prim's MST:** Separates the clean rings cleanly (**Inlier ARI $= 1.0000$**). Single-linkage graph cutting follows the continuous ring manifold across the open spatial gap.
4. Switch to **Two Moons** ($k=2$, Noise: $0.0$, Outliers: $0\%$) and re-run.
   - **K-Means:** Slices through the crescent moons (**Inlier ARI $< 0.50$**).
   - **MST:** Recovers the two interlocking manifolds under clean conditions (**Inlier ARI $= 1.0000$**).
5. **Viva Talking Point:**
   > *"Under zero-noise conditions, this illustrates the fundamental difference in inductive bias: centroid-based algorithms assume convex, Voronoi-partitioned clusters, whereas graph-theoretic MST clustering assumes path connectivity via short edges. However, as we demonstrate next, MST's advantage on non-linear manifolds is not unconditional once noise bridges are present."*

---

### Stage 4: Robustness Perturbations & The "Chaining Effect"
1. Keep **Two Moons** selected.
2. Increase **Gaussian Noise ($\sigma$)** to `0.12` and set **Outlier Contamination Rate** to `0.08` (8% outliers).
3. Click **🚀 Generate & Run Clustering**.
4. Inspect the **MST Result** plot with tree edges enabled:
   - Explain how uniform random outliers can land in the spatial gap between the two crescent moons.
   - If an outlier creates a "bridge" where pairwise distances are shorter than the longest intra-cluster edge, Prim's MST links the two distinct moons together—this is the classical **chaining effect**.
5. Point out **Inlier ARI vs Full ARI**:
   - Inlier ARI measures recovery of the genuine crescent points.
   - Full ARI penalizes both algorithms because neither assigns an explicit outlier class.
6. **Viva Talking Point:**
   > *"While MST is not constrained by convex shape assumptions, single-linkage graph partitioning is highly sensitive to noise bridges. Random uniform outliers landing in the spatial gap between two dense manifolds can artificially chain them together, degrading MST robustness."*

---

### Stage 5: Empirical Benchmark CSV Import
1. Select **Dataset & CSV Import** from the sidebar.
2. Upload a sample CSV containing 2 numerical columns (e.g. coordinates $x, y$) and an optional label column.
3. Show the examiner:
   - The interactive table preview and row count reporting.
   - The dropdown column mapping for Feature 1, Feature 2, and Class Label.
   - If no label column is provided, the dashboard reports **ARI as N/A**—emphasize that the system **never invents or fabricates ground-truth metrics**.
4. Click **🚀 Load & Run Clustering on CSV** to demonstrate execution on external data.

---

### Stage 6: Scientific Reproducibility via JSON Configuration
1. Select **Reproducibility & Configuration** from the sidebar.
2. Display the versioned JSON code block adhering to `ExperimentConfig` schema `1.0.0`.
3. Click **⬇️ Download Configuration (.json)**.
4. **Viva Talking Point:**
   > *"Every synthetic benchmark is deterministic. By exporting and importing this versioned configuration, any researcher running this code on any platform will reproduce the exact coordinate matrix, noise jitter, and clustering outcome down to floating-point precision."*

---

## 4. Frequently Asked Viva Questions & Model Answers

### Q1: Why did you implement K-Means and MST from scratch in pure NumPy rather than using `scikit-learn` or `scipy`?
**Model Answer:**
> *"Using library black-boxes obscures algorithm mechanics and tie-breaking behavior. By building Lloyd's K-Means and dense Prim's MST from scratch in pure NumPy, we implemented deterministic K-Means++ initialization, explicit empty-cluster reseeding, and canonical tie-breaking on graph cuts. We use `scipy` and `scikit-learn` strictly in our test suite as independent verification benchmarks."*

---

### Q2: What is the computational time complexity of dense Prim's MST vs K-Means?
**Model Answer:**
> *"Dense Prim's MST runs in $O(N^2)$ time and $O(N)$ auxiliary space. Every step iterates over all unvisited vertices to relax minimum edge distances without storing a dense $N \times N$ matrix. Lloyd's K-Means runs in $O(I \cdot k \cdot N \cdot D)$ time, where $I$ is iteration count, $k$ is clusters, and $D$ is feature dimensions. For interactive dashboard responsiveness, we recommend $N \le 600$ observations for MST."*

---

### Q3: Why is Inlier ARI separated from Full-Data ARI?
**Model Answer:**
> *"In our synthetic benchmark pipeline, uniform outliers are injected with label $-1$. Standard K-Means and MST assign all points into $k$ clusters and do not have an outlier rejection mechanism. Inlier ARI measures whether the core manifold topology was recovered despite noise, whereas Full ARI penalizes algorithms for absorbing outliers into clusters."*

---

### Q4: Can we compare K-Means Inertia with MST Weight?
**Model Answer:**
> *"No, sir. They represent fundamentally different mathematical quantities. K-Means Inertia is the Within-Cluster Sum of Squares (squared Euclidean distances to centroids in units of distance squared). MST Weight is the linear sum of Euclidean edge lengths along the spanning tree (in units of distance). Directly comparing them would be scientifically invalid."*

---

### Q5: Why is the Silhouette Score misleading on Concentric Circles?
**Model Answer:**
> *"The Silhouette Coefficient measures the ratio of intra-cluster distance to nearest neighboring cluster distance. It assumes convex, globular cluster shapes. On concentric rings, a point in the inner circle is geographically closer to the outer ring than to points on the opposite side of its own ring. Consequently, Silhouette gives a low or negative score to concentric rings even when MST partitions them with 100% ground-truth accuracy."*

---

### Q6: How does seed decoupling work in your noise pipeline?
**Model Answer:**
> *"We use NumPy's `SeedSequence` to spawn two independent PRNG streams: one exclusively for inlier Gaussian jitter, and one exclusively for uniform outlier placement. This ensures that changing the outlier contamination rate does not alter the inlier noise coordinates, allowing controlled paired experiments."*

---

## 5. Technical Stack & Deployment Prerequisites

- **Python Runtime:** Python 3.12 (64-bit)
- **Frontend / UI:** Streamlit (`>=1.35.0, <2.0.0`)
- **Charting Engine:** Plotly (`>=5.20.0, <6.0.0`)
- **Scientific Computing:** NumPy, Pandas, SciPy, scikit-learn
- **Automated Testing:** pytest (`>=8.0.0, <9.0.0`) with `streamlit.testing.v1.AppTest`
