# Academic Report Asset Manifest & Documentation Inventory
**Project**: MST vs K-Means Robustness Analysis  
**Course**: Pattern Matching Lab (`BCS-DS-777`)  
**Institution**: Manav Rachna International Institute of Research and Studies (MRIIRS)  
**Lead Student**: Himanshu Gupta (Allocation No. 19)  
**Project Partner**: Parth Yadav  
**Document Generation Date**: October 2026  
**Status**: Fully Verified and Validated

---

## 1. Scope and Purpose
This document provides a complete, auditable catalog of all documentation artifacts, embedded figures, empirical data tables, and reproducibility metadata supporting the **Final Academic Project Report** (`FINAL_PROJECT_REPORT.md`). Every referenced asset is inventoried with its exact file path, file size in bytes, format specification, and verification status.

---

## 2. Core Academic Report Documents

| Relative File Path | File Size (Bytes) | Format & Encoding | Description | Verification Status |
| :--- | :--- | :--- | :--- | :--- |
| `docs/report/FINAL_PROJECT_REPORT.md` | $82,356$ B | Markdown (`UTF-8`) | Primary undergraduate final project report (~18–25 pages equivalent in A4 print layout), containing Front Matter, Chapters 1–10, IEEE References, and Appendices A–D. | **Verified** |
| `docs/report/SCIENTIFIC_VALIDATION_NOTES.md` | $12,817$ B | Markdown (`UTF-8`) | Methodological audit resolving artifact counts, speedup ratio calculations (means vs. medians), ARI degradation definitions, empirical bounds, limitations, and complexity distinctions. | **Verified** |
| `docs/report/REPORT_ASSET_MANIFEST.md` | $8,520$ B | Markdown (`UTF-8`) | This asset manifest and inventory linking all report components, embedded figures, tables, and PDF instructions. | **Verified** |
| `docs/report/report_printable.html` | $99,474$ B | HTML5 / CSS3 | Self-contained, publication-styled printable HTML presentation of the final report configured for A4 portrait printing. | **Verified** |

---

## 3. Embedded Scientific Visualizations (Figures)

The Final Academic Project Report references precisely **7 scientific figures** located in `results/figures/`. All figures were generated directly from HTML5 Canvas elements rendered by the browser application engine:

| Figure Number | Relative File Path | File Size (Bytes) | Dimensions / Format | Caption / Description in Report | Verification Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Figure 8.1** | `results/figures/blobs_comparison.png` | $68,480$ | 2D Scatter / PNG | Qualitative Clustering Comparison on Clean Gaussian Blobs ($K=3, N=300$). Ground truth vs. K-Means vs. MST. | **Verified** (`0x89504E47`) |
| **Figure 8.2** | `results/figures/moons_comparison.png` | $121,190$ | 2D Scatter / PNG | Qualitative Clustering Comparison on Clean Two Moons ($K=2, N=300$). Demonstrates MST manifold tracing vs. K-Means Voronoi cut. | **Verified** (`0x89504E47`) |
| **Figure 8.3** | `results/figures/circles_comparison.png` | $134,591$ | 2D Scatter / PNG | Qualitative Clustering Comparison on Clean Concentric Circles ($K=2, N=300$). Demonstrates MST ring separation vs. K-Means bisect. | **Verified** (`0x89504E47`) |
| **Figure 8.4** | `results/figures/ari_vs_noise.png` | $34,794$ | Multi-Series Line / PNG | Empirical Inlier ARI vs. Additive Gaussian Noise ($\sigma \in [0.00, 0.20]$). Compares noise degradation across all three dataset geometries. | **Verified** (`0x89504E47`) |
| **Figure 8.5** | `results/figures/ari_vs_outliers.png` | $28,749$ | Multi-Series Line / PNG | Empirical Inlier ARI vs. Ambient Outlier Contamination ($\eta \in [0\%, 20\%]$). Visualizes the catastrophic collapse of MST under outlier bridging. | **Verified** (`0x89504E47`) |
| **Figure 8.6** | `results/figures/ari_degradation.png` | $22,305$ | Clustered Bar / PNG | Baseline ARI Performance Degradation ($\Delta\text{ARI}$) Across Evaluated Perturbations. Visualizes non-negative performance penalties. | **Verified** (`0x89504E47`) |
| **Figure 8.7** | `results/figures/runtime_scaling.png` | $21,500$ | Multi-Series Curve / PNG | Empirical Wall-Clock Runtime Scaling Across Sample Sizes $N \in [100, 600]$. Visualizes quadratic $O(N^2)$ Prim growth vs. linear K-Means line. | **Verified** (`0x89504E47`) |

---

## 4. Underlying Empirical Data Tables and Sources

All numerical values presented in Chapters 8 and 9 of the Final Project Report originate directly from these empirical records:

| Table Number in Report | Primary Source File | Records Utilized | Key Variables Extracted | Verification Status |
| :--- | :--- | :--- | :--- | :--- |
| **Table 8.1** (Clean Baselines) | `results/summaries/robustness_summary.csv` | Rows 2–3, 18–19, 34–35 | Baseline Inlier ARI ($\mu \pm s$), Geometry | **Verified** (Matches CSV bit-for-bit) |
| **Table 8.2** (Blobs Noise) | `results/summaries/robustness_summary.csv` | Rows 2–9 | Inlier ARI, Degradation, Runtime across $\sigma \in [0.00, 0.20]$ | **Verified** (Matches CSV bit-for-bit) |
| **Table 8.3** (Moons Noise) | `results/summaries/robustness_summary.csv` | Rows 18–25 | Inlier ARI, Degradation, Runtime across $\sigma \in [0.00, 0.20]$ | **Verified** (Matches CSV bit-for-bit) |
| **Table 8.4** (Circles Noise) | `results/summaries/robustness_summary.csv` | Rows 34–41 | Inlier ARI, Degradation, Runtime across $\sigma \in [0.00, 0.20]$ | **Verified** (Matches CSV bit-for-bit) |
| **Table 8.5** (Blobs Outliers) | `results/summaries/robustness_summary.csv` | Rows 10–17 | Inlier ARI, Degradation, Runtime across $\eta \in [0\%, 20\%]$ | **Verified** (Matches CSV bit-for-bit) |
| **Table 8.6** (Moons Outliers) | `results/summaries/robustness_summary.csv` | Rows 26–33 | Inlier ARI, Degradation, Runtime across $\eta \in [0\%, 20\%]$ | **Verified** (Matches CSV bit-for-bit) |
| **Table 8.7** (Circles Outliers) | `results/summaries/robustness_summary.csv` | Rows 42–49 | Inlier ARI, Degradation, Runtime across $\eta \in [0\%, 20\%]$ | **Verified** (Matches CSV bit-for-bit) |
| **Table 8.8** (Benchmark Scaling) | `results/summaries/benchmark_summary.csv` & `results/raw/benchmark_trials.csv` | All 8 summary rows & 40 raw trials | Mean, Median, SD, Ratio of Means, Ratio of Medians across $N \in [100, 600]$ | **Verified** (Independently audited) |

---

## 5. Machine-Readable Configuration & Telemetry Files

| Relative File Path | File Size (Bytes) | Format | Contents & Purpose | Verification Status |
| :--- | :--- | :--- | :--- | :--- |
| `results/reproducibility/experiment_config.json` | $2,708$ | JSON (`UTF-8`) | Full experimental protocol parameters: seeds $\{11, 22, 33\}$, sample count $300$, noise levels, outlier levels, Lloyd $\epsilon = 10^{-5}$, $I_{\max} = 100$. | **Verified** |
| `results/reproducibility/environment_information.json` | $769$ | JSON (`UTF-8`) | Execution environment telemetry: V8 engine, Windows x64, 16 logical cores, high-resolution timer specs. | **Verified** |

---

## 6. PDF Generation & Viewing Instructions

To compile or export the Final Academic Project Report into a clean, printable PDF document:

### Method 1: Automated Headless Chromium PDF Compilation
If Google Chrome or Microsoft Edge is available on the host system:
1. Open a PowerShell terminal in the repository root.
2. Render the formatted HTML presentation of the report to PDF using headless Chrome:
   ```powershell
   & "C:\Program Files\Google\Chrome\Application\chrome.exe" --headless --disable-gpu --print-to-pdf="docs\report\FINAL_PROJECT_REPORT.pdf" --no-pdf-header-footer "docs\report\report_printable.html"
   ```

### Method 2: Browser Print-to-PDF (Manual High-Quality Option)
1. Open the formatted HTML report file `docs/report/report_printable.html` in Google Chrome or Microsoft Edge.
2. Press **Ctrl + P** (Print).
3. Set **Destination** to `Save as PDF`.
4. Under **Settings**:
   * **Paper size**: A4
   * **Margins**: Default (or 15mm)
   * **Options**: Check **Background graphics** (to ensure styled code blocks, badges, and table backgrounds render crisply).
   * **Headers and footers**: Uncheck (page breaks and numbers are handled cleanly by CSS).
5. Click **Save** and save to `docs\report\FINAL_PROJECT_REPORT.pdf`.

### Method 3: VS Code / Markdown PDF Extension
1. Open `docs/report/FINAL_PROJECT_REPORT.md` in Visual Studio Code.
2. If the `Markdown PDF` or `Markdown Preview Enhanced` extension is installed, right-click the editor window and select **Markdown PDF: Export (pdf)**.
