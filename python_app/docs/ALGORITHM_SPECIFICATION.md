# Mathematical Specification & Algorithm Theory
## MST vs K-Means Robustness Analysis — Phase M2

### Academic Context
- **Course:** Pattern Matching Lab (`BCS-DS-777`)
- **Institution:** Manav Rachna International Institute of Research and Studies (MRIIRS), School of Engineering & Technology
- **Degree:** B.Tech Computer Science & Engineering (AIML), 7th Semester (2026–2027)
- **Student Researchers:**
  - Himanshu Gupta (Roll No: `[REDACTED_STUDENT_IDENTIFIER]`)
  - Parth Yadav (Roll No: `[REDACTED_STUDENT_IDENTIFIER]`)
- **Package Location:** `python_app/clustering_lab/algorithms/`

---

## 1. Overview and Problem Definition

Clustering is an unsupervised learning task that partitions an unlabeled dataset:
$$X = \{x_1, x_2, \ldots, x_N\} \subset \mathbb{R}^D$$
into $k$ meaningful subsets (clusters) $C = \{C_0, C_1, \ldots, C_{k-1}\}$ such that samples within the same cluster exhibit high similarity, while samples in different clusters exhibit low similarity.

In this research suite, two fundamentally contrasting clustering paradigms are examined:
1. **Lloyd's K-Means:** A **centroid-based, parametric** algorithm that minimizes intra-cluster variance under Euclidean geometric assumptions.
2. **Euclidean Minimum Spanning Tree (MST) Clustering:** A **graph-theoretic, non-parametric** algorithm that partitions data by cutting the most significant global graph bottlenecks (equivalent to single-linkage hierarchical clustering).

---

## 2. Lloyd's K-Means Clustering

### 2.1 Mathematical Objective
K-Means partitions $N$ observations into $k$ clusters by minimizing the **Within-Cluster Sum of Squares (WCSS)**, also referred to as **Inertia** ($J$):

$$J(C, \mu) = \sum_{c=0}^{k-1} \sum_{x_i \in C_c} \|x_i - \mu_c\|_2^2$$

where:
- $\mu_c \in \mathbb{R}^D$ is the centroid (mean coordinate) of cluster $C_c$.
- $\|x_i - \mu_c\|_2^2 = \sum_{d=1}^D (x_{id} - \mu_{cd})^2$ is the squared Euclidean distance between sample $x_i$ and centroid $\mu_c$.

### 2.2 K-Means++ Initialization
Standard uniform random initialization of centroids is susceptible to sub-optimal local minima. The **K-Means++** heuristic resolves this by spreading out initial cluster seeds:

1. **First Center Selection:** Choose the first centroid $\mu_0$ uniformly at random from $X$:
   $$P(\mu_0 = x_i) = \frac{1}{N}$$
2. **Subsequent Centers Selection:** For $c = 1, \ldots, k-1$:
   - For each observation $x_i \in X$, compute its shortest squared distance to any already chosen center:
     $$D(x_i)^2 = \min_{j < c} \|x_i - \mu_j\|_2^2$$
   - Sample the next centroid $\mu_c$ from $X$ with probability proportional to $D(x_i)^2$:
     $$P(\mu_c = x_i) = \frac{D(x_i)^2}{\sum_{j=1}^N D(x_j)^2}$$

> **Important Theoretical Distinction:**
> Arthur and Vassilvitskii (2007) proved that K-Means++ achieves an **$O(\log k)$ competitive ratio** in expectation:
> $$\mathbb{E}[J_{\text{init}}] \le 8(\ln k + 2) J_{\text{opt}}$$
> **Clarification:** The bound $O(\log k)$ refers strictly to the **expected approximation ratio of clustering cost (inertia)** relative to the global optimum, **not** to the runtime complexity of the initialization phase.

### 2.3 Lloyd's Alternating Optimization Algorithm
After initialization, Lloyd's algorithm alternates between two steps until convergence:

1. **Assignment Step:** Each observation $x_i$ is assigned to its nearest centroid:
   $$c(i) = \arg\min_{c \in \{0, \ldots, k-1\}} \|x_i - \mu_c\|_2^2$$
   *Tie-Breaking:* In our implementation, distance ties are resolved deterministically by choosing the lowest cluster index $\min(c)$.

2. **Update Step:** Each centroid is recomputed as the arithmetic mean of its assigned points:
   $$\mu_c = \frac{1}{|C_c|} \sum_{x_i \in C_c} x_i$$

### 2.4 Convergence & Empty Cluster Handling
- **Convergence Criterion:** The algorithm terminates when the maximum Euclidean displacement across all centroids falls below a predefined tolerance $\varepsilon$:
  $$\max_{c} \|\mu_c^{(t)} - \mu_c^{(t-1)}\|_2 < \varepsilon$$
  or when the iteration count reaches `max_iter`.
- **Empty Cluster Strategy:** If a cluster becomes empty ($|C_c| = 0$), the empty centroid is reseeded at the sample $x_i$ that currently has the maximum squared distance to its assigned centroid.
- **Mathematical Limits on Degenerate Data:** If a dataset contains fewer than $k$ distinct coordinate values ($U < k$), it is mathematically impossible to construct $k$ distinct non-empty clusters. In this regime, redundant centroids will naturally overlap with existing sample coordinates.

---

## 3. Euclidean Minimum Spanning Tree (MST) Clustering

### 3.1 Graph Representation & Spanning Tree
Let the complete Euclidean graph be $G = (V, E)$, where:
- Each observation $x_i$ is a vertex $v_i \in V = \{0, 1, \ldots, N-1\}$.
- Every pair $(u, v)$ with $u \neq v$ has an undirected edge with weight equal to the Euclidean distance:
  $$w(u, v) = \|x_u - x_v\|_2$$
- The graph has $|V| = N$ vertices and $|E| = \frac{N(N-1)}{2}$ edges.

A **Spanning Tree** $T = (V, E_T)$ is a connected, acyclic subgraph spanning all $N$ vertices, containing exactly $|E_T| = N - 1$ edges.

The **Minimum Spanning Tree (MST)** minimizes the total edge weight:
$$W(T) = \sum_{e \in E_T} w(e)$$

### 3.2 Dense Prim's Algorithm
Prim's algorithm grows a single tree $T$ starting from an arbitrary root (vertex 0):
1. Maintain for each unvisited vertex $v$ its minimum distance to the growing tree:
   $$\text{min\_dist}[v] = \min_{u \in T} w(u, v)$$
2. At each step, select the unvisited vertex $u^*$ with minimal $\text{min\_dist}[u^*]$:
   $$u^* = \arg\min_{v \notin T} \text{min\_dist}[v]$$
   *Deterministic Tie-Breaking:* If multiple unvisited vertices achieve the same minimal distance, the vertex with the lowest index is selected.
3. Add edge $(\text{parent}[u^*], u^*)$ to $E_T$, mark $u^*$ as visited, and relax all unvisited neighbors $v$:
   $$\text{if } w(u^*, v) < \text{min\_dist}[v] \implies \text{min\_dist}[v] \leftarrow w(u^*, v), \; \text{parent}[v] \leftarrow u^*$$
4. Repeat for $N - 1$ steps.

### 3.3 The Cut Property and Single-Linkage Equivalence
The **Cut Property** states: for any cut $(S, V \setminus S)$ in graph $G$, the minimum-weight edge crossing the cut belongs to the MST.

To partition $X$ into $k$ clusters:
1. Sort all $N - 1$ tree edges in descending order of weight:
   $$w(e_{(1)}) \ge w(e_{(2)}) \ge \cdots \ge w(e_{(N-1)})$$
2. **Remove the $(k - 1)$ longest edges:**
   $$E_{\text{cut}} = \{e_{(1)}, e_{(2)}, \ldots, e_{(k-1)}\}$$
3. The remaining forest $E_{\text{retained}} = E_T \setminus E_{\text{cut}}$ contains:
   $$|E_{\text{retained}}| = (N - 1) - (k - 1) = N - k \text{ edges}$$
   forming exactly **$k$ connected components**.
4. Connected components are recovered using **Disjoint Set Union (Union-Find)** with path compression and rank optimization.

> **Equivalence to Single-Linkage Hierarchical Clustering:**
> Removing the $(k - 1)$ longest edges of an MST produces partitions mathematically identical to cutting a single-linkage dendrogram at the $(k - 1)$-th largest merge height.

---

## 4. Complexity and Performance Profile

| Dimension | Lloyd's K-Means | Dense Prim's MST Clustering |
| :--- | :--- | :--- |
| **Time Complexity** | $O(I \cdot N \cdot k \cdot D)$ ($I$ = iterations, $D$ = dimensions) | $O(N^2)$ distance evaluations + $O(N \log N)$ edge sort |
| **Space Complexity** | $O(N \cdot D + k \cdot D)$ | $O(N)$ auxiliary arrays (`min_dist`, `parent`, `in_tree`) |
| **Distance Matrix Storage** | None (computed dynamically per iteration) | None (computed row-by-row on the fly in $O(N)$ space) |
| **Deterministic Guarantee** | Stochastic initialization; deterministic with fixed seed | Fully deterministic (fixed graph topology and tie-breaking) |
| **Boundary Cases** | $k=1$ (single mean), $k=N$ (each sample is a center) | $k=1$ (0 cuts), $k=N$ ($N-1$ cuts, 0 retained weight) |

---

## 5. Inductive Biases, Strengths, and Limitations

### 5.1 Lloyd's K-Means
- **Inductive Bias:** Assumes clusters are convex, isotropic (spherical), and roughly equal in spatial variance.
- **Strengths:**
  - Computationally efficient for large $N$ when $k \ll N$.
  - Highly robust to minor background noise when clusters are well-separated compact Gaussians.
- **Limitations:**
  - Completely fails on non-globular manifolds (e.g., concentric rings, interlocking moons) because it enforces linear Voronoi decision boundaries.
  - Sensitive to extreme outliers, which pull centroids away from true cluster cores.

### 5.2 Euclidean MST Clustering
- **Inductive Bias:** Assumes clusters are connected submanifolds separated by low-density regions.
- **Strengths:**
  - Arbitrary cluster geometry: perfectly traces concentric circles, spirals, and interlocking moons without requiring convexity.
  - Global graph optimality via the minimum spanning tree cut property.
- **Limitations:**
  - **Chaining Effect:** Highly sensitive to noise bridges. A single spurious noise point positioned between two distinct clusters can cause the MST to link them with a short edge, failing to cut the true inter-cluster boundary.
