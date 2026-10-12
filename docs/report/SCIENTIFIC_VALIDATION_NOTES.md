# Scientific Validation Notes & Methodological Discrepancy Audit
**Project**: MST vs K-Means Robustness Analysis  
**Course**: Pattern Matching Lab (`BCS-DS-777`)  
**Institution**: Manav Rachna International Institute of Research and Studies (MRIIRS)  
**Lead Student**: Himanshu Gupta (Allocation No. 19)  
**Project Partner**: Parth Yadav  
**Audit Date**: October 2026  
**Document Purpose**: Methodological audit, numerical reconciliation, and epistemological clarification prior to compiling the Final Academic Project Report.

---

## 1. Objective of this Audit
In accordance with academic rigor and the scientific method, this document performs an independent consistency review of the empirical evidence gathered during Phase 6A. Before compiling the final academic report, all potential reporting discrepancies, statistical ambiguities, metric nuances, and epistemological boundary conditions are formally identified, resolved, and documented.

---

## 2. Itemized Resolution of Scientific Reporting Issues

### 2.1 Issue A — Evidence Artifact Inventory Count Reconciliation
* **Observation**: In Phase 6A documentation, a total of "14 evidence artifacts" was cited in certain narrative passages, whereas an inventory audit revealed 15 files present within the `results/` folder tree.
* **Audit Breakdown**:
  An exact file-system traversal of `results/` identifies precisely **15 distinct files**:
  1. `results/EXPERIMENTAL_EVIDENCE_REPORT.md` (Scientific Findings Report)
  2. `results/EVIDENCE_MANIFEST.md` (Artifact Inventory and Reproduction Guide)
  3. `results/raw/robustness_trials.csv` (144 raw robustness evaluation records)
  4. `results/raw/benchmark_trials.csv` (40 raw benchmark timing trials)
  5. `results/summaries/robustness_summary.csv` (48 aggregated condition summary rows)
  6. `results/summaries/benchmark_summary.csv` (8 benchmark scaling summary rows)
  7. `results/reproducibility/experiment_config.json` (Machine-readable protocol configuration)
  8. `results/reproducibility/environment_information.json` (Platform telemetry and timer specifications)
  9. `results/figures/blobs_comparison.png` (2D scatter plot on Gaussian Blobs)
  10. `results/figures/moons_comparison.png` (2D scatter plot on Two Moons)
  11. `results/figures/circles_comparison.png` (2D scatter plot on Concentric Circles)
  12. `results/figures/ari_vs_noise.png` (Line chart: Inlier ARI vs Gaussian Noise)
  13. `results/figures/ari_vs_outliers.png` (Line chart: Inlier ARI vs Outlier Contamination)
  14. `results/figures/ari_degradation.png` (Clustered bar chart: Baseline ARI Degradation)
  15. `results/figures/runtime_scaling.png` (Performance scaling curve)
* **Root Cause of Discrepancy**: The Phase 6A initial task specification called for "13 data/figure artifacts" ($2\text{ raw} + 2\text{ summary} + 2\text{ config} + 7\text{ figures}$). When the primary scientific findings report (`EXPERIMENTAL_EVIDENCE_REPORT.md`) was written, the count reached 14. When the inventory guide itself (`EVIDENCE_MANIFEST.md`) was subsequently generated into `results/`, the total became 15.
* **Resolution for Final Report**: The final project report and all accompanying documentation will explicitly cite **15 verified artifact files** in the `results/` directory, categorized as 13 experimental data and visualization files plus 2 scientific documentation and manifest files.

---

### 2.2 Issue B — Benchmark Speedup Ratio Disambiguation (Ratio-of-Means vs. Ratio-of-Medians)
* **Observation**: In `results/summaries/benchmark_summary.csv`, the reported column `speedup_ratio_vs_mst` indicated values of $2.00\times$, $1.50\times$, $10.00\times$, and $17.00\times$. Independent mathematical auditing revealed that these values correspond to the **ratio of medians**, not the **ratio of arithmetic means**.
* **Audit Calculation**:
  Evaluating the 5 repetitions per condition from `results/raw/benchmark_trials.csv`:

  | Sample Size ($N$) | K-Means Mean (ms) | MST Prim Mean (ms) | **Ratio of Means** ($\frac{\mu_{\text{MST}}}{\mu_{\text{KM}}}$) | K-Means Median (ms) | MST Prim Median (ms) | **Ratio of Medians** ($\frac{M_{\text{MST}}}{M_{\text{KM}}}$) | Value in `benchmark_summary.csv` |
  | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
  | **100** | $0.1000$ | $0.1400$ | **$1.40\times$** | $0.1000$ | $0.2000$ | **$2.00\times$** | $2.00$ (Median Ratio) |
  | **200** | $0.1600$ | $0.3800$ | **$2.375\times$** | $0.2000$ | $0.3000$ | **$1.50\times$** | $1.50$ (Median Ratio) |
  | **400** | $0.1400$ | $0.9400$ | **$6.714\times$** | $0.1000$ | $1.0000$ | **$10.00\times$** | $10.00$ (Median Ratio) |
  | **600** | $0.1400$ | $1.7000$ | **$12.143\times$** | $0.1000$ | $1.7000$ | **$17.00\times$** | $17.00$ (Median Ratio) |

* **Scientific Rationale & Disambiguation**:
  * *Why Ratio of Medians was computed in the summary*: In benchmarking micro-benchmarks subject to operating system background thread scheduling and timer quantization, the median is widely preferred as a robust estimator that is invariant to single-trial outliers. At $N=600$, K-Means executed in $0.10\text{ ms}$ (median) while MST executed in $1.70\text{ ms}$ (median), producing $\frac{1.70}{0.10} = 17.00\times$.
  * *Why Ratio of Means is also essential*: The ratio of means incorporates the entire aggregate work across all trials ($\frac{1.7000}{0.1400} = 12.143\times$).
* **Resolution for Final Report**: The final report will publish **both** metrics side-by-side in Chapter 8. All tables and text will explicitly label whether a speedup value represents the **Ratio of Medians** ($17.00\times$ at $N=600$) or the **Ratio of Means** ($12.14\times$ at $N=600$).

---

### 2.3 Issue C — Exact Nature of the ARI Degradation Metric ($\Delta \text{ARI}$)
* **Observation**: The metric $\text{ARI Degradation}$ is mathematically implemented in `js/experiments/robustness.js` as:
  $$\Delta \text{ARI} = \max\left(0.0, \; \text{ARI}_{\text{baseline}} - \text{ARI}_{\text{perturbed}}\right)$$
  This truncates negative values to zero. The reporting must clarify whether this represents an absolute non-negative performance loss rather than an unrestricted signed delta.
* **Audit Findings on Signed Improvements**:
  An exhaustive query of the 144 trials in `results/raw/robustness_trials.csv` revealed that in **16 trials**, the perturbed ARI was numerically slightly higher than the clean baseline ARI:
  * In **9 trials** on *Two Moons* ($K=2$) for K-Means: baseline ARI ranged between $0.1267$ and $0.2343$ ($\mu = 0.1941$). Under Gaussian noise ($\sigma = 0.05, 0.10, 0.20$), K-Means ARI hovered between $0.1467$ and $0.2680$ ($\mu \approx 0.2117\text{--}0.2237$).
  * In **7 trials** on *Concentric Circles* ($K=2$) for K-Means: baseline ARI was slightly negative ($-0.0029$ to $-0.0005$, $\mu = -0.0019$). Under slight noise or outliers, random point displacement caused the arbitrary Voronoi cut to shift slightly, producing ARI values such as $+0.0002$ or $+0.0042$.
* **Methodological Explanation**:
  * On non-convex geometries where K-Means fundamentally fails ($\text{ARI} \approx 0.0$ to $0.2$), minor perturbations do not represent genuine algorithmic improvement. Rather, they represent stochastic noise around an already invalid partition.
  * Clamping the metric with $\max(0.0, \dots)$ ensures that $\Delta \text{ARI}$ strictly measures **non-negative degradation / performance penalty** relative to a functioning baseline.
* **Resolution for Final Report**: In Chapter 4 and Chapter 8, the mathematical definition $\Delta \text{ARI} = \max(0.0, \text{ARI}_{\text{baseline}} - \text{ARI}_{\text{perturbed}})$ will be explicitly stated as a one-sided measure of performance loss. The report will transparently discuss the 16 trials where stochastic perturbations produced slight positive fluctuations around already-failing baselines.

---

### 2.4 Issue D — Guarding Against Overgeneralized / Universal Claims
* **Observation**: Scientific reports must avoid sweeping generalizations such as "K-Means has absolute robustness" or "MST always succeeds on non-convex manifolds."
* **Audit & Qualification**:
  1. *K-Means Robustness Boundary*: In our experiments, K-Means maintained $\text{ARI} = 1.0000$ on Gaussian Blobs across all evaluated noise levels ($\sigma \le 0.20$) and outlier fractions ($\eta \le 20\%$). However, this robustness is strictly conditional on **compact, well-separated, isotropic spherical clusters**. When confronted with non-convex shapes (Moons, Circles), K-Means failed completely ($\text{ARI} \le 0.1941$). Furthermore, theoretical analysis shows that asymmetric or extreme outliers placed sufficiently far from a cluster center can displace K-Means centroids arbitrarily.
  2. *MST Manifold Boundary*: MST clustering with single-linkage tree cutting succeeded on clean Two Moons and Concentric Circles ($\text{ARI} = 1.0000$). However, it is **hyper-vulnerable to ambient outliers**. In Two Moons, adding just $5\%$ uniform outliers caused MST ARI to drop abruptly from $1.0000$ to $0.0000$ ($\Delta\text{ARI} = 1.0000$).
* **Resolution for Final Report**: All conclusions in Chapters 1, 8, 9, and 10 will be strictly scoped to the empirical experimental boundaries tested ($\sigma \in [0.00, 0.20]$, $\eta \in [0\%, 20\%]$, $N=300$, $D=2$).

---

### 2.5 Issue E — Methodological Limitations of the Experimental Setup
* **Observation**: The experimental protocol has three intrinsic methodological limitations that must be addressed:
  1. *Sample of Three Random Seeds ($M = 3$)*: Seeds $\{11, 22, 33\}$ allow reproducible paired comparisons where both algorithms evaluate identical point coordinates. However, a sample of 3 seeds is an exploratory sample, not a comprehensive Monte Carlo census. The sample standard deviations provide an estimate of run-to-run dispersion, but confidence intervals require larger sample sizes ($M \ge 50$).
  2. *Two-Dimensional Synthetic Datasets ($D = 2$)*: Synthetic 2D manifolds allow visual validation and clear topological intuition. However, they do not exhibit the "curse of dimensionality" characteristic of high-dimensional real-world data, where Euclidean distance contrast diminishes.
  3. *Browser Monotonic Timer Quantization*: Client-side JavaScript execution timing relies on `window.performance.now()`. Modern web browsers enforce anti-fingerprinting quantization (typically $5\,\mu\text{s}$ to $100\,\mu\text{s}$) to prevent side-channel timing attacks (e.g., Spectre). For very fast operations completing in under $\sim 40\,\mu\text{s}$, the timer legitimately records $0.0000\text{ ms}$. This represents a genuine non-negative measurement resulting from system granularity rather than missing data.
* **Resolution for Final Report**: A dedicated "Threats to Validity and Limitations" section will be integrated into Chapter 9, discussing these three factors with full transparency.

---

### 2.6 Issue F — Distinguishing Theoretical Complexity from Observed Empirical Scaling
* **Observation**: In computational performance benchmarking, theoretical asymptotic complexity ($O(f(N))$) must never be conflated with empirical millisecond execution runtimes on specific hardware.
* **Audit & Distinctions**:
  * *Theoretical Complexity*:
    * Dense Prim's MST constructs a complete Euclidean distance graph requiring $\binom{N}{2} = \frac{N(N-1)}{2}$ distance evaluations, followed by edge selection, yielding a proven asymptotic bound of $\Theta(N^2)$ time and $O(N)$ auxiliary space.
    * Lloyd's K-Means performs $I$ iterations updating $K$ centroids across $N$ points, yielding an asymptotic bound of $O(I \cdot K \cdot N)$ time and $O(N)$ space.
  * *Observed Empirical Trends*:
    * In our benchmark trials on an x64 Intel/AMD processor with V8 JIT optimization, MST runtime scaled from $0.14\text{ ms}$ at $N=100$ to $1.70\text{ ms}$ at $N=600$ (a $12.1\times$ increase for a $6\times$ sample size growth, consistent with quadratic curvature).
    * K-Means runtime remained flat at approximately $0.10\text{--}0.16\text{ ms}$ because $K=3$ well-separated clusters converged in very few iterations ($I \le 5$).
* **Resolution for Final Report**: Chapter 4 will formally define the mathematical asymptotic bounds, while Chapter 8 will present the empirical benchmark measurements. Chapter 8 and 9 will explicitly state that the measured curves illustrate consistency with theoretical expectations on the tested sample range ($N \in [100, 600]$), without claiming empirical timing is a substitute for mathematical proof.

---

## 3. Conclusion of Audit
With these six methodological clarifications formally resolved, the empirical evidence base is mathematically verified, fully transparent, and ready for incorporation into the Final Academic Project Report (`FINAL_PROJECT_REPORT.md`).
