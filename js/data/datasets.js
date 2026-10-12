/**
 * MST vs K-Means Robustness Analysis
 * Module: Synthetic Dataset Generation
 * Pure Vanilla JavaScript - No dependencies
 */

(function (window) {
  'use strict';

  window.MSTKMeans = window.MSTKMeans || {};
  const { createPRNG, sampleGaussian, sampleUniform } = window.MSTKMeans.PRNG;

  /**
   * Compute bounding box for an array of points
   * @param {Array<{x: number, y: number}>} points
   * @returns {{minX: number, maxX: number, minY: number, maxY: number}}
   */
  function computeBounds(points) {
    if (!points || points.length === 0) {
      return { minX: -1, maxX: 1, minY: -1, maxY: 1 };
    }
    let minX = Infinity, maxX = -Infinity;
    let minY = Infinity, maxY = -Infinity;
    for (let i = 0; i < points.length; i++) {
      const p = points[i];
      if (p.x < minX) minX = p.x;
      if (p.x > maxX) maxX = p.x;
      if (p.y < minY) minY = p.y;
      if (p.y > maxY) maxY = p.y;
    }
    return { minX, maxX, minY, maxY };
  }

  /**
   * Inject uniform outliers across padded bounding box
   * @param {Array<Object>} inliers Existing inlier points
   * @param {number} outlierCount Number of outliers to generate
   * @param {function(): number} rng PRNG
   * @returns {Array<Object>} Injected outlier points
   */
  function generateOutliers(inliers, outlierCount, rng) {
    if (outlierCount <= 0) return [];
    const bounds = computeBounds(inliers);
    const padX = (bounds.maxX - bounds.minX) * 0.15 || 0.5;
    const padY = (bounds.maxY - bounds.minY) * 0.15 || 0.5;
    const minX = bounds.minX - padX;
    const maxX = bounds.maxX + padX;
    const minY = bounds.minY - padY;
    const maxY = bounds.maxY + padY;

    const outliers = [];
    const startIndex = inliers.length;
    for (let i = 0; i < outlierCount; i++) {
      outliers.push({
        id: startIndex + i,
        x: sampleUniform(rng, minX, maxX),
        y: sampleUniform(rng, minY, maxY),
        groundTruth: -1, // outlier label
        isOutlier: true
      });
    }
    return outliers;
  }

  /**
   * Generate Gaussian Blobs
   * @param {Object} options
   * @param {number} options.n Total points (inliers + outliers)
   * @param {number} options.k Number of clusters (2 to 6)
   * @param {number} options.noise Standard deviation of cluster noise
   * @param {number} options.outlierFraction Fraction of points as outliers (0 to 0.4)
   * @param {number} options.seed Random seed
   */
  function generateBlobs(options = {}) {
    const {
      n = 300,
      k = 3,
      noise = 0.25,
      outlierFraction = 0.0,
      seed = 42
    } = options;

    const rng = createPRNG(seed);
    const outlierCount = Math.floor(n * outlierFraction);
    const inlierCount = Math.max(1, n - outlierCount);

    // Standard cluster centers spread evenly in a circle or fixed coordinates
    const centers = [];
    const radius = 2.5;
    for (let i = 0; i < k; i++) {
      const angle = (2 * Math.PI * i) / k;
      centers.push({
        x: radius * Math.cos(angle),
        y: radius * Math.sin(angle)
      });
    }

    const inliers = [];
    for (let i = 0; i < inlierCount; i++) {
      const clusterIdx = i % k;
      const center = centers[clusterIdx];
      const px = center.x + sampleGaussian(rng, 0, noise);
      const py = center.y + sampleGaussian(rng, 0, noise);
      inliers.push({
        id: i,
        x: px,
        y: py,
        groundTruth: clusterIdx,
        isOutlier: false
      });
    }

    const outliers = generateOutliers(inliers, outlierCount, rng);
    const allPoints = inliers.concat(outliers);

    return {
      name: 'Gaussian Blobs',
      type: 'blobs',
      points: allPoints,
      inliers,
      outliers,
      k,
      noise,
      outlierFraction,
      seed,
      bounds: computeBounds(allPoints)
    };
  }

  /**
   * Generate Two Moons Dataset
   * Non-linear interleaving crescent manifolds (k=2)
   */
  function generateMoons(options = {}) {
    const {
      n = 300,
      noise = 0.1,
      outlierFraction = 0.0,
      seed = 42
    } = options;

    const k = 2; // Fixed to 2 manifolds
    const rng = createPRNG(seed);
    const outlierCount = Math.floor(n * outlierFraction);
    const inlierCount = Math.max(1, n - outlierCount);

    const inliers = [];
    for (let i = 0; i < inlierCount; i++) {
      const clusterIdx = i % 2;
      // Angle parameter in [0, PI]
      const theta = sampleUniform(rng, 0, Math.PI);
      let px, py;
      if (clusterIdx === 0) {
        // Upper crescent
        px = Math.cos(theta);
        py = Math.sin(theta);
      } else {
        // Lower crescent offset
        px = 1.0 - Math.cos(theta);
        py = 1.0 - Math.sin(theta) - 0.5;
      }

      px += sampleGaussian(rng, 0, noise);
      py += sampleGaussian(rng, 0, noise);

      inliers.push({
        id: i,
        x: px,
        y: py,
        groundTruth: clusterIdx,
        isOutlier: false
      });
    }

    const outliers = generateOutliers(inliers, outlierCount, rng);
    const allPoints = inliers.concat(outliers);

    return {
      name: 'Two Moons',
      type: 'moons',
      points: allPoints,
      inliers,
      outliers,
      k,
      noise,
      outlierFraction,
      seed,
      bounds: computeBounds(allPoints)
    };
  }

  /**
   * Generate Concentric Circles Dataset
   * Non-linear nested rings (k=2)
   */
  function generateCircles(options = {}) {
    const {
      n = 300,
      noise = 0.08,
      outlierFraction = 0.0,
      seed = 42
    } = options;

    const k = 2; // Inner and Outer ring
    const rng = createPRNG(seed);
    const outlierCount = Math.floor(n * outlierFraction);
    const inlierCount = Math.max(1, n - outlierCount);

    const innerRadius = 0.8;
    const outerRadius = 2.2;

    const inliers = [];
    for (let i = 0; i < inlierCount; i++) {
      const clusterIdx = i % 2;
      const r = clusterIdx === 0 ? innerRadius : outerRadius;
      const theta = sampleUniform(rng, 0, 2 * Math.PI);

      let px = r * Math.cos(theta) + sampleGaussian(rng, 0, noise);
      let py = r * Math.sin(theta) + sampleGaussian(rng, 0, noise);

      inliers.push({
        id: i,
        x: px,
        y: py,
        groundTruth: clusterIdx,
        isOutlier: false
      });
    }

    const outliers = generateOutliers(inliers, outlierCount, rng);
    const allPoints = inliers.concat(outliers);

    return {
      name: 'Concentric Circles',
      type: 'circles',
      points: allPoints,
      inliers,
      outliers,
      k,
      noise,
      outlierFraction,
      seed,
      bounds: computeBounds(allPoints)
    };
  }

  /**
   * Main dataset generator dispatcher
   */
  function generateDataset(type, options) {
    switch (type) {
      case 'blobs':
        return generateBlobs(options);
      case 'moons':
        return generateMoons(options);
      case 'circles':
        return generateCircles(options);
      default:
        return generateBlobs(options);
    }
  }

  window.MSTKMeans.Datasets = {
    generateBlobs,
    generateMoons,
    generateCircles,
    generateDataset,
    computeBounds
  };
})(window);
