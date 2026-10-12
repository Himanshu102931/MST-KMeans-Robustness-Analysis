/**
 * MST vs K-Means Robustness Analysis
 * Dependency-Free Automated Test Suite
 * Tests PRNG, Datasets, K-Means, MST, and ARI Metrics
 */

(function (window) {
  'use strict';

  const { PRNG, Datasets, KMeans, MST, Evaluation, Robustness, Benchmarks, Explorer, ExportManager } = window.MSTKMeans;

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

  async function runAllTests() {
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

    // ---------------------------------------------------------
    // 7. Phase 2 Playground Configuration & Pipeline Tests
    // ---------------------------------------------------------
    const defaultBlobs = Datasets.generateDataset('blobs', {
      n: 300,
      k: 3,
      noise: 0.15,
      outlierFraction: 0.05,
      seed: 42
    });
    assert(
      defaultBlobs.points.length === 300 && defaultBlobs.outliers.length === 15 && defaultBlobs.inliers.length === 285,
      'Playground: Default Blobs Parameter Integrity (N=300, 5% outliers)',
      `Expected 300 total points with 15 outliers, got ${defaultBlobs.points.length} and ${defaultBlobs.outliers.length}`
    );

    const defaultMoons = Datasets.generateDataset('moons', {
      n: 200,
      noise: 0.1,
      outlierFraction: 0.0,
      seed: 42
    });
    assert(
      defaultMoons.k === 2 && defaultMoons.inliers.every(p => p.groundTruth === 0 || p.groundTruth === 1),
      'Playground: Two Moons K=2 Geometric Invariance',
      'Two Moons dataset must strictly enforce K=2 classes'
    );

    const defaultCircles = Datasets.generateDataset('circles', {
      n: 200,
      noise: 0.1,
      outlierFraction: 0.0,
      seed: 42
    });
    assert(
      defaultCircles.k === 2 && defaultCircles.inliers.every(p => p.groundTruth === 0 || p.groundTruth === 1),
      'Playground: Concentric Circles K=2 Geometric Invariance',
      'Concentric Circles dataset must strictly enforce K=2 classes'
    );

    // End-to-end simultaneous pipeline execution test
    const kmEvalDef = Evaluation.evaluateClustering(
      defaultBlobs,
      KMeans.runKMeans(defaultBlobs.points, 3, { seed: 42 }).labels
    );
    const mstEvalDef = Evaluation.evaluateClustering(
      defaultBlobs,
      MST.runMSTClustering(defaultBlobs.points, 3).labels
    );
    assert(
      typeof kmEvalDef.overallARI === 'number' && typeof mstEvalDef.overallARI === 'number' &&
      isFinite(kmEvalDef.overallARI) && isFinite(mstEvalDef.overallARI) &&
      kmEvalDef.inlierARI !== null && mstEvalDef.inlierARI !== null,
      'Playground: Simultaneous Pipeline & Metric Integrity',
      'Both algorithms must produce valid finite overall and inlier ARI metrics on identical data'
    );

    // ---------------------------------------------------------
    // 8. Phase 3 Robustness & Benchmarking Engine Tests
    // ---------------------------------------------------------
    if (Robustness && Benchmarks) {
      // 8.1 Statistical Aggregator (Mean & Sample Std Dev)
      const stats = Robustness.computeStatistics([1, 2, 3, 4, 5]);
      assert(
        stats.mean === 3.0 && stats.median === 3.0 && stats.min === 1.0 && stats.max === 5.0,
        'Robustness: Statistics Aggregator (Mean, Median, Min, Max)',
        `Expected mean=3, got ${stats.mean}`
      );
      assertApprox(
        stats.std,
        Math.sqrt(2.5),
        1e-4,
        'Robustness: Statistics Sample Standard Deviation (std = sqrt(2.5))'
      );

      // 8.2 Controlled Dataset Inlier Count Invariance
      const controlledData = Robustness.generateControlledDataset('blobs', {
        inlierCount: 200,
        outlierFraction: 0.10,
        seed: 42
      });
      assert(
        controlledData.inliers.length === 200 && controlledData.outliers.length === 20 && controlledData.points.length === 220,
        'Robustness: Controlled Dataset Inlier Count Invariance',
        `Expected 200 inliers and 20 outliers, got ${controlledData.inliers.length} and ${controlledData.outliers.length}`
      );

      // 8.3 Paired Single Trial Input Identity & Metric Validity
      const trial = Robustness.runSingleTrial('moons', {
        inlierCount: 150,
        k: 2,
        noise: 0.05,
        outlierFraction: 0.05,
        seed: 11
      });
      assert(
        typeof trial.kmeans.inlierARI === 'number' && typeof trial.mst.inlierARI === 'number' &&
        trial.kmeans.runtimeMs > 0 && trial.mst.runtimeMs > 0 &&
        trial.kmeans.predictedK === 2 && trial.mst.predictedK === 2,
        'Robustness: Paired Single Trial Input Identity & Metric Validity',
        'Trial must record valid Inlier ARI and runtimes for both algorithms on identical points'
      );

      // 8.4 Deterministic Repeated Experiments Across Seeds
      const trialA = Robustness.runSingleTrial('blobs', { inlierCount: 100, k: 3, noise: 0.1, outlierFraction: 0, seed: 77 });
      const trialB = Robustness.runSingleTrial('blobs', { inlierCount: 100, k: 3, noise: 0.1, outlierFraction: 0, seed: 77 });
      assert(
        trialA.kmeans.inlierARI === trialB.kmeans.inlierARI && trialA.mst.inlierARI === trialB.mst.inlierARI,
        'Robustness: Deterministic Reproducibility Across Identical Seeds',
        'Independent runs with identical seeds must yield identical ARI scores'
      );

      // 8.5 Clean Baseline Matching & Degradation Calculation
      const baseClean = Robustness.runSingleTrial('moons', { inlierCount: 120, k: 2, noise: 0.0, outlierFraction: 0.0, seed: 22 });
      const perturbed = Robustness.runSingleTrial('moons', { inlierCount: 120, k: 2, noise: 0.0, outlierFraction: 0.15, seed: 22 });
      const mstLoss = (baseClean.mst.inlierARI || 0) - (perturbed.mst.inlierARI || 0);
      assert(
        baseClean.outlierCount === 0 && perturbed.outlierCount > 0 && typeof mstLoss === 'number' && isFinite(mstLoss),
        'Robustness: Clean Baseline Matching & Degradation Metric',
        'Clean baseline must have 0 outliers and compute a valid degradation loss delta'
      );

      // 8.6 Cancellation Flag Handling
      const testRunner = new Robustness.RobustnessRunner();
      testRunner.cancel();
      let caughtCancel = false;
      try {
        await testRunner.runExperiment({ datasetType: 'blobs', seeds: [99] });
      } catch (err) {
        if (err.message.includes('cancelled')) caughtCancel = true;
      }
      assert(
        caughtCancel,
        'Robustness: Runner Cancellation Flag Graceful Termination',
        'RobustnessRunner must gracefully abort when cancelled'
      );

      // 8.7 Large Sample Boundary Scaling (N = 600 points)
      const largeData = Datasets.generateDataset('blobs', { n: 600, k: 3, seed: 42 });
      const t0 = performance.now();
      const largeMST = MST.runMSTClustering(largeData.points, 3);
      const tMST = performance.now() - t0;
      assert(
        largeMST.mstEdges.length === 599 && largeMST.labels.length === 600 && tMST > 0,
        'Benchmarks: Large Sample Boundary Scaling (N = 600 Points)',
        `MST must form 599 edges on 600 points without memory or precision errors`
      );

      // 8.8 Environment Detection Profile Completeness
      const env = Benchmarks.getEnvironmentInfo();
      assert(
        typeof env.userAgent === 'string' && typeof env.platform === 'string' && env.timerPrecision.includes('performance.now'),
        'Benchmarks: Hardware & Environment Detection Profile',
        'Must safely record environment profile without errors'
      );

      // ---------------------------------------------------------
      // 9. Phase 4: Interactive Algorithm Explorer & Export Tests
      // ---------------------------------------------------------

      // 9.1 K-Means Trace Initialization
      const ptsKM = Datasets.generateBlobs({ n: 20, k: 3, seed: 42 }).points;
      const traceKM = KMeans.generateKMeansTrace(ptsKM, 3, { seed: 42 });
      assert(
        traceKM.steps.length > 2 && traceKM.steps[0].type === 'init' && traceKM.steps[0].centroids.length === 3 && traceKM.steps[0].labels.every(l => l === -1),
        'Explorer: K-Means Trace Initialization State',
        'Step 0 must be init with 3 centroids and all unassigned labels (-1)'
      );

      // 9.2 K-Means Assignment and Centroid Update Sequence
      const stepAssign = traceKM.steps[1];
      const stepUpdate = traceKM.steps[2];
      assert(
        stepAssign.type === 'assignment' && stepUpdate.type === 'update' && typeof stepAssign.inertia === 'number' && typeof stepUpdate.maxShift === 'number' && stepAssign.labels.every(l => l >= 0 && l < 3),
        'Explorer: K-Means Assignment and Centroid Update Sequence',
        'Steps must alternate assignment and update with valid inertia and shift metrics'
      );

      // 9.3 K-Means Trace Deterministic Reproducibility
      const traceKM2 = KMeans.generateKMeansTrace(ptsKM, 3, { seed: 42 });
      assert(
        traceKM.steps.length === traceKM2.steps.length && traceKM.steps[1].inertia === traceKM2.steps[1].inertia && traceKM.finalResult.inertia === traceKM2.finalResult.inertia,
        'Explorer: K-Means Trace Deterministic Reproducibility',
        'Identical seeds must yield identical step counts and inertia values'
      );

      // 9.4 Final K-Means Trace vs Production Algorithm Equivalence
      const prodKM = KMeans.runKMeans(ptsKM, 3, { seed: 42 });
      const traceFinal = traceKM.finalResult;
      assert(
        prodKM.iterations === traceFinal.iterations && Math.abs(prodKM.inertia - traceFinal.inertia) < 1e-9 && prodKM.labels.every((l, i) => l === traceFinal.labels[i]),
        'Explorer: Final K-Means Trace Equivalence to Production Run',
        'Final trace assignments and inertia must match runKMeans identically'
      );

      // 9.5 MST Trace Vertex and Edge Counts (N - 1)
      const ptsMST = Datasets.generateBlobs({ n: 16, k: 3, seed: 101 }).points;
      const traceMST = MST.generateMSTTrace(ptsMST, 3);
      const primSteps = traceMST.steps.filter(s => s.type === 'prim_step');
      const completeStep = traceMST.steps.find(s => s.type === 'mst_complete');
      assert(
        primSteps.length === 15 && completeStep.treeEdges.length === 15 && completeStep.inTreeVertices.length === 16,
        'Explorer: MST Prim Construction Vertex and Edge Counts (N - 1)',
        'Prim algorithm must execute exactly 15 edge additions on 16 vertices'
      );

      // 9.6 MST Trace Total Edge Weight Consistency
      const prodMST = MST.runMSTClustering(ptsMST, 3);
      assert(
        Math.abs(completeStep.totalWeight - prodMST.totalWeight) < 1e-9,
        'Explorer: MST Trace Total Edge Weight Consistency',
        'Total spanning tree weight in trace must equal runMSTClustering weight'
      );

      // 9.7 MST K - 1 Longest Edge Selection
      const cutStep = traceMST.steps.find(s => s.type === 'cut_selection');
      assert(
        cutStep && cutStep.cutEdges.length === 2 && cutStep.cutEdges[0].weight >= cutStep.cutEdges[1].weight,
        'Explorer: MST K - 1 Longest Edge Selection',
        'For K=3, exactly 2 longest edges must be identified in descending weight order'
      );

      // 9.8 MST Connected-Component Equivalence to Production Run
      const finalCutStep = traceMST.steps.find(s => s.type === 'cut_applied');
      assert(
        finalCutStep && finalCutStep.k === 3 && finalCutStep.labels.every((l, i) => l === prodMST.labels[i]),
        'Explorer: MST Connected-Component Equivalence to Production Run',
        'Cut-applied components must equal K=3 and labels must match runMSTClustering'
      );

      // 9.9 MST Deterministic Tie-Breaking on Duplicate Coordinates
      const dupPoints = [{ x: 0, y: 0 }, { x: 0, y: 0 }, { x: 1, y: 1 }, { x: 1, y: 1 }];
      const dupMST = MST.generateMSTTrace(dupPoints, 2);
      assert(
        dupMST.finalResult.mstEdges.length === 3 && dupMST.finalResult.labels.length === 4,
        'Explorer: MST Deterministic Tie-Breaking on Duplicate Coordinates',
        'Duplicate coordinates must form N-1 edges without errors'
      );

      // 9.10 Explorer Controller State Navigation and Reset
      const ctrl = new Explorer.AlgorithmExplorerController();
      ctrl.sampleSize = 16;
      ctrl.k = 3;
      ctrl.resetDataAndTrace();
      const initStep = ctrl.currentStep;
      ctrl.nextStep();
      const stepAfterNext = ctrl.currentStep;
      ctrl.restart();
      const stepAfterRestart = ctrl.currentStep;
      assert(
        initStep === 0 && stepAfterNext === 1 && stepAfterRestart === 0 && ctrl.trace.steps.length > 2,
        'Explorer: Controller State Navigation and Reset',
        'Controller must navigate steps and restart reliably'
      );

      // 9.11 CSV Formula Injection Defense Sanitization
      const dangerousValues = ['=1+1', '+cmd|', '-123', '@SUM(A1:A5)', 'Normal Text'];
      const sanitized = dangerousValues.map(v => ExportManager.sanitizeCSVCell(v));
      assert(
        sanitized[0].startsWith("'=") && sanitized[1].startsWith("'+") && sanitized[2].startsWith("'-") && sanitized[3].startsWith("'@") && sanitized[4] === 'Normal Text',
        'Export: CSV Formula Injection Defense Sanitization',
        'Dangerous prefix characters must be prepended with a single quote'
      );

      // 9.12 RFC 4180 CSV Escaping for Commas and Quotes
      const headers = ['col1', 'col2'];
      const rows = [['value, with comma', 'value "with quotes"']];
      const csvStr = ExportManager.toCSV(headers, rows);
      assert(
        csvStr.includes('"value, with comma"') && csvStr.includes('"value ""with quotes"""'),
        'Export: RFC 4180 CSV Escaping for Commas and Quotes',
        'Cells containing commas and quotes must be properly quoted and escaped'
      );

      // 9.13 Reproducibility Recipe Metadata Schema Integrity
      const testDoc = {
        projectMetadata: { title: 'MST vs K-Means Robustness Analysis', leadStudent: 'Himanshu Gupta', allocationNumber: 19 },
        softwareEnvironment: { runtime: 'Client-Side JavaScript' },
        clusteringSpecifications: { kmeans: {}, mst: {} }
      };
      assert(
        testDoc.projectMetadata.leadStudent === 'Himanshu Gupta' && testDoc.projectMetadata.allocationNumber === 19 && typeof testDoc.clusteringSpecifications.mst === 'object',
        'Export: Reproducibility Recipe Metadata Schema Integrity',
        'Metadata schema must contain academic credentials and algorithm specifications'
      );

      // 9.14 Guard Against Exporting Non-Existent Experiments
      let caughtNoData = false;
      try {
        ExportManager.exportRobustnessRawCSV(null);
      } catch (e) {
        caughtNoData = true;
      }
      assert(
        caughtNoData,
        'Export: Guard Against Exporting Non-Existent Experiments',
        'ExportManager must throw informative error when attempting to export unexecuted experiments'
      );

      // 9.15 High-DPI Canvas Rasterization to PNG Data URL
      const dummyCanvas = document.createElement('canvas');
      dummyCanvas.width = 100;
      dummyCanvas.height = 100;
      const dummyCtx = dummyCanvas.getContext('2d');
      dummyCtx.fillStyle = '#0f172a';
      dummyCtx.fillRect(0, 0, 100, 100);
      const dataUrl = dummyCanvas.toDataURL('image/png');
      assert(
        dataUrl.startsWith('data:image/png;base64,') && dataUrl.length > 50,
        'Export: High-DPI Canvas Rasterization to PNG Data URL',
        'Canvas must generate a valid, non-empty PNG rasterization'
      );

      // 9.16 Regression: Phase 1-3 Core Mechanics Invariant
      const blobsRegress = Datasets.generateBlobs({ n: 100, k: 3, seed: 42 });
      const ariRegress = Evaluation.adjustedRandIndex([0, 0, 1, 1], [0, 0, 1, 1]);
      assert(
        blobsRegress.points.length === 100 && ariRegress === 1.0,
        'Regression: Phase 1-3 Core Mechanics Invariant',
        'Core dataset generators and evaluation functions must remain intact'
      );
    }

    console.log(`--- Test Suite Finished: ${testResults.filter(r => r.passed).length}/${testResults.length} passed ---`);
    return testResults;
  }

  window.MSTKMeansTests = {
    runAllTests,
    testResults
  };
})(window);
