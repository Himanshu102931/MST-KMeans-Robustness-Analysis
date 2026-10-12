# Experimental Evidence and Research Results Report
**MST-Based Clustering vs. K-Means: Quantitative Robustness Analysis**

* **Course**: Pattern Matching Lab (`BCS-DS-777`)
* **Academic Institution**: Manav Rachna International Institute of Research and Studies (MRIIRS)
* **Lead Researcher / Student**: Himanshu Gupta (Allocation No. 19)
* **Project Partner**: Parth Yadav
* **Git Commit Checkpoint**: `caca5cd` (`main` branch)
* **Execution Environment**: Client-Side Vanilla JavaScript (V8 Engine, Monotonic High-Resolution Timer `performance.now()`)
* **Hardware Architecture**: 16 Logical CPU Threads, x64 Windows 10/11 Architecture (`Win32` platform)

---

## 1. Executive Summary & Research Objective

### 1.1 Allocated Research Objective
The official academic objective of this investigation is to **rigorously compare Minimum Spanning Tree (MST)-based clustering against K-Means clustering under controlled perturbations—specifically additive Gaussian noise, uniform outlier contamination, and non-linear manifold geometry—using objective, quantitative robustness metrics**.

### 1.2 Core Research Questions
1. **Geometric Manifold Disentanglement**: Does MST clustering with single-linkage tree-cutting successfully recover non-convex, manifold-based cluster geometries (concentric rings and interlocking semicircles) where centroid-based Voronoi partitioning (K-Means) is theoretically expected to fail?
2. **Noise Sensitivity ($\sigma$)**: How do gradual increases in isotropic Gaussian noise ($\sigma \in [0.00, 0.20]$) degrade the partition fidelity of MST and K-Means across convex versus non-convex geometries?
3. **Outlier Vulnerability ($\eta$)**: How does uniform ambient outlier contamination ($\eta \in [0\%, 20\%]$) impact single-linkage edge cutting compared to Lloyd's centroid-shifting heuristic when evaluated strictly across ground-truth inliers?
4. **Computational Asymptotics**: How do the practical client-side JavaScript execution runtimes scale for dense Prim's MST ($O(N^2)$) versus Lloyd's K-Means ($O(I \cdot K \cdot N)$) across sample sizes $N \in [100, 600]$?

---

## 2. Experimental Hypotheses & Epistemological Status

To maintain scientific integrity, this report explicitly distinguishes between **hypotheses**, **mathematical expectations**, **directly measured empirical outcomes**, and **subsequent interpretations**.

| Item | Statement | Epistemological Category | Empirical Outcome |
| :--- | :--- | :--- | :--- |
| **H1** | K-Means will fail completely on Concentric Circles ($K=2$) and Two Moons ($K=2$) even in clean conditions because linear Voronoi boundaries cannot separate non-convex clusters. | Mathematical / Theoretical Expectation | **Confirmed**: Clean baseline K-Means achieved $\text{ARI} = -0.0019$ on Circles and $\text{ARI} = 0.1941$ on Moons. |
| **H2** | MST clustering will achieve perfect separation ($\text{ARI} = 1.0000$) on clean non-convex geometries. | Mathematical / Theoretical Expectation | **Confirmed**: Clean baseline MST achieved $\text{ARI} = 1.0000$ on all three datasets (Blobs, Moons, Circles). |
| **H3** | MST clustering is universally superior to K-Means on manifold structures under all perturbation levels. | Hypothesis (Refuted) | **Refuted**: MST is hyper-vulnerable to outlier bridging. In Two Moons, adding just $5\%$ outliers dropped MST Inlier ARI from $1.0000$ to $0.0000$ ($\Delta\text{ARI} = 1.0000$), whereas K-Means degraded by only $0.0022$. |
| **H4** | K-Means is robust to isotropic noise and uniform outliers on convex Gaussian Blobs ($K=3$). | Hypothesis (Confirmed) | **Confirmed**: K-Means maintained $\text{ARI} = 1.0000$ across all noise levels ($\sigma \le 0.20$) and all outlier levels ($\eta \le 20\%$), suffering $\Delta\text{ARI} = 0.0000$. |
| **H5** | MST dense Prim execution scales quadratically ($O(N^2)$) while K-Means scales approximately linearly per iteration ($O(N)$), yielding widening execution disparity as $N$ increases. | Mathematical Expectation & Measured Result | **Confirmed**: At $N=100$, MST took $0.14\text{ ms}$ vs K-Means $0.10\text{ ms}$ ($1.4\times$). At $N=600$, MST took $1.70\text{ ms}$ vs K-Means $0.14\text{ ms}$ ($12.1\times$ to $17.0\times$ speedup for K-Means). |

---

## 3. Dataset Families and Controlled Perturbation Protocol

All synthetic datasets were deterministically generated using an internal pseudo-random number generator (PRNG) initialized with fixed seeds $\mathcal{S} \in \{11, 22, 33\}$. For all robustness trials, the baseline inlier sample count was held fixed at $N_{\text{inliers}} = 300$.

### 3.1 Dataset Geometries
1. **Gaussian Blobs ($K=3$, Convex)**:
   * 3 synthetic isotropic bivariate normal distributions centered in Euclidean 2D space.
   * Ground-truth cluster proportions: Balanced ($100$ points per cluster).
   * Characteristic: Linearly separable, compact, spherical clusters.
2. **Two Moons ($K=2$, Non-Convex Interlocking Manifolds)**:
   * Two interleaving semicircular arcs separated by a non-linear Euclidean margin.
   * Ground-truth cluster proportions: Balanced ($150$ points per crescent).
   * Characteristic: Connected continuous manifolds requiring transitivity rather than spatial centrality.
3. **Concentric Circles ($K=2$, Non-Convex Nested Rings)**:
   * An inner circle of radius $r_1$ surrounded by a concentric outer ring of radius $r_2$.
   * Ground-truth cluster proportions: Balanced ($150$ points per ring).
   * Characteristic: Linearly non-separable; cluster centroids coincide at $(0, 0)$.

### 3.2 Perturbation Regimes
To prevent confounding interactions between Gaussian noise and ambient outliers, two separate controlled sweeps were conducted:
* **Experiment A — Noise Sensitivity Sweep**:
  * Gaussian noise standard deviation $\sigma \in \{0.00, 0.05, 0.10, 0.20\}$ added to inlier coordinates via Box-Muller transformation.
  * Uniform outlier contamination held strictly at $\eta = 0.00$ ($0$ outliers).
* **Experiment B — Outlier Robustness Sweep**:
  * Uniform ambient outliers $\eta \in \{0\%, 5\%, 10\%, 20\%\}$ sampled uniformly over the bounding box $[x_{\min} - \Delta, x_{\max} + \Delta] \times [y_{\min} - \Delta, y_{\max} + \Delta]$.
  * Exact point counts: $\eta = 0\%$ ($0$ outliers), $\eta = 5\%$ ($15$ outliers, total $N=315$), $\eta = 10\%$ ($30$ outliers, total $N=330$), $\eta = 20\%$ ($60$ outliers, total $N=360$).
  * Gaussian noise held strictly at $\sigma = 0.00$.
* **Experiment C — Clean Geometry Baseline**:
  * Identical baseline coordinates $(\sigma = 0.00, \eta = 0\%)$ evaluated for both algorithms across all three seeds.

---

## 4. Algorithmic Implementations

Both algorithms were implemented natively in client-side JavaScript without third-party mathematical libraries.

### 4.1 Lloyd's K-Means Algorithm
* **Initialization**: K-Means++ deterministic sampling ($D^2$ weighting based on minimum squared distance to chosen centroids).
* **Objective Function**: Minimization of within-cluster sum of squares (WCSS / Inertia):
  $$\mathcal{J} = \sum_{k=1}^K \sum_{x_i \in C_k} \| x_i - \mu_k \|^2$$
* **Update Scheme**: Batch Lloyd iteration with coordinate convergence tolerance $\epsilon = 10^{-5}$ and maximum iterations $I_{\max} = 100$.
* **Empty Cluster Strategy**: Reseeding using the point farthest from any current centroid.

### 4.2 MST-Based Clustering
* **Minimum Spanning Tree Construction**: Prim's dense algorithm operating over the complete Euclidean graph $G = (V, E)$, $|V| = N$.
  * Key array: Min-weight edge connecting visited to unvisited vertices.
  * Time Complexity: $\Theta(N^2)$ distance evaluations; Auxiliary Memory: $O(N)$.
* **Clustering Partition Scheme**: Sorting all $N - 1$ edges of the computed spanning tree by Euclidean length and deleting the $(K - 1)$ longest edges.
* **Component Assignment**: Disjoint Set Union (Union-Find) with path compression and rank optimization to label the $K$ connected components.
* **Deterministic Tie-Breaking**: Ordered by edge weight, source vertex index, and target vertex index.

---

## 5. Quantitative Evaluation Metrics

### 5.1 Adjusted Rand Index (ARI)
Clustering quality was evaluated against ground-truth labels using the Adjusted Rand Index (Hubert & Arabie, 1985). Given ground truth $U = \{u_1, \dots, u_R\}$ and predicted clustering $V = \{v_1, \dots, v_C\}$, let $n_{ij} = |u_i \cap v_j|$, $a_i = \sum_j n_{ij}$, and $b_j = \sum_i n_{ij}$:

$$\text{ARI} = \frac{\sum_{i,j} \binom{n_{ij}}{2} - \left[ \sum_i \binom{a_i}{2} \sum_j \binom{b_j}{2} \right] \Big/ \binom{n}{2}}{\frac{1}{2}\left[ \sum_i \binom{a_i}{2} + \sum_j \binom{b_j}{2} \right] - \left[ \sum_i \binom{a_i}{2} \sum_j \binom{b_j}{2} \right] \Big/ \binom{n}{2}}$$

* **Range**: $[-1.0, 1.0]$. An ARI of $1.0000$ indicates identical cluster partitions up to label permutation. Values near $0.0$ indicate random chance agreement. Negative values indicate worse than chance concordance.

### 5.2 Inlier ARI Protocol
When outliers were injected into the dataset, **ARI was computed strictly over the $N_{\text{inliers}} = 300$ original inlier points**. 
* *Scientific Justification*: In practical unsupervised learning, uniformly distributed background outliers do not constitute a meaningful natural cluster. Including outlier points in the contingency table would artificially distort the partition index or reward algorithms that group disparate boundary outliers into an arbitrary $K$-th partition.

### 5.3 Baseline Degradation ($\Delta \text{ARI}$)
To isolate perturbation sensitivity from initial geometric incompatibility, degradation was measured relative to the clean paired baseline ($\text{ARI}_{\text{baseline}}$) on the exact same seed:

$$\Delta \text{ARI} = \max\left(0.0, \; \text{ARI}_{\text{baseline}} - \text{ARI}_{\text{perturbed}}\right)$$

---

## 6. Empirical Robustness Results & Summary Tables

The controlled robustness experiments produced **144 individual trial evaluations** (3 datasets $\times$ 8 conditions $\times$ 3 seeds $\times$ 2 algorithms) aggregated into **48 condition summary records**.

### 6.1 Gaussian Blobs ($K=3$, Inliers $N=300$)
*Clean Baseline ($\sigma=0.00, \eta=0\%$): K-Means $\text{ARI} = 1.0000 \pm 0.0000$; MST $\text{ARI} = 1.0000 \pm 0.0000$.*

| Perturbation Regime | Parameter Level | Algorithm | Inlier ARI (Mean $\pm$ SD) | Median ARI | [Min, Max] ARI | ARI Degradation ($\Delta\text{ARI}$) | Mean Runtime (ms) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Noise Sensitivity** | $\sigma = 0.00$ | K-Means | $1.0000 \pm 0.0000$ | $1.0000$ | $[1.0000, 1.0000]$ | $0.0000 \pm 0.0000$ | $0.633 \pm 0.777$ |
| | $\sigma = 0.00$ | MST | $1.0000 \pm 0.0000$ | $1.0000$ | $[1.0000, 1.0000]$ | $0.0000 \pm 0.0000$ | $1.900 \pm 1.217$ |
| | $\sigma = 0.05$ | K-Means | $1.0000 \pm 0.0000$ | $1.0000$ | $[1.0000, 1.0000]$ | $0.0000 \pm 0.0000$ | $0.000 \pm 0.000$ |
| | $\sigma = 0.05$ | MST | $1.0000 \pm 0.0000$ | $1.0000$ | $[1.0000, 1.0000]$ | $0.0000 \pm 0.0000$ | $0.900 \pm 0.529$ |
| | $\sigma = 0.10$ | K-Means | $1.0000 \pm 0.0000$ | $1.0000$ | $[1.0000, 1.0000]$ | $0.0000 \pm 0.0000$ | $0.133 \pm 0.058$ |
| | $\sigma = 0.10$ | MST | $1.0000 \pm 0.0000$ | $1.0000$ | $[1.0000, 1.0000]$ | $0.0000 \pm 0.0000$ | $0.633 \pm 0.252$ |
| | $\sigma = 0.20$ | K-Means | $1.0000 \pm 0.0000$ | $1.0000$ | $[1.0000, 1.0000]$ | $0.0000 \pm 0.0000$ | $0.067 \pm 0.115$ |
| | $\sigma = 0.20$ | MST | $1.0000 \pm 0.0000$ | $1.0000$ | $[1.0000, 1.0000]$ | $0.0000 \pm 0.0000$ | $0.567 \pm 0.231$ |
| **Outlier Robustness** | $\eta = 5\%$ ($15$ pts) | K-Means | $1.0000 \pm 0.0000$ | $1.0000$ | $[1.0000, 1.0000]$ | $0.0000 \pm 0.0000$ | $0.033 \pm 0.058$ |
| | $\eta = 5\%$ ($15$ pts) | MST | $0.7132 \pm 0.2484$ | $0.5698$ | $[0.5698, 1.0000]$ | $0.2868 \pm 0.2484$ | $0.533 \pm 0.252$ |
| | $\eta = 10\%$ ($30$ pts) | K-Means | $1.0000 \pm 0.0000$ | $1.0000$ | $[1.0000, 1.0000]$ | $0.0000 \pm 0.0000$ | $0.067 \pm 0.058$ |
| | $\eta = 10\%$ ($30$ pts) | MST | $0.7132 \pm 0.2484$ | $0.5698$ | $[0.5698, 1.0000]$ | $0.2868 \pm 0.2484$ | $0.467 \pm 0.115$ |
| | $\eta = 20\%$ ($60$ pts) | K-Means | $1.0000 \pm 0.0000$ | $1.0000$ | $[1.0000, 1.0000]$ | $0.0000 \pm 0.0000$ | $0.067 \pm 0.058$ |
| | $\eta = 20\%$ ($60$ pts) | MST | $0.3799 \pm 0.3290$ | $0.5698$ | $[0.0000, 0.5698]$ | $0.6201 \pm 0.3290$ | $0.733 \pm 0.306$ |

---

### 6.2 Two Moons ($K=2$, Inliers $N=300$)
*Clean Baseline ($\sigma=0.00, \eta=0\%$): K-Means $\text{ARI} = 0.1941 \pm 0.0588$; MST $\text{ARI} = 1.0000 \pm 0.0000$.*

| Perturbation Regime | Parameter Level | Algorithm | Inlier ARI (Mean $\pm$ SD) | Median ARI | [Min, Max] ARI | ARI Degradation ($\Delta\text{ARI}$) | Mean Runtime (ms) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Noise Sensitivity** | $\sigma = 0.00$ | K-Means | $0.1941 \pm 0.0588$ | $0.2214$ | $[0.1267, 0.2343]$ | $0.0000 \pm 0.0000$ | $0.233 \pm 0.208$ |
| | $\sigma = 0.00$ | MST | $1.0000 \pm 0.0000$ | $1.0000$ | $[1.0000, 1.0000]$ | $0.0000 \pm 0.0000$ | $0.733 \pm 0.321$ |
| | $\sigma = 0.05$ | K-Means | $0.2117 \pm 0.0564$ | $0.2409$ | $[0.1467, 0.2475]$ | $0.0000 \pm 0.0000$ | $0.133 \pm 0.058$ |
| | $\sigma = 0.05$ | MST | $1.0000 \pm 0.0000$ | $1.0000$ | $[1.0000, 1.0000]$ | $0.0000 \pm 0.0000$ | $0.833 \pm 0.451$ |
| | $\sigma = 0.10$ | K-Means | $0.2237 \pm 0.0534$ | $0.2475$ | $[0.1626, 0.2611]$ | $0.0000 \pm 0.0000$ | $0.033 \pm 0.058$ |
| | $\sigma = 0.10$ | MST | $0.6667 \pm 0.5773$ | $1.0000$ | $[0.0001, 1.0000]$ | $0.3333 \pm 0.5773$ | $0.567 \pm 0.153$ |
| | $\sigma = 0.20$ | K-Means | $0.2210 \pm 0.0472$ | $0.2214$ | $[0.1736, 0.2680]$ | $0.0000 \pm 0.0000$ | $0.100 \pm 0.100$ |
| | $\sigma = 0.20$ | MST | $0.0000 \pm 0.0000$ | $0.0000$ | $[0.0000, 0.0000]$ | $1.0000 \pm 0.0000$ | $0.700 \pm 0.265$ |
| **Outlier Robustness** | $\eta = 5\%$ ($15$ pts) | K-Means | $0.1920 \pm 0.0566$ | $0.2214$ | $[0.1267, 0.2278]$ | $0.0022 \pm 0.0037$ | $0.133 \pm 0.058$ |
| | $\eta = 5\%$ ($15$ pts) | MST | $0.0000 \pm 0.0000$ | $0.0000$ | $[0.0000, 0.0000]$ | $1.0000 \pm 0.0000$ | $0.633 \pm 0.208$ |
| | $\eta = 10\%$ ($30$ pts) | K-Means | $0.1862 \pm 0.0557$ | $0.2152$ | $[0.1219, 0.2215]$ | $0.0080 \pm 0.0043$ | $0.133 \pm 0.115$ |
| | $\eta = 10\%$ ($30$ pts) | MST | $0.0000 \pm 0.0000$ | $0.0000$ | $[0.0000, 0.0000]$ | $1.0000 \pm 0.0000$ | $0.700 \pm 0.400$ |
| | $\eta = 20\%$ ($60$ pts) | K-Means | $0.1764 \pm 0.0521$ | $0.1968$ | $[0.1172, 0.2152]$ | $0.0177 \pm 0.0171$ | $0.133 \pm 0.058$ |
| | $\eta = 20\%$ ($60$ pts) | MST | $0.0000 \pm 0.0000$ | $0.0000$ | $[0.0000, 0.0000]$ | $1.0000 \pm 0.0000$ | $0.967 \pm 0.503$ |

---

### 6.3 Concentric Circles ($K=2$, Inliers $N=300$)
*Clean Baseline ($\sigma=0.00, \eta=0\%$): K-Means $\text{ARI} = -0.0019 \pm 0.0012$; MST $\text{ARI} = 1.0000 \pm 0.0000$.*

| Perturbation Regime | Parameter Level | Algorithm | Inlier ARI (Mean $\pm$ SD) | Median ARI | [Min, Max] ARI | ARI Degradation ($\Delta\text{ARI}$) | Mean Runtime (ms) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Noise Sensitivity** | $\sigma = 0.00$ | K-Means | $-0.0019 \pm 0.0012$ | $-0.0022$ | $[-0.0029, -0.0005]$ | $0.0000 \pm 0.0000$ | $0.200 \pm 0.000$ |
| | $\sigma = 0.00$ | MST | $1.0000 \pm 0.0000$ | $1.0000$ | $[1.0000, 1.0000]$ | $0.0000 \pm 0.0000$ | $1.033 \pm 0.493$ |
| | $\sigma = 0.05$ | K-Means | $-0.0019 \pm 0.0006$ | $-0.0022$ | $[-0.0022, -0.0012]$ | $0.0002 \pm 0.0004$ | $0.167 \pm 0.153$ |
| | $\sigma = 0.05$ | MST | $1.0000 \pm 0.0000$ | $1.0000$ | $[1.0000, 1.0000]$ | $0.0000 \pm 0.0000$ | $0.833 \pm 0.208$ |
| | $\sigma = 0.10$ | K-Means | $+0.0002 \pm 0.0037$ | $-0.0005$ | $[-0.0031, +0.0042]$ | $0.0001 \pm 0.0001$ | $0.200 \pm 0.100$ |
| | $\sigma = 0.10$ | MST | $1.0000 \pm 0.0000$ | $1.0000$ | $[1.0000, 1.0000]$ | $0.0000 \pm 0.0000$ | $1.233 \pm 0.208$ |
| | $\sigma = 0.20$ | K-Means | $-0.0030 \pm 0.0002$ | $-0.0030$ | $[-0.0033, -0.0029]$ | $0.0012 \pm 0.0011$ | $0.067 \pm 0.115$ |
| | $\sigma = 0.20$ | MST | $0.0935 \pm 0.0813$ | $0.1327$ | $[0.0000, 0.1477]$ | $0.9065 \pm 0.0813$ | $0.833 \pm 0.586$ |
| **Outlier Robustness** | $\eta = 5\%$ ($15$ pts) | K-Means | $-0.0017 \pm 0.0006$ | $-0.0017$ | $[-0.0022, -0.0011]$ | $0.0004 \pm 0.0007$ | $0.233 \pm 0.058$ |
| | $\eta = 5\%$ ($15$ pts) | MST | $0.3333 \pm 0.5774$ | $0.0000$ | $[0.0000, 1.0000]$ | $0.6667 \pm 0.5774$ | $0.667 \pm 0.058$ |
| | $\eta = 10\%$ ($30$ pts) | K-Means | $-0.0008 \pm 0.0013$ | $-0.0004$ | $[-0.0022, +0.0003]$ | $0.0000 \pm 0.0000$ | $0.167 \pm 0.115$ |
| | $\eta = 10\%$ ($30$ pts) | MST | $0.3333 \pm 0.5774$ | $0.0000$ | $[0.0000, 1.0000]$ | $0.6667 \pm 0.5774$ | $1.067 \pm 0.416$ |
| | $\eta = 20\%$ ($60$ pts) | K-Means | $+0.0003 \pm 0.0033$ | $+0.0011$ | $[-0.0034, +0.0031]$ | $0.0004 \pm 0.0006$ | $0.100 \pm 0.000$ |
| | $\eta = 20\%$ ($60$ pts) | MST | $0.0000 \pm 0.0000$ | $0.0000$ | $[0.0000, 0.0000]$ | $1.0000 \pm 0.0000$ | $0.800 \pm 0.265$ |

---

## 7. Performance Benchmarks and Runtime Scaling

Benchmarking was executed on Gaussian Blobs ($K=3$) across sample sizes $N \in \{100, 200, 400, 600\}$. Each condition was preceded by warm-up iterations and measured across **5 independent trials**.

### 7.1 Measured Runtime Statistics
*(Data Source: `results/summaries/benchmark_summary.csv`)*

| Sample Size ($N$) | Algorithm | Measured Repetitions | Mean Runtime (ms) | Median Runtime (ms) | Standard Deviation (ms) | Min Runtime (ms) | Max Runtime (ms) | Speedup Ratio (MST / KM) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **100** | K-Means | 5 | $0.1000$ | $0.1000$ | $0.1225$ | $0.0000$ | $0.3000$ | **$2.00\times$** |
| **100** | MST Prim Dense | 5 | $0.1400$ | $0.2000$ | $0.0894$ | $0.0000$ | $0.2000$ | $1.00\times$ |
| **200** | K-Means | 5 | $0.1600$ | $0.2000$ | $0.0548$ | $0.1000$ | $0.2000$ | **$1.50\times$** |
| **200** | MST Prim Dense | 5 | $0.3800$ | $0.3000$ | $0.1924$ | $0.2000$ | $0.7000$ | $1.00\times$ |
| **400** | K-Means | 5 | $0.1400$ | $0.1000$ | $0.1140$ | $0.0000$ | $0.3000$ | **$10.00\times$** |
| **400** | MST Prim Dense | 5 | $0.9400$ | $1.0000$ | $0.2408$ | $0.6000$ | $1.2000$ | $1.00\times$ |
| **600** | K-Means | 5 | $0.1400$ | $0.1000$ | $0.0548$ | $0.1000$ | $0.2000$ | **$17.00\times$** |
| **600** | MST Prim Dense | 5 | $1.7000$ | $1.7000$ | $0.2828$ | $1.3000$ | $2.1000$ | $1.00\times$ |

### 7.2 Browser Timer Quantization & Hardware Environment
* **Timer Granularity**: The measurements utilize `window.performance.now()`. In modern chromium-based browsers, timer resolution is quantized to mitigate microarchitectural side-channel attacks (e.g., Spectre). Typical quantization steps range between $5\,\mu\text{s}$ and $100\,\mu\text{s}$. Sub-millisecond operations completing in under $\sim 40\,\mu\text{s}$ legitimately record as $0.0000\text{ ms}$, which represents a genuine non-negative measurement rather than missing data.
* **Process Memory Isolation**: Process-level RAM allocations are strictly sandboxed and inaccessible to standard web APIs; therefore, memory usage was evaluated theoretically ($\Theta(N)$ auxiliary memory for Prim's array vs. $\Theta(N)$ for K-Means cluster assignments).

---

## 8. Visual Evidence Analysis

Seven scientific figures were generated directly by the browser visualization engine and saved into `results/figures/`.

### 8.1 Figure 1 — Gaussian Blobs Qualitative Comparison
* **File**: `results/figures/blobs_comparison.png`
* **Visualization**: 2D coordinate scatter plots comparing ground truth against K-Means and MST clustering partitions.
* **Scientific Observation**: Both algorithms cleanly identify the 3 convex spherical clusters. K-Means establishes linear Voronoi bisectors that cleanly divide the coordinate space. MST forms dense subtrees over each centroid and cleanly cuts the two longest inter-blob connecting edges, yielding identical partitions ($\text{ARI} = 1.0000$).

### 8.2 Figure 2 — Two Moons Qualitative Comparison
* **File**: `results/figures/moons_comparison.png`
* **Visualization**: Interlocking crescent manifolds ($K=2$).
* **Scientific Observation**: K-Means slices across both crescents with a vertical/diagonal hyperplane, grouping the top half of both arcs together and the bottom half together ($\text{ARI} = 0.1941$). In contrast, MST constructs continuous single-linkage chains along each crescent manifold, isolating the single long edge bridging the tips of the two moons and achieving perfect disentanglement ($\text{ARI} = 1.0000$).

### 8.3 Figure 3 — Concentric Circles Qualitative Comparison
* **File**: `results/figures/circles_comparison.png`
* **Visualization**: Nested ring manifolds ($K=2$).
* **Scientific Observation**: Because the inner core and outer circle share an identical Euclidean centroid $(0, 0)$, K-Means cuts the circles into semi-circular halves ($\text{ARI} = -0.0019$), demonstrating near-zero agreement with ground truth. MST links intra-ring neighbors with small edge lengths ($\sim \frac{2\pi r}{N}$), leaving the radial gap between rings as the maximum edge in the tree, which is cleanly severed ($\text{ARI} = 1.0000$).

### 8.4 Figure 4 — Partition Quality vs. Gaussian Noise ($\sigma$)
* **File**: `results/figures/ari_vs_noise.png`
* **Visualization**: Inlier ARI plotted across noise levels $\sigma \in [0.00, 0.20]$ for all three geometries.
* **Scientific Observation**: K-Means exhibits flat horizontal resilience on Blobs ($\text{ARI} = 1.0000$). On Concentric Circles, MST remains stable at $\text{ARI} = 1.0000$ through $\sigma = 0.10$, but abruptly collapses at $\sigma = 0.20$ to $\text{ARI} = 0.0935$. On Two Moons, MST degrades from $\text{ARI} = 1.0000$ ($\sigma = 0.05$) to $0.6667$ ($\sigma = 0.10$) and $0.0000$ ($\sigma = 0.20$).

### 8.5 Figure 5 — Partition Quality vs. Outlier Contamination ($\eta$)
* **File**: `results/figures/ari_vs_outliers.png`
* **Visualization**: Inlier ARI plotted across outlier fractions $\eta \in [0\%, 20\%]$.
* **Scientific Observation**: This figure demonstrates the central vulnerability of MST clustering: uniform outliers act as bridging catalysts. On Two Moons, adding just $5\%$ outliers drops MST ARI catastrophically to $0.0000$. On Blobs, MST drops from $1.0000$ to $0.7132$ ($5\%$) and $0.3799$ ($20\%$). Meanwhile, K-Means maintains $\text{ARI} = 1.0000$ across all outlier levels on Gaussian Blobs.

### 8.6 Figure 6 — ARI Baseline Degradation ($\Delta \text{ARI}$)
* **File**: `results/figures/ari_degradation.png`
* **Visualization**: Clustered bar chart of degradation relative to clean baselines.
* **Scientific Observation**: K-Means experiences almost zero degradation across all conditions ($\Delta\text{ARI} \le 0.0177$) because its centroid updates are smoothed over large sample sizes ($N=300$). Conversely, MST exhibits severe degradation under outliers ($\Delta\text{ARI} = 1.0000$ on Moons, $0.6667$ on Circles, and $0.6201$ on Blobs).

### 8.7 Figure 7 — Runtime Scaling & Computational Complexity
* **File**: `results/figures/runtime_scaling.png`
* **Visualization**: Execution runtime (ms) vs. sample size $N \in [100, 600]$ with asymptotic curve annotations.
* **Scientific Observation**: K-Means runtime remains flat at $\approx 0.10\text{--}0.16\text{ ms}$ because convergence occurs in few iterations on well-separated clusters. Dense Prim's MST exhibits clear quadratic growth, rising from $0.14\text{ ms}$ at $N=100$ to $1.70\text{ ms}$ at $N=600$, confirming the $O(N^2)$ theoretical model.

---

## 9. Comprehensive Comparative Analysis & Failure Modes

### 9.1 Summary of Algorithm Strengths and Vulnerabilities

| Dimension | Lloyd's K-Means Algorithm | MST-Based Single-Linkage Clustering |
| :--- | :--- | :--- |
| **Cluster Geometry Assumption** | Convex, spherical, linearly separable Voronoi cells. | Arbitrary non-linear manifolds; single-linkage connected components. |
| **Non-Convex Manifolds (Clean)** | **Critical Failure**: Slices through manifolds; achieves $\text{ARI} \le 0.19$. | **Superior**: Disentangles complex topologies; achieves perfect $\text{ARI} = 1.0000$. |
| **Isotropic Noise Resistance** | **High**: Centroid averaging dampens zero-mean Gaussian perturbations. | **Moderate**: Stable at moderate noise, but collapses when noise bridges inter-cluster gaps. |
| **Outlier Contamination Resistance** | **High on Convex Clusters**: Inertia is relatively stable; maintains $\text{ARI} = 1.0000$ on Blobs. | **Catastrophic Failure**: Outliers create peripheral branches that consume tree cuts or bridge clusters. |
| **Computational Complexity** | $O(I \cdot K \cdot N)$ where $I \ll N$. Fast, scales well to large sample sizes. | $O(N^2)$ for dense Prim. Quadratic memory/distance bottleneck. |

### 9.2 The MST Outlier Bridging and Pendant Edge Collapse
The experimental data reveals the exact mathematical mechanism causing MST to fail under uniform outlier contamination:
1. **The Longest-Edge Cut Mechanism**: To partition an $N$-vertex graph into $K$ components, the algorithm removes the $(K - 1)$ edges with the largest Euclidean lengths.
2. **Pendant Edge Formation**: When outliers are scattered uniformly across the bounding box, they often lie far from any inlier cluster. The edge connecting an isolated outlier to its nearest neighbor in the spanning tree has a very large Euclidean distance.
3. **Cut Misallocation**: Consequently, the $(K - 1)$ longest edges in the entire spanning tree are consumed by severing isolated outlier points (forming singleton clusters consisting of $1$ outlier) rather than severing the genuine bottleneck edge between the true clusters.
4. **Resulting Partition**: All $N_{\text{inliers}} = 300$ ground-truth points remain trapped in a single giant component, while the remaining $K - 1$ clusters contain only isolated outliers. Evaluated across the 300 inliers, all inliers share the exact same cluster label, resulting in $\text{ARI} = 0.0000$.

### 9.3 The K-Means Centroid Orthogonality Failure
Conversely, the failure of K-Means on Concentric Circles is structural:
* The inner circle has centroid $\mu_1 \approx (0, 0)$ and radius $r_1$.
* The outer circle has centroid $\mu_2 \approx (0, 0)$ and radius $r_2 > r_1$.
* Any Voronoi partition defined by hyperplanes $\{x \in \mathbb{R}^2 : \|x - \mu_A\| = \|x - \mu_B\|\}$ divides the space into half-planes passing through the origin. No linear boundary can separate an interior sphere from a concentric spherical shell.

---

## 10. Threats to Validity & Limitations

1. **Finite Seed Sampling ($M = 3$)**: While seeds $\{11, 22, 33\}$ provide identical paired testbeds for both algorithms, a sample of 3 seeds reflects limited statistical power. The observed standard deviations indicate variability across random initializations, but larger Monte Carlo sweeps ($M \ge 50$) would be necessary to establish confidence intervals.
2. **Two-Dimensional Feature Spaces**: All synthetic experiments were restricted to $D = 2$ dimensions. In higher dimensions ($D \gg 2$), the curse of dimensionality increases distance concentration, which degrades Euclidean distance contrast for both MST construction and K-Means centroid allocation.
3. **Dense Graph Representation**: Prim's algorithm was executed using an all-pairs Euclidean metric ($\Theta(N^2)$). Sparse Delaunay triangulations in 2D could theoretically construct the Euclidean MST in $O(N \log N)$ time, altering runtime scaling.
4. **Browser Timer Coarsening**: Execution times under $0.05\text{ ms}$ were subject to browser security quantization, resulting in some trials recording $0.000\text{ ms}$. This limitation was handled transparently by reporting median and mean values across repetitions rather than relying on single-pass timers.

---

## 11. Reproducibility & Verification

To reproduce these exact experimental results in any standard desktop web browser:
1. Open [`index.html`](file:///d:/7th%20Sem/PM/Mini%20project/MST-KMeans-Robustness-Analysis/index.html) or [`tests/export_artifacts.html`](file:///d:/7th%20Sem/PM/Mini%20project/MST-KMeans-Robustness-Analysis/tests/export_artifacts.html) directly in Chrome, Edge, or Brave.
2. The experiment suite executes deterministically using PRNG seeds $11, 22, 33$.
3. All exported raw trial rows match `results/raw/robustness_trials.csv` and `results/raw/benchmark_trials.csv` bit-for-bit.
4. Automated verification confirmed that all $144$ robustness trials and $40$ benchmark trials are strictly valid, non-negative, and mathematically bounded within $[-1.0, 1.0]$.
