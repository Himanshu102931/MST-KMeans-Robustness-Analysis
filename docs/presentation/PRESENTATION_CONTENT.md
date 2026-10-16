# 15-Slide Academic Presentation Content
## MST vs K-Means Robustness Analysis: A Comparative Quantitative Investigation

* **Course**: Pattern Matching Lab (`BCS-DS-777`)
* **Department**: Department of Computer Science and Engineering
* **Institution**: Manav Rachna International Institute of Research and Studies (MRIIRS), Faridabad, India
* **Student Presenters**:
  * **Himanshu Gupta** — Project Allocation No.: **19**
  * **Parth Yadav** — Project Partner
* **Faculty Mentor**: [Course Instructor / Faculty Mentor Name]
* **Aspect Ratio**: 16:9 Widescreen Layout

---

## Slide 1 — Title Slide

* **Slide Title**: MST vs K-Means Robustness Analysis
* **Subtitle**: A Comparative Quantitative Investigation of Graph-Theoretic Spanning Forest Clustering and Centroid Voronoi Partitioning Under Controlled Topological and Stochastic Perturbations
* **Key Metadata**:
  * **Course**: Pattern Matching Lab (`BCS-DS-777`), 7th Semester B.Tech. CSE
  * **Institution**: Manav Rachna International Institute of Research and Studies (MRIIRS)
  * **Student Lead**: Himanshu Gupta (Allocation Number: **19**)
  * **Project Partner**: Parth Yadav
  * **Mentor**: Department of Computer Science & Engineering, FET, MRIIRS
  * **Repository**: `https://github.com/Himanshu102931/MST-KMeans-Robustness-Analysis`
* **Visual Elements**: Institutional emblem placeholder, clean technical badge ("Phase 6C Final Defense Deck"), GitHub checkpoint tag (`1baf1c9`).

---

## Slide 2 — Introduction: Unsupervised Clustering & Robustness

* **Slide Title**: Introduction: The Challenge of Unsupervised Clustering
* **Core Concept**:
  * **Unsupervised Pattern Recognition**: Partitioning unlabelled feature space $\mathcal{X} \subset \mathbb{R}^D$ into $K$ cohesive, well-separated subsets without ground-truth supervision during training.
  * **The Fundamental Dilemma**: Clustering algorithms make strong mathematical assumptions (inductive biases) about cluster shape and boundary geometry.
* **The Paradigm Conflict**:
  * **Centroid-Based Voronoi Partitioning (K-Means)**: Assumes clusters are compact, convex, spherical, and linearly separable.
  * **Graph-Theoretic Connectivity (MST)**: Assumes clusters are continuous topological manifolds traced via single-linkage proximity.
* **The Robustness Imperative**:
  * Real-world scientific data violates textbook assumptions: sensor noise, non-linear physical structures, and ambient outlier contamination are ubiquitous.
  * **Research Goal**: Quantitatively measure where each algorithm succeeds, where it breaks down, and how quickly performance degrades under controlled perturbations.

---

## Slide 3 — Research Problem Statement

* **Slide Title**: Problem Statement & Core Research Questions
* **Official Allocated Objective**:
  > *"Compare MST-based clustering and K-Means under noise, outliers, and non-linear data distributions using quantitative robustness measures."*  
  > *(Allocation Number: 19 | Pattern Matching Lab BCS-DS-777)*
* **Four Core Research Questions**:
  1. **RQ1 (Manifold Disentanglement)**: Can single-linkage tree-cutting recover complex non-convex geometries (interlocking crescents and concentric rings) where K-Means is theoretically expected to fail?
  2. **RQ2 (Noise Sensitivity)**: At what quantitative threshold of Gaussian noise ($\sigma$) do continuous manifolds bridge, degrading partition quality?
  3. **RQ3 (Outlier Vulnerability)**: How severely does ambient uniform outlier contamination ($\eta$) degrade inlier clustering, and does MST suffer from cut misallocation?
  4. **RQ4 (Computational Scalability)**: How do empirical runtimes scale for dense Prim's MST ($O(N^2)$) vs. Lloyd's K-Means ($O(I \cdot K \cdot N)$) across sample sizes $N \in [100, 600]$?

---

## Slide 4 — Project Objectives & Scope

* **Slide Title**: Measurable Objectives & Experimental Scope
* **Five Measurable Learning Objectives**:
  * **LO-1 (Native Implementation)**: Implement Lloyd's K-Means (with K-Means++ seeding) and dense Prim's MST natively in vanilla JavaScript without external libraries (64 passing unit tests).
  * **LO-2 (Synthetic Engine)**: Build a deterministic synthetic data generator with exact coordinate reproducibility across fixed seeds ($\mathcal{S} \in \{11, 22, 33\}$).
  * **LO-3 (Controlled Robustness)**: Execute 144 paired trials measuring Inlier Adjusted Rand Index (ARI) and baseline degradation ($\Delta\text{ARI}$).
  * **LO-4 (Performance Benchmarks)**: Profile execution runtimes across $N \in [100, 600]$ using high-resolution monotonic browser timers (`performance.now()`).
  * **LO-5 (Interactive Dashboard)**: Deploy an open, auditable web application featuring interactive algorithm exploration, live sweeps, and scientific exports.
* **Scope & Boundaries**:
  * 2D Euclidean feature space ($D = 2$); sample sizes $N \in [100, 600]$; cluster counts $K \in \{2, 3\}$.
  * Zero Python, Node.js, npm, or backend dependencies—100% browser-native client-side execution.

---

## Slide 5 — Lloyd's K-Means Algorithm

* **Slide Title**: Centroid Optimization: Lloyd's K-Means & K-Means++
* **Objective Function (Within-Cluster Sum of Squares / Inertia)**:
  $$\mathcal{J} = \sum_{k=1}^K \sum_{x_i \in C_k} \| x_i - \mu_k \|^2$$
* **Algorithmic Workflow**:
  1. **K-Means++ Seeding (Arthur & Vassilvitskii, 2007)**: First centroid chosen uniformly at random; subsequent centroids sampled with probability $P(x) \propto D(x)^2$ to maximize spatial dispersion.
  2. **Assignment Step**: Assign each observation to the nearest centroid under Euclidean distance: $l_i = \arg\min_k \|x_i - \mu_k\|^2$.
  3. **Update Step**: Recompute centroids as arithmetic means: $\mu_k = \frac{1}{|C_k|} \sum_{x_i \in C_k} x_i$.
  4. **Convergence**: Terminate when centroid displacement $< 10^{-5}$ or max iterations ($100$) reached.
* **Inherent Strengths & Limitations**:
  * **Strength**: Fast linear convergence per iteration ($O(K \cdot N)$); centroid averaging naturally filters zero-mean Gaussian noise.
  * **Structural Flaw**: Cluster boundaries are strictly linear Voronoi hyperplanes; mathematically incapable of separating non-convex manifolds.

---

## Slide 6 — Minimum Spanning Tree (MST) Clustering

* **Slide Title**: Graph Connectivity: Prim's Algorithm & Zahn's Clustering
* **Mathematical Foundation (Zahn, 1971 | Prim, 1957)**:
  * Complete Euclidean Graph $G = (V, E)$ where $|V| = N$ and edge weights $w(u, v) = \| u - v \|_2$.
  * Minimum Spanning Tree $T = (V, E_T)$ spans all $N$ vertices with exactly $N - 1$ edges minimizing total weight $\sum_{e \in E_T} w(e)$.
* **Algorithmic Workflow**:
  1. **Prim's Dense Construction**: Greedily grow tree from vertex $0$ using priority key array $\kappa[v] = \min_{u \in S} \|u - v\|$; total distance evaluations: $\Theta(N^2)$.
  2. **Tree Cutting (Zahn's Inconsistency Criterion)**: Sort all $N - 1$ edges in descending order of length; delete the $(K - 1)$ longest edges.
  3. **Component Extraction**: Use Disjoint Set Union (Union-Find) with path compression and rank optimization to identify the $K$ connected subtrees.
* **Inherent Strengths & Limitations**:
  * **Strength**: Discovers arbitrary continuous non-linear topological manifolds via single-linkage connectivity.
  * **Structural Flaw**: Highly vulnerable to outlier bridging and pendant edge cut misallocation; quadratic time complexity ($\Theta(N^2)$).

---

## Slide 7 — System Architecture & Technology Stack

* **Slide Title**: Proposed System Architecture: 100% Browser-Native
* **Design Philosophy**: Zero installation barrier, complete algorithmic transparency, fully reproducible on any modern desktop browser.
* **Component Architecture**:
  * **Data Layer (`js/data/`)**: Deterministic LCG PRNG (`prng.js`), synthetic manifold coordinate generators with Box-Muller noise (`datasets.js`).
  * **Algorithm Layer (`js/algorithms/`)**: Pure JavaScript K-Means (`kmeans.js`) and Prim's MST with Union-Find (`mst.js`).
  * **Evaluation Layer (`js/metrics/`)**: Hubert & Arabie (1985) Adjusted Rand Index (ARI) and baseline degradation engine (`evaluation.js`).
  * **Experiment Orchestration (`js/experiments/`)**: Automated parameter sweeps (`robustness.js`) and monotonic micro-benchmarks (`benchmarks.js`).
  * **Visualization & Export Layer (`js/export/`)**: High-DPI Canvas renderers, step-by-step interactive explorer, CSV trial exporter, and PNG chart generator.
* **Verification**: Verified across Google Chrome, Microsoft Edge, Brave, and Mozilla Firefox (64/64 automated unit tests passing).

---

## 8. Slide 8 — Dataset Geometries & Topological Properties

* **Slide Title**: Synthetic Dataset Families ($N_{\text{inliers}} = 300$)
* **Three Canonical Geometric Families**:
  1. **Gaussian Blobs ($K=3$, Convex)**:
     * Three compact, isotropic spherical normal distributions ($\sigma_{\text{cluster}} = 0.6$).
     * Balanced: $100$ points/cluster; linearly separable.
  2. **Two Moons ($K=2$, Non-Convex Interlocking Manifolds)**:
     * Two interleaving semicircular arcs ($r = 1.0$) separated by non-linear Euclidean margins.
     * Balanced: $150$ points/crescent; requires single-linkage transitivity.
  3. **Concentric Circles ($K=2$, Non-Convex Nested Rings)**:
     * Inner ring ($r_1 = 0.5$) surrounded by outer ring ($r_2 = 1.0$).
     * Balanced: $150$ points/ring; centroids coincide at $(0, 0)$.
* **Visual Representation**: Direct rendering from application canvas showing clean ground-truth coordinate distributions.

---

## 9. Slide 9 — Experimental Methodology & Robustness Protocol

* **Slide Title**: Controlled Experimental Design & Evaluation Protocol
* **Strict Independent Variable Separation**:
  * **Experiment A — Noise Sensitivity Sweep**: Additive Gaussian noise $\sigma \in \{0.00, 0.05, 0.10, 0.20\}$; outlier contamination fixed at $\eta = 0\%$.
  * **Experiment B — Outlier Robustness Sweep**: Uniform ambient outliers $\eta \in \{0\%, 5\%, 10\%, 20\%\}$ ($0, 15, 30, 60$ points); Gaussian noise fixed at $\sigma = 0.00$.
  * **Experiment C — Clean Baseline Matching**: Identical coordinate baseline evaluated under $(\sigma = 0.00, \eta = 0\%)$.
* **Rigorous Paired Protocol**:
  * Deterministic seeds $\mathcal{S} \in \{11, 22, 33\}$; both algorithms evaluate **identical point coordinates**.
  * Total Trials: $3\text{ datasets} \times 8\text{ conditions} \times 3\text{ seeds} \times 2\text{ algorithms} = \mathbf{144\text{ paired evaluations}}$.
* **Evaluation Metrics**:
  * **Adjusted Rand Index (ARI)** (Hubert & Arabie, 1985): Chance-corrected partition concordance in $[-1.0, 1.0]$.
  * **Inlier ARI Protocol**: Evaluated strictly over the $300$ ground-truth inliers to prevent artificial cluster inflation from uniform background outliers.
  * **Baseline Degradation**: $\Delta\text{ARI} = \max(0.0, \text{ARI}_{\text{baseline}} - \text{ARI}_{\text{perturbed}})$.

---

## 10. Slide 10 — Clean Baseline Geometry Results

* **Slide Title**: Empirical Baseline Clustering: The Topological Contrast
* **Empirical Measurements ($\sigma = 0.00, \eta = 0\%, N=300$)**:

| Dataset Family | Requested $K$ | K-Means Inlier ARI ($\mu \pm s$) | MST Inlier ARI ($\mu \pm s$) | Topological Outcome |
| :--- | :---: | :---: | :---: | :--- |
| **Gaussian Blobs** | $3$ | **$1.0000 \pm 0.0000$** | **$1.0000 \pm 0.0000$** | Both achieve perfect separation. |
| **Two Moons** | $2$ | **$0.1941 \pm 0.0588$** | **$1.0000 \pm 0.0000$** | MST traces crescents; K-Means cuts across arcs. |
| **Concentric Circles** | $2$ | **$-0.0019 \pm 0.0012$** | **$1.0000 \pm 0.0000$** | MST separates rings; K-Means splits into half-circles. |

* **Embedded Evidence**: Side-by-side scatter plots from `results/figures/`:
  * *Figure 8.1 (Blobs)*: Both Voronoi cells and spanning tree cuts cleanly identify the 3 spherical clusters.
  * *Figure 8.2 (Moons)*: K-Means bisects both crescents with a straight line; MST traces the curved manifolds.
  * *Figure 8.3 (Circles)*: Coinciding centroids at $(0, 0)$ force K-Means into chance-level agreement ($\text{ARI} \approx 0.0$).

---

## 11. Slide 11 — Noise Sensitivity Analysis ($\sigma \in [0.00, 0.20]$)

* **Slide Title**: Experiment A: Robustness Under Gaussian Coordinate Noise
* **Empirical Chart**: `results/figures/ari_vs_noise.png`
* **Key Numerical Observations**:
  * **Gaussian Blobs**: Both K-Means and MST maintain **$\text{ARI} = 1.0000 \pm 0.0000$** across all noise levels ($\sigma \le 0.20$). Inter-blob Euclidean margins remain wider than coordinate dispersion.
  * **Two Moons**: MST holds $\text{ARI} = 1.0000$ at $\sigma = 0.05$, drops to $\text{ARI} = 0.6667 \pm 0.5773$ at $\sigma = 0.10$, and collapses to $\mathbf{0.0000}$ at $\sigma = 0.20$ ($\Delta\text{ARI} = 1.0000$). K-Means remains structurally stuck at $\text{ARI} \approx 0.21\text{--}0.22$.
  * **Concentric Circles**: MST maintains perfect $\text{ARI} = 1.0000$ through $\sigma = 0.10$, but abruptly collapses to $\mathbf{0.0935 \pm 0.0813}$ at $\sigma = 0.20$ ($\Delta\text{ARI} = 0.9065$).
* **Topological Mechanism**: High noise creates Euclidean "shortcuts" across the inter-cluster boundary that are shorter than the longest intra-cluster edges, causing single-linkage bridging.

---

## 12. Slide 12 — Outlier Vulnerability & MST Pendant Edge Collapse

* **Slide Title**: Experiment B: Outlier Robustness & The MST Cut Collapse
* **Empirical Charts**: `results/figures/ari_vs_outliers.png` & `results/figures/ari_degradation.png`
* **The Central Discovery: Catastrophic MST Outlier Failure**:
  * On Two Moons, adding just **$5\%$ uniform outliers ($15$ points)** causes MST Inlier ARI to plunge from **$1.0000$ directly to $0.0000$** ($\Delta\text{ARI} = 1.0000$).
  * On Gaussian Blobs, K-Means maintains perfect **$\text{ARI} = 1.0000$** across all outlier fractions up to $20\%$, while MST degrades to $\text{ARI} = 0.7132$ ($5\%$) and $\mathbf{0.3799}$ ($20\%$).
* **The Mathematical Explanation (Cut Misallocation)**:
  1. Isolated outliers scattered in sparse background regions form long **pendant edges** connecting to the spanning tree.
  2. Because pendant edges are longer than the genuine bottleneck edge between the true clusters, **the $(K - 1)$ longest edge cuts are consumed by severing isolated outliers into singleton clusters**.
  3. Consequently, all $300$ true inliers remain lumped together in a single giant component ($\text{ARI} = 0.0000$).
  4. In contrast, K-Means centroid updates average across all points; uniform outliers exert balanced pulling forces, preserving Voronoi partition stability on Blobs.

---

## 13. Slide 13 — Performance Benchmarking & Computational Scalability

* **Slide Title**: Computational Performance & Asymptotic Complexity
* **Empirical Chart**: `results/figures/runtime_scaling.png` (Gaussian Blobs, $K=3, N \in [100, 600]$)
* **Measured Runtime Statistics & Disambiguation**:

| Sample Size ($N$) | K-Means Mean (ms) | MST Prim Mean (ms) | **Ratio of Means** ($\frac{\mu_{\text{MST}}}{\mu_{\text{KM}}}$) | K-Means Median (ms) | MST Prim Median (ms) | **Ratio of Medians** ($\frac{M_{\text{MST}}}{M_{\text{KM}}}$) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **100** | $0.1000$ | $0.1400$ | **$1.40\times$** | $0.1000$ | $0.2000$ | **$2.00\times$** |
| **200** | $0.1600$ | $0.3800$ | **$2.38\times$** | $0.2000$ | $0.3000$ | **$1.50\times$** |
| **400** | $0.1400$ | $0.9400$ | **$6.71\times$** | $0.1000$ | $1.0000$ | **$10.00\times$** |
| **600** | $0.1400$ | $1.7000$ | **$12.14\times$** | $0.1000$ | $1.7000$ | **$17.00\times$** |

* **Key Takeaways**:
  * **Asymptotic Growth**: Dense Prim's MST exhibits clear quadratic growth ($\Theta(N^2)$), rising from $0.14\text{ ms}$ to $1.70\text{ ms}$. K-Means remains sub-millisecond ($0.10\text{--}0.16\text{ ms}$) due to fast linear iteration ($O(I \cdot K \cdot N)$).
  * **Speedup Disambiguation**: Ratio of means yields **$12.14\times$** speedup; ratio of medians yields **$17.00\times$** speedup at $N=600$.
  * **Timer Quantization**: Browser security timer coarsening ($5\text{--}100\,\mu\text{s}$) produces valid $0.000\text{ ms}$ readings on fast passes.

---

## 14. Slide 14 — Conclusions, Decision Heuristic & Limitations

* **Slide Title**: Scientific Conclusions & Practical Decision Framework
* **Summary of Empirical Findings**:
  * **K-Means**: Highly robust on compact, spherical clusters ($\text{ARI} = 1.0000$), but fundamentally fails on non-convex manifolds ($\text{ARI} \le 0.1941$).
  * **MST Clustering**: Outstanding on clean non-convex manifolds ($\text{ARI} = 1.0000$), but catastrophically fragile under ambient outliers ($\Delta\text{ARI} \to 1.0000$ under $5\%$ outliers).
* **Practitioner Decision Heuristic**:
  * *Spherical clusters + background noise/outliers* $\implies$ **Select K-Means**.
  * *Continuous non-linear manifolds + pristine/filtered data* $\implies$ **Select MST Clustering**.
  * *Non-convex geometry + heavy outlier contamination* $\implies$ **Neither standard algorithm is suitable**; use density-based methods (DBSCAN) or outlier-trimmed MST.
* **Methodological Limitations**:
  * Exploratory seed sample ($M = 3$); 2D synthetic feature space ($D = 2$); browser timer quantization.
* **Future Work**: Density-filtered MST (trimming high $k$-NN distance vertices), sparse Delaunay triangulations ($O(N \log N)$), and higher-dimensional evaluation.

---

## 15. Slide 15 — Academic References & Defense Q&A

* **Slide Title**: References & Viva Defense Q&A
* **Key Academic References**:
  * **MacQueen (1967)** & **Lloyd (1982)** — Foundations of K-Means optimization and vector quantization.
  * **Arthur & Vassilvitskii (2007)** — K-Means++ $D^2$ randomized seeding and approximation bounds.
  * **Prim (1957)** & **Zahn (1971)** — Minimum Spanning Trees and graph-theoretic gestalt clustering.
  * **Rand (1971)** & **Hubert & Arabie (1985)** — Adjusted Rand Index chance-corrected partition evaluation.
  * **Jain (2010)** — *Data Clustering: 50 Years Beyond K-Means*, Pattern Recognition Letters.
* **Open Source Repository**:
  * `https://github.com/Himanshu102931/MST-KMeans-Robustness-Analysis`
* **Closing Prompt**:
  * *"Thank you for your time and guidance. We welcome questions, critiques, and discussion from the evaluation committee."*
  * **Presenters**: Himanshu Gupta (Alloc. No. 19) & Parth Yadav | MRIIRS | Pattern Matching Lab (`BCS-DS-777`)
