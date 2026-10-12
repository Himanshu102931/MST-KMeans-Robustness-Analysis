/**
 * MST vs K-Means Robustness Analysis
 * Module: Quantitative Evaluation Metrics (Adjusted Rand Index & Inlier Metrics)
 * Pure Vanilla JavaScript - No dependencies
 */

(function (window) {
  'use strict';

  window.MSTKMeans = window.MSTKMeans || {};

  /**
   * Combination formula: n choose 2 = n * (n - 1) / 2
   */
  function comb2(n) {
    if (n < 2) return 0;
    return (n * (n - 1)) / 2;
  }

  /**
   * Compute Adjusted Rand Index (Hubert & Arabie, 1985)
   * Measures agreement between two clusterings, corrected for chance.
   * Range: [-1, 1], where 1.0 = identical clusterings, 0.0 = expected random chance.
   * NOTE: ARI is NOT classification accuracy. It does not assume 1:1 label identity.
   *
   * @param {Array<number>} labelsTrue Ground truth labels
   * @param {Array<number>} labelsPred Predicted cluster labels
   * @returns {number} Adjusted Rand Index
   */
  function adjustedRandIndex(labelsTrue, labelsPred) {
    if (!labelsTrue || !labelsPred) return 0;
    const n = labelsTrue.length;
    if (n !== labelsPred.length) {
      throw new Error('Label arrays must have identical length');
    }
    if (n < 2) return 1.0;

    // 1. Build contingency table
    // Map arbitrary labels to contiguous 0..R-1 and 0..C-1
    const trueMap = new Map();
    const predMap = new Map();

    for (let i = 0; i < n; i++) {
      const t = labelsTrue[i];
      const p = labelsPred[i];
      if (!trueMap.has(t)) trueMap.set(t, trueMap.size);
      if (!predMap.has(p)) predMap.set(p, predMap.size);
    }

    const numRows = trueMap.size;
    const numCols = predMap.size;

    // Special case: single cluster vs single cluster
    if (numRows === 1 && numCols === 1) return 1.0;

    // 2D contingency matrix initialized to 0
    const contingency = [];
    for (let r = 0; r < numRows; r++) {
      contingency.push(new Int32Array(numCols));
    }

    const rowSums = new Int32Array(numRows);
    const colSums = new Int32Array(numCols);

    for (let i = 0; i < n; i++) {
      const r = trueMap.get(labelsTrue[i]);
      const c = predMap.get(labelsPred[i]);
      contingency[r][c]++;
      rowSums[r]++;
      colSums[c]++;
    }

    // 2. Sum combinations of cell values
    let sumCombNij = 0;
    for (let r = 0; r < numRows; r++) {
      for (let c = 0; c < numCols; c++) {
        sumCombNij += comb2(contingency[r][c]);
      }
    }

    // 3. Sum combinations of row and column margins
    let sumCombA = 0;
    for (let r = 0; r < numRows; r++) {
      sumCombA += comb2(rowSums[r]);
    }

    let sumCombB = 0;
    for (let c = 0; c < numCols; c++) {
      sumCombB += comb2(colSums[c]);
    }

    const totalComb = comb2(n);
    if (totalComb === 0) return 1.0;

    const expectedIndex = (sumCombA * sumCombB) / totalComb;
    const maxIndex = (sumCombA + sumCombB) / 2.0;
    const denominator = maxIndex - expectedIndex;

    // Edge cases: denominator near zero
    if (Math.abs(denominator) < 1e-12) {
      return sumCombNij === maxIndex ? 1.0 : 0.0;
    }

    const ari = (sumCombNij - expectedIndex) / denominator;
    // Clamp to theoretically valid range [-1.0, 1.0] to guard against floating-point epsilon
    return Math.max(-1.0, Math.min(1.0, ari));
  }

  /**
   * Compute Inlier ARI: Evaluates clustering exclusively on the original synthetic inliers.
   * Crucial for robustness analysis: determines if the manifold shape was properly clustered
   * regardless of how peripheral noise or injected outliers were handled.
   *
   * @param {Array<number>} labelsTrue Ground truth labels
   * @param {Array<number>} labelsPred Predicted cluster labels
   * @param {Array<boolean>} isOutlier Array of boolean flags indicating outlier points
   * @returns {number|null} Inlier Adjusted Rand Index or null if no inliers
   */
  function computeInlierARI(labelsTrue, labelsPred, isOutlier) {
    if (!labelsTrue || !labelsPred || !isOutlier) return null;
    const n = labelsTrue.length;
    const filteredTrue = [];
    const filteredPred = [];

    for (let i = 0; i < n; i++) {
      if (!isOutlier[i]) {
        filteredTrue.push(labelsTrue[i]);
        filteredPred.push(labelsPred[i]);
      }
    }

    if (filteredTrue.length < 2) return null;
    return adjustedRandIndex(filteredTrue, filteredPred);
  }

  /**
   * Full evaluation summary package for a clustering experiment
   */
  function evaluateClustering(dataset, predictedLabels) {
    const trueLabels = dataset.points.map(p => p.groundTruth);
    const isOutlier = dataset.points.map(p => !!p.isOutlier);

    const overallARI = adjustedRandIndex(trueLabels, predictedLabels);
    const inlierARI = computeInlierARI(trueLabels, predictedLabels, isOutlier);

    return {
      n: dataset.points.length,
      inlierCount: dataset.inliers.length,
      outlierCount: dataset.outliers.length,
      overallARI,
      inlierARI,
      overallARIPercent: (overallARI * 100).toFixed(2) + '%',
      inlierARIPercent: inlierARI !== null ? (inlierARI * 100).toFixed(2) + '%' : 'N/A'
    };
  }

  window.MSTKMeans.Evaluation = {
    comb2,
    adjustedRandIndex,
    computeInlierARI,
    evaluateClustering
  };
})(window);
