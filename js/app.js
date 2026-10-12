/**
 * MST vs K-Means Robustness Analysis
 * Module: Application Controller & UI State Orchestrator (Phase 3)
 * Pure Vanilla JavaScript - No dependencies
 */

(function (window) {
  'use strict';

  const { Datasets, KMeans, MST, Evaluation, Visualizer, Robustness, Benchmarks, ChartRenderer } = window.MSTKMeans;

  // Default playground parameters
  const DEFAULTS = {
    dataset: 'blobs',
    sampleSize: 300,
    clusters: 3,
    noise: 0.15,
    outlierFraction: 0.05,
    seed: 42
  };

  // Experiment & Benchmark Runners
  const robustnessRunner = new Robustness.RobustnessRunner();
  const benchmarkRunner = new Benchmarks.BenchmarkRunner();

  // DOM Elements cache
  let dom = {};

  function initDOM() {
    dom = {
      // Navigation
      navButtons: document.querySelectorAll('.nav-btn'),
      appViews: document.querySelectorAll('.app-view'),
      btnJumpToPlayground: document.getElementById('btn-jump-to-playground'),

      // Playground Controls
      datasetSelect: document.getElementById('dataset-select'),
      sampleSizeInput: document.getElementById('sample-size-input'),
      sampleSizeVal: document.getElementById('sample-size-val'),
      clusterCountGroup: document.getElementById('cluster-count-group'),
      clusterCountInput: document.getElementById('cluster-count-input'),
      clusterCountVal: document.getElementById('cluster-count-val'),
      noiseLevelInput: document.getElementById('noise-level-input'),
      noiseLevelVal: document.getElementById('noise-level-val'),
      outlierFractionInput: document.getElementById('outlier-fraction-input'),
      outlierFractionVal: document.getElementById('outlier-fraction-val'),
      randomSeedInput: document.getElementById('random-seed-input'),
      btnRandomSeed: document.getElementById('btn-random-seed'),
      btnRun: document.getElementById('btn-run'),
      btnRunSidebar: document.getElementById('btn-run-sidebar'),
      btnResetDefaults: document.getElementById('btn-reset-defaults'),
      btnResetSidebar: document.getElementById('btn-reset-sidebar'),

      // Playground Canvases
      canvasGroundTruth: document.getElementById('canvas-ground-truth'),
      canvasKMeans: document.getElementById('canvas-kmeans'),
      canvasMST: document.getElementById('canvas-mst'),

      // Playground Badges
      groundTruthBadge: document.getElementById('ground-truth-badge'),
      kmeansBadge: document.getElementById('kmeans-badge'),
      mstBadge: document.getElementById('mst-badge'),

      // Playground Metrics Table
      summaryText: document.getElementById('dataset-summary-text'),
      kmOverallARI: document.getElementById('m-kmeans-overall-ari'),
      mstOverallARI: document.getElementById('m-mst-overall-ari'),
      kmInlierARI: document.getElementById('m-kmeans-inlier-ari'),
      mstInlierARI: document.getElementById('m-mst-inlier-ari'),
      kmRuntime: document.getElementById('m-kmeans-runtime'),
      mstRuntime: document.getElementById('m-mst-runtime'),
      kmK: document.getElementById('m-kmeans-k'),
      mstK: document.getElementById('m-mst-k'),
      kmInertia: document.getElementById('m-kmeans-inertia'),
      mstWeight: document.getElementById('m-mst-weight'),
      kmDetails: document.getElementById('m-kmeans-details'),
      mstDetails: document.getElementById('m-mst-details'),
      educationalText: document.getElementById('educational-insight-text'),

      // Results & Export In-Memory Summary
      exportDatasetName: document.getElementById('export-dataset-name'),
      exportSampleSize: document.getElementById('export-sample-size'),
      exportInlierOutlierBreakdown: document.getElementById('export-inlier-outlier-breakdown'),
      exportKSeed: document.getElementById('export-k-seed'),
      exportKmARI: document.getElementById('export-km-ari'),
      exportMstARI: document.getElementById('export-mst-ari'),
      exportRuntimes: document.getElementById('export-runtimes'),

      // Robustness Analysis Controls
      robDatasetSelect: document.getElementById('rob-dataset-select'),
      robSampleSize: document.getElementById('rob-sample-size'),
      robSweepType: document.getElementById('rob-sweep-type'),
      robSeedMode: document.getElementById('rob-seed-mode'),
      btnRunRobustness: document.getElementById('btn-run-robustness'),
      btnCancelRobustness: document.getElementById('btn-cancel-robustness'),
      robProgressPanel: document.getElementById('rob-progress-panel'),
      robProgressStatus: document.getElementById('rob-progress-status'),
      robProgressPercent: document.getElementById('rob-progress-percent'),
      robProgressBarFill: document.getElementById('rob-progress-bar-fill'),
      canvasChartNoise: document.getElementById('canvas-chart-noise'),
      canvasChartOutliers: document.getElementById('canvas-chart-outliers'),
      canvasChartDegradation: document.getElementById('canvas-chart-degradation'),
      robSummaryMeta: document.getElementById('rob-summary-meta'),
      robResultsTableBody: document.getElementById('rob-results-table-body'),
      robTakeawayText: document.getElementById('rob-takeaway-text'),

      // Performance Benchmarks Controls
      bmDatasetSelect: document.getElementById('bm-dataset-select'),
      bmRepetitionsSelect: document.getElementById('bm-repetitions-select'),
      btnRunBenchmark: document.getElementById('btn-run-benchmark'),
      btnCancelBenchmark: document.getElementById('btn-cancel-benchmark'),
      bmProgressPanel: document.getElementById('bm-progress-panel'),
      bmProgressStatus: document.getElementById('bm-progress-status'),
      bmProgressPercent: document.getElementById('bm-progress-percent'),
      bmProgressBarFill: document.getElementById('bm-progress-bar-fill'),
      canvasChartScaling: document.getElementById('canvas-chart-scaling'),
      bmResultsTableBody: document.getElementById('bm-results-table-body'),
      bmEnvPlatform: document.getElementById('bm-env-platform'),
      bmEnvCores: document.getElementById('bm-env-cores'),
      bmEnvPrecision: document.getElementById('bm-env-precision'),
      bmEnvAgent: document.getElementById('bm-env-agent')
    };
  }

  function switchView(targetViewId) {
    if (!targetViewId) return;

    dom.navButtons.forEach(btn => {
      const isMatch = btn.getAttribute('data-view') === targetViewId;
      btn.classList.toggle('active', isMatch);
      btn.setAttribute('aria-selected', isMatch ? 'true' : 'false');
    });

    dom.appViews.forEach(view => {
      const isMatch = view.id === targetViewId;
      view.classList.toggle('active-view', isMatch);
    });

    // Re-render visible canvases on tab switch
    if (targetViewId === 'view-playground') {
      setTimeout(() => executePlaygroundExperiment(), 50);
    } else if (targetViewId === 'view-robustness' && robustnessRunner.lastResults) {
      setTimeout(() => renderRobustnessResults(robustnessRunner.lastResults), 50);
    } else if (targetViewId === 'view-benchmarks' && benchmarkRunner.lastResults) {
      setTimeout(() => renderBenchmarkResults(benchmarkRunner.lastResults), 50);
    }
  }

  function getARIClass(val) {
    if (val === null || val === undefined) return '';
    if (val >= 0.75) return 'metric-score-high';
    if (val >= 0.40) return 'metric-score-med';
    return 'metric-score-low';
  }

  // ------------------------------------------------------------------------
  // Playground Implementation
  // ------------------------------------------------------------------------

  function updatePlaygroundControlReadouts() {
    dom.sampleSizeVal.textContent = dom.sampleSizeInput.value;
    dom.clusterCountVal.textContent = dom.clusterCountInput.value;
    dom.noiseLevelVal.textContent = parseFloat(dom.noiseLevelInput.value).toFixed(2);
    dom.outlierFractionVal.textContent = `${Math.round(dom.outlierFractionInput.value * 100)}%`;

    const type = dom.datasetSelect.value;
    if (type === 'moons' || type === 'circles') {
      dom.clusterCountInput.value = '2';
      dom.clusterCountVal.textContent = '2';
      dom.clusterCountInput.disabled = true;
      dom.clusterCountGroup.style.opacity = '0.5';
    } else {
      dom.clusterCountInput.disabled = false;
      dom.clusterCountGroup.style.opacity = '1.0';
    }
  }

  function resetPlaygroundToDefaults() {
    dom.datasetSelect.value = DEFAULTS.dataset;
    dom.sampleSizeInput.value = DEFAULTS.sampleSize;
    dom.clusterCountInput.value = DEFAULTS.clusters;
    dom.noiseLevelInput.value = DEFAULTS.noise;
    dom.outlierFractionInput.value = DEFAULTS.outlierFraction;
    dom.randomSeedInput.value = DEFAULTS.seed;

    updatePlaygroundControlReadouts();
    executePlaygroundExperiment();
  }

  function executePlaygroundExperiment() {
    const datasetType = dom.datasetSelect.value;
    const n = parseInt(dom.sampleSizeInput.value, 10);
    const k = (datasetType === 'moons' || datasetType === 'circles') ? 2 : parseInt(dom.clusterCountInput.value, 10);
    const noise = parseFloat(dom.noiseLevelInput.value);
    const outlierFraction = parseFloat(dom.outlierFractionInput.value);
    const seed = parseInt(dom.randomSeedInput.value, 10) || 42;

    const dataset = Datasets.generateDataset(datasetType, {
      n,
      k,
      noise,
      outlierFraction,
      seed
    });

    const kmeansResult = KMeans.runKMeans(dataset.points, k, { seed, initMethod: 'kmeans++' });
    const mstResult = MST.runMSTClustering(dataset.points, k);

    const kmEval = Evaluation.evaluateClustering(dataset, kmeansResult.labels);
    const mstEval = Evaluation.evaluateClustering(dataset, mstResult.labels);

    Visualizer.renderGroundTruth(dom.canvasGroundTruth, dataset);
    Visualizer.renderKMeans(dom.canvasKMeans, dataset, kmeansResult);
    Visualizer.renderMST(dom.canvasMST, dataset, mstResult);

    dom.groundTruthBadge.textContent = `N=${dataset.points.length} (${dataset.outliers.length} outliers)`;
    dom.kmeansBadge.textContent = `K=${kmeansResult.centroids.length} (${kmeansResult.iterations} iters)`;
    dom.mstBadge.textContent = `${mstResult.cutEdges.length} cuts (${mstResult.k} components)`;

    dom.summaryText.textContent = `Dataset: ${dataset.name} | Total Points: ${dataset.points.length} (${dataset.inliers.length} inliers, ${dataset.outliers.length} outliers) | Seed: ${seed}`;

    dom.kmOverallARI.textContent = kmEval.overallARI.toFixed(3);
    dom.kmOverallARI.className = `metric-val-highlight ${getARIClass(kmEval.overallARI)}`;

    dom.mstOverallARI.textContent = mstEval.overallARI.toFixed(3);
    dom.mstOverallARI.className = `metric-val-highlight ${getARIClass(mstEval.overallARI)}`;

    const kmInlierStr = kmEval.inlierARI !== null ? kmEval.inlierARI.toFixed(3) : 'N/A';
    dom.kmInlierARI.textContent = kmInlierStr;
    dom.kmInlierARI.className = `metric-val-highlight ${getARIClass(kmEval.inlierARI)}`;

    const mstInlierStr = mstEval.inlierARI !== null ? mstEval.inlierARI.toFixed(3) : 'N/A';
    dom.mstInlierARI.textContent = mstInlierStr;
    dom.mstInlierARI.className = `metric-val-highlight ${getARIClass(mstEval.inlierARI)}`;

    dom.kmRuntime.textContent = `${kmeansResult.runtimeMs.toFixed(2)} ms`;
    dom.mstRuntime.textContent = `${mstResult.runtimeMs.toFixed(2)} ms`;

    if (dom.kmK) dom.kmK.textContent = `K = ${kmeansResult.centroids.length}`;
    if (dom.mstK) dom.mstK.textContent = `${mstResult.k} components formed`;

    dom.kmInertia.textContent = `Inertia: ${kmeansResult.inertia.toFixed(1)}`;
    dom.mstWeight.textContent = `Weight: ${mstResult.totalWeight.toFixed(2)}`;

    dom.kmDetails.textContent = `${kmeansResult.iterations} iterations (${kmeansResult.converged ? 'converged' : 'max-iter'})`;
    dom.mstDetails.textContent = `${mstResult.cutEdges.length} edges cut, ${mstResult.k} components`;

    updatePlaygroundEducationalInsights(datasetType, noise, outlierFraction, kmEval, mstEval);

    // Sync Results & Export summary
    if (dom.exportDatasetName) {
      dom.exportDatasetName.textContent = dataset.name;
      dom.exportSampleSize.textContent = `${dataset.points.length}`;
      dom.exportInlierOutlierBreakdown.textContent = `${dataset.inliers.length} inliers, ${dataset.outliers.length} outliers (${Math.round(outlierFraction * 100)}%)`;
      dom.exportKSeed.textContent = `K=${k}, Seed=${seed}, Noise=\u03C3=${noise.toFixed(2)}`;
      dom.exportKmARI.textContent = kmInlierStr;
      dom.exportKmARI.className = `metric-val-highlight ${getARIClass(kmEval.inlierARI)}`;
      dom.exportMstARI.textContent = mstInlierStr;
      dom.exportMstARI.className = `metric-val-highlight ${getARIClass(mstEval.inlierARI)}`;
      dom.exportRuntimes.textContent = `K-Means: ${kmeansResult.runtimeMs.toFixed(2)} ms | MST: ${mstResult.runtimeMs.toFixed(2)} ms`;
    }
  }

  function updatePlaygroundEducationalInsights(type, noise, outlierFraction, kmEval, mstEval) {
    if (type === 'moons' || type === 'circles') {
      if (outlierFraction === 0 && noise <= 0.15) {
        dom.educationalText.innerHTML = `<strong>Manifold Structure Advantage:</strong> On non-linear manifolds like <em>${type === 'moons' ? 'Two Moons' : 'Concentric Circles'}</em>, <strong>MST clustering achieves near-perfect separation</strong> (Inlier ARI: ${mstEval.inlierARI.toFixed(3)}) because Euclidean spanning paths follow manifold continuity. In contrast, <strong>K-Means fails</strong> (Inlier ARI: ${kmEval.inlierARI.toFixed(3)}) because its centroid-based Voronoi partition cannot represent non-convex shapes.`;
      } else {
        dom.educationalText.innerHTML = `<strong>Single-Linkage Vulnerability (Noise Bridges):</strong> With ${Math.round(outlierFraction * 100)}% outliers and &sigma;=${noise.toFixed(2)}, notice how outliers and noise points create single-linkage "bridges" between separate manifolds. In basic MST edge-cutting, cutting the longest edges may sever single isolated outlier points rather than the bridge between clusters, degrading MST performance. Compare <em>Overall ARI</em> vs <em>Inlier ARI</em> to observe this!`;
      }
    } else {
      if (outlierFraction > 0.1) {
        dom.educationalText.innerHTML = `<strong>Gaussian Blobs under Outlier Contamination:</strong> For convex blobs, <strong>K-Means</strong> remains relatively stable but its centroids are pulled slightly by extreme outliers. For <strong>MST</strong>, outliers frequently form long pendant edges; cutting the K-1 longest edges can isolate individual outlier leaves into their own singleton clusters instead of separating the main blobs!`;
      } else {
        dom.educationalText.innerHTML = `<strong>Gaussian Blobs (Convex Clusters):</strong> On isotropic spherical clusters, <strong>K-Means</strong> excels because the data matches its inductive bias (minimizing Euclidean squared variance). <strong>MST clustering</strong> also performs well provided cluster inter-distances exceed intra-cluster edge lengths.`;
      }
    }
  }

  // ------------------------------------------------------------------------
  // Robustness Analysis Controller (Phase 3)
  // ------------------------------------------------------------------------

  async function handleRunRobustness() {
    const datasetType = dom.robDatasetSelect.value;
    const inlierCount = parseInt(dom.robSampleSize.value, 10);
    const sweepType = dom.robSweepType.value;
    const seeds = dom.robSeedMode.value === 'research' ? [11, 22, 33, 44, 55] : [11, 22, 33];

    dom.btnRunRobustness.disabled = true;
    dom.btnCancelRobustness.disabled = false;
    dom.robProgressPanel.style.display = 'flex';
    dom.robProgressBarFill.style.width = '0%';
    dom.robProgressPercent.textContent = '0%';

    robustnessRunner.isCancelled = false;

    try {
      const results = await robustnessRunner.runExperiment({
        datasetType,
        inlierCount,
        sweepType,
        seeds
      }, (fraction, statusText) => {
        const pct = Math.round(fraction * 100);
        dom.robProgressBarFill.style.width = `${pct}%`;
        dom.robProgressPercent.textContent = `${pct}%`;
        dom.robProgressStatus.textContent = statusText;
      });

      renderRobustnessResults(results);
    } catch (err) {
      if (err.message.includes('cancelled')) {
        dom.robProgressStatus.textContent = 'Experiment cancelled by user.';
      } else {
        console.error(err);
        dom.robProgressStatus.textContent = `Error: ${err.message}`;
      }
    } finally {
      dom.btnRunRobustness.disabled = false;
      dom.btnCancelRobustness.disabled = true;
      setTimeout(() => {
        dom.robProgressPanel.style.display = 'none';
      }, 1500);
    }
  }

  function handleCancelRobustness() {
    robustnessRunner.cancel();
    dom.btnCancelRobustness.disabled = true;
    dom.robProgressStatus.textContent = 'Cancelling experiment...';
  }

  function renderRobustnessResults(results) {
    if (!results) return;

    dom.robSummaryMeta.textContent = `Dataset: ${results.datasetType} | Inliers: ${results.inlierCount} | Seeds evaluated: [${results.seeds.join(', ')}]`;

    // 1. Chart 1: Noise Sweep (Inlier ARI vs Noise Level)
    if (results.aggregatedNoise && results.aggregatedNoise.length > 0) {
      const noiseTicks = results.aggregatedNoise.map(s => `\u03C3=${s.stepValue.toFixed(2)}`);
      const kmNoiseData = results.aggregatedNoise.map(s => ({ mean: s.kmeans.inlierARI.mean, std: s.kmeans.inlierARI.std }));
      const mstNoiseData = results.aggregatedNoise.map(s => ({ mean: s.mst.inlierARI.mean, std: s.mst.inlierARI.std }));

      ChartRenderer.renderLineChartWithErrorBars(dom.canvasChartNoise, {
        title: 'Inlier ARI vs Noise Level (\u03C3)',
        xLabel: 'Gaussian Noise Level (\u03C3)',
        yLabel: 'Inlier ARI',
        xTicks: noiseTicks,
        kmData: kmNoiseData,
        mstData: mstNoiseData,
        yMin: 0.0,
        yMax: 1.0
      });
    } else {
      ChartRenderer.renderEmptyState(dom.canvasChartNoise, 'Noise sweep not included in this run');
    }

    // 2. Chart 2: Outlier Sweep (Inlier ARI vs Outlier %)
    if (results.aggregatedOutliers && results.aggregatedOutliers.length > 0) {
      const outlierTicks = results.aggregatedOutliers.map(s => `${Math.round(s.stepValue * 100)}%`);
      const kmOutlierData = results.aggregatedOutliers.map(s => ({ mean: s.kmeans.inlierARI.mean, std: s.kmeans.inlierARI.std }));
      const mstOutlierData = results.aggregatedOutliers.map(s => ({ mean: s.mst.inlierARI.mean, std: s.mst.inlierARI.std }));

      ChartRenderer.renderLineChartWithErrorBars(dom.canvasChartOutliers, {
        title: 'Inlier ARI vs Outlier Contamination (%)',
        xLabel: 'Outlier Fraction (% of inliers)',
        yLabel: 'Inlier ARI',
        xTicks: outlierTicks,
        kmData: kmOutlierData,
        mstData: mstOutlierData,
        yMin: 0.0,
        yMax: 1.0
      });
    } else {
      ChartRenderer.renderEmptyState(dom.canvasChartOutliers, 'Outlier sweep not included in this run');
    }

    // 3. Chart 3: Degradation from Matched Baseline (Bar Chart)
    const degradationSteps = [];
    const kmDegradation = [];
    const mstDegradation = [];

    if (results.aggregatedNoise) {
      results.aggregatedNoise.forEach(s => {
        degradationSteps.push(`\u03C3=${s.stepValue.toFixed(2)}`);
        kmDegradation.push(s.kmeans.degradation.mean);
        mstDegradation.push(s.mst.degradation.mean);
      });
    }
    if (results.aggregatedOutliers) {
      results.aggregatedOutliers.forEach(s => {
        if (s.stepValue > 0) {
          degradationSteps.push(`+${Math.round(s.stepValue * 100)}% out`);
          kmDegradation.push(s.kmeans.degradation.mean);
          mstDegradation.push(s.mst.degradation.mean);
        }
      });
    }

    if (degradationSteps.length > 0) {
      ChartRenderer.renderDegradationBarChart(dom.canvasChartDegradation, {
        title: 'Matched Baseline Degradation (\u0394ARI Loss)',
        xTicks: degradationSteps,
        kmDegradation,
        mstDegradation
      });
    } else {
      ChartRenderer.renderEmptyState(dom.canvasChartDegradation, 'No degradation data');
    }

    // 4. Populate Results Table
    dom.robResultsTableBody.innerHTML = '';
    const allSweeps = (results.aggregatedNoise || []).concat(results.aggregatedOutliers || []);

    // Baseline average inlier ARI
    const baselineKM = computeMean(results.baselines.map(b => b.kmeans.inlierARI || 0));
    const baselineMST = computeMean(results.baselines.map(b => b.mst.inlierARI || 0));

    allSweeps.forEach(s => {
      const isNoise = s.paramKey === 'noise';
      const label = isNoise ? `Noise Sweep (\u03C3 = ${s.stepValue.toFixed(2)}, Outliers = 0%)` : `Outlier Sweep (${Math.round(s.stepValue * 100)}% Outliers, \u03C3 = 0.05)`;
      const baseVal = isNoise ? (baselineKM + baselineMST) / 2 : baselineKM;

      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td><strong>${label}</strong></td>
        <td>KM: ${baselineKM.toFixed(3)} | MST: ${baselineMST.toFixed(3)}</td>
        <td class="metric-val-highlight">${s.kmeans.inlierARI.mean.toFixed(3)} &plusmn; ${s.kmeans.inlierARI.std.toFixed(3)}</td>
        <td class="metric-val-highlight">${s.mst.inlierARI.mean.toFixed(3)} &plusmn; ${s.mst.inlierARI.std.toFixed(3)}</td>
        <td style="color: ${s.kmeans.degradation.mean > 0.2 ? '#f87171' : '#fbbf24'}; font-family: monospace;">-${s.kmeans.degradation.mean.toFixed(3)}</td>
        <td style="color: ${s.mst.degradation.mean > 0.2 ? '#f87171' : '#34d399'}; font-family: monospace;">-${s.mst.degradation.mean.toFixed(3)}</td>
        <td>${s.sampleCount} seeds</td>
      `;
      dom.robResultsTableBody.appendChild(tr);
    });

    // 5. Dynamic Educational Insight based on actual data
    updateRobustnessTakeaways(results);
  }

  function computeMean(arr) {
    if (!arr || arr.length === 0) return 0;
    return arr.reduce((a, b) => a + b, 0) / arr.length;
  }

  function updateRobustnessTakeaways(results) {
    const isNonLinear = results.datasetType === 'moons' || results.datasetType === 'circles';
    if (isNonLinear) {
      dom.robTakeawayText.innerHTML = `
        <strong>Manifold Topological Degradation:</strong> On non-linear <em>${results.datasetType}</em>, 
        MST clustering maintains strong Inlier ARI under pure low noise baselines. However, notice how adding 
        outlier contamination creates single-linkage bridges between manifolds, triggering sudden drop-offs in MST Inlier ARI. 
        K-Means exhibits flat low ARI throughout because its spherical inductive bias cannot partition non-convex geometries.
      `;
    } else {
      dom.robTakeawayText.innerHTML = `
        <strong>Gaussian Blobs Robustness Profile:</strong> On convex Gaussian clusters, 
        K-Means demonstrates remarkable resilience, with its centroids resisting outlier pulling until high contamination fractions. 
        For MST clustering, outliers form peripheral pendant edges; cutting the longest edges frequently isolates individual outliers as singletons, 
        causing true blob clusters to merge and driving up &Delta;ARI loss.
      `;
    }
  }

  // ------------------------------------------------------------------------
  // Performance Benchmarks Controller (Phase 3)
  // ------------------------------------------------------------------------

  function initEnvironmentProfile() {
    const env = Benchmarks.getEnvironmentInfo();
    if (dom.bmEnvPlatform) dom.bmEnvPlatform.textContent = env.platform;
    if (dom.bmEnvCores) dom.bmEnvCores.textContent = `${env.logicalCores} Logical Threads`;
    if (dom.bmEnvPrecision) dom.bmEnvPrecision.textContent = env.timerPrecision;
    if (dom.bmEnvAgent) dom.bmEnvAgent.textContent = env.userAgent.substring(0, 75) + '...';
  }

  async function handleRunBenchmark() {
    const datasetType = dom.bmDatasetSelect.value;
    const repetitions = parseInt(dom.bmRepetitionsSelect.value, 10);
    const sampleSizes = [100, 200, 400, 600];

    dom.btnRunBenchmark.disabled = true;
    dom.btnCancelBenchmark.disabled = false;
    dom.bmProgressPanel.style.display = 'flex';
    dom.bmProgressBarFill.style.width = '0%';
    dom.bmProgressPercent.textContent = '0%';

    benchmarkRunner.isCancelled = false;

    try {
      const results = await benchmarkRunner.runBenchmark({
        sampleSizes,
        repetitions,
        datasetType
      }, (fraction, statusText) => {
        const pct = Math.round(fraction * 100);
        dom.bmProgressBarFill.style.width = `${pct}%`;
        dom.bmProgressPercent.textContent = `${pct}%`;
        dom.bmProgressStatus.textContent = statusText;
      });

      renderBenchmarkResults(results);
    } catch (err) {
      if (err.message.includes('cancelled')) {
        dom.bmProgressStatus.textContent = 'Benchmark cancelled by user.';
      } else {
        console.error(err);
        dom.bmProgressStatus.textContent = `Error: ${err.message}`;
      }
    } finally {
      dom.btnRunBenchmark.disabled = false;
      dom.btnCancelBenchmark.disabled = true;
      setTimeout(() => {
        dom.bmProgressPanel.style.display = 'none';
      }, 1500);
    }
  }

  function handleCancelBenchmark() {
    benchmarkRunner.cancel();
    dom.btnCancelBenchmark.disabled = true;
    dom.bmProgressStatus.textContent = 'Cancelling benchmark...';
  }

  function renderBenchmarkResults(benchmarkData) {
    if (!benchmarkData || !benchmarkData.results) return;

    const { results } = benchmarkData;
    const sampleSizes = results.map(r => r.n);
    const kmTimes = results.map(r => ({ mean: r.kmeans.mean, std: r.kmeans.std }));
    const mstTimes = results.map(r => ({ mean: r.mst.mean, std: r.mst.std }));

    // 1. Render Runtime Scaling Chart
    ChartRenderer.renderRuntimeScalingChart(dom.canvasChartScaling, {
      title: `Empirical Runtime vs Sample Size N (${benchmarkData.config.datasetType})`,
      sampleSizes,
      kmTimes,
      mstTimes
    });

    // 2. Populate Benchmark Table
    dom.bmResultsTableBody.innerHTML = '';
    results.forEach(row => {
      const tr = document.createElement('tr');
      const ratioStr = row.ratio >= 1.0 ? `${row.ratio.toFixed(2)}x slower` : `${(1 / row.ratio).toFixed(2)}x faster`;
      const ratioColor = row.ratio > 2.0 ? '#fbbf24' : '#34d399';

      tr.innerHTML = `
        <td style="font-family: var(--font-mono); font-weight: 600;">N = ${row.n} points</td>
        <td style="font-family: var(--font-mono);">${row.kmeans.mean.toFixed(2)} &plusmn; ${row.kmeans.std.toFixed(2)} ms (med: ${row.kmeans.median.toFixed(2)})</td>
        <td style="font-family: var(--font-mono);">${row.mst.mean.toFixed(2)} &plusmn; ${row.mst.std.toFixed(2)} ms (med: ${row.mst.median.toFixed(2)})</td>
        <td style="font-family: var(--font-mono); color: ${ratioColor}; font-weight: 600;">${row.ratio.toFixed(2)}x (${ratioStr})</td>
      `;
      dom.bmResultsTableBody.appendChild(tr);
    });
  }

  // ------------------------------------------------------------------------
  // Event Bindings & Lifecycle
  // ------------------------------------------------------------------------

  function bindEvents() {
    // Navigation routing
    dom.navButtons.forEach(btn => {
      btn.addEventListener('click', () => {
        const targetView = btn.getAttribute('data-view');
        switchView(targetView);
      });
    });

    if (dom.btnJumpToPlayground) {
      dom.btnJumpToPlayground.addEventListener('click', () => {
        switchView('view-playground');
      });
    }

    // Playground listeners
    dom.datasetSelect.addEventListener('change', () => {
      updatePlaygroundControlReadouts();
      executePlaygroundExperiment();
    });

    [dom.sampleSizeInput, dom.clusterCountInput, dom.noiseLevelInput, dom.outlierFractionInput].forEach(elem => {
      elem.addEventListener('input', updatePlaygroundControlReadouts);
      elem.addEventListener('change', executePlaygroundExperiment);
    });

    dom.btnRandomSeed.addEventListener('click', () => {
      dom.randomSeedInput.value = Math.floor(Math.random() * 90000) + 1000;
      executePlaygroundExperiment();
    });

    dom.randomSeedInput.addEventListener('change', executePlaygroundExperiment);

    [dom.btnRun, dom.btnRunSidebar].forEach(btn => {
      if (btn) btn.addEventListener('click', executePlaygroundExperiment);
    });

    [dom.btnResetDefaults, dom.btnResetSidebar].forEach(btn => {
      if (btn) btn.addEventListener('click', resetPlaygroundToDefaults);
    });

    // Robustness Analysis listeners
    if (dom.btnRunRobustness) dom.btnRunRobustness.addEventListener('click', handleRunRobustness);
    if (dom.btnCancelRobustness) dom.btnCancelRobustness.addEventListener('click', handleCancelRobustness);

    // Performance Benchmark listeners
    if (dom.btnRunBenchmark) dom.btnRunBenchmark.addEventListener('click', handleRunBenchmark);
    if (dom.btnCancelBenchmark) dom.btnCancelBenchmark.addEventListener('click', handleCancelBenchmark);

    // Window Resize debouncer
    window.addEventListener('resize', () => {
      clearTimeout(window.__resizeTimer);
      window.__resizeTimer = setTimeout(() => {
        const activeView = document.querySelector('.app-view.active-view');
        if (!activeView) return;
        if (activeView.id === 'view-playground') executePlaygroundExperiment();
        else if (activeView.id === 'view-robustness' && robustnessRunner.lastResults) renderRobustnessResults(robustnessRunner.lastResults);
        else if (activeView.id === 'view-benchmarks' && benchmarkRunner.lastResults) renderBenchmarkResults(benchmarkRunner.lastResults);
      }, 100);
    });
  }

  // Initial Empty State Render for Charts
  function initChartEmptyStates() {
    if (dom.canvasChartNoise) ChartRenderer.renderEmptyState(dom.canvasChartNoise, 'Run Robustness Experiments to plot Inlier ARI vs Noise Level');
    if (dom.canvasChartOutliers) ChartRenderer.renderEmptyState(dom.canvasChartOutliers, 'Run Robustness Experiments to plot Inlier ARI vs Outliers');
    if (dom.canvasChartDegradation) ChartRenderer.renderEmptyState(dom.canvasChartDegradation, 'Run Robustness Experiments to plot Baseline Degradation Loss');
    if (dom.canvasChartScaling) ChartRenderer.renderEmptyState(dom.canvasChartScaling, 'Run Performance Benchmarks to plot Empirical Scaling Curves');
  }

  // Bootstrap on DOM Ready
  window.addEventListener('DOMContentLoaded', () => {
    initDOM();
    initEnvironmentProfile();
    updatePlaygroundControlReadouts();
    initChartEmptyStates();
    bindEvents();
    executePlaygroundExperiment();
  });

  window.MSTKMeans.App = {
    DEFAULTS,
    switchView,
    resetPlaygroundToDefaults,
    executePlaygroundExperiment,
    handleRunRobustness,
    handleRunBenchmark
  };
})(window);
