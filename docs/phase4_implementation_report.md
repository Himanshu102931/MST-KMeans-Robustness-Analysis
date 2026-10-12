# Phase 4 Implementation Report: Interactive Algorithm Explorer, Scientific Visualizations, and Export System

**Project**: MST vs K-Means Robustness Analysis  
**Student**: Himanshu Gupta (Allocation No: 19)  
**Project Partner**: Parth Yadav  
**Institution**: Manav Rachna International Institute of Research and Studies (MRIIRS)  
**Course**: Pattern Matching Lab (BCS-DS-777)  
**Date**: October 12, 2026  

---

## 1. Executive Summary

Phase 4 completes the pedagogical and scientific dissemination layer of the browser-native research platform. It introduces:
1. **Interactive Algorithm Explorer**: Step-by-step visual dissection of Lloyd's K-Means clustering (initialization, Voronoi nearest-neighbor assignment, center of mass recalculation, and convergence) and Prim's Euclidean Minimum Spanning Tree clustering (frontier edge relaxation, greedy tree growth, $K-1$ longest edge selection, and connected-component partitioning).
2. **Scientific Data Export Hub**: Client-side, offline export of tabular datasets (CSV with formula injection defense), per-run robustness observations, aggregated statistics, performance benchmarks, machine-readable reproducibility recipes (JSON), and publication-ready Canvas figures (PNG).

The entire system remains **100% browser-native, offline-capable, and file:// compatible**, with zero external npm dependencies, build tooling, or server runtimes.

---

## 2. Automated Test Suite Results

The dependency-free automated test suite in `tests/test_suite.js` was expanded from **38 tests to 54 automated assertions**, covering all components across Phases 1 through 4.

- **Total Tests**: **54**
- **Passed**: **54 (100%)**
- **Failed**: **0**
- **Execution Time**: ~69.80 ms
- **Console Errors**: **0**

### Phase 4 Test Assertions Added:
1. `Explorer: K-Means Trace Initialization State`: Verifies Step 0 initialization has $K$ centroids and all unassigned labels (-1).
2. `Explorer: K-Means Assignment and Centroid Update Sequence`: Validates alternating assignment/update steps, bounded label ranges, and non-negative inertia.
3. `Explorer: K-Means Trace Deterministic Reproducibility`: Confirms that identical seeds produce bitwise identical trace snapshots.
4. `Explorer: Final K-Means Trace Equivalence to Production Run`: Confirms that the final state of `generateKMeansTrace` matches `runKMeans` bitwise identically.
5. `Explorer: MST Prim Construction Vertex and Edge Counts (N - 1)`: Confirms that Prim's algorithm executes exactly $N-1$ edge additions on $N$ vertices.
6. `Explorer: MST Trace Total Edge Weight Consistency`: Confirms that cumulative tree weight equals the sum of edge weights and matches `runMSTClustering.totalWeight`.
7. `Explorer: MST K - 1 Longest Edge Selection`: Confirms that exactly $K-1$ longest edges are selected for deletion in descending weight order.
8. `Explorer: MST Connected-Component Equivalence to Production Run`: Confirms that removing $K-1$ edges partitions the graph into $K$ components matching `runMSTClustering` labels.
9. `Explorer: MST Deterministic Tie-Breaking on Duplicate Coordinates`: Confirms stable, deterministic handling of co-located points and equidistant edges.
10. `Explorer: Controller State Navigation and Reset`: Validates `nextStep()`, `prevStep()`, `goToStep()`, and `restart()` state transitions.
11. `Export: CSV Formula Injection Defense Sanitization`: Verifies prepending `'` to leading `=, +, -, @, \t, \r` characters.
12. `Export: RFC 4180 CSV Escaping for Commas and Quotes`: Verifies quoting and escaping of special characters.
13. `Export: Reproducibility Recipe Metadata Schema Integrity`: Verifies JSON document schema containing credentials and algorithm parameters.
14. `Export: Guard Against Exporting Non-Existent Experiments`: Verifies that unexecuted experiments throw clear errors instead of fabricating fake data.
15. `Export: High-DPI Canvas Rasterization to PNG Data URL`: Validates canvas rasterization into clean PNG images.
16. `Regression: Phase 1-3 Core Mechanics Invariant`: Verifies that core PRNG, dataset generation, and ARI metrics remain unaffected.

---

## 3. Architecture & Module Breakdown

```
├── index.html                      (Complete 6-section UI with Phase 4 Explorer & Export Hub)
├── css/main.css                    (Dark scientific styling, scrubber controls, responsive grids)
├── js/
│   ├── algorithms/
│   │   ├── kmeans.js               (Lloyd's algorithm + generateKMeansTrace)
│   │   └── mst.js                  (Prim's MST + generateMSTTrace + DisjointSet)
│   ├── data/
│   │   ├── datasets.js             (Gaussian Blobs, Two Moons, Concentric Circles)
│   │   └── prng.js                 (Mulberry32 PRNG + Box-Muller Gaussian sampler)
│   ├── experiments/
│   │   ├── benchmarks.js           (Performance benchmarking + hardware detection)
│   │   └── robustness.js           (Controlled noise & outlier sweeps)
│   ├── explorer/
│   │   └── explorer.js             (AlgorithmExplorerController playback & UI state)
│   ├── export/
│   │   └── export_manager.js       (CSV, JSON, PNG exporter with formula injection defense)
│   ├── metrics/
│   │   └── evaluation.js           (Adjusted Rand Index, Inlier ARI, contingency matrix)
│   ├── visualization/
│   │   ├── canvas_renderer.js      (Playground canvas renderer)
│   │   ├── chart_renderer.js       (Scientific line charts with error bars & bar charts)
│   │   └── explorer_renderer.js    (High-DPI canvas step visualizer for K-Means & MST)
│   └── app.js                      (Global controller, event bindings, session sync)
├── tests/
│   ├── test_runner.html            (Automated browser test runner)
│   └── test_suite.js               (54 automated tests)
└── docs/
    └── phase4_implementation_report.md
```

---

## 4. Algorithmic Step-by-Step Visualization Mechanics

### A. K-Means Explorer
- **State Sequence**: `Initialization (Step 0) → [Assignment → Centroid Update] × Iterations → Convergence`.
- **Authenticity**: Visual snapshots are generated directly from the mathematical state of Lloyd's algorithm. Centroids represent exact coordinate averages, assignments represent Voronoi nearest neighbors, and inertia values represent the true Within-Cluster Sum of Squares ($J = \sum_{i=1}^N ||\mathbf{x}_i - \boldsymbol{\mu}_{y_i}||^2$).
- **Visual Features**:
  - Dotted colored lines link each observation to its assigned centroid.
  - Dashed crimson vectors with arrowheads demonstrate the centroid relocation trajectory from $\boldsymbol{\mu}_{\text{old}}$ to $\boldsymbol{\mu}_{\text{new}}$.
  - Centroids are displayed as prominent glowing diamonds with centroid IDs ($C_1, C_2, \dots$).

### B. Euclidean MST Prim's Explorer
- **State Sequence**: `Root Initialization (Step 0) → Prim's Greedy Tree Additions (Steps 1 to N-1) → MST Complete → Longest Edge Cut Selection → Clustering Complete`.
- **Authenticity**: Prim's dense algorithm operates in $O(N^2)$ time with Euclidean edge weights $w(u, v) = \sqrt{(x_u - x_v)^2 + (y_u - y_v)^2}$.
- **Visual Features**:
  - Frontier candidate edges are displayed as faint dotted lines.
  - The actively relaxing minimum edge is highlighted in bright amber with weight callout ($w = \dots$).
  - Accepted tree edges are rendered in emerald green.
  - In the partitioning phase, the $K-1$ longest edges are highlighted in dashed crimson with a cut badge, then removed to reveal $K$ distinct colored connected components.
  - Pedagogical commentary explains why basic MST longest-edge clustering suffers from single-linkage chaining and vulnerability to isolated outliers.

---

## 5. Scientific Export System Specifications

| Export Target | Format | Schema / Contents | Defense / Safeguards |
|---|---|---|---|
| **Playground Dataset** | CSV | `point_index, x, y, ground_truth_label, is_outlier, kmeans_predicted_cluster, mst_predicted_cluster` | Formula injection defense (`=, +, -, @` escaped) |
| **Playground Metrics** | CSV | `dataset, sample_count, k, noise, outlier_fraction, seed, algorithm_name, inlier_ari, runtime_ms, inertia_or_weight` | RFC 4180 comma/quote escaping |
| **Robustness Raw Observations** | CSV | Per-run observations across all seeds: `dataset_family, seed, N, k, noise, outliers, sweep_type, algorithm, inlier_ari, baseline_ari, degradation, runtime` | Disabled until experiment is executed; throws descriptive error if unexecuted |
| **Robustness Aggregated** | CSV | Summary statistics: `parameter_group, sweep_param, value, algorithm, repetitions, mean_ari, std_ari, mean_degradation` | Live state synchronization |
| **Performance Benchmarks** | CSV | `sample_size, algorithm, trial_id, runtime_ms, mean_ms, std_ms, median_ms, speedup_vs_mst, hardware_platform, hardware_cores` | Actual `performance.now()` measurements |
| **Reproducibility Recipe** | JSON | Full metadata, student credentials, random seeds, algorithm configurations, and hardware environment | Sanitized: no filesystem paths, tokens, or private data |
| **Scientific Figures** | PNG | Rasterized high-DPI canvas images (Ground Truth, K-Means, MST, ARI vs Noise, ARI vs Outliers, Degradation, Runtime Scaling, Active Explorer) | Native `canvas.toBlob` with revoked object URLs |

---

## 6. Known Limitations & Scientific Observations

1. **Browser Single-Threaded Event Loop**:
   - Animation playback uses `setInterval` timed by the playback speed setting. While smooth on small datasets ($N \le 40$), large datasets are constrained to ensure high frame rates and responsive scrubber interaction.
2. **Security-First CSV Formatting**:
   - In accordance with CWE-1236, spreadsheet formula injection characters (`=, +, -, @`) are prepended with a single quote. When imported into spreadsheet viewers (Microsoft Excel, Google Sheets, LibreOffice Calc), these cells are safely treated as raw strings rather than executable expressions.
3. **Memory Measurements Transparency**:
   - Per Phase 3 guidelines, memory measurements are reported via theoretical space complexity ($O(N+K)$ for K-Means vs $O(N)$ for Prim's MST) rather than inventing uncalibrated browser heap numbers.
