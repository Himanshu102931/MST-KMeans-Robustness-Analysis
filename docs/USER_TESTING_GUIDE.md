# User Testing Guide: MST vs K-Means Robustness Analysis

**Student:** Himanshu Gupta (Allocation #19)  
**Partner:** Parth Yadav  
**Course:** Pattern Matching Lab (BCS-DS-777)  
**Institution:** Manav Rachna International Institute of Research and Studies (MRIIRS)  

This guide provides simple, step-by-step instructions for testing every major feature of the **MST vs K-Means Robustness Analysis** dashboard. No programming knowledge or command-line tools are required.

---

## Prerequisites & Launching

The application is completely self-contained and runs in any modern web browser (Google Chrome, Microsoft Edge, Mozilla Firefox, or Safari).

1. Locate the project folder on your computer:
   `d:\7th Sem\PM\Mini project\MST-KMeans-Robustness-Analysis`
2. Double-click **`index.html`** to open the main dashboard in your browser.
3. (Optional) To open the automated test suite directly, double-click **`tests/test_runner.html`**, or click the **"🧪 Run Unit Tests"** button in the top-right corner of the dashboard header.

---

## Feature 1: Automated Unit Test Runner

**Goal:** Verify that all 63 algorithmic and scientific unit tests pass.

1. In the top-right header, click **"🧪 Run Unit Tests"**.
2. A new tab will open showing the **Automated Algorithm Test Suite**.
3. **What to observe:**
   - Look at the top summary card: It should display **`63 / 63`** in bright green with an execution time under `100 ms`.
   - Scroll through the test list: Each test should display a green **PASSED** badge.
4. Click the blue **"🔄 Re-run Tests"** button to confirm determinism.
5. Click **"← Back to Dashboard"** to return to the main platform.

---

## Feature 2: Overview & Academic Credentials

**Goal:** Inspect the research objective and student credentials.

1. On the left sidebar menu, click **"Overview"**.
2. **What to observe:**
   - Notice the header badge: **`PHASE 5: VERIFIED ACADEMIC PLATFORM`**.
   - Review student credentials: **Himanshu Gupta (Alloc #19)**, **Parth Yadav**, **MRIIRS**, **BCS-DS-777**.
   - Read the **Official Research Objective** comparing graph-theoretic single-linkage clustering with centroidal partitioning.
3. Click the blue **"Open Interactive Playground →"** button to jump directly into clustering experiments.

---

## Feature 3: Interactive Clustering Playground

**Goal:** Interactively generate synthetic datasets and observe side-by-side clustering in real time.

1. On the left sidebar, click **"Playground"**.
2. **Test 1: Convex Gaussian Blobs**
   - Under **Dataset Parameters**, keep **Dataset Geometry** as `Gaussian Blobs (Convex)`.
   - Drag **Sample Size (N)** to `300`.
   - Drag **Gaussian Noise (σ)** to `0.15`.
   - Drag **Outlier Fraction** to `6%`.
   - Click the blue **"▶ Run Comparison"** button.
   - **What to observe:**
     - **Panel 1 (Ground Truth):** Points are colored by their true cluster. Injected outliers are marked with distinct red outer halos.
     - **Panel 2 (K-Means):** Shows spherical partitions with white crosshair markers (`+`) at the computed centroids.
     - **Panel 3 (MST Clustering):** Shows the Euclidean Minimum Spanning Tree with solid green lines for retained edges and red dashed lines for cut edges.
3. **Test 2: Non-Convex Concentric Circles (The Acid Test)**
   - Change **Dataset Geometry** to `Concentric Circles (Non-Convex)`.
   - Click **"▶ Run Comparison"**.
   - **What to observe:**
     - **MST:** Correctly separates the inner circle from the outer ring ($\text{Inlier ARI} \approx 100\%$).
     - **K-Means:** Slices through the rings like a pie ($\text{Inlier ARI} \approx 0\%$), visually demonstrating its geometric limitation.
4. **Test 3: Reset to Defaults**
   - Click the **"↺ Reset to Defaults"** button at the top right.
   - Verify that all sliders and geometries reset to their initial default values ($N=300$, Blobs, $\sigma=0.05$, $0\%$ outliers).

---

## Feature 4: Robustness Analysis & Stress Testing

**Goal:** Run automated sweeps to observe how noise and outliers degrade clustering accuracy.

1. On the left sidebar, click **"Robustness"**.
2. Under **Sweep Experiment**, select `Dual Sweep (Noise & Outliers)`.
3. Under **Trial Repetitions**, select `Quick Demo (3 seeds: 11, 22, 33)`.
4. Click the blue **"▶ Run Robustness Experiments"** button.
5. **What to observe:**
   - A progress bar appears showing live execution progress.
   - Notice the **"■ Cancel"** button becomes active; clicking it will safely halt experiments mid-run.
   - **Chart 1 (Inlier ARI vs Noise):** Plots accuracy degradation curves for both algorithms as Gaussian noise increases.
   - **Chart 2 (Inlier ARI vs Outliers):** Plots accuracy degradation as uniform outliers are injected.
   - **Chart 3 (Matched Baseline Loss ΔARI):** Compares how much accuracy was lost compared to the clean baseline.
   - **Observation Table:** Displays numerical Mean $\pm 1\sigma$ standard deviation for each trial condition.

---

## Feature 5: Computational Performance Benchmarking

**Goal:** Measure empirical execution times across dataset sizes ($N = 100, 200, 400, 600$).

1. On the left sidebar, click **"Benchmarks"**.
2. **What to observe before running:**
   - The **Client Runtime Environment & Hardware Profile** card automatically detects your Operating System, CPU Core count, browser User Agent, and timer resolution (`performance.now()`).
3. Click the blue **"▶ Run Performance Benchmarks"** button.
4. **What to observe during & after run:**
   - The status bar indicates JIT compiler warm-up followed by repeated timing loops.
   - **Scaling Chart:** Displays empirical runtimes alongside theoretical $O(N)$ vs $O(N^2)$ asymptotic curves.
   - **Benchmark Table:** Shows Mean and Median runtimes for K-Means vs MST, along with the measured speedup ratio ($T_{\text{MST}} / T_{\text{KM}}$).
   - Notice that while K-Means scales near-linearly, MST runtime grows quadratically ($O(N^2)$) due to all-pairs Euclidean distance calculations.

---

## Feature 6: Step-by-Step Algorithm Explorer

**Goal:** Step through each algorithmic phase (centroid updates or Prim's edge additions) with playback controls.

1. On the left sidebar, click **"Algorithm Explorer"**.
2. **Test 1: K-Means Lloyd Exploration**
   - Click the **"⦿ K-Means Step-by-Step"** pill button.
   - Select **Points (N):** `20 Points (Recommended)`.
   - Click **"Next Step →"** repeatedly:
     - **Step 1:** Shows initial K-Means++ centroids.
     - **Step 2:** Shows points assigned to their nearest centroid with voronoi-style colored lines.
     - **Step 3:** Centroids shift to the arithmetic mean of their assigned cluster points.
     - Notice the readouts on the right update live: `Iteration`, `Inertia (WCSS)`, and `Centroid Shift`.
   - Click **"Play"** to watch the automated animation at selected speed (`1.0x`, `2.0x`).
   - Click **"↺ Restart"** to return to Step 1.
3. **Test 2: MST Prim Exploration**
   - Click the **"✂ MST Prim's Step-by-Step"** pill button.
   - Click **"Next Step →"**:
     - **Step 1:** Root vertex is selected and seeded into the tree.
     - **Steps 2 to N-1:** Dotted candidate edges appear; at each step, the shortest frontier edge turns solid green and joins the tree.
     - **Cut Phase:** The longest $K-1$ edges turn red dashed lines and are cut, splitting the tree into $K$ colored components.
     - Notice the explanation text box on the right provides pedagogical commentary for each step.

---

## Feature 7: Scientific Export Hub

**Goal:** Download publication-ready datasets (CSV), reproducibility recipes (JSON), and chart figures (PNG).

1. On the left sidebar, click **"Results & Export"**.
2. **Download Dataset CSV:**
   - Click **"⬇ Download Dataset CSV"**.
   - Your browser will download a file named `mst_kmeans_dataset_playground_....csv`.
   - Open it in Excel or Notepad: Verify that coordinates $(x, y)$, ground truth labels, outlier tags, and predicted labels are formatted cleanly without corrupted characters.
3. **Download Metrics CSV:**
   - Click **"⬇ Download Metrics CSV"**.
   - Verify that session metrics (Inlier ARI, Overall ARI, runtime) download cleanly.
4. **Download Reproducibility Recipe (JSON):**
   - Click **"⬇ Download Reproducibility Recipe (JSON)"**.
   - Open the JSON file: It contains complete academic credentials (Himanshu Gupta, Allocation #19, MRIIRS), PRNG seeds, algorithm parameters, and hardware specifications.
5. **Export Canvas PNG Figures:**
   - Scroll down to the **Publication-Ready Canvas Figures** section.
   - Click any **"Export PNG"** button (e.g., *Playground: Side-by-Side Canvas*).
   - Your browser will download a crisp high-DPI image with legends and titles suitable for academic report embedding.

---

## Verification Summary Checklist

- [x] Test suite reports **63 / 63 passed** with 0 errors.
- [x] All 6 navigation sidebar tabs switch views instantly.
- [x] Sliders and inputs update parameters dynamically.
- [x] Concentric circles demonstrate MST manifold recovery vs K-Means geometric slicing.
- [x] Robustness and benchmark experiments run smoothly with cancel buttons active.
- [x] Algorithm Explorer steppers animate centroid movements and Prim edge growth.
- [x] CSV, JSON, and PNG exports download with valid file structures.
