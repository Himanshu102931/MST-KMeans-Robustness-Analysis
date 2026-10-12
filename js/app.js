/**
 * MST vs K-Means Robustness Analysis
 * Module: Application Controller & UI State Orchestrator
 * Pure Vanilla JavaScript - No dependencies
 */

(function (window) {
  'use strict';

  const { Datasets, KMeans, MST, Evaluation, Visualizer } = window.MSTKMeans;

  // DOM Elements cache
  let dom = {};

  function initDOM() {
    dom = {
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

      // Canvases
      canvasGroundTruth: document.getElementById('canvas-ground-truth'),
      canvasKMeans: document.getElementById('canvas-kmeans'),
      canvasMST: document.getElementById('canvas-mst'),

      // Badges
      groundTruthBadge: document.getElementById('ground-truth-badge'),
      kmeansBadge: document.getElementById('kmeans-badge'),
      mstBadge: document.getElementById('mst-badge'),

      // Metrics Table
      summaryText: document.getElementById('dataset-summary-text'),
      kmOverallARI: document.getElementById('m-kmeans-overall-ari'),
      mstOverallARI: document.getElementById('m-mst-overall-ari'),
      kmInlierARI: document.getElementById('m-kmeans-inlier-ari'),
      mstInlierARI: document.getElementById('m-mst-inlier-ari'),
      kmRuntime: document.getElementById('m-kmeans-runtime'),
      mstRuntime: document.getElementById('m-mst-runtime'),
      kmInertia: document.getElementById('m-kmeans-inertia'),
      mstWeight: document.getElementById('m-mst-weight'),
      kmDetails: document.getElementById('m-kmeans-details'),
      mstDetails: document.getElementById('m-mst-details'),
      educationalText: document.getElementById('educational-insight-text')
    };
  }

  function getARIClass(val) {
    if (val === null || val === undefined) return '';
    if (val >= 0.75) return 'metric-score-high';
    if (val >= 0.40) return 'metric-score-med';
    return 'metric-score-low';
  }

  function updateControlReadouts() {
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

  function executeExperiment() {
    const datasetType = dom.datasetSelect.value;
    const n = parseInt(dom.sampleSizeInput.value, 10);
    const k = (datasetType === 'moons' || datasetType === 'circles') ? 2 : parseInt(dom.clusterCountInput.value, 10);
    const noise = parseFloat(dom.noiseLevelInput.value);
    const outlierFraction = parseFloat(dom.outlierFractionInput.value);
    const seed = parseInt(dom.randomSeedInput.value, 10) || 42;

    // 1. Generate Synthetic Dataset
    const dataset = Datasets.generateDataset(datasetType, {
      n,
      k,
      noise,
      outlierFraction,
      seed
    });

    // 2. Run K-Means
    const kmeansResult = KMeans.runKMeans(dataset.points, k, {
      seed,
      initMethod: 'kmeans++'
    });

    // 3. Run MST Clustering
    const mstResult = MST.runMSTClustering(dataset.points, k);

    // 4. Quantitative Evaluation
    const kmEval = Evaluation.evaluateClustering(dataset, kmeansResult.labels);
    const mstEval = Evaluation.evaluateClustering(dataset, mstResult.labels);

    // 5. Render Canvases
    Visualizer.renderGroundTruth(dom.canvasGroundTruth, dataset);
    Visualizer.renderKMeans(dom.canvasKMeans, dataset, kmeansResult);
    Visualizer.renderMST(dom.canvasMST, dataset, mstResult);

    // 6. Update Badges
    dom.groundTruthBadge.textContent = `N=${dataset.points.length} (${dataset.outliers.length} outliers)`;
    dom.kmeansBadge.textContent = `K=${kmeansResult.centroids.length} (${kmeansResult.iterations} iters)`;
    dom.mstBadge.textContent = `${mstResult.cutEdges.length} cuts (${mstResult.k} components)`;

    // 7. Update Metrics Table
    dom.summaryText.textContent = `Dataset: ${dataset.name} | Total Points: ${dataset.points.length} (${dataset.inliers.length} inliers, ${dataset.outliers.length} outliers) | Seed: ${seed}`;

    // Overall ARI
    dom.kmOverallARI.textContent = kmEval.overallARI.toFixed(3);
    dom.kmOverallARI.className = `metric-val-highlight ${getARIClass(kmEval.overallARI)}`;

    dom.mstOverallARI.textContent = mstEval.overallARI.toFixed(3);
    dom.mstOverallARI.className = `metric-val-highlight ${getARIClass(mstEval.overallARI)}`;

    // Inlier ARI
    const kmInlierStr = kmEval.inlierARI !== null ? kmEval.inlierARI.toFixed(3) : 'N/A';
    dom.kmInlierARI.textContent = kmInlierStr;
    dom.kmInlierARI.className = `metric-val-highlight ${getARIClass(kmEval.inlierARI)}`;

    const mstInlierStr = mstEval.inlierARI !== null ? mstEval.inlierARI.toFixed(3) : 'N/A';
    dom.mstInlierARI.textContent = mstInlierStr;
    dom.mstInlierARI.className = `metric-val-highlight ${getARIClass(mstEval.inlierARI)}`;

    // Runtime
    dom.kmRuntime.textContent = `${kmeansResult.runtimeMs.toFixed(2)} ms`;
    dom.mstRuntime.textContent = `${mstResult.runtimeMs.toFixed(2)} ms`;

    // Structural metrics
    dom.kmInertia.textContent = `Inertia: ${kmeansResult.inertia.toFixed(1)}`;
    dom.mstWeight.textContent = `Weight: ${mstResult.totalWeight.toFixed(2)}`;

    // Details
    dom.kmDetails.textContent = `${kmeansResult.iterations} iterations (${kmeansResult.converged ? 'converged' : 'max-iter'})`;
    dom.mstDetails.textContent = `${mstResult.cutEdges.length} edges cut, ${mstResult.k} components`;

    // 8. Update Educational Insights
    updateEducationalInsights(datasetType, noise, outlierFraction, kmEval, mstEval);
  }

  function updateEducationalInsights(type, noise, outlierFraction, kmEval, mstEval) {
    if (type === 'moons' || type === 'circles') {
      if (outlierFraction === 0 && noise <= 0.15) {
        dom.educationalText.innerHTML = `<strong>Manifold Structure Advantage:</strong> On non-linear manifolds like <em>${type === 'moons' ? 'Two Moons' : 'Concentric Circles'}</em>, <strong>MST clustering achieves near-perfect separation</strong> (ARI: ${mstEval.overallARI.toFixed(3)}) because Euclidean spanning paths follow manifold continuity. In contrast, <strong>K-Means fails</strong> (ARI: ${kmEval.overallARI.toFixed(3)}) because its centroid-based Voronoi partition cannot represent non-convex shapes.`;
      } else {
        dom.educationalText.innerHTML = `<strong>Single-Linkage Vulnerability (Noise Bridges):</strong> With ${Math.round(outlierFraction * 100)}% outliers and &sigma;=${noise.toFixed(2)}, notice how outliers and noise points create single-linkage "bridges" between separate manifolds. In basic MST edge-cutting, cutting the longest edges may sever single isolated outlier points rather than the bridge between clusters, degrading MST performance. Compare <em>Overall ARI</em> vs <em>Inlier ARI</em> to observe this!`;
      }
    } else {
      if (outlierFraction > 0.1) {
        dom.educationalText.innerHTML = `<strong>Gaussian Blobs under Outlier Contamination:</strong> For convex blobs, <strong>K-Means</strong> remains relatively stable but its centroids are pulled slightly by extreme outliers. For <strong>MST</strong>, outliers frequently form long pendant edges; cutting the $K-1$ longest edges can isolate individual outlier leaves into their own singleton clusters instead of separating the main blobs!`;
      } else {
        dom.educationalText.innerHTML = `<strong>Gaussian Blobs (Convex Clusters):</strong> On isotropic spherical clusters, <strong>K-Means</strong> excels because the data matches its inductive bias (minimizing Euclidean squared variance). <strong>MST clustering</strong> also performs well provided cluster inter-distances exceed intra-cluster edge lengths.`;
      }
    }
  }

  function bindEvents() {
    dom.datasetSelect.addEventListener('change', () => {
      updateControlReadouts();
      executeExperiment();
    });

    [dom.sampleSizeInput, dom.clusterCountInput, dom.noiseLevelInput, dom.outlierFractionInput].forEach(elem => {
      elem.addEventListener('input', () => {
        updateControlReadouts();
      });
      elem.addEventListener('change', () => {
        executeExperiment();
      });
    });

    dom.btnRandomSeed.addEventListener('click', () => {
      dom.randomSeedInput.value = Math.floor(Math.random() * 90000) + 1000;
      executeExperiment();
    });

    dom.randomSeedInput.addEventListener('change', () => {
      executeExperiment();
    });

    dom.btnRun.addEventListener('click', () => {
      executeExperiment();
    });

    window.addEventListener('resize', () => {
      // Debounced re-render on resize
      clearTimeout(window.__resizeTimer);
      window.__resizeTimer = setTimeout(executeExperiment, 100);
    });
  }

  // Auto-init on page load
  window.addEventListener('DOMContentLoaded', () => {
    initDOM();
    updateControlReadouts();
    bindEvents();
    executeExperiment();
  });

  window.MSTKMeans.App = {
    executeExperiment
  };
})(window);
