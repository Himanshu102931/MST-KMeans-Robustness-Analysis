/**
 * MST vs K-Means Robustness Analysis
 * Module: K-Means Clustering Algorithm
 * Pure Vanilla JavaScript - No dependencies
 */

(function (window) {
  'use strict';

  window.MSTKMeans = window.MSTKMeans || {};
  const { createPRNG } = window.MSTKMeans.PRNG;

  /**
   * Euclidean distance squared between two 2D points
   */
  function distSq(p1, p2) {
    const dx = p1.x - p2.x;
    const dy = p1.y - p2.y;
    return dx * dx + dy * dy;
  }

  /**
   * Euclidean distance between two 2D points
   */
  function dist(p1, p2) {
    return Math.sqrt(distSq(p1, p2));
  }

  /**
   * Initialize centroids using K-Means++ algorithm
   * @param {Array<{x: number, y: number}>} points
   * @param {number} k Number of clusters
   * @param {function(): number} rng Deterministic PRNG
   * @returns {Array<{x: number, y: number}>} Initial centroids
   */
  function initKMeansPlusPlus(points, k, rng) {
    const n = points.length;
    if (n === 0 || k <= 0) return [];
    if (n <= k) {
      return points.map(p => ({ x: p.x, y: p.y }));
    }

    const centroids = [];
    // 1. Pick first center uniformly at random
    const firstIdx = Math.floor(rng() * n);
    centroids.push({ x: points[firstIdx].x, y: points[firstIdx].y });

    // Pre-allocated array of min distances squared
    const dSq = new Float64Array(n);
    for (let i = 0; i < n; i++) {
      dSq[i] = distSq(points[i], centroids[0]);
    }

    // 2. Pick remaining k - 1 centers
    for (let c = 1; c < k; c++) {
      let sumD = 0;
      for (let i = 0; i < n; i++) {
        sumD += dSq[i];
      }

      let nextCenter;
      if (sumD <= 1e-12) {
        // Fallback: choose random point
        const fallbackIdx = Math.floor(rng() * n);
        nextCenter = { x: points[fallbackIdx].x, y: points[fallbackIdx].y };
      } else {
        const threshold = rng() * sumD;
        let runningSum = 0;
        let selectedIdx = n - 1;
        for (let i = 0; i < n; i++) {
          runningSum += dSq[i];
          if (runningSum >= threshold) {
            selectedIdx = i;
            break;
          }
        }
        nextCenter = { x: points[selectedIdx].x, y: points[selectedIdx].y };
      }

      centroids.push(nextCenter);

      // Update minimum distances
      for (let i = 0; i < n; i++) {
        const d = distSq(points[i], nextCenter);
        if (d < dSq[i]) {
          dSq[i] = d;
        }
      }
    }

    return centroids;
  }

  /**
   * Execute K-Means clustering
   * @param {Array<{x: number, y: number}>} points Point array
   * @param {number} k Number of clusters
   * @param {Object} options Configuration options
   * @param {number} [options.maxIterations=100] Maximum Lloyd iterations
   * @param {number} [options.tolerance=1e-5] Convergence tolerance for centroid shift
   * @param {number} [options.seed=42] Random seed for reproducibility
   * @param {string} [options.initMethod='kmeans++'] 'kmeans++' or 'random'
   * @returns {Object} Clustering result
   */
  function runKMeans(points, k, options = {}) {
    const startTime = performance.now();
    const {
      maxIterations = 100,
      tolerance = 1e-5,
      seed = 42,
      initMethod = 'kmeans++'
    } = options;

    const n = points.length;
    if (n === 0) {
      return {
        labels: [],
        centroids: [],
        iterations: 0,
        converged: true,
        inertia: 0,
        runtimeMs: 0,
        history: []
      };
    }

    const actualK = Math.min(Math.max(1, Math.floor(k)), n);
    const rng = createPRNG(seed);

    let centroids;
    if (initMethod === 'kmeans++') {
      centroids = initKMeansPlusPlus(points, actualK, rng);
    } else {
      // Simple random sample
      const indices = Array.from({ length: n }, (_, i) => i);
      // Fisher-Yates partial shuffle
      for (let i = 0; i < actualK; i++) {
        const j = i + Math.floor(rng() * (n - i));
        const temp = indices[i];
        indices[i] = indices[j];
        indices[j] = temp;
      }
      centroids = indices.slice(0, actualK).map(idx => ({ x: points[idx].x, y: points[idx].y }));
    }

    const labels = new Int32Array(n);
    const history = []; // Keep track of centroids per iteration if needed for animation
    history.push(centroids.map(c => ({ x: c.x, y: c.y })));

    let converged = false;
    let iteration = 0;

    while (iteration < maxIterations && !converged) {
      iteration++;

      // 1. Assignment step: Assign each point to nearest centroid
      for (let i = 0; i < n; i++) {
        let bestDist = Infinity;
        let bestCluster = 0;
        for (let c = 0; c < actualK; c++) {
          const d = distSq(points[i], centroids[c]);
          if (d < bestDist) {
            bestDist = d;
            bestCluster = c;
          }
        }
        labels[i] = bestCluster;
      }

      // 2. Update step: Compute new centroid positions
      const clusterCounts = new Int32Array(actualK);
      const newSumsX = new Float64Array(actualK);
      const newSumsY = new Float64Array(actualK);

      for (let i = 0; i < n; i++) {
        const c = labels[i];
        clusterCounts[c]++;
        newSumsX[c] += points[i].x;
        newSumsY[c] += points[i].y;
      }

      const nextCentroids = [];
      let maxShift = 0;

      for (let c = 0; c < actualK; c++) {
        if (clusterCounts[c] > 0) {
          const newX = newSumsX[c] / clusterCounts[c];
          const newY = newSumsY[c] / clusterCounts[c];
          const shift = dist({ x: newX, y: newY }, centroids[c]);
          if (shift > maxShift) maxShift = shift;
          nextCentroids.push({ x: newX, y: newY });
        } else {
          // Handle empty cluster: reseed at the point farthest from its assigned centroid
          let maxD = -1;
          let farthestPointIdx = 0;
          for (let i = 0; i < n; i++) {
            const currentC = labels[i];
            const d = distSq(points[i], centroids[currentC]);
            if (d > maxD) {
              maxD = d;
              farthestPointIdx = i;
            }
          }
          nextCentroids.push({
            x: points[farthestPointIdx].x,
            y: points[farthestPointIdx].y
          });
          maxShift = Infinity; // Force another iteration
        }
      }

      centroids = nextCentroids;
      history.push(centroids.map(c => ({ x: c.x, y: c.y })));

      if (maxShift < tolerance) {
        converged = true;
      }
    }

    // Final inertia calculation (Within-Cluster Sum of Squares)
    let inertia = 0;
    for (let i = 0; i < n; i++) {
      inertia += distSq(points[i], centroids[labels[i]]);
    }

    const runtimeMs = performance.now() - startTime;

    return {
      labels: Array.from(labels),
      centroids,
      iterations: iteration,
      converged,
      inertia,
      runtimeMs,
      history
    };
  }

  /**
   * Generate step-by-step execution trace of K-Means clustering for interactive educational exploration.
   * Every snapshot represents an authentic computational state.
   *
   * @param {Array<{x: number, y: number}>} points Point array
   * @param {number} k Number of clusters
   * @param {Object} options Configuration options
   * @returns {{steps: Array<Object>, finalResult: Object}}
   */
  function generateKMeansTrace(points, k, options = {}) {
    const startTime = performance.now();
    const {
      maxIterations = 100,
      tolerance = 1e-5,
      seed = 42,
      initMethod = 'kmeans++'
    } = options;

    const n = points.length;
    if (n === 0) {
      return {
        steps: [{
          stepIndex: 0,
          type: 'init',
          iteration: 0,
          centroids: [],
          previousCentroids: [],
          labels: [],
          inertia: 0,
          maxShift: 0,
          converged: true,
          clusterCounts: [],
          explanation: 'Empty dataset: No points to cluster.'
        }],
        finalResult: {
          labels: [],
          centroids: [],
          iterations: 0,
          converged: true,
          inertia: 0,
          runtimeMs: 0
        }
      };
    }

    const actualK = Math.min(Math.max(1, Math.floor(k)), n);
    const rng = createPRNG(seed);

    let centroids;
    if (initMethod === 'kmeans++') {
      centroids = initKMeansPlusPlus(points, actualK, rng);
    } else {
      const indices = Array.from({ length: n }, (_, i) => i);
      for (let i = 0; i < actualK; i++) {
        const j = i + Math.floor(rng() * (n - i));
        const temp = indices[i];
        indices[i] = indices[j];
        indices[j] = temp;
      }
      centroids = indices.slice(0, actualK).map(idx => ({ x: points[idx].x, y: points[idx].y }));
    }

    const labels = new Int32Array(n).fill(-1);
    const steps = [];

    // Step 0: Initialization snapshot
    steps.push({
      stepIndex: 0,
      type: 'init',
      iteration: 0,
      centroids: centroids.map(c => ({ x: c.x, y: c.y })),
      previousCentroids: [],
      labels: Array.from(labels),
      inertia: null,
      maxShift: null,
      converged: false,
      clusterCounts: new Array(actualK).fill(0),
      explanation: `Step 1 — K-Means++ Initialization: Placed ${actualK} initial centroids using seeded probabilistic distance sampling. Observations are unassigned.`
    });

    let converged = false;
    let iteration = 0;

    while (iteration < maxIterations && !converged) {
      iteration++;

      // 1. Assignment step: Assign each point to nearest centroid
      for (let i = 0; i < n; i++) {
        let bestDist = Infinity;
        let bestCluster = 0;
        for (let c = 0; c < actualK; c++) {
          const d = distSq(points[i], centroids[c]);
          if (d < bestDist) {
            bestDist = d;
            bestCluster = c;
          }
        }
        labels[i] = bestCluster;
      }

      // Compute inertia for current assignments & current centroids
      let currentInertia = 0;
      for (let i = 0; i < n; i++) {
        currentInertia += distSq(points[i], centroids[labels[i]]);
      }

      // Count points per cluster
      const counts = new Array(actualK).fill(0);
      for (let i = 0; i < n; i++) {
        counts[labels[i]]++;
      }

      steps.push({
        stepIndex: steps.length,
        type: 'assignment',
        iteration,
        centroids: centroids.map(c => ({ x: c.x, y: c.y })),
        previousCentroids: [],
        labels: Array.from(labels),
        inertia: currentInertia,
        maxShift: null,
        converged: false,
        clusterCounts: counts,
        explanation: `Iteration ${iteration} — Assignment: Assigned all ${n} points to their nearest centroid in Euclidean space. Current inertia (WCSS) = ${currentInertia.toFixed(3)}.`
      });

      // 2. Update step: Compute new centroid positions
      const clusterCounts = new Int32Array(actualK);
      const newSumsX = new Float64Array(actualK);
      const newSumsY = new Float64Array(actualK);

      for (let i = 0; i < n; i++) {
        const c = labels[i];
        clusterCounts[c]++;
        newSumsX[c] += points[i].x;
        newSumsY[c] += points[i].y;
      }

      const prevCentroidsCopy = centroids.map(c => ({ x: c.x, y: c.y }));
      const nextCentroids = [];
      let maxShift = 0;

      for (let c = 0; c < actualK; c++) {
        if (clusterCounts[c] > 0) {
          const newX = newSumsX[c] / clusterCounts[c];
          const newY = newSumsY[c] / clusterCounts[c];
          const shift = dist({ x: newX, y: newY }, centroids[c]);
          if (shift > maxShift) maxShift = shift;
          nextCentroids.push({ x: newX, y: newY });
        } else {
          // Empty cluster handling: reseed at farthest point
          let maxD = -1;
          let farthestPointIdx = 0;
          for (let i = 0; i < n; i++) {
            const currentC = labels[i];
            const d = distSq(points[i], centroids[currentC]);
            if (d > maxD) {
              maxD = d;
              farthestPointIdx = i;
            }
          }
          nextCentroids.push({
            x: points[farthestPointIdx].x,
            y: points[farthestPointIdx].y
          });
          maxShift = Infinity;
        }
      }

      centroids = nextCentroids;

      // Recompute inertia with new centroid positions
      let updatedInertia = 0;
      for (let i = 0; i < n; i++) {
        updatedInertia += distSq(points[i], centroids[labels[i]]);
      }

      if (maxShift < tolerance) {
        converged = true;
      }

      steps.push({
        stepIndex: steps.length,
        type: 'update',
        iteration,
        centroids: centroids.map(c => ({ x: c.x, y: c.y })),
        previousCentroids: prevCentroidsCopy,
        labels: Array.from(labels),
        inertia: updatedInertia,
        maxShift,
        converged,
        clusterCounts: counts,
        explanation: converged
          ? `Iteration ${iteration} — Centroid Update & Convergence: Centroids updated to cluster means. Shift (${maxShift.toFixed(5)}) is below tolerance (${tolerance}). Algorithm has converged!`
          : `Iteration ${iteration} — Centroid Update: Centroids relocated to arithmetic means of assigned observations (max shift: ${maxShift.toFixed(5)}). Continuing to next iteration.`
      });
    }

    const runtimeMs = performance.now() - startTime;

    return {
      steps,
      finalResult: {
        labels: Array.from(labels),
        centroids,
        iterations: iteration,
        converged,
        inertia: steps[steps.length - 1].inertia,
        runtimeMs
      }
    };
  }

  window.MSTKMeans.KMeans = {
    runKMeans,
    generateKMeansTrace,
    dist,
    distSq
  };
})(window);
