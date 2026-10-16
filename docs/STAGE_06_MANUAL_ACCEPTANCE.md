# STAGE 06: USER-LED MANUAL ACCEPTANCE TESTING RECORD
## Minimum Spanning Tree (MST) vs. Lloyd's K-Means Robustness Analysis

- **Document Version:** 1.4.1 (Stage 06 Formally Approved & Accepted by Project Owner; Master Documentation Synchronized)
- **Baseline Git Commit:** `3e95e82` (Stage 06 Batch 2 commit consolidating Explorer fix, scientific guidance, and regression tests)
- **Active Branch:** `feature/python-streamlit-migration`
- **Application Framework:** Streamlit 1.42.0 on Python 3.12 (NumPy / SciPy / Plotly / Pandas)
- **Test Date:** October 15, 2026 (Stage 06 Completed & Formally Accepted by Project Owner; Local Brave on Windows)
- **Stage 06 Status:** **`COMPLETED — ACCEPTED BY PROJECT OWNER (October 15, 2026)`**
- **Lead Project Authors:** Himanshu Gupta & Parth Yadav (*Equal Attribution*)
- **Academic Course:** Pattern Matching Lab (BCS-DS-777), 7th Semester, MRIIRS

---

## 1. Objectives & Testing Principles

This document provides the authoritative, non-technical manual acceptance testing procedure and official verification record for the project owner and academic examiners. It documents the systematic, step-by-step verification of all eight application modules in a real web browser without requiring code modifications.

### Core Testing Principles
1. **Mathematical Grounding over Fixed Arbitrary Values:** Clustering outputs depend on stochastic initializations (Lloyd's K-Means) and seed permutations. Verification focuses on mathematical invariants (e.g., $ARI \in [-1.0, 1.0]$, $\mathcal{O}(N^2)$ vs. $\mathcal{O}(N)$ runtime scaling, single-linkage chaining failure on uniform noise) rather than fabricated fixed decimal numbers.
2. **Honest User Verification:** Every test item reflects actual manual verification conducted on the local Streamlit application primarily using the Brave browser on Windows 11.
3. **Reproducible Preconditions:** Every protocol lists the exact starting view, widget inputs, and fixtures required.
4. **Strict Privacy Compliance:** Verifies that no institutional student registration identifiers or allocation identifiers appear anywhere in user-facing text, academic cards, or exported files.

---

## 2. Environment Setup, Testing Chronology & Scope Boundaries

### 2.1 Testing Campaign Chronology & Milestone Sequence
The complete Stage 06 verification campaign followed this sequence of verified milestones:
1. **Initial Browser Acceptance Discovery:** Interactive manual testing on the local Streamlit application discovered two defects:
   - Defect `S06-DEFECT-001` (P2): Clustering Playground `Reset Defaults` raised `StreamlitWidgetAlreadyInstantiatedError`.
   - Defect `S06-DEFECT-002` (P1): Algorithm Explorer crashed with `TypeError: unexpected keyword argument 'radius'` on Concentric Circles and Two Moons.
2. **Defect Remediation & Targeted Regression Coverage:** Both defects were resolved in `python_app/app.py` and `python_app/clustering_lab/data/synthetic.py`. Additional dedicated automated regression tests were added and validated (4 tests for Playground reset in commit `3cbe6f1`; 5 defect tests across Explorer, data, and dashboard plus 2 scientific guidance regression tests in commit `3e95e82`, totaling 11 added regression tests), expanding the automated test suite to 168 tests, all verified green locally and in CI.
3. **Three-Commit Cycle Completion:** Commit `3e95e82` completed the previous three-commit development cycle (`74dbc8a`, `3cbe6f1`, `3e95e82`).
4. **Remote Branch Push:** The three commits were pushed successfully to remote branch `feature/python-streamlit-migration`.
5. **Remote GitHub Actions CI Validation:** GitHub Actions completed successfully on Ubuntu with Python 3.12, verifying all 168 automated tests passing with zero failures.
6. **Continuation of Local Browser Testing:** Manual acceptance testing resumed locally in the Brave browser on Windows 11 against `http://localhost:8501`.
7. **Negative Boundaries & Visual Checks:** Playground stale-state retention (M3), negative CSV boundaries (`05_invalid_nonnumeric.csv`), malformed JSON handling (`07_malformed_config.json`), sample publication PNG export (S2), final overview checks (M1), and supplementary quality gates (S3–S8) were completed and confirmed.
8. **Detailed Numerical & Algorithmic Module Confirmation:** Performance Benchmarks execution and CSV export (M4), synchronized Algorithm Explorer step navigation (M5), and Robustness Analysis sweep execution with artifact downloads (M6) were confirmed by the project owner.
9. **Formal Project Owner Acceptance:** Project owner formally approved and accepted Stage 06 on October 15, 2026.

### 2.2 Operational Scope & Environment Boundaries
To ensure strict traceability:
- **Git Commit Baseline:** Commit `3e95e82` on branch `feature/python-streamlit-migration`.
- **Local Manual Browser Acceptance:** Verified on `http://localhost:8501` using the Brave browser on Windows 11.
- **Remote GitHub CI Validation:** GitHub Actions workflow verified green with 168 passing tests.
- **Cloud Deployment Verification:** Reserved for Stage 07 upon separate authorization. The public Streamlit Community Cloud instance (`https://mst-kmeans-robustness-analysis.streamlit.app/`) has not yet received a separately confirmed Stage 07 live-cloud acceptance.

### 2.3 Local Application Startup
Manual acceptance testing was executed against the local Streamlit application server:

1. Open PowerShell in the project root directory (`d:\7th Sem\PM\Mini project\MST-KMeans-Robustness-Analysis`).
2. Set the Python path and launch the Streamlit server using `uv`:
   ```powershell
   $env:PYTHONPATH="python_app"
   uv run --python 3.12 --with-requirements python_app/requirements-dev.txt streamlit run python_app/app.py
   ```
3. The terminal outputs the local network URL (typically `http://localhost:8501`).
4. Open Brave, Google Chrome, Mozilla Firefox, or Microsoft Edge and navigate to:
   ```text
   http://localhost:8501
   ```
5. **To stop the local server:** Return to the PowerShell terminal and press `Ctrl + C`.

### 2.4 Test Fixtures Directory
Manual test fixtures are located in:
`docs/manual_test_fixtures/`

| Fixture File | Type | Purpose | Expected Behavior |
|---|---|---|---|
| `01_valid_labeled.csv` | CSV | 12 samples, 2D coordinates, 3 classes | Parses cleanly; ARI computed against labels |
| `02_valid_unlabeled.csv` | CSV | 8 samples, 2D coordinates, no labels | Parses cleanly; ARI displayed as N/A |
| `03_headerless.csv` | CSV | 6 samples, 2 numeric columns, no header | Without custom header toggle, first row ('1.0', '1.1') is treated as header (5 data rows parsed); documented unsupported UI capability |
| `04_whitespace_headers.csv` | CSV | Padded column headers (`  x_axis  `) | Automatically trims whitespace; maps cleanly |
| `05_invalid_nonnumeric.csv` | CSV | String corruptions in coordinate cells | Rejection banner with clear parsing error |
| `06_missing_coordinates.csv` | CSV | Only 1 numeric feature column | Rejection banner (minimum 2 coordinates required) |
| `07_malformed_config.json` | JSON | Truncated/syntax-broken JSON | Error alert: `Invalid experiment configuration` |
| `08_valid_config.json` | JSON | Valid Concentric Circles schema 1.0.0 | Exact UI restoration and clustering re-execution |

---

## 3. Test Session Organization

Testing was organized into three focused sessions covering the entire functional footprint:

```
+----------------------------------------------------------------------------------------------------+
| Session A: Foundational Interface & Core Playground (Protocols M1, M2, M2-R1, M3)                  |
| Focus: Academic branding, visual design system, dual algorithm execution, and reset/stale handling |
+----------------------------------------------------------------------------------------------------+
                                                  │
                                                  ▼
+----------------------------------------------------------------------------------------------------+
| Session B: Advanced Compute Engines & Educational Diagnostics (Protocols M4, M5, M6)                |
| Focus: Performance benchmarks, Prim step-by-step state trace, and paired robustness sweeps        |
+----------------------------------------------------------------------------------------------------+
                                                  │
                                                  ▼
+----------------------------------------------------------------------------------------------------+
| Session C: External Data, Configuration & Supplementary Quality Gates (Protocols M7, M8, S1–S8)     |
| Focus: CSV import pipeline, JSON round-trips, privacy audit, downloads, and responsive layout      |
+----------------------------------------------------------------------------------------------------+
```

---

## 4. Evaluation Criteria & Status Definitions

- **`PASS`**: Verified functional; UI behavior, visual appearance, and mathematical invariants match or exceed specified expectations in live browser testing.
- **`FAIL`**: An unhandled exception, visual breakage, calculation error, or broken workflow occurred.
- **`BLOCKED`**: The test could not be executed due to an issue in an earlier step.
- **`FIX VERIFIED BY USER`**: Defect remediation has been directly tested, confirmed resolved, and signed off by the project owner in the live browser environment.
- **`ACCEPTED`**: Formal approval granted by the project owner for the completed testing campaign.

### Defect Severity Levels
- **Critical (P1):** Application crash, white screen, unhandled Python exception, or mathematical violation.
- **Major (P2):** Primary workflow failure (e.g. export button fails to download, algorithm execution halts, button crash).
- **Minor (P3):** Visual layout glitch, misaligned text, or delayed interaction that does not block completion.
- **Trivial (P4):** Minor typo or non-blocking cosmetic detail.

---

## 5. Detailed Test Protocols

### SESSION A: Foundational Interface & Core Playground

#### Protocol M1: Overview & Academic Identity
- **Target Module:** `Overview` (Default Landing Page)
- **Goal:** Verify academic metadata, dark theme styling, system badge, and absence of private student IDs.
- **Preconditions:** Fresh application boot at `http://localhost:8501`.

| Step | UI Action | Expected Result | Actual Result | Status | Screenshot / Notes |
|:---:|---|---|---|:---:|---|
| M1.1 | Observe the top left sidebar and header. | Sidebar displays "🔬 MST vs K-Means Lab", "Pattern Matching Lab (BCS-DS-777)", and "Himanshu Gupta & Parth Yadav (Equal Attribution)". | Displays exact lab title, course code, and equal attribution. | `PASS` | Confirmed in Brave on Oct 15, 2026. |
| M1.2 | Expand the "Academic Course Details" expander in the sidebar. | Displays Institution (MRIIRS), School of Engineering & Technology, Course Instructor (**Mr. Aman Kumar**), and Course Code. | All course, institution, and instructor metadata render accurately. | `PASS` | Confirmed in Brave on Oct 15, 2026. |
| M1.3 | Check for institutional identifiers across the entire sidebar and main page. | **Zero** student registration identifiers or allocation identifiers appear anywhere in user-facing UI or exported files. | User confirmed zero institutional registration identifiers or allocation identifiers found in visible sidebar or main page. | `PASS` | Confirmed by project owner in local Brave testing on Oct 15, 2026; automated privacy tests independently enforce zero forbidden identifiers across rendered templates. |
| M1.4 | Inspect the system runtime badge in the sidebar. | Displays `Python 3.12 (Streamlit 1.42.0)` with a green indicator dot. | Runtime badge displays `Python 3.12 (Streamlit 1.42.0)` with green dot. | `PASS` | Confirmed in Brave on Oct 15, 2026. |
| M1.5 | Observe main page title and overview comparison cards. | Header displays "MST vs K-Means Robustness Analysis"; comparison cards contrast Lloyd's K-Means (Centroidal) with Prim's MST (Graph-Theoretic). | Page header and dual comparison cards render with dark glassmorphic styling. | `PASS` | Confirmed in Brave on Oct 15, 2026. |

---

#### Protocol M2: Playground Dual Execution & Topological Inductive Bias
- **Target Module:** `Clustering Playground`
- **Goal:** Execute dual clustering on non-convex Two Moons topology and confirm algorithm inductive biases.
- **Preconditions:** Navigate to `Clustering Playground` via the sidebar navigation radio.

> [!NOTE]
> **Implementation Note on Controls:**
> In the application, Two Moons has fixed $k=2$ crescent geometry. The execution button is labeled **`🚀 Generate & Run Clustering`**.

| Step | UI Action | Expected Result | Actual Result | Status | Screenshot / Notes |
|:---:|---|---|---|:---:|---|
| M2.1 | Expand "⚙️ Dataset & Algorithm Configuration". | Configuration panel opens displaying Dataset Topology, Sample Count, Seed, and Perturbation sliders. | Configuration panel opens smoothly displaying all parameter widgets. | `PASS` | Confirmed in Brave on Oct 15, 2026. |
| M2.2 | Set **Dataset Topology** = `Two Moons`. | Cluster count is automatically set to fixed $k=2$; geometry caption displays radius 1.0. | Cluster count locks to $k=2$; crescent geometry caption renders. | `PASS` | Confirmed in Brave on Oct 15, 2026. |
| M2.3 | Set **Inlier Sample Count** = `300`. | Slider updates smoothly; caption reports Inliers: 300. | Slider moves smoothly; caption reports Inliers: 300. | `PASS` | Confirmed in Brave on Oct 15, 2026. |
| M2.4 | Set **Gaussian Noise (σ)** = `0.05` and **Outlier Contamination Rate** = `0.05`. | Caption updates: Inliers: **300**, Injected Outliers: **15**, Total N: **315**. Total N remains $\le 600$. | Caption updates: 300 inliers, 15 outliers, Total N: 315. | `PASS` | Confirmed in Brave on Oct 15, 2026. |
| M2.5 | Click **`🚀 Generate & Run Clustering`**. | Spinner runs; green success alert appears: "Successfully clustered 315 observations into k=2 components." | Dual clustering completes; green success alert renders. | `PASS` | Confirmed in Brave on Oct 15, 2026. |
| M2.6 | Click tab **"Lloyd's K-Means Result"**. | Plotly figure displays partition governed by linear Voronoi cells; on non-convex crescents, linear bisectors typically split curvilinear clusters. Centroids marked by golden stars. Inlier ARI evaluates within mathematically bounded $[-1.0, 1.0]$. | Linear Voronoi bisector fragments crescents; centroids marked by stars; Inlier ARI in $[-1.0, 1.0]$. | `PASS` | Confirmed in Brave on Oct 15, 2026. |
| M2.7 | Click tab **"Prim's MST Result"**. | Plotly figure displays connected components following density-connected paths along the crescent manifolds when inter-manifold separation is clear; illustrates graph-theoretic single-linkage inductive bias. Both ARIs evaluate within valid $[-1.0, 1.0]$ bounds. Retained edges in teal/cyan. | Single-linkage graph cut tracks non-convex crescents; retained edges in teal; ARI in $[-1.0, 1.0]$. | `PASS` | Confirmed in Brave on Oct 15, 2026. |
| M2.8 | Review the comparative metrics table below the plots. | Reports Inlier ARI, Full-Data ARI, Silhouette Score, and Wall-Clock Runtime for both algorithms side-by-side. | Side-by-side metric comparison table renders all 4 metrics for both algorithms. | `PASS` | Confirmed in Brave on Oct 15, 2026. |

---

#### Protocol M2-R1: Playground Reset Defaults & Widget State Lifecycle (S06-DEFECT-001 Verification)
- **Target Module:** `Clustering Playground`
- **Goal:** Verify that clicking "Reset Defaults" safely resets all configuration parameters to baseline defaults without widget instantiation errors, and that re-clustering executes cleanly.
- **Preconditions:** Active Clustering Playground with modified non-default parameters (e.g. from Protocol M2).

| Step | UI Action | Expected Result | Actual Result | Status | Screenshot / Notes |
|:---:|---|---|---|:---:|---|
| M2-R1.1 | In Clustering Playground, confirm non-default parameters are set (e.g., Topology = Two Moons, $N=160$, Noise $= 0.08$). | Non-default settings are active in the controls expander. | Non-default controls verified active. | `PASS` | Verified in Brave on Oct 15, 2026. |
| M2-R1.2 | Click **`🔄 Reset Defaults`** button. | Application executes pre-render reset callback; page refreshes cleanly without crashing. | Pre-render callback executes cleanly; zero crash or multi-rerun loop occurs. | `FIX VERIFIED BY USER` | Confirmed by project owner in Brave browser on Oct 15, 2026 ("yes reset work"). |
| M2-R1.3 | Check the application screen for errors. | **Zero** red exception panels or `StreamlitWidgetAlreadyInstantiatedError` messages appear. | No exception banners rendered. Zero widget lifecycle crashes. | `FIX VERIFIED BY USER` | Defect S06-DEFECT-001 eliminated; verified by project owner on Oct 15, 2026. |
| M2-R1.4 | Inspect all widget controls in the expander. | Controls return to baseline: Topology = `Gaussian Blobs`, Inlier Count = `300`, Seed = `42`, Noise = `0.0`, Outliers = `0.0`, $k = 3`, Dispersion = `0.4`, Radius = `3.5`. | All controls restored to baseline defaults. | `PASS` | Verified in Brave on Oct 15, 2026. |
| M2-R1.5 | Check notification banner below action buttons. | Green feedback banner displays: `Configuration reset to Gaussian Blobs baseline.` | Green reset notification banner displayed. | `PASS` | Verified in Brave on Oct 15, 2026. |
| M2-R1.6 | Inspect displayed clustering visualizations and metrics. | Rendered results match the baseline Gaussian Blobs ($N=300, k=3$); no stale warning banner is displayed because controls equal executed parameters. | Rendered plots match baseline Blobs; zero stale warning displayed. | `PASS` | Verified in Brave on Oct 15, 2026. |
| M2-R1.7 | Click **`🚀 Generate & Run Clustering`** with the reset parameters. | Dual clustering executes smoothly on Gaussian Blobs without errors. | Dual clustering executes smoothly on baseline Blobs. | `PASS` | Verified in Brave on Oct 15, 2026. |
| M2-R1.8 | Click tabs and verify charts and metrics. | Both algorithms achieve strong clustering recovery on well-separated globular blobs ($ARI > 0.80$ typical); metric tables populate with valid finite metrics ($ARI \in [-1.0, 1.0]$). | Plots and metric tables populate with valid finite metrics ($ARI \in [-1.0, 1.0]$). | `PASS` | Verified in Brave on Oct 15, 2026. |

---

#### Protocol M3: Playground Stale-State Persistence (ISSUE-06 Remediation)
- **Target Module:** `Clustering Playground`
- **Goal:** Verify that modifying sliders does NOT collapse existing plots, but displays an amber stale banner until recomputation.
- **Preconditions:** Active execution displayed from Protocol M2 or M2-R1.

| Step | UI Action | Expected Result | Actual Result | Status | Screenshot / Notes |
|:---:|---|---|---|:---:|---|
| M3.1 | Without clicking any action button, adjust **Gaussian Noise (σ)** from `0.00` to `0.10`. | **Visualizations do not disappear or collapse.** Previous clustering plots remain fully rendered. | Existing plots remain fully rendered and interactive; no plot collapse occurs. | `PASS` | Verified in Brave on Oct 15, 2026. |
| M3.2 | Check the area directly below the configuration container. | A prominent amber warning banner appears: `⚠️ Parameters Modified — Showing Previous Clustering Results`. | Amber warning banner rendered cleanly below controls. | `PASS` | Verified in Brave on Oct 15, 2026. |
| M3.3 | Verify presence of the recompute button. | `⚡ Recompute / Update Visualizations` button is visible next to an explanatory caption. | Recompute button visible alongside explanatory caption. | `PASS` | Verified in Brave on Oct 15, 2026. |
| M3.4 | Click **`⚡ Recompute / Update Visualizations`**. | Application recalculates with noise $\sigma=0.10$; plots refresh with updated coordinates; amber stale banner dismisses. | Application recomputes clustering; plots update to $\sigma=0.10$; banner dismisses. | `PASS` | Verified in Brave on Oct 15, 2026. |

---

### SESSION B: Advanced Compute Engines & Educational Diagnostics

#### Protocol M4: Performance Benchmarks & Asymptotic Complexity
- **Target Module:** `Performance Benchmarks`
- **Goal:** Verify empirical wall-clock timing measurement, sample standard deviation ($ddof=1$), and $\mathcal{O}(N)$ vs $\mathcal{O}(N^2)$ scaling.
- **Preconditions:** Navigate to `Performance Benchmarks` via sidebar.
- **Operational Status:** `PASS — USER VERIFIED` (Module execution and raw CSV export verified in Brave on Oct 15, 2026).

> [!NOTE]
> **Implementation Note on Controls:**
> Sample sizes multiselect defaults to `[100, 200, 400, 600]`. Deselect `600` to benchmark $\{100, 200, 400\}$. Button label is **`🚀 Run Benchmarks`**.

| Step | UI Action | Expected Result | Actual Result | Status | Screenshot / Notes |
|:---:|---|---|---|:---:|---|
| M4.1 | In Sample Sizes multiselect, select exactly `100`, `200`, `400`. | Preflight estimate reports: `3 sizes × 5 repetitions = 15 measured trials (36 total algorithm executions including warm-up)`. | Preflight estimator displays 15 measured trials (36 total runs with warm-up). | `PASS` | Verified in Brave on Oct 15, 2026. |
| M4.2 | Ensure **Measured Repetitions per Size** = `5` and **Include 1 Warm-up Stage** = Checked. | Warm-up checkbox remains enabled; preflight indicator shows green safe badge. | Warm-up enabled; safe indicator displays green badge. | `PASS` | Verified in Brave on Oct 15, 2026. |
| M4.3 | Click **`🚀 Run Benchmarks`**. | Progress bar increments through trials with status text indicating current size, repetition, and algorithm. | Progress bar increments smoothly through all repetitions to 100%. | `PASS` | Verified in Brave on Oct 15, 2026. |
| M4.4 | Inspect the metric cards at the top of results. | Displays Max Scale (N=400), K-Means Mean, Prim MST Mean, and Ratio of Means (MST / KM). | Metric cards render Max Scale, K-Means Mean, MST Mean, and Ratio of Means. | `PASS` | Verified in Brave on Oct 15, 2026. |
| M4.5 | Click tab **"📈 Runtime Scaling Curves"**. | Plotly chart displays empirical runtime curves across measured sample sizes. Empirical trends illustrate contrasting computational growth profiles (near-linear centroid iterations vs. dense quadratic edge evaluations; theoretical complexity $\mathcal{O}(N)$ vs $\mathcal{O}(N^2)$ discussed separately). | User confirmed runtime scaling plots displayed correctly in local Brave testing; measured runtime values were not archived in this record. | `PASS` | Runtime curves rendered smoothly; confirmed by project owner in local Brave testing on Oct 15, 2026. |
| M4.6 | Click tab **"📊 Summary Statistics Table"**. | Table lists sample size, repetitions, mean, median, and Bessel-corrected sample standard deviation ($ddof=1$). Measured runtimes capture system timing variability across repetitions without assuming strictly monotonic scaling on individual OS runs. | Summary table populates sample sizes, repetitions, mean, median, and sample std ($ddof=1$). | `PASS` | Verified in Brave on Oct 15, 2026. |
| M4.7 | Click tab **"💾 Research Data Export"** and click **`📄 Raw Trials CSV`**. | File `benchmark_trials.csv` downloads with columns: `sample_size, repetition, algorithm, runtime_ms, k, seed, timestamp`. | File `benchmark_trials.csv` exported and reported valid by the project owner in local Brave testing. | `PASS` | Export downloaded and was reported valid by the project owner in Brave on Oct 15, 2026. |

---

#### Protocol M5: Algorithm Explorer Step-by-Step Educational Visualizer (ISSUE-05 & S06-DEFECT-002 Remediation)
- **Target Module:** `Algorithm Explorer`
- **Goal:** Verify Prim's MST and K-Means step trace synchronization between navigation buttons and slider with zero double reruns and no dataset generation crashes on non-blob topologies.
- **Preconditions:** Navigate to `Algorithm Explorer` via sidebar.
- **Operational Status:** `PASS — USER VERIFIED` (S06-DEFECT-002 resolved and verified in Brave browser by project owner on Oct 15, 2026: "yes M5 working"; navigation buttons and slider synchronization verified).

> [!NOTE]
> **Implementation Note on Controls:**
> Algorithm radio option is labeled **`Dense Prim's MST`**.

| Step | UI Action | Expected Result | Actual Result | Status | Screenshot / Notes |
|:---:|---|---|---|:---:|---|
| M5.1 | Select radio **`Dense Prim's MST`**. | Educational controls expand. Topology defaults to Two Moons / Circles. | Controls expand cleanly without unhandled exceptions. | `PASS` | Confirmed in Brave on Oct 15, 2026 ("yes M5 working"). |
| M5.2 | Set **Dataset Topology** = `Concentric Circles`, **Observations** = `20`, **Clusters (k)** = `2`. | Dataset generates cleanly without `TypeError: generate_circles() got an unexpected keyword argument 'radius'`. Trace is automatically generated for $N=20$. Total steps $= 19$ tree growth steps $+ 1$ cut step. | Concentric Circles dataset generated without errors; visualizer renders trace for $N=20$. | `FIX VERIFIED BY USER` | S06-DEFECT-002 verified resolved by project owner in Brave on Oct 15, 2026. |
| M5.2b | Set **Dataset Topology** = `Two Moons`, **Observations** = `20`, **Clusters (k)** = `2`. | Dataset generates cleanly without `TypeError: generate_moons() got an unexpected keyword argument 'radius'`. Trace is automatically generated. | Two Moons dataset generated without errors; visualizer renders trace for $N=20$. | `FIX VERIFIED BY USER` | S06-DEFECT-002 verified resolved by project owner in Brave on Oct 15, 2026. |
| M5.3 | Click **`Next ▶`** button 5 times sequentially. | Step index advances cleanly from 0 to 5; slider updates in lockstep to 5; active candidate edge displays in orange glow. | Step index and slider advance in lockstep from 0 to 5; candidate edge highlighted. | `PASS` | Synchronized button stepping verified by project owner on Oct 15, 2026. |
| M5.4 | Drag the **Step Navigation** slider directly back to Step 2. | Plot instantly updates to Step 2 state; exactly 2 edges connected; vertex highlight reflects step 2 frontier. | Plot updates instantly to step 2 state with 2 edges connected. | `PASS` | Slider scrubbing verified by project owner on Oct 15, 2026. |
| M5.5 | Click **`Next ▶`** again. | Step index advances cleanly to Step 3 without skipping, page flashing, or jumping to step 6. | Step advances cleanly to step 3 without jumping or double reruns. | `PASS` | Verified by project owner on Oct 15, 2026. |
| M5.6 | Click **`Last ⏭`**. | Step advances to the final cut stage; the longest cut edge is highlighted in red dashes, separating inner and outer rings. | Step advances to final cut stage; longest cut edge highlighted in red dashes. | `PASS` | Verified by project owner on Oct 15, 2026. |

---

#### Protocol M6: Robustness Analysis Sweeps & Failure Modes
- **Target Module:** `Robustness Analysis`
- **Goal:** Execute Quick preset robustness sweep (72 paired trials) and verify degradation error bands.
- **Preconditions:** Navigate to `Robustness Analysis` via sidebar.
- **Operational Status:** `PASS — USER VERIFIED` (Module execution, error bands, and raw CSV/JSON exports verified in Brave on Oct 15, 2026).

> [!NOTE]
> **Implementation Note on Accounting:**
> Quick Mode executes across 3 families $\times$ 3 seeds $\times$ 8 points $= 72$ paired trials ($144$ sweep clustering runs $+ 36$ baseline runs $= 180$ total algorithm executions). Execution button is labeled **`🚀 Execute Robustness Analysis Engine`**.

| Step | UI Action | Expected Result | Actual Result | Status | Screenshot / Notes |
|:---:|---|---|---|:---:|---|
| M6.1 | Verify **Execution Mode Preset** = `Quick Mode (3 Seeds — Fast Demo)`. | Seeds display `[11, 22, 33]`; experiment plan confirms 72 paired comparisons. | Quick Mode verified with seeds [11, 22, 33] and 72 paired comparisons. | `PASS` | Verified in Brave on Oct 15, 2026. |
| M6.2 | Ensure all 3 topologies are selected: Gaussian Blobs, Two Moons, Concentric Circles. | Selected count = 3; sweep type = Both Sweeps (Noise & Outliers). | All 3 topologies selected; Both Sweeps enabled. | `PASS` | Verified in Brave on Oct 15, 2026. |
| M6.3 | Click **`🚀 Execute Robustness Analysis Engine`**. | Progress bar displays sweep execution through all 72 trials to completion without unhandled exceptions. | Sweep engine executes through all 72 trials without unhandled exceptions. | `PASS` | Verified in Brave on Oct 15, 2026. |
| M6.4 | Click tab **"📉 Gaussian Noise Sweep"**. | Dual-panel Plotly figure renders Inlier ARI vs $\sigma$ with shaded $\pm 1\sigma$ standard deviation error bands. | Dual-panel Plotly figure renders Inlier ARI vs $\sigma$ with $\pm 1\sigma$ shaded error bands. | `PASS` | Verified in Brave on Oct 15, 2026. |
| M6.5 | Click tab **"📉 Uniform Outlier Contamination Sweep"**. | Dual-panel Plotly figure displays Inlier ARI response across uniform outlier rates with shaded error bands. Illustrates empirical sensitivity where spurious bridging points can induce single-linkage chaining in MST, alongside centroid shifts in K-Means under diffuse contamination. | Uniform outlier sweep illustrates empirical sensitivity and single-linkage chaining response. | `PASS` | Verified in Brave on Oct 15, 2026. |
| M6.6 | Click tab **"💾 Export Sweep Artifacts"** and download **`📄 Raw Trial Observations (CSV)`**. | CSV downloads containing raw trial observations with complete provenance metadata (implementation expectation: 144 sweep result rows for Quick Mode across 3 families $\times$ 3 seeds $\times$ 8 points $\times$ 2 sweeps). | Raw trial observations CSV exported and reported valid by the project owner in local Brave testing; individual rows were not independently counted in this record. | `PASS` | Export downloaded and was reported valid by the project owner in Brave on Oct 15, 2026. |

---

### SESSION C: External Data, Configuration & Supplementary Quality Gates

#### Protocol M7: CSV Dataset Import & Tabular Pipeline
- **Target Module:** `Dataset & CSV Import`
- **Goal:** Upload a custom tabular dataset, map coordinates, and hand off to Playground.
- **Preconditions:** Navigate to `Dataset & CSV Import` via sidebar; ensure test fixture `01_valid_labeled.csv` is accessible.
- **Operational Status:** `PASS — USER VERIFIED` (Core tabular pipeline and invalid CSV rejection verified in Brave on Oct 15, 2026).

> [!NOTE]
> **Implementation Note on Headerless CSVs:**
> The Python data loader supports headerless CSVs via `load_dataset_from_csv(..., has_header=False)`. However, the current Streamlit UI tabular parser always expects standard CSVs with a header row (`pd.read_csv` default). Positional index selection for headerless files is currently an unsupported UI capability; if a headerless file (e.g. `03_headerless.csv`) is uploaded, the first row is treated as column names.

| Step | UI Action | Expected Result | Actual Result | Status | Screenshot / Notes |
|:---:|---|---|---|:---:|---|
| M7.1 | In the file uploader, upload `docs/manual_test_fixtures/01_valid_labeled.csv`. | Green success notification appears: `File parsed successfully: 01_valid_labeled.csv (12 rows, 3 columns)`. | Green notification confirms 12 rows, 3 columns parsed. | `PASS` | Verified in Brave on Oct 15, 2026. |
| M7.2 | Inspect the preview table. | First 8 rows of CSV render cleanly with numeric coordinate columns. | Preview table renders coordinate rows cleanly. | `PASS` | Verified in Brave on Oct 15, 2026. |
| M7.3 | Set **Feature 1 (X Axis)** = `x_coord`, **Feature 2 (Y Axis)** = `y_coord`, **Ground-Truth Label** = `ground_truth_class`. | Column selectors map cleanly; target clusters $k$ defaults to 3. | Column selectors map cleanly; target clusters $k=3$. | `PASS` | Verified in Brave on Oct 15, 2026. |
| M7.4 | Click **`🚀 Load & Run Clustering on CSV`**. | Success message displays: "Successfully processed CSV dataset: 12 points clustered." | Success message confirms 12 points clustered. | `PASS` | Verified in Brave on Oct 15, 2026. |
| M7.5 | Navigate to **Clustering Playground** via the sidebar. | Playground mounts imported data; blue source notice displays: `Currently displaying imported CSV data ('01_valid_labeled.csv')`. | Playground mounts imported data; blue source notice renders. | `PASS` | Verified in Brave on Oct 15, 2026. |
| M7.6 | Return to `Dataset & CSV Import` and upload `docs/manual_test_fixtures/05_invalid_nonnumeric.csv`. | Application displays clear error banner stating non-numeric values were detected, without crashing. | Clear error banner renders stating non-numeric coordinate values detected; zero crash. | `PASS` | Negative boundary verified by project owner on Oct 15, 2026. |

---

#### Protocol M8: Configuration Export, Modification & Session Restoration
- **Target Module:** `Reproducibility & Configuration`
- **Goal:** Export JSON configuration, modify UI parameters, and restore exact session state from file.
- **Preconditions:** Navigate to `Reproducibility & Configuration` via sidebar.
- **Operational Status:** `PASS — USER VERIFIED` (Synthetic JSON export/restoration and invalid JSON rejection verified in Brave on Oct 15, 2026).

> [!NOTE]
> **Implementation Note on CSV-Origin Datasets:**
> When the active dataset originates from an external CSV, the application displays an informational notice: *"Current active dataset was imported from an external CSV. JSON configuration files reproduce synthetic geometries and cannot regenerate external CSV tabular data without the original source file."* The project owner observed and verified this notice in Brave; this is intended application behavior, NOT a defect. When switching back to a synthetic dataset, the JSON export and restoration workflow operates smoothly.

| Step | UI Action | Expected Result | Actual Result | Status | Screenshot / Notes |
|:---:|---|---|---|:---:|---|
| M8.1 | Review the **Export Current Configuration** panel on the left. | Displays active topology, sample count, cluster count, and pretty-printed JSON schema `1.0.0`. | Panel displays active geometry parameters and pretty-printed JSON schema `1.0.0`. | `PASS` | Confirmed in Brave on Oct 15, 2026 ("m8 working"). |
| M8.2 | Click **`⬇️ Download Configuration (.json)`**. | A valid JSON file (`clustering_config_....json`) downloads to the browser download folder. | Valid JSON file downloads to browser downloads directory. | `PASS` | Confirmed in Brave on Oct 15, 2026 ("m8 working"). |
| M8.3 | In the right panel ("Upload valid configuration JSON"), upload `docs/manual_test_fixtures/08_valid_config.json`. | Success message displays: `Configuration valid: Family circles, N=200, Seed=777`. Parsed dictionary renders in interactive JSON tree. | Success banner displays valid Concentric Circles configuration; JSON tree rendered. | `PASS` | Confirmed in Brave on Oct 15, 2026 ("m8 working"). |
| M8.4 | Click **`Apply Configuration & Regenerate`**. | Application reloads and applies config; navigates to Playground where Concentric Circles ($N=200$, seed 777) is rendered. | Application restores state; navigates to Playground where Concentric Circles is rendered. | `PASS` | Confirmed in Brave on Oct 15, 2026 ("m8 working"). |
| M8.5 | Upload `docs/manual_test_fixtures/07_malformed_config.json` to the uploader. | Application displays red error banner: `Invalid experiment configuration: Malformed configuration JSON`, preventing state corruption. | Red error banner displayed; malformed configuration rejected safely without state corruption. | `PASS` | Negative boundary verified by project owner on Oct 15, 2026. |

---

## 6. Supplementary Manual Acceptance Gates

| ID | Focus Area | Specific Action | Acceptance Standard | Status | Notes |
|:---:|---|---|---|:---:|---|
| **S1** | **Methodology / Help View** | Open `Methodology / Help` view. | Full theoretical formulations (Lloyd updates, Prim cut condition, ARI formula) render in LaTeX; Viva defense guide is readable. | `PASS` | Rendering verified and confirmed by project owner in local Brave testing on Oct 15, 2026 ("M7 and Supplementary works"). |
| **S2** | **Publication PNG Exports** | In Playground, click `📥 Download Ground Truth Plot (Publication PNG)`. | A valid, uncorrupted PNG image downloads containing publication-quality high-DPI rendered scatter points. | `PASS` | User confirmed sample publication PNG download rendered and opened cleanly in local Brave testing; exhaustive manual inspection of every possible export permutation was not conducted. |
| **S3** | **Responsive Viewport** | Resize browser window to mobile width ($<768\text{px}$). | Sidebar collapses to standard mobile hamburger menu; metric cards stack vertically; Plotly charts adapt to container width. | `PASS` | Fluid CSS and responsive Plotly layouts adapt cleanly to narrow mobile viewports; verified in local Brave testing. |
| **S4** | **Cross-View Session Isolation** | Run clustering in Playground, navigate through all 8 views sequentially, then return to Playground. | Previously computed clustering plots and metric cards remain fully rendered; zero session state loss or recalculation delay. | `PASS` | Session state isolation preserves executed results across all eight views without recalculation delay; verified in local Brave testing. |
| **S5** | **Browser Console Audit** | Open Browser Developer Tools (`F12` $\to$ Console). Perform several runs. | **Zero** unhandled JavaScript errors, missing asset 404s, or broken WebSocket disconnect loops. | `PASS` | Clean developer console in Brave; zero uncaught exceptions or network 404s; verified by project owner on Oct 15, 2026. |
| **S6** | **Keyboard Accessibility** | Use `Tab`, `Shift+Tab`, and `Enter` to navigate controls without mouse. | Focus indicators are visible; buttons and inputs can be triggered via keyboard. | `PASS` | Full tab traversal and button triggering verified functional without mouse dependency; verified in local Brave testing. |
| **S7** | **Public Privacy Audit** | Perform page text search (`Ctrl + F`) for university registration identifiers across all modules. | Exactly **0** student registration identifiers or allocation identifiers found across application views and exports. | `PASS` | User confirmed manual search yielded zero matches in local Brave testing. Comprehensive absence across code comments, HTML renders, and CSV/JSON exports is independently enforced by automated privacy test suite (`test_academic_metadata_and_forbidden_strings`, `test_comprehensive_public_privacy_enforcement`). |
| **S8** | **Plotly Visual Interactivity** | Hover over individual points and edges in Playground and Explorer. | Hover tooltips display exact $(X, Y)$ coordinates, predicted cluster ID, and ground truth label; zoom/pan controls operate smoothly without distortion. | `PASS` | Isotropic aspect ratios, coordinate hover tooltips, and pan/zoom controls respond smoothly; verified in local Brave testing. |

---

## 7. Defect & Observation Log

| Log ID | Module | Protocol Step | Severity (P1–P4) | Observed Behavior | Steps to Reproduce | Resolution Status |
|:---:|---|---|---|---|---|:---:|
| **S06-DEFECT-001** | Clustering Playground | `Reset Defaults` (M2-R1.2–M2-R1.3) | **P2 — Major** | Clicking `Reset Defaults` button raised `StreamlitWidgetAlreadyInstantiatedError: st.session_state['pg_dataset_family'] cannot be modified after the widget with that key is instantiated.` | In Clustering Playground, adjust sliders or topology, then click `Reset Defaults`. Originally reproduced by project owner on Oct 15, 2026. | **`FIX VERIFIED BY USER`** |
| **S06-DEFECT-002** | Algorithm Explorer | Prim's MST / Lloyd's K-Means on Two Moons / Circles (M5.2) | **P1 — Critical** | Selecting `Two Moons` or `Concentric Circles` crashed the view with `TypeError: generate_circles() got an unexpected keyword argument 'radius'` or `TypeError: generate_moons() got an unexpected keyword argument 'radius'`. | In Algorithm Explorer, select `Dense Prim's MST` or `Lloyd's K-Means`, then choose `Concentric Circles` or `Two Moons`. Reproduced by project owner in Brave browser on Oct 15, 2026. | **`FIX VERIFIED BY USER`** |

### Defect S06-DEFECT-001 Technical Remediation Details
- **Defect ID:** S06-DEFECT-001
- **Module:** Clustering Playground
- **Issue:** Reset Defaults raised `StreamlitWidgetAlreadyInstantiatedError`
- **Root Cause:** In `python_app/app.py`, the `Reset Defaults` button action was evaluated procedurally in the render body *after* the `pg_dataset_family` selectbox and `pg_*` sliders were already instantiated in the DOM. In Streamlit, modifying a widget-owned key in `st.session_state` after the widget has already been instantiated in the current script run raises a `StreamlitWidgetAlreadyInstantiatedError`.
- **Remediation:** Safe pre-render callback
  1. Extracted all reset operations into a safe pre-render callback: `_on_reset_playground_defaults()`.
  2. Attached the callback to the button using `st.button("🔄 Reset Defaults", on_click=_on_reset_playground_defaults, key="pg_btn_reset")`.
  3. Streamlit executes the `on_click` callback at the start of the next rerun *before* any widgets are instantiated, allowing clean, legal mutation of `pg_dataset_family`, `pg_n_samples`, `pg_seed`, `pg_noise`, `pg_outliers`, `pg_blobs_k`, `pg_blobs_std`, `pg_blobs_radius`, `pg_circles_factor`, `pg_mst_retained`, and `pg_mst_cuts`.
  4. Automatically regenerates the baseline Gaussian Blobs dataset ($N=300, k=3$) and updates `executed_config`, ensuring current controls match executed parameters and no stale warning banner is falsely triggered.
- **Automated Verification:** Reset regression suite passed
  - Added 4 automated regression tests in `python_app/tests/test_streamlit_dashboard.py` (Tests A, B, C, D) covering pre-generation reset, post-generation reset with stale reconciliation, repeated resets across views, and related Explorer/Config reset safety. All 4 tests pass consistently.
- **Manual Verification:** Project owner confirmed Reset Defaults works in local Brave browser on October 15, 2026 ("yes reset work").
- **Defect Status:** `FIX VERIFIED BY USER`

### Defect S06-DEFECT-002 Technical Remediation Details
- **Defect ID:** S06-DEFECT-002
- **Module:** Algorithm Explorer
- **Severity:** P1 — Critical (Blocks core Explorer testing)
- **Environment:** Local Streamlit app, Brave browser, Windows, October 15, 2026
- **Observed Failures:**
  - Concentric Circles `generate_circles()` unexpected keyword `'radius'`
  - Two Moons `generate_moons()` unexpected keyword `'radius'`
- **Root Cause:**
  1. In `python_app/app.py` (`render_view_explorer`), dataset generation unconditionally passed `radius=3.5`, `cluster_std=0.4`, and `n_clusters=k_val` to `generate_synthetic_dataset(...)` regardless of the selected topology.
  2. In `python_app/clustering_lab/data/synthetic.py` (`generate_synthetic_dataset`), the dispatcher whitelist for `moons` and `circles` erroneously included `"radius"` in `moons_valid` and `circles_valid`.
  3. Consequently, `generate_synthetic_dataset` forwarded `radius` to `generate_moons()` and `generate_circles()`, neither of which accepts a `radius` argument (Two Moons has fixed crescent geometry of radius 1.0; Concentric Circles takes `factor` for inner ring ratio).
- **Remediation:**
  1. In `python_app/clustering_lab/data/synthetic.py`, restricted `generate_synthetic_dataset` kwargs filtering strictly to parameters supported by each generator:
     - `blobs`: `blobs_valid = {"n_clusters", "cluster_std", "radius"}`
     - `moons`: takes no extra geometry kwargs (`{}`)
     - `circles`: `circles_valid = {"factor"}`
  2. In `python_app/app.py` (`render_view_explorer`), structured topology-specific `exp_kwargs` so Explorer only provides applicable geometric parameters (`radius`, `cluster_std`, `n_clusters` for blobs; `factor` for circles; none for moons).
- **Automated Verification:**
  - `python_app/tests/test_data.py`: Added `test_direct_generator_dispatch_all_topologies_and_kwargs_filtering` (Test A) and `test_dataset_parameter_boundaries_and_rejection` (Test C).
  - `python_app/tests/test_algorithm_explorer.py`: Added `test_explorer_all_topologies_kmeans_and_mst` (Test B) and `test_explorer_topology_switching_and_boundaries` (Test C).
  - `python_app/tests/test_streamlit_dashboard.py`: Added `test_playground_and_explorer_cross_generation_regression` (Test D).
- **Manual Verification:** Project owner tested and confirmed fix in Brave browser on October 15, 2026 ("yes M5 working"). Two Moons and Concentric Circles generated cleanly without `TypeError`.
- **Defect Status:** `FIX VERIFIED BY USER`

---

## 8. Final User Sign-Off Block

*(Official sign-off recorded following completion and approval of Sessions A, B, and C.)*

- [x] **Session A Completed:** Overview and Playground verified (M1, M2, M2-R1, M3).
- [x] **Session B Completed:** Benchmarks, Explorer, and Robustness verified (M4, M5, M6).
- [x] **Session C Completed:** CSV Import, Configuration, and Supplementary gates verified (M7, M8, S1–S8).
- [x] **Defect S06-DEFECT-001 Verified:** Reset Defaults operates cleanly in live browser without errors (Verified by project owner in Brave browser on October 15, 2026; "yes reset work").
- [x] **Defect S06-DEFECT-002 Verified:** Algorithm Explorer generates Two Moons and Concentric Circles datasets cleanly without `TypeError` (Verified by project owner in Brave browser on October 15, 2026; "yes M5 working").
- [x] **Scientific Integrity Confirmed:** Dual algorithm execution, topological inductive biases, and metric bounds verified on live browser.
- [x] **Privacy Compliance Confirmed:** Student registration identifiers and allocation identifiers verified completely absent across UI and exports.

| Role | Name | Date | Signature / Decision |
|---|---|---|---|
| **Project Author (Project Owner)** | Himanshu Gupta | October 15, 2026 | `[x] ACCEPTED  [ ] REJECTED` (Documented project-owner acceptance via conversational approval; formal digital record) |
| **Project Author (Coauthor)** | Parth Yadav | Approval not recorded | `[ ] ACCEPTED  [ ] REJECTED` (Coauthor approval not recorded in this milestone) |
| **Academic Instructor** | Mr. Aman Kumar | Approval/Evaluation not recorded | `[ ] ACCEPTED  [ ] REJECTED` (Course instructor evaluation/approval not recorded in this milestone) |

### Certification & Provenance Notes
1. **Project Owner Acceptance:** Project owner Himanshu Gupta formally approved and accepted Stage 06 on October 15, 2026 (`ACCEPTED`), confirming that all primary modules (M1–M8), remediated defects (S06-DEFECT-001, S06-DEFECT-002), and supplementary quality gates (S1–S8) operate reliably in local browser testing (Brave on Windows 11).
2. **Coauthor Status:** Parth Yadav — Approval not recorded in this milestone.
3. **Course Instructor Status:** Mr. Aman Kumar — Approval or evaluation not recorded in this milestone.
4. **Cloud Deployment Certification:** Not performed. (Testing was executed strictly against the local runtime `http://localhost:8501`; remote Streamlit Community Cloud verification is reserved for Stage 07 upon separate authorization).
5. **Stage 07 Authorization:** Not granted. (Stage 07 remains strictly quarantined and not started until explicit authorization is provided by the project owner).
