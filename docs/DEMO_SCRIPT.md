# Live Academic Demonstration Script
## 5-to-7 Minute Interactive Walkthrough for Project Evaluation & Lab Viva

* **Course**: Pattern Matching Lab (`BCS-DS-777`)
* **Project**: MST vs K-Means Robustness Analysis
* **Lead Demonstrator**: Himanshu Gupta (Allocation No. 19)
* **Co-Demonstrator**: Parth Yadav
* **Faculty Guide / Instructor**: Mr. Aman Kumar, Assistant Professor
* **Institution**: Manav Rachna International Institute of Research and Studies (MRIIRS), Faridabad
* **Target Duration**: 5:00 to 7:00 Minutes
* **Application Platform**: Interactive Streamlit Research Laboratory (`python_app/app.py`)
* **Live Deployment URL**: [https://mst-kmeans-robustness-analysis.streamlit.app/](https://mst-kmeans-robustness-analysis.streamlit.app/)

---

## Demonstration Checklist & Setup Pre-Flight

Before inviting the examiners to the screen:
1. Ensure the Streamlit application is running locally:
   ```powershell
   $env:PYTHONPATH = "python_app"
   streamlit run python_app/app.py
   ```
   *(Or have the live Streamlit Cloud URL loaded in Google Chrome or Microsoft Edge at full screen (`F11`)).*
2. Have a second terminal window prepared to demonstrate the automated test suite:
   ```powershell
   $env:PYTHONPATH = "python_app"
   pytest python_app/tests -v
   ```
3. Verify browser zoom is set to **100%** (or **90%** if on a 1080p display) so Plotly charts, sidebar controls, and data tables are fully visible without horizontal scrolling.
4. Keep the local `Downloads` directory accessible to verify CSV and JSON configuration downloads.

---

## Timed Demonstration Walkthrough

```
+---------------------------------------------------------------------------------------------------+
|  PHASE / TIME   |  STREAMLIT VIEW             |  EXACT USER ACTION & SPOKEN HIGHLIGHT             |
+-----------------+-----------------------------+---------------------------------------------------+
| 0:00 - 0:45     | 1. Overview                 | Show academic cards, research abstract & badges   |
| 0:45 - 1:45     | 2. Clustering Playground    | Blobs (K=3, 300 pts) -> Both achieve ARI = 1.0000 |
| 1:45 - 2:45     | 2. Clustering Playground    | Two Moons (K=2) -> Linear K-Means cuts vs MST 1.0 |
| 2:45 - 3:30     | 2. Clustering Playground    | Add 5% outliers -> Demonstrate Pendant Collapse   |
| 3:30 - 4:15     | 5. Robustness Analysis      | Run paired noise & outlier sweep -> Show bands    |
| 4:15 - 5:00     | 3. Performance Benchmarks   | Run N in [100..600] -> Show O(N^2) vs O(N*K*I)    |
| 5:00 - 5:45     | 4. Algorithm Explorer       | Step through Prim's edge relaxations & tree cuts  |
| 5:45 - 6:30     | 6-7. CSV / Config & Pytest  | Export config JSON -> Run 169 automated tests     |
+---------------------------------------------------------------------------------------------------+
```

---

### Step 1: Opening & Overview (0:00 – 0:45)
* **User Action**:
  * Navigate to **1. Overview** in the Streamlit sidebar.
  * Highlight the research abstract, inductive bias cards, and institutional credentials.
* **Demonstrator Dialogue (Himanshu Gupta)**:
  > *"Respected examiners, welcome to our live demonstration. Our research platform is built natively in Python using Streamlit and pure NumPy algorithm implementations from first principles, with zero external clustering library delegation.
  > In the sidebar and header, you will observe our academic accreditation: Allocation Number 19, Pattern Matching Lab (`BCS-DS-777`), MRIIRS, under the guidance of Mr. Aman Kumar.
  > The platform comprises eight specialized research modules: the Clustering Playground, Performance Benchmarks, the Algorithm Explorer, Robustness Analysis, Dataset & CSV Import, Reproducibility & Configuration, and Methodology. Let us begin in the Playground."*

---

### Step 2: Playground — Gaussian Blobs ($K=3$) (0:45 – 1:45)
* **User Action**:
  * In the sidebar navigation, select **2. Clustering Playground**.
  * In the parameter controls:
    * **Dataset Topology**: Select `Gaussian Blobs`.
    * **Sample Size ($N$)**: Set to `300`.
    * **Number of Clusters ($K$)**: Set to `3`.
    * **Gaussian Noise ($\sigma$)**: Keep at `0.00`.
    * **Outlier Rate**: Keep at `0%`.
  * Click the **Generate & Cluster Data** button.
* **Demonstrator Dialogue (Parth Yadav)**:
  > *"Here we generate 300 clean observations from three well-separated Gaussian Blobs.
  > Notice the two synchronized 1:1 isotropic Plotly viewports: on the left is Lloyd's K-Means with K-Means++ initialization; on the right is dense Prim's Euclidean Minimum Spanning Tree.
  > Look at the quantitative metrics table below: both algorithms achieve an Adjusted Rand Index of exactly 1.0000.
  > Because Gaussian Blobs satisfy the compactness and convexity assumptions of both models, K-Means easily draws linear Voronoi hyperplanes, while Prim's MST constructs the spanning tree and cuts the two longest inter-cluster edges with zero misclassification."*

---

### Step 3: Playground — Two Moons Topological Contrast (1:45 – 2:45)
* **User Action**:
  * In the Playground controls, change **Dataset Topology** to `Two Moons`.
  * Set **Number of Clusters ($K$)** to `2`.
  * Keep **Noise ($\sigma$)** at `0.00` and **Outliers** at `0%`.
  * Click **Generate & Cluster Data**.
* **Demonstrator Dialogue (Himanshu Gupta)**:
  > *"Now watch what happens when we switch to a non-convex, manifold-based geometry: Two Moons.
  > Notice the stark theoretical contrast: K-Means cuts directly across both interlocking crescents with a linear boundary, achieving an Inlier ARI of only approximately 0.19 to 0.25. Its objective function mathematically minimizes squared Euclidean distance to centroids, forcing linear Voronoi partitions that can never conform to curved manifolds regardless of iteration budget.
  > In contrast, Prim's MST achieves a perfect Inlier ARI of 1.0000. Operating on single-linkage geometric proximity, MST traces the manifold structure along each crescent and cuts the single bridge connecting the tips."*

---

### Step 4: Playground — The 5% Outlier Stress Test (2:45 – 3:30)
* **User Action**:
  * Keep topology as `Two Moons`.
  * Slide **Outlier Rate** to `5%` (injecting uniform ambient noise across the bounding box).
  * Click **Generate & Cluster Data**.
* **Demonstrator Dialogue (Parth Yadav)**:
  > *"Here is our core empirical discovery: we inject just 5% uniform ambient outliers.
  > Instantly, graph-theoretic MST clustering suffers catastrophic collapse!
  > Notice the right Plotly viewport: a distant outlier in the bounding-box corner creates a long 'pendant' branch. When MST cuts the $K-1 = 1$ longest edge, that single cut is consumed isolating the lone outlier into its own singleton cluster, leaving both interlocking crescent moons trapped together in the remaining cluster.
  > In the metrics table, Inlier ARI plummets from 1.0000 straight to 0.0000.
  > This visually proves Pendant Edge Cut Misallocation—the primary failure mode of single-linkage graph clustering."*

---

### Step 5: Robustness Analysis Suite (3:30 – 4:15)
* **User Action**:
  * Select **5. Robustness Analysis** from the sidebar navigation.
  * Show the sweep regime controls: Noise sweep ($\sigma \in [0.00, 0.20]$) and Outlier sweep ($\epsilon \in [0.00, 0.20]$).
  * Select `Quick Mode (3 Seeds: 11, 22, 33)` and click **Run Robustness Experiment**.
  * Allow the progress bar to complete.
* **Demonstrator Dialogue (Himanshu Gupta)**:
  > *"In the Robustness Analysis module, the system runs paired Monte Carlo sweeps across deterministic seeds where both algorithms receive exact bitwise-identical feature coordinates.
  > The interactive Plotly charts with $\pm 1\sigma$ sample standard deviation error bands clearly illustrate the divergence:
  > Under Gaussian coordinate jitter, MST is resilient up to moderate noise but degrades as coordinates overlap.
  > Under uniform outlier contamination, MST experiences an immediate cliff at just 5% outliers, while K-Means degrades gracefully.
  > The degradation cards confirm that K-Means suffers negligible degradation on Blobs, while MST suffers severe degradation on non-convex manifolds once ambient noise is present."*

---

### Step 6: Performance Benchmarks & Runtime Scaling (4:15 – 5:00)
* **User Action**:
  * Select **3. Performance Benchmarks** from the sidebar navigation.
  * Sample sizes: `100, 200, 400, 600`.
  * Repetitions: `5`.
  * Click **Run Benchmarks**.
* **Demonstrator Dialogue (Parth Yadav)**:
  > *"In the Performance Benchmarks section, we profile clustering wall-clock execution time using Python's high-resolution monotonic timer (`time.perf_counter`) with pre-benchmark warm-up exclusion.
  > Look at the empirical scaling curves: at $N = 100$, both algorithms execute in fractions of a millisecond.
  > But as $N$ scales to 600, dense Prim's MST scales quadratically according to its theoretical $\Theta(N^2)$ all-pairs distance complexity, whereas K-Means scales linearly $\mathcal{O}(I \cdot N \cdot K \cdot D)$.
  > The ratio-of-means table quantitatively confirms that K-Means is substantially faster on larger sample sizes."*

---

### Step 7: Algorithm Explorer — Step-by-Step Mechanics (5:00 – 5:45)
* **User Action**:
  * Select **4. Algorithm Explorer** from the sidebar navigation.
  * Select **Prim's MST Explorer** (or K-Means Centroid Explorer).
  * Step forward 3–4 times using the **Next Step** button or move the iteration slider.
* **Demonstrator Dialogue (Himanshu Gupta)**:
  > *"For pedagogical clarity and lab evaluation, we built an educational Algorithm Explorer.
  > As we step forward through Prim's algorithm on a micro-dataset, the visualization tracks the visited vertex set growing, candidate frontier edges being evaluated, and the minimum-weight edge committed to the tree.
  > In the cut phase, the longest edges are severed, partitioning the Disjoint Set Union into colored components.
  > Every step is accompanied by mathematical commentary and LaTeX formulas."*

---

### Step 8: CSV / Config Provenance & Automated Test Suite (5:45 – 6:30)
* **User Action**:
  * Navigate to **7. Reproducibility & Configuration** to show JSON schema v1.0.0 export and restoration.
  * Switch to the terminal window and run:
    ```powershell
    $env:PYTHONPATH = "python_app"
    pytest python_app/tests -v
    ```
* **Demonstrator Dialogue (Parth Yadav & Himanshu Gupta)**:
  > *"Finally, every experimental result supports strict scientific provenance with one-click JSON reproducibility configuration and CSV dataset export.
  > To verify total software engineering rigor, here is our complete automated test suite: 169 automated tests covering algorithm convergence, graph invariants, synthetic generation, noise decoupling, CSV validation, and Streamlit AppTest UI integrity pass with a 100% success rate.
  > This concludes our live demonstration. We are ready for your questions."*

---

## Contingency & Backup Demonstration Strategies

1. **If local Streamlit server encounters port collision or slow startup**:
   * *Action*: Immediately switch to the live deployed Streamlit Cloud application: [https://mst-kmeans-robustness-analysis.streamlit.app/](https://mst-kmeans-robustness-analysis.streamlit.app/).
2. **If an interactive figure shows a stale marker after modifying a slider**:
   * *Action*: Click the **Generate & Cluster Data** button to re-execute clustering. The deterministic PRNG guarantees identical results for identical seeds.
3. **If examiners ask to see a specific seed or verify paper data**:
   * *Action*: Enter seed `11` on Two Moons ($N=300$). This generates the exact coordinates analyzed in Table 8.3 and Table 8.6 of the final academic project report.
4. **If examiners request reference parity verification**:
   * *Action*: Point to `test_reference_validation.py` which mathematically validates our custom Lloyd's K-Means and dense Prim's MST against `scikit-learn` and `scipy` reference implementations.
