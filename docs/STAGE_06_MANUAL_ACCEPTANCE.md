# STAGE 06: USER-LED MANUAL ACCEPTANCE TESTING RECORD
## Minimum Spanning Tree (MST) vs. Lloyd's K-Means Robustness Analysis

- **Document Version:** 1.2.0 (User-Verified Fix for S06-DEFECT-001)
- **Baseline Git Commit:** `74dbc8a` + Local Fix `S06-DEFECT-001`
- **Active Branch:** `feature/python-streamlit-migration`
- **Application Framework:** Streamlit 1.42.0 on Python 3.12 (NumPy / SciPy / Plotly / Pandas)
- **Test Date:** October 15, 2026 (Defect S06-DEFECT-001 Verified by User; Manual Protocols In Progress)
- **Lead Project Authors:** Himanshu Gupta & Parth Yadav (*Equal Attribution*)
- **Academic Course:** Pattern Matching Lab (BCS-DS-777), 7th Semester, MRIIRS

---

## 1. Objectives & Testing Principles

This document provides the authoritative, non-technical manual acceptance testing procedure for the project owner and academic examiners. It enables systematic, step-by-step verification of all eight application modules in a real web browser without requiring code modifications.

### Core Testing Principles
1. **Mathematical Grounding over Fixed Arbitrary Values:** Clustering outputs depend on stochastic initializations (Lloyd's K-Means) and seed permutations. Verification focuses on mathematical invariants (e.g., $ARI \in [-1.0, 1.0]$, $O(N^2)$ vs. $O(N)$ runtime scaling, single-linkage chaining failure on uniform noise) rather than fabricated fixed decimal numbers.
2. **Honest Initial Status:** All test items are initialized to `NOT TESTED` (except remediated defects awaiting user retest, marked `AWAITING USER RETEST`). No results, logs, or screenshots are pre-filled or assumed.
3. **Reproducible Preconditions:** Every protocol lists the exact starting view, widget inputs, and fixtures required.
4. **Strict Privacy Compliance:** Verifies that no institutional student roll numbers appear anywhere in user-facing text, academic cards, or exported files.

---

## 2. Environment Setup & Startup Instructions

### 2.1 Local Application Startup
To test local commit `74dbc8a` and the S06-DEFECT-001 remediation before pushing to GitHub or deploying to Streamlit Community Cloud:

1. Open PowerShell in the project root directory (`d:\7th Sem\PM\Mini project\MST-KMeans-Robustness-Analysis`).
2. Set the Python path and launch the Streamlit server using `uv`:
   ```powershell
   $env:PYTHONPATH="python_app"
   uv run --python 3.12 --with-requirements python_app/requirements-dev.txt streamlit run python_app/app.py
   ```
3. The terminal will output the local network URL (typically `http://localhost:8501`).
4. Open Google Chrome, Mozilla Firefox, Brave, or Microsoft Edge and navigate to:
   ```text
   http://localhost:8501
   ```
5. **To stop the local server:** Return to the PowerShell terminal and press `Ctrl + C`.

> [!NOTE]
> **Streamlit Community Cloud Notice:**
> The public cloud instance at `https://mst-kmeans-robustness-analysis.streamlit.app/` reflects the remote GitHub branch. Commit `74dbc8a` and local defect fixes are currently local. Local manual acceptance testing must be conducted on `http://localhost:8501` prior to the Stage 07 release deployment.

### 2.2 Test Fixtures Directory
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

Testing is divided into three focused sessions to prevent fatigue and ensure thorough coverage:

```
+----------------------------------------------------------------------------------------------------+
| Session A: Foundational Interface & Core Playground (Protocols M1, M2, M2-R1, M3)                  |
| Estimated Time: 15–20 minutes                                                                      |
| Focus: Academic branding, visual design system, dual algorithm execution, and reset/stale handling |
+----------------------------------------------------------------------------------------------------+
                                                  │
                                                  ▼
+----------------------------------------------------------------------------------------------------+
| Session B: Advanced Compute Engines & Educational Diagnostics (Protocols M4, M5, M6)                |
| Estimated Time: 25–30 minutes                                                                      |
| Focus: Performance benchmarks, Prim step-by-step state trace, and paired robustness sweeps        |
+----------------------------------------------------------------------------------------------------+
                                                  │
                                                  ▼
+----------------------------------------------------------------------------------------------------+
| Session C: External Data, Configuration & Supplementary Quality Gates (Protocols M7, M8, S1–S8)     |
| Estimated Time: 25–35 minutes                                                                      |
| Focus: CSV import pipeline, JSON round-trips, privacy audit, downloads, and responsive layout      |
+----------------------------------------------------------------------------------------------------+
```

---

## 4. Evaluation Criteria & Status Definitions

- **`PASS`**: The UI behavior, visual appearance, and mathematical invariants match or exceed specified expectations.
- **`FAIL`**: An unhandled exception, visual breakage, calculation error, or broken workflow occurred.
- **`BLOCKED`**: The test could not be executed due to an issue in an earlier step.
- **`FIX VERIFIED BY USER`**: Defect remediation has been directly verified and confirmed functional by the project owner in the live browser environment.
- **`PENDING USER CONFIRMATION`**: Detailed check awaiting explicit manual confirmation during formal acceptance testing.
- **`NOT TESTED`**: Initial unexecuted state prior to user execution.

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
| M1.1 | Observe the top left sidebar and header. | Sidebar displays "🔬 MST vs K-Means Lab", "Pattern Matching Lab (BCS-DS-777)", and "Himanshu Gupta & Parth Yadav (Equal Attribution)". | | `NOT TESTED` | |
| M1.2 | Expand the "Academic Course Details" expander in the sidebar. | Displays Institution (MRIIRS), School of Engineering & Technology, Course Instructor (**Mr. Aman Kumar**), and Course Code. | | `NOT TESTED` | |
| M1.3 | Check for institutional roll numbers across the entire sidebar and main page. | **Zero** student roll numbers (`1/23/SET/...`) or allocation tags (`Allocation #19`) appear anywhere. | | `NOT TESTED` | |
| M1.4 | Inspect the system runtime badge in the sidebar. | Displays `Python 3.12 (Streamlit 1.42.0)` with a green indicator dot. | | `NOT TESTED` | |
| M1.5 | Observe main page title and overview comparison cards. | Header displays "MST vs K-Means Robustness Analysis"; comparison cards contrast Lloyd's K-Means (Centroidal) with Prim's MST (Graph-Theoretic). | | `NOT TESTED` | |

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
| M2.1 | Expand "⚙️ Dataset & Algorithm Configuration". | Configuration panel opens displaying Dataset Topology, Sample Count, Seed, and Perturbation sliders. | | `NOT TESTED` | |
| M2.2 | Set **Dataset Topology** = `Two Moons`. | Cluster count is automatically set to fixed $k=2$; geometry caption displays radius 1.0. | | `NOT TESTED` | |
| M2.3 | Set **Inlier Sample Count** = `300`. | Slider updates smoothly; caption reports Inliers: 300. | | `NOT TESTED` | |
| M2.4 | Set **Gaussian Noise (σ)** = `0.05` and **Outlier Contamination Rate** = `0.05`. | Caption updates: Inliers: **300**, Injected Outliers: **15**, Total N: **315**. Total N remains $\le 600$. | | `NOT TESTED` | |
| M2.5 | Click **`🚀 Generate & Run Clustering`**. | Spinner runs; green success alert appears: "Successfully clustered 315 observations into k=2 components." | | `NOT TESTED` | |
| M2.6 | Click tab **"Lloyd's K-Means Result"**. | Plotly figure displays partition governed by linear Voronoi cells; on non-convex crescents, linear bisectors typically split curvilinear clusters. Centroids marked by golden stars. Inlier ARI evaluates within mathematically bounded $[-1.0, 1.0]$. | | `NOT TESTED` | |
| M2.7 | Click tab **"Prim's MST Result"**. | Plotly figure displays connected components following density-connected paths along the crescent manifolds when inter-manifold separation is clear; illustrates graph-theoretic single-linkage inductive bias. Both ARIs evaluate within valid $[-1.0, 1.0]$ bounds. Retained edges in teal/cyan. | | `NOT TESTED` | |
| M2.8 | Review the comparative metrics table below the plots. | Reports Inlier ARI, Full-Data ARI, Silhouette Score, and Wall-Clock Runtime for both algorithms side-by-side. | | `NOT TESTED` | |

---

#### Protocol M2-R1: Playground Reset Defaults & Widget State Lifecycle (S06-DEFECT-001 Verification)
- **Target Module:** `Clustering Playground`
- **Goal:** Verify that clicking "Reset Defaults" safely resets all configuration parameters to baseline defaults without widget instantiation errors, and that re-clustering executes cleanly.
- **Preconditions:** Active Clustering Playground with modified non-default parameters (e.g. from Protocol M2).

| Step | UI Action | Expected Result | Actual Result | Status | Screenshot / Notes |
|:---:|---|---|---|:---:|---|
| M2-R1.1 | In Clustering Playground, confirm non-default parameters are set (e.g., Topology = Two Moons, $N=160$, Noise $= 0.08$). | Non-default settings are active in the controls expander. | | `PENDING USER CONFIRMATION` | |
| M2-R1.2 | Click **`🔄 Reset Defaults`** button. | Application executes pre-render reset callback; page refreshes cleanly without crashing. | Callback executes cleanly; no crash or multi-rerun loop occurs. | `PASS` | Confirmed by project owner in Brave browser on Oct 15, 2026 ("yes reset work"). |
| M2-R1.3 | Check the application screen for errors. | **Zero** red exception panels or `StreamlitWidgetAlreadyInstantiatedError` messages appear. | No exception banners rendered. | `PASS` | Defect S06-DEFECT-001 eliminated; verified by project owner on Oct 15, 2026. |
| M2-R1.4 | Inspect all widget controls in the expander. | Controls return to baseline: Topology = `Gaussian Blobs`, Inlier Count = `300`, Seed = `42`, Noise = `0.0`, Outliers = `0.0`, $k = 3$, Dispersion = `0.4`, Radius = `3.5`. | | `PENDING USER CONFIRMATION` | |
| M2-R1.5 | Check notification banner below action buttons. | Green feedback banner displays: `Configuration reset to Gaussian Blobs baseline.` | | `PENDING USER CONFIRMATION` | |
| M2-R1.6 | Inspect displayed clustering visualizations and metrics. | Rendered results match the baseline Gaussian Blobs ($N=300, k=3$); no stale warning banner is displayed because controls equal executed parameters. | | `PENDING USER CONFIRMATION` | |
| M2-R1.7 | Click **`🚀 Generate & Run Clustering`** with the reset parameters. | Dual clustering executes smoothly on Gaussian Blobs without errors. | | `NOT TESTED` | Pending user execution during comprehensive testing. |
| M2-R1.8 | Click tabs and verify charts and metrics. | Both algorithms achieve strong clustering recovery on well-separated globular blobs ($ARI > 0.80$ typical); metric tables populate with valid finite metrics ($ARI \in [-1.0, 1.0]$). | | `NOT TESTED` | Pending user execution during comprehensive testing. |

---

#### Protocol M3: Playground Stale-State Persistence (ISSUE-06 Remediation)
- **Target Module:** `Clustering Playground`
- **Goal:** Verify that modifying sliders does NOT collapse existing plots, but displays an amber stale banner until recomputation.
- **Preconditions:** Active execution displayed from Protocol M2 or M2-R1.

| Step | UI Action | Expected Result | Actual Result | Status | Screenshot / Notes |
|:---:|---|---|---|:---:|---|
| M3.1 | Without clicking any action button, adjust **Gaussian Noise (σ)** from `0.00` to `0.10`. | **Visualizations do not disappear or collapse.** Previous clustering plots remain fully rendered. | | `NOT TESTED` | |
| M3.2 | Check the area directly below the configuration container. | A prominent amber warning banner appears: `⚠️ Parameters Modified — Showing Previous Clustering Results`. | | `NOT TESTED` | |
| M3.3 | Verify presence of the recompute button. | `⚡ Recompute / Update Visualizations` button is visible next to an explanatory caption. | | `NOT TESTED` | |
| M3.4 | Click **`⚡ Recompute / Update Visualizations`**. | Application recalculates with noise $\sigma=0.10$; plots refresh with updated coordinates; amber stale banner dismisses. | | `NOT TESTED` | |

---

### SESSION B: Advanced Compute Engines & Educational Diagnostics

#### Protocol M4: Performance Benchmarks & Asymptotic Complexity
- **Target Module:** `Performance Benchmarks`
- **Goal:** Verify empirical wall-clock timing measurement, sample standard deviation ($ddof=1$), and $O(N)$ vs $O(N^2)$ scaling.
- **Preconditions:** Navigate to `Performance Benchmarks` via sidebar.

> [!NOTE]
> **Implementation Note on Controls:**
> Sample sizes multiselect defaults to `[100, 200, 400, 600]`. Deselect `600` to benchmark $\{100, 200, 400\}$. Button label is **`🚀 Run Benchmarks`**.

| Step | UI Action | Expected Result | Actual Result | Status | Screenshot / Notes |
|:---:|---|---|---|:---:|---|
| M4.1 | In Sample Sizes multiselect, select exactly `100`, `200`, `400`. | Preflight estimate reports: `3 sizes × 5 repetitions = 15 measured trials (36 total algorithm executions including warm-up)`. | | `NOT TESTED` | |
| M4.2 | Ensure **Measured Repetitions per Size** = `5` and **Include 1 Warm-up Stage** = Checked. | Warm-up checkbox remains enabled; preflight indicator shows green safe badge. | | `NOT TESTED` | |
| M4.3 | Click **`🚀 Run Benchmarks`**. | Progress bar increments through trials with status text indicating current size, repetition, and algorithm. | | `NOT TESTED` | |
| M4.4 | Inspect the metric cards at the top of results. | Displays Max Scale (N=400), K-Means Mean, Prim MST Mean, and Ratio of Means (MST / KM). | | `NOT TESTED` | |
| M4.5 | Click tab **"📈 Runtime Scaling Curves"**. | Plotly chart displays empirical runtime curves across measured sample sizes. Empirical trends illustrate contrasting computational growth profiles (near-linear centroid iterations vs. dense quadratic edge evaluations). | | `NOT TESTED` | |
| M4.6 | Click tab **"📊 Summary Statistics Table"**. | Table lists sample size, repetitions, mean, median, and Bessel-corrected sample standard deviation ($ddof=1$). Measured runtimes capture system timing variability across repetitions without assuming strictly monotonic scaling on individual OS runs. | | `NOT TESTED` | |
| M4.7 | Click tab **"💾 Research Data Export"** and click **`📄 Raw Trials CSV`**. | File `benchmark_trials.csv` downloads with columns: `sample_size, repetition, algorithm, runtime_ms, k, seed, timestamp`. | | `NOT TESTED` | |

---

#### Protocol M5: Algorithm Explorer Step-by-Step Educational Visualizer (ISSUE-05 Remediation)
- **Target Module:** `Algorithm Explorer`
- **Goal:** Verify Prim's MST step trace synchronization between navigation buttons and slider with zero double reruns.
- **Preconditions:** Navigate to `Algorithm Explorer` via sidebar.

> [!NOTE]
> **Implementation Note on Controls:**
> Algorithm radio option is labeled **`Dense Prim's MST`**.

| Step | UI Action | Expected Result | Actual Result | Status | Screenshot / Notes |
|:---:|---|---|---|:---:|---|
| M5.1 | Select radio **`Dense Prim's MST`**. | Educational controls expand. Topology defaults to Two Moons / Circles. | | `NOT TESTED` | |
| M5.2 | Set **Dataset Topology** = `Concentric Circles`, **Observations** = `20`, **Clusters (k)** = `2`. | Trace is automatically generated for $N=20$. Total steps $= 19$ tree growth steps $+ 1$ cut step. | | `NOT TESTED` | |
| M5.3 | Click **`Next ▶`** button 5 times sequentially. | Step index advances cleanly from 0 to 5; slider updates in lockstep to 5; active candidate edge displays in orange glow. | | `NOT TESTED` | |
| M5.4 | Drag the **Step Navigation** slider directly back to Step 2. | Plot instantly updates to Step 2 state; exactly 2 edges connected; vertex highlight reflects step 2 frontier. | | `NOT TESTED` | |
| M5.5 | Click **`Next ▶`** again. | Step index advances cleanly to Step 3 without skipping, page flashing, or jumping to step 6. | | `NOT TESTED` | |
| M5.6 | Click **`Last ⏭`**. | Step advances to the final cut stage; the longest cut edge is highlighted in red dashes, separating inner and outer rings. | | `NOT TESTED` | |

---

#### Protocol M6: Robustness Analysis Sweeps & Failure Modes
- **Target Module:** `Robustness Analysis`
- **Goal:** Execute Quick preset robustness sweep (72 paired trials) and verify degradation error bands.
- **Preconditions:** Navigate to `Robustness Analysis` via sidebar.

> [!NOTE]
> **Implementation Note on Accounting:**
> Quick Mode executes across 3 families $\times$ 3 seeds $\times$ 8 points $= 72$ paired trials ($144$ sweep clustering runs $+ 36$ baseline runs $= 180$ total algorithm executions). Execution button is labeled **`🚀 Execute Robustness Analysis Engine`**.

| Step | UI Action | Expected Result | Actual Result | Status | Screenshot / Notes |
|:---:|---|---|---|:---:|---|
| M6.1 | Verify **Execution Mode Preset** = `Quick Mode (3 Seeds — Fast Demo)`. | Seeds display `[11, 22, 33]`; experiment plan confirms 72 paired comparisons. | | `NOT TESTED` | |
| M6.2 | Ensure all 3 topologies are selected: Gaussian Blobs, Two Moons, Concentric Circles. | Selected count = 3; sweep type = Both Sweeps (Noise & Outliers). | | `NOT TESTED` | |
| M6.3 | Click **`🚀 Execute Robustness Analysis Engine`**. | Progress bar displays sweep execution through all 72 trials to completion without unhandled exceptions. | | `NOT TESTED` | |
| M6.4 | Click tab **"📉 Gaussian Noise Sweep"**. | Dual-panel Plotly figure renders Inlier ARI vs $\sigma$ with shaded $\pm 1\sigma$ standard deviation error bands. | | `NOT TESTED` | |
| M6.5 | Click tab **"📉 Uniform Outlier Contamination Sweep"**. | Dual-panel Plotly figure displays Inlier ARI response across uniform outlier rates with shaded error bands. Illustrates empirical sensitivity where spurious bridging points can induce single-linkage chaining in MST, alongside centroid shifts in K-Means under diffuse contamination. | | `NOT TESTED` | |
| M6.6 | Click tab **"💾 Export Sweep Artifacts"** and download **`📄 Raw Trial Observations (CSV)`**. | CSV downloads containing all 144 sweep result rows with complete provenance metadata. | | `NOT TESTED` | |

---

### SESSION C: External Data, Configuration & Supplementary Quality Gates

#### Protocol M7: CSV Dataset Import & Tabular Pipeline
- **Target Module:** `Dataset & CSV Import`
- **Goal:** Upload a custom tabular dataset, map coordinates, and hand off to Playground.
- **Preconditions:** Navigate to `Dataset & CSV Import` via sidebar; ensure test fixture `01_valid_labeled.csv` is accessible.

> [!NOTE]
> **Implementation Note on Headerless CSVs:**
> The current UI tabular parser always expects standard CSVs with a header row (`pd.read_csv` default). If a headerless CSV (such as fixture `03_headerless.csv`) is uploaded, pandas defaults to treating the first data row as column names. Positional index selection for headerless files is currently an unsupported UI capability.

| Step | UI Action | Expected Result | Actual Result | Status | Screenshot / Notes |
|:---:|---|---|---|:---:|---|
| M7.1 | In the file uploader, upload `docs/manual_test_fixtures/01_valid_labeled.csv`. | Green success notification appears: `File parsed successfully: 01_valid_labeled.csv (12 rows, 3 columns)`. | | `NOT TESTED` | |
| M7.2 | Inspect the preview table. | First 8 rows of CSV render cleanly with numeric coordinate columns. | | `NOT TESTED` | |
| M7.3 | Set **Feature 1 (X Axis)** = `x_coord`, **Feature 2 (Y Axis)** = `y_coord`, **Ground-Truth Label** = `ground_truth_class`. | Column selectors map cleanly; target clusters $k$ defaults to 3. | | `NOT TESTED` | |
| M7.4 | Click **`🚀 Load & Run Clustering on CSV`**. | Success message displays: "Successfully processed CSV dataset: 12 points clustered." | | `NOT TESTED` | |
| M7.5 | Navigate to **Clustering Playground** via the sidebar. | Playground mounts imported data; blue source notice displays: `Currently displaying imported CSV data ('01_valid_labeled.csv')`. | | `NOT TESTED` | |
| M7.6 | Return to `Dataset & CSV Import` and upload `docs/manual_test_fixtures/05_invalid_nonnumeric.csv`. | Application displays clear error banner stating non-numeric values were detected, without crashing. | | `NOT TESTED` | |

---

#### Protocol M8: Configuration Export, Modification & Session Restoration
- **Target Module:** `Reproducibility & Configuration`
- **Goal:** Export JSON configuration, modify UI parameters, and restore exact session state from file.
- **Preconditions:** Navigate to `Reproducibility & Configuration` via sidebar.

| Step | UI Action | Expected Result | Actual Result | Status | Screenshot / Notes |
|:---:|---|---|---|:---:|---|
| M8.1 | Review the **Export Current Configuration** panel on the left. | Displays active topology, sample count, cluster count, and pretty-printed JSON schema `1.0.0`. | | `NOT TESTED` | |
| M8.2 | Click **`⬇️ Download Configuration (.json)`**. | A valid JSON file (`clustering_config_....json`) downloads to the browser download folder. | | `NOT TESTED` | |
| M8.3 | In the right panel ("Upload valid configuration JSON"), upload `docs/manual_test_fixtures/08_valid_config.json`. | Success message displays: `Configuration valid: Family circles, N=200, Seed=777`. Parsed dictionary renders in interactive JSON tree. | | `NOT TESTED` | |
| M8.4 | Click **`Apply Configuration & Regenerate`**. | Application reloads and applies config; navigates to Playground where Concentric Circles ($N=200$, seed 777) is rendered. | | `NOT TESTED` | |
| M8.5 | Upload `docs/manual_test_fixtures/07_malformed_config.json` to the uploader. | Application displays red error banner: `Invalid experiment configuration: Malformed configuration JSON`, preventing state corruption. | | `NOT TESTED` | |

---

## 6. Supplementary Manual Acceptance Gates

| ID | Focus Area | Specific Action | Acceptance Standard | Status | Notes |
|:---:|---|---|---|:---:|---|
| **S1** | **Methodology / Help View** | Open `Methodology / Help` view. | Full theoretical formulations (Lloyd updates, Prim cut condition, ARI formula) render in LaTeX; Viva defense guide is readable. | `NOT TESTED` | |
| **S2** | **Publication PNG Exports** | In Playground, click `📥 Download Ground Truth Plot (Publication PNG)`. | A valid, uncorrupted PNG image downloads containing publication-quality high-DPI rendered scatter points. | `NOT TESTED` | |
| **S3** | **Responsive Viewport** | Resize browser window to mobile width ($<768\text{px}$). | Sidebar collapses to standard mobile hamburger menu; metric cards stack vertically; Plotly charts adapt to container width. | `NOT TESTED` | |
| **S4** | **Cross-View Session Isolation** | Run clustering in Playground, navigate through all 8 views sequentially, then return to Playground. | Previously computed clustering plots and metric cards remain fully rendered; zero session state loss or recalculation delay. | `NOT TESTED` | |
| **S5** | **Browser Console Audit** | Open Browser Developer Tools (`F12` $\to$ Console). Perform several runs. | **Zero** unhandled JavaScript errors, missing asset 404s, or broken WebSocket disconnect loops. | `NOT TESTED` | |
| **S6** | **Keyboard Accessibility** | Use `Tab`, `Shift+Tab`, and `Enter` to navigate controls without mouse. | Focus indicators are visible; buttons and inputs can be triggered via keyboard. | `NOT TESTED` | |
| **S7** | **Public Privacy Audit** | Perform page text search (`Ctrl + F`) for university roll numbers across all modules. | Exactly **0** matches found across the entire application interface and exports. | `NOT TESTED` | |
| **S8** | **Plotly Visual Interactivity** | Hover over individual points and edges in Playground and Explorer. | Hover tooltips display exact $(X, Y)$ coordinates, predicted cluster ID, and ground truth label; zoom/pan controls operate smoothly without distortion. | `NOT TESTED` | |

---

## 7. Defect & Observation Log

| Log ID | Module | Protocol Step | Severity (P1–P4) | Observed Behavior | Steps to Reproduce | Resolution Status |
|:---:|---|:---:|:---:|---|---|:---:|
| **S06-DEFECT-001** | Clustering Playground | `Reset Defaults` (M2-R1.2–M2-R1.3) | **P2 — Major** | Clicking `Reset Defaults` button raised `StreamlitWidgetAlreadyInstantiatedError: st.session_state['pg_dataset_family'] cannot be modified after the widget with that key is instantiated.` | In Clustering Playground, adjust sliders or topology, then click `Reset Defaults`. Originally reproduced by project owner on Oct 15, 2026. | **`FIX VERIFIED BY USER`** |

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
- **Manual Verification:** Project owner confirms Reset Defaults works in local Brave browser on October 15, 2026 ("yes reset work").
- **Defect Status:** `FIX VERIFIED BY USER`

---

## 8. Final User Sign-Off Block

*(To be completed by the project owner / examiner upon finishing Sessions A, B, and C.)*

- [ ] **Session A Completed:** Overview and Playground verified (M1, M2, M2-R1, M3).
- [ ] **Session B Completed:** Benchmarks, Explorer, and Robustness verified (M4, M5, M6).
- [ ] **Session C Completed:** CSV Import, Configuration, and Supplementary gates verified (M7, M8, S1–S8).
- [x] **Defect S06-DEFECT-001 Verified:** Reset Defaults operates cleanly in live browser without errors (Verified by project owner in Brave browser on October 15, 2026; "yes reset work").
- [ ] **Scientific Integrity Confirmed:** Dual algorithm execution and topological biases verified on live browser.
- [ ] **Privacy Compliance Confirmed:** University roll numbers verified completely absent.

| Role | Name | Date | Signature / Decision |
|---|---|---|---|
| **Project Author** | Himanshu Gupta | __________________ | `[ ] ACCEPTED  [ ] REJECTED` |
| **Project Author** | Parth Yadav | __________________ | `[ ] ACCEPTED  [ ] REJECTED` |
| **Academic Instructor** | Mr. Aman Kumar | __________________ | `[ ] ACCEPTED  [ ] REJECTED` |
