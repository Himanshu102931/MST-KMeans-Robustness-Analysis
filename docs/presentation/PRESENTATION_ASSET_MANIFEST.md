# Presentation Asset Manifest & Inventory
**Project**: MST vs K-Means Robustness Analysis  
**Course**: Pattern Matching Lab (`BCS-DS-777`)  
**Institution**: Manav Rachna International Institute of Research and Studies (MRIIRS)  
**Lead Student**: Himanshu Gupta (Allocation No. 19)  
**Project Partner**: Parth Yadav  
**Phase**: 6C Presentation & Viva Defense  

---

## 1. Presentation Documents & Source Artifacts

| Relative File Path | File Size / Format | Description & Purpose |
| :--- | :--- | :--- |
| `docs/presentation/PRESENTATION_CONTENT.md` | ~$15,000` B` (Markdown) | Comprehensive 15-slide text, mathematics, layout design, and table specifications. |
| `docs/presentation/PRESENTATION_SPEAKER_NOTES.md` | ~$13,000` B` (Markdown) | Full spoken dialogue script for Himanshu Gupta and Parth Yadav with 10–12 minute timing markers. |
| `docs/presentation/PRESENTATION_ASSET_MANIFEST.md` | ~$6,500` B` (Markdown) | This asset manifest and inventory linking all presentation elements. |
| `docs/presentation/presentation.html` | Interactive HTML5 / CSS3 | Standalone 16:9 widescreen presentation deck with keyboard controls (←/→), fullscreen toggle, and high-DPI figure embeds. |
| `docs/presentation/MST_vs_KMeans_Final_Presentation.pptx` | Microsoft PowerPoint PPTX | Native 16:9 widescreen PowerPoint deck with embedded images and slide notes. |
| `docs/presentation/generate_pptx.ps1` | PowerShell COM Script | Automated script generating the native PowerPoint deck using Microsoft Office automation. |

---

## 2. Embedded Scientific Visualizations in Slides

| Slide Number | Referenced Figure File | Resolution / Type | Visual Content & Role |
| :--- | :--- | :--- | :--- |
| **Slide 8 & 10** | `results/figures/blobs_comparison.png` | 2D Scatter (PNG) | Ground truth vs. K-Means vs. MST on clean Gaussian Blobs ($K=3, \text{ARI}=1.0000$). |
| **Slide 8 & 10** | `results/figures/moons_comparison.png` | 2D Scatter (PNG) | Contrast on clean Two Moons ($K=2$): MST manifold tracing vs. K-Means Voronoi cut. |
| **Slide 8 & 10** | `results/figures/circles_comparison.png` | 2D Scatter (PNG) | Contrast on Concentric Circles ($K=2$): MST ring cut vs. K-Means zero-concordance split. |
| **Slide 11** | `results/figures/ari_vs_noise.png` | Multi-Series Line (PNG) | Inlier ARI vs. Gaussian Noise ($\sigma \in [0.00, 0.20]$), showing the breakdown of MST on Moons and Circles. |
| **Slide 12** | `results/figures/ari_vs_outliers.png` | Multi-Series Line (PNG) | Inlier ARI vs. Ambient Outlier Contamination ($\eta \in [0\%, 20\%]$), showing the 5% outlier collapse of MST. |
| **Slide 12** | `results/figures/ari_degradation.png` | Clustered Bar (PNG) | Baseline Performance Degradation ($\Delta\text{ARI}$) across all regimes, illustrating outlier sensitivity. |
| **Slide 13** | `results/figures/runtime_scaling.png` | Scaling Curves (PNG) | Wall-clock execution time (ms) vs. Sample Size $N \in [100, 600]$, highlighting $O(N^2)$ vs. $O(N)$. |

---

## 3. Underlying Empirical Data Records for Presentation Tables

| Slide Number | Table Title | Data Source File | Primary Values Cited |
| :--- | :--- | :--- | :--- |
| **Slide 10** | Clean Baseline Geometry Results | `results/summaries/robustness_summary.csv` | Blobs: $1.0000$ vs $1.0000$; Moons: $1.0000$ vs $0.1941$; Circles: $1.0000$ vs $-0.0019$. |
| **Slide 11** | Noise Sensitivity Milestones | `results/summaries/robustness_summary.csv` | Blobs: Stable $1.0000$; Circles: Stable to $\sigma=0.10$, collapses to $0.0935$ at $\sigma=0.20$; Moons: Collapses to $0.0000$ at $\sigma=0.20$. |
| **Slide 12** | Outlier Robustness Milestones | `results/summaries/robustness_summary.csv` | Moons: Drops from $1.0000$ to $0.0000$ at $\eta=5\%$; Blobs: KM remains $1.0000$ up to $20\%$, MST drops to $0.3799$. |
| **Slide 13** | Micro-Benchmark Scaling Statistics | `results/summaries/benchmark_summary.csv` & `results/raw/benchmark_trials.csv` | $N=100$: KM $0.10$ ms, MST $0.14$ ms; $N=600$: KM $0.14$ ms, MST $1.70$ ms; Ratio of Means: $12.14\times$; Ratio of Medians: $17.00\times$. |
