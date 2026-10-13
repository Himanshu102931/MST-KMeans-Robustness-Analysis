# Algorithm Explorer Guide
## Step-by-Step Educational Micro-Visualizer & Algorithmic Mechanics

### Academic Project Information
- **Course:** Pattern Matching Lab (`BCS-DS-777`)
- **Institution:** Manav Rachna International Institute of Research and Studies (MRIIRS), School of Engineering & Technology
- **Degree:** B.Tech Computer Science & Engineering (AIML), 7th Semester (2026–2027)
- **Student Researchers:**
  - Himanshu Gupta (Roll No: `[REDACTED_STUDENT_IDENTIFIER]`)
  - Parth Yadav (Roll No: `[REDACTED_STUDENT_IDENTIFIER]`)
- **Course Instructor:** Mr. Aman Kumar, Assistant Professor
- **Active Branch:** `feature/python-streamlit-migration`
- **Module Path:** `python_app/clustering_lab/algorithms/explorer.py`

---

## 1. Educational Objective

The Algorithm Explorer module transforms complex clustering algorithms into an intuitive, step-by-step interactive laboratory. While typical clustering dashboards only show the input dataset and the final clustered output, the Algorithm Explorer exposes the **exact internal algorithmic state** at every stage:
- Centroid placement probabilities in K-Means++
- Voronoi cell assignments and centroid drift in Lloyd's iteration
- Frontier relaxation and edge addition in Prim's tree growth
- Graph cutting and connected component formation in MST clustering

> [!IMPORTANT]
> **Zero Discrepancy Principle:** The visualizer does NOT use decorative animations or mock algorithms. The explorer executes the **actual mathematical logic and tie-breaking rules** of the custom Python implementations (`kmeans.py` and `mst.py`). The final snapshot of the explorer is mathematically identical to the production output for the same input coordinates and seed.

---

## 2. Lloyd's K-Means Algorithmic Breakdown

### Step 0: Raw Observations Snapshot
- All $N$ observations are shown as unassigned gray points in 2D space.
- No centroids or cluster boundaries exist yet.

### Steps 1 to $k$: K-Means++ Centroid Initialization
To prevent poor local minima associated with arbitrary random initialization, K-Means++ seeds centroids iteratively:
1. **First Centroid ($\mu_1$):** Chosen uniformly at random from $X$.
2. **Subsequent Centroids ($\mu_2, \dots, \mu_k$):** For each point $x \in X$, compute its squared Euclidean distance to the nearest existing centroid:
   $$D(x) = \min_{j < m} \| x - \mu_j \|$$
3. Next centroid $\mu_m$ is sampled from the probability distribution proportional to $D(x)^2$:
   $$P(x) = \frac{D(x)^2}{\sum_{x' \in X} D(x')^2}$$
Each step displays the new centroid placed as a prominent star symbol.

### Iteration Steps: Lloyd's Optimization Loop
For each iteration $t = 1, 2, \dots$:
1. **Assignment Step (Voronoi Partition):** Each point $x_i$ is assigned to its nearest centroid:
   $$c(i) = \arg\min_{j \in \{0, \dots, k-1\}} \| x_i - \mu_j \|^2$$
   The chart shows points colored by their new cluster assignments.
2. **Update Step (Centroid Arithmetic Mean):** Each centroid is relocated to the arithmetic center of all points assigned to it:
   $$\mu_j^{(t+1)} = \frac{1}{|S_j|} \sum_{x \in S_j} x$$
   The visualizer shows the centroid stars shifting to their new coordinates, displaying maximum shift $\|\Delta \mu\|$.
3. **Convergence Evaluation:** If $\max_j \|\mu_j^{(t+1)} - \mu_j^{(t)}\| < \text{tol}$, the algorithm terminates.

---

## 3. Prim's MST Algorithmic Breakdown

### Step 0: Root Vertex Initialization
- Vertex $0$ is designated as the root of the spanning tree $V_{\text{tree}} = \{v_0\}$.
- Distance array is initialized: $d(v_0) = 0$, $d(v) = \infty$ for all $v \neq v_0$.
- No edges have been drawn.

### Steps 1 to $N-1$: Sequential Minimum Edge Additions
Dense Prim's algorithm expands the spanning tree one vertex at a time:
1. **Cut Edge Selection:** Identifies the unvisited vertex $u \in V \setminus V_{\text{tree}}$ with minimal connection distance to the current tree:
   $$e^* = \arg\min_{u \in V \setminus V_{\text{tree}}, v \in V_{\text{tree}}} \| X_u - X_v \|$$
   - The selected edge is added to $E_{\text{MST}}$ and highlighted in **bold orange**.
   - Tree vertices are updated in **green**; unvisited vertices remain gray.
2. **Frontier Relaxation:** Distances from the newly added vertex $u$ to all remaining unvisited vertices are updated:
   $$d(w) = \min(d(w), \| X_w - X_u \|)$$

### Step: Completed Spanning Tree
- The Minimum Spanning Tree contains exactly $N - 1$ edges spanning all $N$ vertices.
- Cumulative tree weight $W = \sum_{e \in E_{\text{MST}}} w(e)$ is reported.

### Step: Cutting the $k - 1$ Longest Edges
- In accordance with graph-theoretic single-linkage clustering, tree edges are sorted in descending order of Euclidean length.
- The $k - 1$ longest tree edges are removed.
- In the explorer, cut edges are rendered as **dashed red lines**, while retained edges remain solid green.

### Final Step: Connected Components Partition
- The remaining $N - k$ edges form a forest of $k$ disjoint connected components.
- Component membership is canonicalized via Disjoint Set Union (DSU) and assigned cluster labels $[0, k-1]$.
- Data points are displayed in their final distinct cluster colors.

---

## 4. Interactive Cockpit & Controls

| Widget | Purpose | Behavior |
| :--- | :--- | :--- |
| **Algorithm Selector** | Toggle between Lloyd's K-Means and Prim's MST | Resets trace to Step 0 |
| **Topology Selector** | Switch between Blobs, Moons, and Circles | Regenerates micro-dataset and trace |
| **Observations ($N$)** | Slider ($10 \le N \le 60$, default 30) | Keeps point counts small for clear graph visibility |
| **Clusters ($k$)** | Slider ($2 \le k \le 5$) | Adjusts centroid count or edge cut count |
| **⏮ First** | Jump to Step 0 | Shows initial dataset state |
| **◀ Prev** | Decrement step index | Rewinds one execution step |
| **Step Slider** | Direct timeline scrubbing | Jumps directly to any step $0 \dots M-1$ |
| **Next ▶** | Increment step index | Advances one execution step |
| **⏭ Last** | Jump to final step | Shows final clustered partition |
| **↺ Reset** | Return to Step 0 | Resets navigation cockpit |
| **Download PNG** | Export publication figure | Downloads current step scatter plot as valid PNG |

---

## 5. Parity Verification Card

At the bottom of every trace, the dashboard executes an automated parity check:
```
✓ Mathematical Parity Verified: The explorer's algorithmic trace precisely matches
the custom production kmeans() / mst_clustering() implementation on identical
coordinates and random seed (100% agreement on cluster labels, inertia, and tree weights).
```
This guarantees that students and examiners can trust every single displayed frame as mathematically genuine.

---

## 6. Viva Demonstration Guide

### Key Questions & Answers

**Q1: How does K-Means++ improve on standard random Lloyd initialization?**
> **Model Answer:** Standard random initialization picks $k$ centroids uniformly from the data, which often places multiple centroids in the same cluster, resulting in poor local minima and slow convergence. K-Means++ chooses the first centroid uniformly, but selects subsequent centroids with probability proportional to their squared distance $D(x)^2$ from already chosen centroids. This spreads centroids apart geometrically across the data space, achieving an expected $\mathcal{O}(\log k)$ approximation guarantee.

**Q2: In Prim's MST clustering, why do we cut the $k-1$ longest edges?**
> **Model Answer:** A spanning tree on $N$ vertices has $N-1$ edges and is minimally connected (removing any single edge divides the tree into 2 connected components). Removing $k-1$ edges partitions the tree into exactly $(N-1) - (k-1) + 1 = k$ connected components. Cutting the $k-1$ *longest* edges maximizes the minimum Euclidean distance between the resulting components, which is the exact mathematical objective of single-linkage clustering.

**Q3: Why limit the interactive explorer to $N \le 60$ observations?**
> **Model Answer:** For educational inspection, vertices, edges, star centroids, and cut boundaries must be visually legible without overlapping into an unreadable solid mass. Furthermore, dense Prim's MST on $N=30$ creates 29 sequential edge additions, providing an ideal step count (around 32 total steps) for an interactive viva demonstration without tedious navigation.
