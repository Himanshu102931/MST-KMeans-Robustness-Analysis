# Live Academic Demonstration Script
## 5-to-7 Minute Interactive Walkthrough for Project Evaluation & Lab Viva

* **Course**: Pattern Matching Lab (`BCS-DS-777`)
* **Project**: MST vs K-Means Robustness Analysis
* **Lead Demonstrator**: Himanshu Gupta (Allocation No. 19)
* **Co-Demonstrator**: Parth Yadav
* **Target Duration**: 5:00 to 7:00 Minutes
* **Application URL**: Local `index.html` (or GitHub Pages live deployment)

---

## Demonstration Checklist & Setup Pre-Flight

Before calling the examiners over to the screen:
1. Ensure `index.html` is open in **Google Chrome** or **Microsoft Edge** at full screen (`F11`).
2. Have a second browser tab open to `tests/test_runner.html` to quickly verify algorithm unit tests.
3. Set browser zoom to **100%** (or **90%** if on a 1080p laptop display) so canvases and controls are fully visible.
4. Keep the Windows `Downloads` folder empty or clean to make exported files immediately apparent.

---

## Timed Demonstration Walkthrough

```
+-----------------------------------------------------------------------------------------------+
|  PHASE / TIME   |  DASHBOARD SECTION         |  EXACT MOUSE ACTION & SPOKEN HIGHLIGHT         |
+-----------------+----------------------------+------------------------------------------------+
| 0:00 - 0:45     | Navigation & Overview      | Open index.html -> Show academic badges        |
| 0:45 - 1:45     | Playground: Blobs          | Set K=3, 300 pts -> Run Both Algorithms        |
| 1:45 - 2:45     | Playground: Two Moons      | Set Two Moons, K=2 -> Contrast Voronoi vs MST  |
| 2:45 - 3:30     | Playground: Outlier Stress | Add 5% outliers -> Demonstrate Pendant Collapse|
| 3:30 - 4:15     | Robustness Suite           | Switch tab -> Click Run Sweep -> Show charts   |
| 4:15 - 5:00     | Performance Benchmarks     | Switch tab -> Run N=[100..600] -> Show scaling |
| 5:00 - 5:45     | Algorithm Explorer         | Switch tab -> Step through Prim's tree growth  |
| 5:45 - 6:30     | Data Exports & Test Suite  | Click CSV export -> Switch to test_runner.html |
+-----------------------------------------------------------------------------------------------+
```

---

### Step 1: Opening & Overview (0:00 – 0:45)
* **Mouse Action**:
  * Open `index.html` in Chrome or Edge.
  * Start on the default **Overview** tab.
* **Demonstrator Dialogue (Himanshu Gupta)**:
  > *"Respected examiners, welcome to our live demonstration. As you can see, our entire research system is 100% browser-native, written in pure vanilla JavaScript and HTML5 Canvas with zero backend dependencies.  
  > In the header, you will notice our official allocation details: Allocation Number 19, Pattern Matching Lab (`BCS-DS-777`), MRIIRS.  
  > The navigation bar gives us immediate access to five functional modules: the Clustering Playground, Robustness Analysis, Performance Benchmarks, the Algorithm Explorer, and the Test Suite. Let us begin in the Playground."*

---

### Step 2: Playground — Gaussian Blobs ($K=3$) (0:45 – 1:45)
* **Mouse Action**:
  * Click the **Playground** tab in the navigation bar.
  * In the left configuration panel:
    * **Dataset**: Select `Gaussian Blobs`.
    * **Sample Size**: Select `300`.
    * **Clusters (K)**: Select `3`.
    * **Noise ($\sigma$)**: Keep at `0.00`.
    * **Outlier %**: Keep at `0%`.
  * Click the green **Run Both Algorithms** button.
* **Demonstrator Dialogue (Parth Yadav)**:
  > *"Here we generate 300 clean observations from three Gaussian Blobs.  
  > Notice the two canvas viewports: on the left is Lloyd's K-Means with K-Means++ initialization; on the right is Prim's Euclidean Minimum Spanning Tree.  
  > Look at the Metrics Comparison table below: both algorithms achieve an Adjusted Rand Index of exactly 1.0000.  
  > Because these clusters are compact and convex, K-Means easily draws linear Voronoi boundaries, while MST builds dense subtrees and severs the two longest inter-cluster edges. Both succeed completely."*

---

### Step 3: Playground — Two Moons Topological Contrast (1:45 – 2:45)
* **Mouse Action**:
  * In the left panel, change **Dataset** to `Two Moons`.
  * Set **Clusters (K)** to `2`.
  * Keep **Noise** at `0.00` and **Outliers** at `0%`.
  * Click **Run Both Algorithms**.
* **Demonstrator Dialogue (Himanshu Gupta)**:
  > *"Now watch what happens when we switch to non-convex geometry: Two Moons.  
  > Notice the stark visual contrast: K-Means cuts across both crescents with a straight line, achieving an ARI of only approximately 0.19. Its linear hyperplane is mathematically blind to the curvature.  
  > On the right, MST achieves a perfect ARI of 1.0000. Because MST operates on single-linkage proximity, it traces the continuous path along each crescent and severs the single bridge across the tips."*

---

### Step 4: Playground — The 5% Outlier Stress Test (2:45 – 3:30)
* **Mouse Action**:
  * Keep dataset as `Two Moons`.
  * Slide **Outlier %** to `5%` (adding 15 ambient points).
  * Click **Run Both Algorithms**.
* **Demonstrator Dialogue (Parth Yadav)**:
  > *"Now watch our primary empirical discovery: we add just 5% uniform outliers—only 15 points.  
  > Instantly, MST collapses! Look at the MST canvas: the algorithm isolates a single outlier point in the corner as its own cluster, while leaving both interlocking moons trapped together in one giant cluster.  
  > In the metrics table, Inlier ARI drops from 1.0000 straight to 0.0000.  
  > This visually proves what we call 'Pendant Edge Cut Misallocation'—outliers create long peripheral branches that steal the algorithm's cut budget."*

---

### Step 5: Robustness Analysis Suite (3:30 – 4:15)
* **Mouse Action**:
  * Click the **Robustness Analysis** tab in the top navigation bar.
  * Point out the Parameter Sweep configuration (Noise $\sigma \in [0.00, 0.20]$, Outliers $\eta \in [0\%, 20\%]$, Seeds $11, 22, 33$).
  * Click the blue **Run Robustness Experiment** button.
  * Allow the progress bar to complete (runs in under 1 second).
* **Demonstrator Dialogue (Himanshu Gupta)**:
  > *"In the Robustness Analysis module, the system automates this across all 144 paired trials in real time.  
  > Notice the generated multi-series line charts:  
  > In the ARI vs. Noise chart, MST holds up to moderate noise, but collapses at $\sigma = 0.20$ as coordinates blur.  
  > In the ARI vs. Outlier chart, MST exhibits a steep drop at 5% and 10% contamination.  
  > The Degradation bar chart below quantitatively confirms that K-Means suffers virtually zero degradation on Blobs, while MST suffers severe degradation on curved shapes when outliers are introduced."*

---

### Step 6: Performance Benchmarks & Runtime Scaling (4:15 – 5:00)
* **Mouse Action**:
  * Click the **Performance Benchmarks** tab in the navigation bar.
  * Select sample sizes: `100, 200, 400, 600`.
  * Repetitions: `5`.
  * Click **Run Benchmark**.
* **Demonstrator Dialogue (Parth Yadav)**:
  > *"In the Performance Benchmarks section, we profile clustering runtimes using the browser's monotonic `performance.now()` timer.  
  > Notice the resulting scaling curves: at $N = 100$, both algorithms execute in a fraction of a millisecond.  
  > But as $N$ reaches 600, dense Prim's MST curves upward quadratically, taking approximately 1.7 milliseconds, while K-Means remains flat at approximately 0.14 milliseconds.  
  > This confirms the theoretical $\Theta(N^2)$ distance bottleneck of dense Prim versus the linear scalability of K-Means."*

---

### Step 7: Algorithm Explorer — Step-by-Step Mechanics (5:00 – 5:45)
* **Mouse Action**:
  * Click the **Algorithm Explorer** tab in the navigation bar.
  * Select **MST Prim Animation** (or K-Means Centroid Migration).
  * Click **Play** (or click **Step Forward** 3–4 times).
* **Demonstrator Dialogue (Himanshu Gupta)**:
  > *"To provide deep pedagogical insight, we built a step-by-step Algorithm Explorer.  
  > As we step forward in Prim's algorithm, you can see the visited vertex set growing, the active cut edges being evaluated, and the minimum-weight edge being highlighted in bright cyan as it is permanently committed to the tree.  
  > This transparently illustrates how graph connectivity is assembled one edge at a time."*

---

### Step 8: Scientific Exports & Test Runner Verification (5:45 – 6:30)
* **Mouse Action**:
  * Scroll to the export panel or return to the Robustness tab.
  * Click **Export Raw Data (CSV)** (shows instant browser download of `robustness_trials.csv`).
  * Switch to the second browser tab: `tests/test_runner.html`.
  * Show the test results container displaying **64 Passed / 0 Failed**.
* **Demonstrator Dialogue (Parth Yadav & Himanshu Gupta)**:
  > *"Finally, every piece of experimental evidence is exportable with one click into standard CSV and high-DPI PNG formats.  
  > And to guarantee software engineering integrity, here is our automated browser test runner: all 64 unit tests covering our PRNG, datasets, K-Means++, Prim MST, and Adjusted Rand Index pass in under 50 milliseconds.  
  > This concludes our live demonstration. We are ready for your questions."*

---

## Contingency & Backup Demonstration Strategies

1. **If the Benchmark takes longer than 2 seconds due to browser background throttling**:
   * *Action*: Do not wait. Immediately explain: *"The benchmark engine executes multiple warm-up iterations and 5 timed repetitions per size using microsecond timers. While it completes, we can review the pre-computed verified benchmark summary table in `results/summaries/benchmark_summary.csv`."*
2. **If a canvas appears un-rendered due to an unexpected browser window resize**:
   * *Action*: Click the **Run Both Algorithms** button again or hit `F5` to reload. The deterministic PRNG guarantees that the exact same dataset will render immediately.
3. **If examiners ask to see a specific seed**:
   * *Action*: In the code or settings, point out seeds `11`, `22`, and `33`. Entering seed `11` on Two Moons will reproduce the exact coordinates analyzed in Table 8.3 and Table 8.6 of our report.
