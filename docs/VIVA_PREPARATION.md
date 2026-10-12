# Comprehensive Viva Voce Preparation Guide
## MST vs K-Means Robustness Analysis — Academic Defense & Oral Exam

* **Course**: Pattern Matching Lab (`BCS-DS-777`)
* **Academic Institution**: Manav Rachna International Institute of Research and Studies (MRIIRS), Faridabad
* **Candidate**: Himanshu Gupta (Allocation No. 19)
* **Project Partner**: Parth Yadav
* **Course Mentor**: [Faculty Mentor Name]
* **Target Audience**: Undergraduate Computer Science Evaluators, External Examiners, and Lab Instructors

---

## Quick Reference Table of High-Yield Examiner Topics

| High-Yield Viva Concept | Core Formula / Algorithmic Concept | Expected Examiner Question |
| :--- | :--- | :--- |
| **Inertia (WCSS)** | $\mathcal{J} = \sum_{k=1}^K \sum_{x_i \in C_k} \| x_i - \mu_k \|^2$ | "Why does K-Means converge to a local minimum?" |
| **Adjusted Rand Index (ARI)** | $\text{ARI} = \frac{\text{Index} - \mathbb{E}[\text{Index}]}{\max(\text{Index}) - \mathbb{E}[\text{Index}]}$ | "Why not use classification accuracy or raw Rand Index?" |
| **Prim's Complexity** | $\Theta(N^2)$ distance evaluations; $O(N)$ priority array | "Why is dense Prim preferred over Kruskal for this problem?" |
| **Pendant Edge Collapse** | $(K - 1)$ longest tree cuts isolate outliers into singletons | "Why does MST fail catastrophically at just 5% outliers?" |
| **Voronoi Hyperplanes** | Boundary: $\{x : \|x - \mu_A\| = \|x - \mu_B\|\}$ | "Why can K-Means never solve concentric circles?" |
| **Degradation Metric** | $\Delta\text{ARI} = \max(0.0, \text{ARI}_{\text{baseline}} - \text{ARI}_{\text{perturbed}})$ | "Why clamp the degradation at zero?" |

---

## Category A: Clustering & Unsupervised Learning

### Q1: What is unsupervised clustering, and how does it differ from classification?
* **Answer**: In classification (supervised learning), each training observation has an explicit ground-truth class label, and the algorithm learns a mapping function from features to labels. In clustering (unsupervised learning), there are no target labels provided during training. The algorithm must discover natural groupings or structural patterns in the feature space based solely on intrinsic geometric similarity or topological proximity.

### Q2: Why did you choose this project comparing MST and K-Means?
* **Answer**:
  > **20–40 Second Model Viva Answer**:  
  > *"Most introductory clustering courses teach K-Means as the default algorithm, demonstrating it on clean, spherical blobs. However, real-world data in biomedical imaging and sensor networks contains non-linear curves, noise, and outliers. We chose this project because K-Means and Minimum Spanning Tree clustering represent two fundamentally opposing paradigms—centroid optimization versus graph connectivity. We wanted to quantitatively measure exactly where each paradigm breaks down under controlled perturbations without relying on black-box libraries."*

### Q3: Why are ground-truth labels used in this project if clustering is unsupervised?
* **Answer**:
  > **20–40 Second Model Viva Answer**:  
  > *"Ground-truth labels are strictly withheld from both algorithms during execution. Neither K-Means nor MST ever sees the labels during clustering. We generate synthetic datasets with known true cluster assignments solely as an external benchmark to compute the Adjusted Rand Index (ARI) after clustering terminates, allowing us to quantitatively evaluate partition recovery quality."*

### Q4: What is an inductive bias in cluster analysis?
* **Answer**: An inductive bias is the set of mathematical assumptions an algorithm makes about the structure of clusters. K-Means assumes that clusters are convex, compact, spherical Voronoi cells. MST assumes that clusters are continuous topological manifolds connected by chains of short pairwise Euclidean distances.

---

## Category B: K-Means Fundamentals

### Q5: What is Lloyd's algorithm, and how does it optimize the K-Means objective?
* **Answer**: Lloyd's algorithm alternates between two steps to minimize within-cluster sum of squares (WCSS):
  1. **Assignment Step**: Assigns each observation $x_i$ to the nearest cluster centroid $\mu_k$ under Euclidean distance.
  2. **Update Step**: Recomputes each centroid $\mu_k$ as the arithmetic mean of all points assigned to cluster $k$.
  Because each step is guaranteed to decrease or maintain WCSS, the algorithm monotonically converges to a local optimum.

### Q6: Why is standard random initialization problematic for K-Means, and how does K-Means++ solve it?
* **Answer**:
  > **20–40 Second Model Viva Answer**:  
  > *"Standard random initialization (Forgy method) picks initial centroids uniformly at random. This frequently places multiple initial centroids inside the same natural cluster, trapping K-Means in poor local minima. Arthur and Vassilvitskii's K-Means++ solves this by selecting the first centroid uniformly, and sampling each subsequent centroid with probability proportional to the squared Euclidean distance $D(x)^2$ to the nearest already-chosen centroid. This spreads out initial seeds and mathematically guarantees an $O(\log K)$ approximation bound relative to the optimal clustering."*

### Q7: Why can K-Means never correctly partition Concentric Circles or Two Moons?
* **Answer**:
  > **20–40 Second Model Viva Answer**:  
  > *"K-Means partitions space using straight linear Voronoi hyperplanes—the perpendicular bisector between two centroids. A straight hyperplane cannot bend around the curved arc of Two Moons. In Concentric Circles, both the inner ring and outer ring share the exact same spatial centroid at $(0, 0)$. Any Voronoi cut divides the plane into half-spaces passing through the center, bisecting both rings into semicircles rather than separating the inner ring from the outer ring, producing an ARI near zero."*

### Q8: How does your implementation handle an empty cluster if all points migrate away from a centroid?
* **Answer**: In `js/algorithms/kmeans.js`, if a cluster becomes empty during an iteration ($|C_k| = 0$), our reseeding strategy immediately relocates that empty centroid to the data point currently possessing the largest squared Euclidean distance from any active centroid. This prevents NaN arithmetic and maintains the requested cluster count $K$.

---

## Category C: Prim's Algorithm & MST Fundamentals

### Q9: What is a Minimum Spanning Tree (MST), and what is the Cut Property?
* **Answer**: An MST of a connected, undirected graph $G = (V, E)$ is an acyclic subgraph connecting all $N$ vertices using exactly $N - 1$ edges with minimal total edge weight. The **Cut Property** states that for any partition of vertices into $S$ and $V \setminus S$, the edge crossing the cut $(S, V \setminus S)$ with the minimum weight must belong to every MST of the graph.

### Q10: Why did you choose Prim's algorithm over Kruskal's algorithm for MST construction?
* **Answer**:
  > **20–40 Second Model Viva Answer**:  
  > *"In our problem, data points lie in continuous Euclidean space, forming a complete graph where all $N(N-1)/2$ pairwise edges exist. For dense graphs where $|E| = \Theta(V^2)$, Prim's algorithm using a distance array operates in $\Theta(N^2)$ time without sorting all $N^2$ edges. Kruskal's algorithm requires sorting all edges, taking $O(E \log E) = O(N^2 \log N)$ time, and requires storing all edges in memory. Thus, dense Prim is computationally and memory-wise optimal for our complete graph."*

### Q11: How does Zahn's MST clustering partition a spanning tree into $K$ clusters?
* **Answer**: Zahn's algorithm computes the full MST containing $N - 1$ edges, sorts the edges in descending order of length, and removes the $(K - 1)$ longest edges. Removing $K - 1$ edges from an acyclic tree disconnects it into exactly $(N - 1) - (K - 1) + 1 = K$ connected subtrees. Each subtree represents an individual cluster.

### Q12: Why does MST succeed on non-convex manifolds under clean conditions?
* **Answer**: MST operates on single-linkage connectivity. Consecutive points along a crescent arc or circle are separated by small intra-cluster step sizes ($\approx 0.02$). The Euclidean gap between distinct clusters is substantially wider ($\approx 0.5$). Consequently, the $(K - 1)$ longest edges in the entire tree invariably lie in the inter-cluster gap. Severing them cleanly isolates the manifolds.

---

## Category D: Mathematical Complexity & Evaluation Metrics

### Q13: What is the Adjusted Rand Index (ARI), and why is it preferred over classification accuracy?
* **Answer**:
  > **20–40 Second Model Viva Answer**:  
  > *"Classification accuracy requires an exact 1-to-1 match between predicted cluster IDs and class labels. In clustering, cluster labels are arbitrary permutations—Cluster 0 could correspond to Class 1. Furthermore, raw accuracy and the raw Rand Index do not correct for chance agreement. Hubert and Arabie's Adjusted Rand Index (ARI) evaluates all $\binom{N}{2}$ pairs of observations and adjusts for chance under a hypergeometric model. It yields an expected value of 0.0 for random label assignments and 1.0 for perfect concordance, making it invariant to label permutations."*

### Q14: What is the mathematical definition of ARI degradation ($\Delta\text{ARI}$), and why clamp it at zero?
* **Answer**:
  $$\Delta \text{ARI} = \max\left(0.0, \; \text{ARI}_{\text{baseline}} - \text{ARI}_{\text{perturbed}}\right)$$
  We clamp it at zero because $\Delta\text{ARI}$ is explicitly designed as a one-sided measure of **performance loss**. On failing baselines (such as K-Means on Circles where baseline ARI is $-0.0029$), adding noise might cause a minor stochastic fluctuation to $+0.0002$. This is not genuine algorithmic improvement; clamping treats random fluctuations around failing baselines as zero degradation.

### Q15: What is the theoretical time complexity of K-Means versus dense Prim's MST?
* **Answer**:
  * **K-Means**: $O(I \cdot K \cdot N)$ time and $O(N + K)$ space, where $I$ is iterations, $K$ is clusters, and $N$ is sample size. In practice, $I$ is small ($I \ll N$), making K-Means scale linearly with $N$.
  * **Prim's Dense MST**: $\Theta(N^2)$ time to evaluate complete graph distances and update keys, plus $O(N \log N)$ to sort tree edges and $O(N \alpha(N))$ for Disjoint Set Union. Total time is dominated by $\Theta(N^2)$, with $O(N)$ auxiliary space.

### Q16: Why should empirical benchmark speedup distinguish the ratio of means from the ratio of medians?
* **Answer**:
  > **20–40 Second Model Viva Answer**:  
  > *"In micro-benchmarks on modern operating systems, individual sub-millisecond execution passes can be affected by CPU throttling, background thread interrupts, or browser garbage collection. The median runtime is a robust statistic that filters out extreme trial spikes, producing a ratio of medians of $17.00\times$ at $N=600$. The ratio of arithmetic means accounts for the total aggregate work across all trials, yielding $12.14\times$. Reporting both avoids cherry-picking and provides full scientific transparency."*

---

## Category E: Noise, Outliers & Robustness Mechanics

### Q17: Why did you separate Gaussian noise experiments from outlier experiments?
* **Answer**: If noise and outliers are added simultaneously, it creates confounded variables. If an algorithm fails, you cannot determine whether failure was caused by coordinate dispersion blurring cluster boundaries or by ambient outlier points bridging the gap. Testing them independently isolates the exact failure mechanism of each perturbation.

### Q18: What is "Pendant Edge Cut Misallocation," and why does it cause MST to fail under outliers?
* **Answer**:
  > **20–40 Second Model Viva Answer**:  
  > *"When uniform outliers are scattered across the bounding box, they land far from inlier clusters. The edge connecting an isolated outlier to the minimum spanning tree is a peripheral 'pendant' edge with a very large Euclidean distance. Because Zahn's clustering naively removes the $(K - 1)$ longest edges in the entire tree, those cuts are consumed by severing isolated outlier points into singleton clusters. Consequently, all 300 genuine inliers remain trapped in a single giant component, causing Inlier ARI to plunge to exactly 0.0000."*

### Q19: Why does K-Means demonstrate high robustness to uniform ambient outliers on Gaussian Blobs?
* **Answer**: In K-Means, centroids are updated as arithmetic means of all cluster members. When outliers are distributed uniformly across the bounding box, their pulling forces are roughly symmetric in all directions. For a cluster with 100 inliers, adding a few uniform outliers causes minimal centroid drift, keeping the Voronoi boundary stable and preserving an Inlier ARI of 1.0000.

### Q20: What is single-linkage chaining?
* **Answer**: Single-linkage chaining occurs when a sequence of intermediate noise points bridges the spatial gap between two distinct clusters. Because single-linkage clustering defines inter-cluster distance as the minimum distance between any pair of points, a contiguous chain of short noise edges causes the algorithm to merge the two clusters into one.

---

## Category F: Experimental Findings & Empirical Results

### Q21: What were the exact ARI scores for K-Means and MST on clean baseline datasets?
* **Answer**:
  * **Gaussian Blobs ($K=3$)**: K-Means = $1.0000 \pm 0.0000$; MST = $1.0000 \pm 0.0000$.
  * **Two Moons ($K=2$)**: K-Means = $0.1941 \pm 0.0588$; MST = $1.0000 \pm 0.0000$.
  * **Concentric Circles ($K=2$)**: K-Means = $-0.0019 \pm 0.0012$; MST = $1.0000 \pm 0.0000$.

### Q22: At what noise level does MST break down on Two Moons and Concentric Circles?
* **Answer**:
  * On **Two Moons**, MST holds at $\text{ARI} = 1.0000$ at $\sigma = 0.05$, degrades to $0.6667$ at $\sigma = 0.10$, and collapses to $0.0000$ at $\sigma = 0.20$ ($\Delta\text{ARI} = 1.0000$).
  * On **Concentric Circles**, MST holds at $\text{ARI} = 1.0000$ through $\sigma = 0.10$, but collapses to $0.0935$ at $\sigma = 0.20$ ($\Delta\text{ARI} = 0.9065$).

### Q23: What happened to MST when 5% outliers were added to Two Moons?
* **Answer**: Inlier ARI collapsed instantly from $1.0000$ to **$0.0000$** ($\Delta\text{ARI} = 1.0000$). The single tree cut ($K - 1 = 1$) was consumed by severing a distant outlier pendant edge, leaving all 300 crescent points lumped together in the remaining component.

### Q24: What were the execution runtimes measured in your performance benchmarks at $N = 600$?
* **Answer**: On Gaussian Blobs ($K=3$), K-Means achieved a mean runtime of $0.1400\text{ ms}$ (median $0.1000\text{ ms}$). Prim's MST achieved a mean runtime of $1.7000\text{ ms}$ (median $1.7000\text{ ms}$). This demonstrated an empirical speedup of $12.14\times$ (ratio of means) and $17.00\times$ (ratio of medians) in favor of K-Means.

---

## Category G: Implementation & Software Architecture

### Q25: Why did you build this project using Vanilla JavaScript rather than Python?
* **Answer**:
  > **20–40 Second Model Viva Answer**:  
  > *"Building this natively in JavaScript allowed us to create a 100% dependency-free, transparent scientific application that runs immediately on any browser without installing Python, Anaconda, or external libraries. It forced us to write the algorithms from scratch—including K-Means++, Prim's algorithm, Union-Find, and the Adjusted Rand Index formula—giving us deep mathematical understanding. Furthermore, it enabled an interactive visual explorer and instant demonstration capabilities for our lab viva."*

### Q26: How did you ensure deterministic reproducibility without a backend database?
* **Answer**: We implemented an internal Linear Congruential Generator (LCG) PRNG in `js/data/prng.js` with modulus $2^{32}$. By passing fixed seed integers ($11, 22, 33$), the generator produces the exact same sequence of pseudo-random floating-point numbers across any browser, guaranteeing bit-for-bit identical coordinates.

### Q27: How did you verify the correctness of your algorithms?
* **Answer**: We engineered an automated test runner (`tests/test_runner.html` and `tests/test_suite.js`) executing **64 unit tests** covering PRNG uniformity, Box-Muller normality, K-Means convergence, Prim MST cut properties, Disjoint Set Union cycle prevention, and mathematical contingency matrix calculations. All 64 tests pass in under 50 ms.

### Q28: How do you measure microsecond execution times in JavaScript, and what are the limitations?
* **Answer**: We use the browser monotonic timer `window.performance.now()`. Unlike `Date.now()`, it measures relative to navigation start and is not subject to system clock adjustments. Its limitation is anti-fingerprinting quantization: modern browsers round timer resolution to between $5\,\mu\text{s}$ and $100\,\mu\text{s}$ to mitigate Spectre side-channel attacks. Operations completing faster than $\sim 40\,\mu\text{s}$ legitimately record as $0.000\text{ ms}$.

---

## Category H: Project Limitations, Partner Roles & Future Scope

### Q29: What are the main scientific limitations of your experimental protocol?
* **Answer**:
  > **20–40 Second Model Viva Answer**:  
  > *"We acknowledge three main limitations: First, testing three random seeds ($M = 3$) provides exploratory variance rather than tight confidence intervals. Second, our datasets are restricted to two-dimensional synthetic manifolds, which do not exhibit high-dimensional metric concentration effects. Third, browser timer quantization coarsens sub-millisecond execution runtimes. However, these choices allowed exact visual auditing and controlled parameter isolation."*

### Q30: What practical recommendation would you give to an engineer choosing between K-Means and MST?
* **Answer**:
  * If the problem domain involves **compact, spherical clusters with background noise or outliers**, select **K-Means** for its noise averaging and linear scalability.
  * If the domain involves **clean, continuous non-linear manifolds without outlier contamination**, select **MST clustering**.
  * If the data contains **both non-convex manifolds AND heavy outliers**, **neither standard algorithm is suitable**; use density-based algorithms like DBSCAN or outlier-trimmed MST.

### Q31: How would you extend this project in the future?
* **Answer**:
  1. **Density-Trimmed MST**: Pruning vertices with high average $k$-nearest-neighbor distance before computing the spanning tree to prevent pendant edge hijacking.
  2. **Delaunay Triangulation**: Constructing Euclidean MSTs in $O(N \log N)$ time using planar Delaunay graphs instead of dense $O(N^2)$ Prim.
  3. **High-Dimensional Spaces**: Benchmarking robustness across dimensions $D \in [2, 100]$.

### Q32: What specific contributions did each project partner make to this work?
* **Answer**:
  * **Himanshu Gupta (Allocation No. 19)**: Focused on algorithmic formulation, dense Prim MST implementation, Union-Find component extraction, mathematical derivations of Adjusted Rand Index, automated robustness sweep orchestration, and evidence verification.
  * **Parth Yadav**: Focused on Lloyd's K-Means with K-Means++ initialization, synthetic manifold generator pipelines (Blobs, Moons, Circles), Canvas visualization layouts, micro-benchmark timing harnesses, and comparative data analysis.
  * *Both partners collaborated equally on experiment execution, scientific validation, report authoring, and presentation preparation.*
