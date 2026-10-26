# User Testing Guide: MST vs K-Means Robustness Analysis

**Student Researchers:** Himanshu Gupta (Allocation #19) & Parth Yadav
**Faculty Guide / Course Instructor:** Mr. Aman Kumar, Assistant Professor
**Course:** Pattern Matching Lab (`BCS-DS-777`)
**Institution:** Manav Rachna International Institute of Research and Studies (MRIIRS), Faridabad
**Platform:** Python 3.12 & Streamlit Web Application (`python_app/app.py`)
**Live URL:** [https://mst-kmeans-robustness-analysis.streamlit.app/](https://mst-kmeans-robustness-analysis.streamlit.app/)

This guide provides structured, step-by-step instructions for testing every major feature of the **MST vs K-Means Robustness Analysis** laboratory.

---

## Prerequisites & Launching

The application can be run locally using Python 3.12 or accessed directly through the live cloud deployment.

### Option 1: Running Locally (Recommended)
1. Open PowerShell or Terminal at the repository root:
   ```powershell
   $env:PYTHONPATH = "python_app"
   streamlit run python_app/app.py
   ```
2. Your browser will automatically open to `http://localhost:8501`.

### Option 2: Accessing Live Cloud Deployment
- Open [https://mst-kmeans-robustness-analysis.streamlit.app/](https://mst-kmeans-robustness-analysis.streamlit.app/) in Google Chrome, Microsoft Edge, Mozilla Firefox, or Brave.

---

## Feature 1: Automated Quality Assurance Test Suite

**Goal:** Verify that all 169 algorithmic, statistical, and UI AppTest assertions pass.

1. In your terminal at the repository root, execute:
   ```powershell
   $env:PYTHONPATH = "python_app"
   pytest python_app/tests -v
   ```
2. **What to observe:**
   - Pytest executes 169 automated test cases across 12 test modules.
   - Look at the final summary line: It should display **`169 passed`** with zero failures, errors, or warnings.
   - Key modules verified:
     - `test_kmeans.py` & `test_mst.py`: Core algorithm invariants, DSU cuts, and K-Means++ convergence.
     - `test_reference_validation.py`: Mathematical parity against SciPy and scikit-learn.
     - `test_robustness_experiment.py`: Paired coordinate isolation, inlier masking, and Bessel-corrected sample standard deviations.
     - `test_streamlit_dashboard.py`: AppTest UI navigation, state persistence, and reset handling.

---

## Feature 2: Overview & Academic Credentials (Module 1)

**Goal:** Inspect research objectives, mathematical formulations, and academic accreditation.

1. In the sidebar radio navigation, select **1. Overview**.
2. **What to observe:**
   - Review institutional credentials: **Pattern Matching Lab (`BCS-DS-777`)**, **MRIIRS**, **Mr. Aman Kumar**, **Himanshu Gupta (Alloc #19)**, **Parth Yadav**.
   - Read the core inductive bias cards comparing centroid-based Voronoi hyperplanes against graph-theoretic single-linkage connectivity.
   - Check the **System Status** card confirming Python 3.12 runtime and pure NumPy package architecture.

---

## Feature 3: Interactive Clustering Playground (Module 2)

**Goal:** Interactively generate synthetic datasets and observe side-by-side clustering in real time.

1. In the sidebar, select **2. Clustering Playground**.
2. **Test 1: Convex Gaussian Blobs**
   - Under **Dataset Topology**, select `Gaussian Blobs`.
   - Set **Sample Size ($N$)**: `300`.
   - Set **Clusters ($K$)**: `3`.
   - Set **Noise ($\sigma$)**: `0.05`.
   - Set **Outlier Rate**: `0%`.
   - Click **Generate & Cluster Data**.
   - **What to observe:**
     - Left Plotly viewport shows K-Means Voronoi partitions with crosshair centroid markers.
     - Right Plotly viewport shows Prim's MST with green solid tree edges and severed inter-cluster cut edges.
     - Metrics table confirms both models achieve an Adjusted Rand Index of $pprox 1.0000$.
3. **Test 2: Non-Convex Concentric Circles (The Acid Test)**
   - Change **Dataset Topology** to `Concentric Circles`.
   - Set **Clusters ($K$)**: `2`.
   - Click **Generate & Cluster Data**.
   - **What to observe:**
     - **MST:** Correctly follows the non-linear manifold, isolating the inner circle from the outer ring ($	ext{Inlier ARI} = 1.0000$).
     - **K-Means:** Bisects both rings with a linear hyperplane ($	ext{Inlier ARI} pprox 0.0000$), visually demonstrating its fundamental geometric limitation.
4. **Test 3: The 5% Outlier Stress Test**
   - On `Two Moons` ($K=2$), set **Outlier Rate** to `5%` ($15$ ambient points).
   - Click **Generate & Cluster Data**.
   - **What to observe:**
     - MST cuts are consumed isolating a lone distant outlier, merging both distinct crescents together. Inlier ARI plummets to $0.0000$ (Pendant Edge Cut Misallocation).
5. **Test 4: Reset to Defaults**
   - Click **Reset to Defaults**. Verify all controls return to default values ($N=300$, Blobs, $\sigma=0.05$, $0\%$ outliers).

---

## Feature 4: Performance Benchmarks (Module 3)

**Goal:** Profile empirical execution times across sample sizes ($N \in \{100, 200, 400, 600\}$).

1. In the sidebar, select **3. Performance Benchmarks**.
2. Keep sample sizes `100, 200, 400, 600` and repetitions at `5`.
3. Click **Run Benchmarks**.
4. **What to observe:**
   - A live progress bar tracks execution with monotonic high-resolution timing (`time.perf_counter`) and warm-up exclusion.
   - **Scaling Curves:** Interactive Plotly curves display empirical runtimes with sample standard deviation error bars.
   - **Complexity Comparison:** Dense Prim's MST curves upward quadratically ($\Theta(N^2)$), while Lloyd's K-Means scales linearly ($\mathcal{O}(I \cdot N \cdot K \cdot D)$).
   - **Export CSV:** Click the download button to export `benchmark_summary.csv`.

---

## Feature 5: Step-by-Step Algorithm Explorer (Module 4)

**Goal:** Step through each algorithmic phase (centroid updates or Prim's edge additions) with interactive controls.

1. In the sidebar, select **4. Algorithm Explorer**.
2. **K-Means Lloyd Exploration:**
   - Select `K-Means Centroid Migration` and set $N=20$.
   - Step through iterations using **Next Step**:
     - **Step 1:** Initial K-Means++ centroids selected proportional to squared distance.
     - **Step 2:** Points assigned to nearest centroid.
     - **Step 3:** Centroids shift to arithmetic means of assigned clusters.
     - Readouts display live `Iteration`, `Inertia (WCSS)`, and `Centroid Shift`.
3. **MST Prim Exploration:**
   - Select `Prim's Minimum Spanning Tree`.
   - Step forward:
     - **Tree Growth:** Active candidate cut edges are evaluated; minimum-weight edge is committed to the tree.
     - **Cut Phase:** The $K-1$ longest edges are severed, partitioning the Disjoint Set Union into colored components.

---

## Feature 6: Robustness Analysis & Stress Testing (Module 5)

**Goal:** Execute paired Monte Carlo sweeps to quantify degradation under noise and outlier perturbations.

1. In the sidebar, select **5. Robustness Analysis**.
2. Select **Sweep Regime**: `Quick Mode (3 Seeds: 11, 22, 33)`.
3. Click **Run Robustness Experiment**.
4. **What to observe:**
   - The engine generates paired trials where both algorithms evaluate identical coordinates.
   - **Chart 1 (Inlier ARI vs Gaussian Noise):** Demonstrates coordinate jitter degradation curves with $\pm 1\sigma$ error bands.
   - **Chart 2 (Inlier ARI vs Outliers):** Demonstrates steep graph-theoretic breakdown under uniform outlier contamination.
   - **Degradation Summary:** Quantitative baseline delta metrics ($\Delta	ext{ARI} = \max(0, 	ext{ARI}_{	ext{base}} - 	ext{ARI}_{	ext{pert}})$).
   - **Export Artifacts:** Download raw trials (`robustness_trials.csv`) or aggregated summaries.

---

## Feature 7: Dataset & CSV Import (Module 6)

**Goal:** Ingest custom user datasets and test validation guards with boundary fixtures.

1. In the sidebar, select **6. Dataset & CSV Import**.
2. **Valid Labeled CSV Test:**
   - Upload `docs/manual_test_fixtures/01_valid_labeled.csv`.
   - Notice the green success banner confirms 12 rows and 3 columns parsed.
   - Click **Send to Clustering Playground** to cluster the custom file.
3. **Negative Boundary Validation:**
   - Upload `docs/manual_test_fixtures/05_invalid_nonnumeric.csv`.
   - Verify the application displays a clear error banner stating non-numeric coordinate values were detected, without crashing.

---

## Feature 8: Reproducibility & Configuration (Module 7)

**Goal:** Test round-trip export and restoration of JSON experiment configuration payloads.

1. In the sidebar, select **7. Reproducibility & Configuration**.
2. **Valid JSON Configuration Import:**
   - In the upload panel, upload `docs/manual_test_fixtures/08_valid_config.json`.
   - Notice the green banner confirms: `Configuration valid: Family circles, N=200, Seed=777`.
   - Inspect the interactive JSON tree showing schema version `1.0.0`.
3. **Malformed JSON Configuration Rejection:**
   - Upload `docs/manual_test_fixtures/07_malformed_config.json`.
   - Verify the application safely displays a red rejection banner preventing state corruption.

---

## Feature 9: Methodology & Help (Module 8)

**Goal:** Review theoretical foundations and viva defense preparation materials.

1. In the sidebar, select **8. Methodology / Help**.
2. **What to observe:**
   - Review formal mathematical definitions of Inertia ($\mathcal{J}$), Total MST Weight, Adjusted Rand Index (Hubert & Arabie 1985), and Silhouette Coefficient.
   - Review algorithmic complexity comparisons and viva examination defense questions.

---

## Verification Summary Checklist

- [x] Pytest suite reports **169 passed** with 0 errors or warnings.
- [x] All 8 Streamlit sidebar navigation views transition smoothly without exceptions.
- [x] Concentric circles demonstrate MST manifold recovery vs K-Means geometric slicing.
- [x] Robustness sweeps execute with paired coordinate guarantees and $\pm 1\sigma$ error bands.
- [x] Performance benchmarks profile wall-clock scaling using monotonic nanosecond timers.
- [x] Algorithm Explorer steppers animate centroid movements and Prim edge growth with LaTeX commentary.
- [x] CSV dataset uploader validates numeric boundaries and safely rejects non-numeric input.
- [x] JSON configuration export and restoration maintain strict schema v1.0.0 fidelity.
