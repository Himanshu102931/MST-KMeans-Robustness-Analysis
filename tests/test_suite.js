/**
 * MST vs K-Means Robustness Analysis
 * Dependency-Free Automated Test Suite
 * Tests PRNG, Datasets, K-Means, MST, and ARI Metrics
 */

(function (window) {
  'use strict';

  const { PRNG, Datasets, KMeans, MST, Evaluation } = window.MSTKMeans;

  const testResults = [];

  function assert(condition, testName, message) {
    if (!condition) {
      const err = new Error(message || 'Assertion failed');
      testResults.push({ name: testName, passed: false, error: err.message });
      console.error(`❌ FAIL: ${testName} - ${err.message}`);
    } else {
      testResults.push({ name: testName, passed: true });
      console.log(`✅ PASS: ${testName}`);
    }
  }

  function assertApprox(actual, expected, tolerance = 1e-4, testName) {
    const diff = Math.abs(actual - expected);
    assert(
      diff <= tolerance,
      testName,
      `Expected ${expected} (±${tolerance}), got ${actual} (diff: ${diff})`
    );
  }

  function runAllTests() {
    testResults.length = 0;
    console.log('--- Starting MST vs K-Means Test Suite ---');

    // ---------------------------------------------------------
    // 1. PRNG Tests
    // ---------------------------------------------------------
    const rng1 = PRNG.createPRNG(12345);
    const rng2 = PRNG.createPRNG(12345);
    const v1 = [rng1(), rng1(), rng1()];
    const v2 = [rng2(), rng2(), rng2()];
    assert(
      v1[0] === v2[0] && v1[1] === v2[1] && v1[2] === v2[2],
      'PRNG: Mulberry32 Determinism',
      'Identical seeds must produce identical random float sequences'
    );

    const rngDiff = PRNG.createPRNG(99999);
    assert(
      rng1() !== rngDiff(),
      'PRNG: Different Seeds Divergence',
      'Different seeds must produce different sequences'
    );

    // Box-Muller empirical mean test (1000 samples)
    const rngNorm = PRNG.createPRNG(42);
    let sumNorm = 0;
    const nSamples = 1000;
    for (let i = 0; i < nSamples; i++) {
      sumNorm += PRNG.sampleGaussian(rngNorm, 0, 1);
    }
    const sampleMean = sumNorm / nSamples;
    assert(
      Math.abs(sampleMean) < 0.15,
      'PRNG: Box-Muller Mean ~ 0',
      `Empirical mean ${sampleMean.toFixed(4)} should be close to 0`
    );

    // ---------------------------------------------------------
    // 2. Synthetic Dataset Tests
    // ---------------------------------------------------------
    const blobs = Datasets.generateBlobs({ n: 200, k: 3, outlierFraction: 0.1, seed: 101 });
    assert(
      blobs.points.length === 200,
      'Datasets: Blobs Total Sample Size',
      `Expected 200 points, got ${blobs.points.length}`
    );
    assert(
      blobs.outliers.length === 20 && blobs.inliers.length === 180,
      'Datasets: Outlier Fraction Separation',
      `Expected 20 outliers and 180 inliers, got ${blobs.outliers.length} and ${blobs.inliers.length}`
    );
    assert(
      blobs.outliers.every(o => o.isOutlier === true && o.groundTruth === -1),
      'Datasets: Outlier Tagging Integrity',
      'Injected outliers must have isOutlier=true and groundTruth=-1'
    );

    const moons = Datasets.generateMoons({ n: 150, noise: 0.05, outlierFraction: 0, seed: 42 });
    assert(
      moons.points.length === 150 && moons.k === 2,
      'Datasets: Two Moons Generation',
      'Two moons should generate k=2 with correct count'
    );

    const circles = Datasets.generateCircles({ n: 150, noise: 0.05, outlierFraction: 0, seed: 42 });
    assert(
      circles.points.length === 150 && circles.k === 2,
      'Datasets: Concentric Circles Generation',
      'Circles should generate k=2 with correct count'
    );

    // ---------------------------------------------------------
    // 3. Adjusted Rand Index (ARI) Metric Tests
    // ---------------------------------------------------------
    // Identical partitions -> ARI = 1.0
    const ariIdentical = Evaluation.adjustedRandIndex([0, 0, 1, 1], [0, 0, 1, 1]);
    assertApprox(ariIdentical, 1.0, 1e-6, 'ARI: Identical Partitions = 1.0');

    // Permuted cluster indices -> ARI = 1.0 (permutation invariance)
    const ariPermuted = Evaluation.adjustedRandIndex([0, 0, 1, 1], [1, 1, 0, 0]);
    assertApprox(ariPermuted, 1.0, 1e-6, 'ARI: Permutation Invariance = 1.0');

    // Single cluster vs single cluster
    const ariSingle = Evaluation.adjustedRandIndex([0, 0, 0], [0, 0, 0]);
    assertApprox(ariSingle, 1.0, 1e-6, 'ARI: Single Cluster Edge Case = 1.0');

    // Known theoretical contingency test
    // U = [0, 0, 0, 1, 1, 1], V = [0, 0, 1, 1, 2, 2]
    // Hand-calculated ARI = (2 - 1.2) / (4.5 - 1.2) = 0.8 / 3.3 ≈ 0.242424...
    const uTest = [0, 0, 0, 1, 1, 1];
    const vTest = [0, 0, 1, 1, 2, 2];
    const ariKnown = Evaluation.adjustedRandIndex(uTest, vTest);
    assertApprox(ariKnown, 0.8 / 3.3, 1e-4, 'ARI: Mathematical Contingency Formula Verification');

    // Inlier ARI filtering test
    const trueLabelsWithOutliers = [0, 0, 1, 1, -1, -1];
    const predLabelsWithOutliers = [0, 0, 1, 1, 0, 1]; // Outliers clustered randomly
    const outlierFlags = [false, false, false, false, true, true];
    const inlierAri = Evaluation.computeInlierARI(trueLabelsWithOutliers, predLabelsWithOutliers, outlierFlags);
    assertApprox(inlierAri, 1.0, 1e-6, 'ARI: Inlier ARI ignores outliers');

    // ---------------------------------------------------------
    // 4. K-Means Algorithm Tests
    // ---------------------------------------------------------
    // Well-separated distinct blobs must cluster with ARI > 0.95
    const separatedBlobs = Datasets.generateBlobs({
      n: 150,
      k: 3,
      noise: 0.05,
      outlierFraction: 0,
      seed: 777
    });
    const kmResult = KMeans.runKMeans(separatedBlobs.points, 3, { seed: 42, initMethod: 'kmeans++' });
    const kmARI = Evaluation.adjustedRandIndex(
      separatedBlobs.points.map(p => p.groundTruth),
      kmResult.labels
    );
    assert(
      kmARI > 0.95,
      'K-Means: Separated Blobs Convergence (ARI > 0.95)',
      `K-Means ARI on separated blobs was ${kmARI.toFixed(4)}`
    );
    assert(
      kmResult.converged === true,
      'K-Means: Convergence Status Flag',
      'Algorithm should converge before maxIterations on well-separated data'
    );
    assert(
      kmResult.centroids.length === 3,
      'K-Means: Centroid Count Matches K',
      `Expected 3 centroids, got ${kmResult.centroids.length}`
    );
    assert(
      kmResult.inertia > 0 && isFinite(kmResult.inertia),
      'K-Means: Valid Finite Inertia',
      `Expected positive inertia, got ${kmResult.inertia}`
    );

    // K-Means reproducibility test
    const kmRun1 = KMeans.runKMeans(separatedBlobs.points, 3, { seed: 100 });
    const kmRun2 = KMeans.runKMeans(separatedBlobs.points, 3, { seed: 100 });
    let sameLabels = true;
    for (let i = 0; i < kmRun1.labels.length; i++) {
      if (kmRun1.labels[i] !== kmRun2.labels[i]) sameLabels = false;
    }
    assert(
      sameLabels,
      'K-Means: Seeded Determinism',
      'Identical seed and data must yield identical label partition'
    );

    // ---------------------------------------------------------
    // 5. Euclidean MST Clustering Tests
    // ---------------------------------------------------------
    const pts = [
      { x: 0, y: 0 },
      { x: 1, y: 0 },
      { x: 2, y: 0 },
      { x: 10, y: 0 },
      { x: 11, y: 0 }
    ];
    // MST of 5 points in line: edges should be (0,1), (1,2), (2,3), (3,4) with weights 1, 1, 8, 1
    const mstResultSmall = MST.runMSTClustering(pts, 2);
    assert(
      mstResultSmall.mstEdges.length === 4,
      'MST: Spanning Tree Property (N - 1 Edges)',
      `Expected 4 edges for 5 vertices, got ${mstResultSmall.mstEdges.length}`
    );
    assert(
      mstResultSmall.cutEdges.length === 1,
      'MST: Cuts K - 1 Longest Edges',
      `For K=2, expected 1 cut edge, got ${mstResultSmall.cutEdges.length}`
    );
    assertApprox(
      mstResultSmall.cutEdges[0].weight,
      8.0,
      1e-4,
      'MST: Correct Longest Edge Cut Identification (weight=8)'
    );
    // After cutting edge between x=2 and x=10, points [0,1,2] should have same label, [3,4] another label
    assert(
      mstResultSmall.labels[0] === mstResultSmall.labels[1] &&
      mstResultSmall.labels[1] === mstResultSmall.labels[2] &&
      mstResultSmall.labels[3] === mstResultSmall.labels[4] &&
      mstResultSmall.labels[0] !== mstResultSmall.labels[3],
      'MST: Connected Component Partitioning Integrity',
      'Components [0,1,2] and [3,4] must have distinct partition labels'
    );

    // Duplicate coordinates handling test
    const ptsWithDupes = [
      { x: 0, y: 0 },
      { x: 0, y: 0 }, // Duplicate!
      { x: 5, y: 5 },
      { x: 5, y: 5 }  // Duplicate!
    ];
    const mstDupes = MST.runMSTClustering(ptsWithDupes, 2);
    assert(
      mstDupes.k === 2 && mstDupes.labels.length === 4,
      'MST: Duplicate Coordinates Graceful Handling',
      'Should handle points with distance 0 without crashing'
    );

    // ---------------------------------------------------------
    // 6. Non-linear Manifold Separation (MST vs K-Means)
    // ---------------------------------------------------------
    // Concentric circles without noise: MST must achieve ARI > 0.95, while K-Means fails
    const cleanCircles = Datasets.generateCircles({ n: 120, noise: 0.02, outlierFraction: 0, seed: 42 });
    const mstCirclesResult = MST.runMSTClustering(cleanCircles.points, 2);
    const mstCirclesARI = Evaluation.adjustedRandIndex(
      cleanCircles.points.map(p => p.groundTruth),
      mstCirclesResult.labels
    );
    assert(
      mstCirclesARI > 0.95,
      'MST: Concentric Circles Manifold Separation (ARI > 0.95)',
      `MST should easily separate clean concentric rings, got ARI: ${mstCirclesARI.toFixed(4)}`
    );

    const kmCirclesResult = KMeans.runKMeans(cleanCircles.points, 2, { seed: 42 });
    const kmCirclesARI = Evaluation.adjustedRandIndex(
      cleanCircles.points.map(p => p.groundTruth),
      kmCirclesResult.labels
    );
    assert(
      kmCirclesARI < 0.25,
      'K-Means: Concentric Circles Inherent Geometric Failure (ARI < 0.25)',
      `K-Means cannot cluster non-convex concentric rings, got ARI: ${kmCirclesARI.toFixed(4)}`
    );

    console.log(`--- Test Suite Finished: ${testResults.filter(r => r.passed).length}/${testResults.length} passed ---`);
    return testResults;
  }

  window.MSTKMeansTests = {
    runAllTests,
    testResults
  };
})(window);
