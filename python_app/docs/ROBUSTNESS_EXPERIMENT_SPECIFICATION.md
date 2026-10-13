# Robustness Experiment Specification
## Scientific Experiment Engine & Monte Carlo Statistical Benchmarking

### Academic Project Information
- **Course:** Pattern Matching Lab (`BCS-DS-777`)
- **Institution:** Manav Rachna International Institute of Research and Studies (MRIIRS), School of Engineering & Technology
- **Degree:** B.Tech Computer Science & Engineering (AIML), 7th Semester (2026–2027)
- **Student Researchers:**
  - Himanshu Gupta (Roll No: `[REDACTED_STUDENT_IDENTIFIER]`)
  - Parth Yadav (Roll No: `[REDACTED_STUDENT_IDENTIFIER]`)
- **Course Instructor:** Mr. Aman Kumar, Assistant Professor
- **Active Branch:** `feature/python-streamlit-migration`
- **Module Path:** `python_app/clustering_lab/experiments/`

---

## 1. Scientific Motivation & Research Question

### Primary Research Question
> **How do graph-theoretic Minimum Spanning Tree (MST) clustering and centroid-based Lloyd's K-Means clustering compare under Gaussian coordinate jitter, uniform outlier contamination, and non-convex geometric data distributions?**

### Algorithmic Inductive Biases
1. **Centroid-Based Lloyd's K-Means:**
   - Optimizes Within-Cluster Sum of Squares (Inertia):
     $$J = \sum_{i=1}^N \| X_i - \mu_{c(i)} \|^2$$
   - Inductive bias assumes isotropic, convex, globular clusters with roughly equal dispersion.
   - Hypothesis: K-Means will struggle on non-convex manifolds (such as concentric rings and crescent moons) because linear Voronoi hyperplanes cannot separate non-linearly separable topological structures. However, its arithmetic mean centroids should remain relatively stable under uniform outlier noise.

2. **Graph-Theoretic Prim's MST Clustering:**
   - Constructs a Euclidean Minimum Spanning Tree $T = (V, E)$ on the complete geometric graph, then removes the $k - 1$ longest tree edges to yield $k$ connected components.
   - Inductive bias assumes clusters are continuous submanifolds separated by empty spatial gaps.
   - Hypothesis: Under clean zero-noise conditions, MST will trace arbitrary continuous curvilinear manifolds with high accuracy. However, single-linkage partitioning is highly sensitive to the "chaining effect": a small number of uniform outliers landing in the inter-manifold gap will create short spurious edges, causing distinct clusters to merge artificially.

---

## 2. Controlled Experiment Design

### 2.1 Synthetic Dataset Manifolds
Experiments evaluate three standardized synthetic 2D distributions:
- **Gaussian Blobs (Convex Baseline):** Balanced globular clusters symmetrically arranged on a circle ($k=3$, $\sigma_{\text{cluster}}=0.4$, radius $r=3.5$).
- **Two Moons (Non-Convex Interlocking Crescents):** Interleaving half-circles ($k=2$).
- **Concentric Circles (Non-Convex Nested Rings):** Concentric rings ($k=2$, inner radius factor $0.45$).

The default research sample size is $N_{\text{inliers}} = 300$ base observations.

### 2.2 Paired Execution Guarantee
For every trial, Lloyd's K-Means and dense Prim's MST execute on the **identical coordinate matrix $X$**, and are evaluated against identical ground-truth labels $y$ and inlier masks. Neither algorithm receives an unfair spatial advantage.

Both algorithms are executed exclusively by the from-scratch pure NumPy implementations (`clustering_lab.algorithms.kmeans` and `clustering_lab.algorithms.mst`).

### 2.3 Separate Univariate Sweeps (Non-Factorial Design)
To isolate specific causal factors without confounding, two separate controlled univariate sweeps are conducted:

1. **Gaussian Noise Sweep:**
   - **Varied Parameter:** Inlier Gaussian jitter standard deviation $\sigma \in \{0.00, 0.05, 0.10, 0.20\}$.
   - **Held Constant:** Outlier contamination rate strictly fixed at $0\%$ ($N_{\text{outliers}} = 0$).
   - **Baseline:** $\sigma = 0.00$ at $0\%$ outliers.

2. **Uniform Outlier Contamination Sweep:**
   - **Varied Parameter:** Outlier contamination fraction $\in \{0\%, 5\%, 10\%, 20\%\}$ ($r \in \{0.00, 0.05, 0.10, 0.20\}$).
   - **Held Constant:** Inlier Gaussian jitter fixed at baseline $\sigma = 0.05$.
   - **Outlier Count:** $N_{\text{outliers}} = \text{round}(N_{\text{inliers}} \times r)$.
   - **Baseline:** $r = 0.00$ at baseline noise $\sigma = 0.05$.

*(Scientific Note: These represent two separate univariate sweeps around well-defined operating points, NOT a full factorial grid).*

### 2.4 Deterministic Seed Schedules
- **Quick Mode (3 Seeds):** `[11, 22, 33]`. Used for rapid interactive demonstrations and viva verification.
- **Extended Mode (10 Seeds):** `[11, 22, 33, 44, 55, 66, 77, 88, 99, 101]`. Recommended for scientific publications to compute meaningful sample standard deviations.
- **Custom Mode:** Allows user-specified seed lists within validated safety limits.

NumPy's `SeedSequence` is used to spawn independent PRNG streams for inlier generation and outlier sampling, ensuring decoupled contamination independence.

---

## 3. Mathematical Metrics & Formulations

### 3.1 Inlier Adjusted Rand Index (Inlier ARI)
Evaluated strictly on genuine inlier points ($N_{\text{inliers}}$):
$$\text{ARI}_{\text{inlier}} = \text{ARI}(y_{\text{true}}[\text{inlier\_mask}], \, y_{\text{pred}}[\text{inlier\_mask}])$$
- Range: $[-0.5, 1.0]$. A score of $1.0$ indicates perfect partition recovery.
- Measures how well the internal cluster manifold topology was preserved despite surrounding noise.

### 3.2 Full-Data Adjusted Rand Index (Full-Data ARI)
Evaluated across all points including outliers (label $-1$):
$$\text{ARI}_{\text{full}} = \text{ARI}(y_{\text{true}}, \, y_{\text{pred}})$$
- Because standard algorithms assign all points into $k$ clusters without an outlier reject class, full ARI naturally penalizes both algorithms for absorbing outliers.

### 3.3 Matched Baseline Pairing & Confound Elimination
To ensure that performance degradation isolates only the intended perturbation, matched baselines are defined separately for each sweep type and paired strictly by **dataset family, random seed, underlying clean inlier coordinates, and clustering algorithm**:
- **Noise Sweep Matched Baseline:** Evaluated at $\sigma = 0.00$ with outlier fraction $r = 0.00$ on the identical family, seed, and algorithm.
- **Outlier Sweep Matched Baseline:** Evaluated at $r = 0.00$ with the **same fixed inlier noise $\sigma = 0.05$** (or `outlier_sweep_base_noise`) on the identical family, seed, and algorithm.
- **Confound Elimination:** Pairing outlier trials against a baseline that already contains the fixed $\sigma = 0.05$ jitter ensures that the calculated $\Delta \text{ARI}$ and degradation loss isolate *only* the causal effect of outlier contamination, rather than confounding outlier addition with initial Gaussian noise.

### 3.4 Signed ARI Change vs Nonnegative Degradation Loss
1. **Signed ARI Change ($\Delta \text{ARI}$):**
   $$\Delta \text{ARI} = \text{ARI}_{\text{trial}} - \text{ARI}_{\text{baseline}}$$
   - Unconstrained signed value. Can be positive (performance improved), negative (degraded), or zero.
2. **Nonnegative Degradation Loss:**
   $$\text{Degradation} = \max(0.0, \, \text{ARI}_{\text{baseline}} - \text{ARI}_{\text{trial}})$$
   - Quantifies the magnitude of performance loss, clamped to $\ge 0.0$.
   - Explicitly distinguished from signed change: if performance improves, degradation loss is strictly $0.0$.

### 3.5 Monte Carlo Statistical Aggregation
For each parameter configuration $(F, \text{sweep}, v, \text{algorithm})$ repeated over $n$ seeds:
- **Sample Mean:**
  $$\bar{x} = \frac{1}{n} \sum_{i=1}^n x_i$$
- **Sample Standard Deviation (Bessel's Correction, $ddof=1$):**
  $$s = \sqrt{\frac{1}{n - 1} \sum_{i=1}^n (x_i - \bar{x})^2} \quad \text{for } n \ge 2$$
  *(For $n = 1$, $s \equiv 0.0$ with clear documentation of single-trial status).*

---

## 4. Computational Safety & Bounded Interactivity

To guarantee responsive execution on commodity hardware without browser or server timeouts:
1. **Inlier Sample Limits:** Enforced in $[20, 500]$ ($N_{\text{total}} \le 600$ points with outliers).
2. **Maximum Outlier Rate:** Enforced $\le 30\%$ ($0.30$).
3. **Seed Cap:** At most $20$ deterministic seeds per execution.
4. **Execution Ceiling:** Total paired trials capped at $500$ ($1000$ algorithm executions). Grids exceeding $500$ trials are rejected before computation starts.
5. **State Consistency:** Changing parameter controls after a run displays an explicit warning preventing stale results from masquerading as matching the new settings.

---

## 5. Data Export & Provenance Isolation

Exported artifacts are strictly isolated from the legacy JavaScript files in `results/`:

| Artifact | Filename | Format | Description |
| :--- | :--- | :--- | :--- |
| **Raw Trials CSV** | `python_robustness_raw_trials.csv` | CSV | Row-by-row records of every individual trial run. |
| **Aggregated Summary CSV** | `python_robustness_summary.csv` | CSV | Sample mean and std dev across repeated seeds for each sweep point. |
| **Configuration JSON** | `robustness_config.json` | JSON | Machine-readable `SweepConfig` specification. |
| **Environment Metadata** | `environment_metadata.json` | JSON | Complete system, Python, and package provenance records. |

### Raw Trial CSV Schema
- `dataset_family`: Topology (`blobs`, `moons`, `circles`)
- `sweep_type`: Sweep category (`noise`, `outlier`)
- `parameter_name`: Varied parameter (`noise_sigma`, `outlier_rate`)
- `parameter_value`: Numeric parameter value
- `seed`: PRNG seed
- `n_inliers`: Inlier count
- `n_outliers`: Outlier count
- `n_total`: Total observations
- `k`: Target cluster count
- `algorithm`: Clustering algorithm (`Lloyd K-Means`, `Prim MST`)
- `inlier_ari`: Inlier ARI score
- `full_ari`: Full-Data ARI score
- `runtime_ms`: Measured execution time in milliseconds
- `baseline_inlier_ari`: Matched baseline Inlier ARI
- `delta_inlier_ari`: Signed ARI change ($\text{ARI} - \text{Baseline}$)
- `degradation_inlier_ari`: Nonnegative degradation loss ($\max(0, \text{Baseline} - \text{ARI})$)

---

## 6. Summary of Empirical Takeaways

1. **Convex Topologies (Gaussian Blobs):** Both algorithms perform with high accuracy ($>0.95$) at low noise, degrading gradually as variance spreads.
2. **Curvilinear Topologies (Concentric Circles & Two Moons):**
   - Clean baseline: MST recovers non-convex manifolds ($1.00$ ARI), whereas K-Means suffers from convex partitioning bias ($<0.50$ ARI).
   - Under uniform outliers: MST degrades rapidly due to the single-linkage chaining effect across inter-cluster gaps.
3. **Statistical Sample Size:** Quick mode ($N=3$) provides qualitative demonstration; Extended mode ($N=10$) is required for formal confidence interval estimation.
