/**
 * MST vs K-Means Robustness Analysis
 * Module: Robustness Experiment Engine
 * Executes controlled noise and outlier sweeps across deterministic seeds
 * Pure Vanilla JavaScript - No dependencies
 */

(function (window) {
  'use strict';

  window.MSTKMeans = window.MSTKMeans || {};
  const { Datasets, KMeans, MST, Evaluation } = window.MSTKMeans;

  /**
   * Helper to yield to browser event loop so UI and progress bars can update
   */
  function yieldToEventLoop() {
    return new Promise(resolve => setTimeout(resolve, 0));
  }

  /**
   * Compute mean and sample standard deviation of an array of numbers
   */
  function computeStatistics(values) {
    if (!values || values.length === 0) {
      return { mean: 0, std: 0, median: 0, min: 0, max: 0, count: 0 };
    }
    const n = values.length;
    const sum = values.reduce((acc, v) => acc + v, 0);
    const mean = sum / n;

    let variance = 0;
    if (n > 1) {
      const sumSqDiff = values.reduce((acc, v) => acc + Math.pow(v - mean, 2), 0);
      variance = sumSqDiff / (n - 1);
    }
    const std = Math.sqrt(variance);

    const sorted = [...values].sort((a, b) => a - b);
    const mid = Math.floor(n / 2);
    const median = (n % 2 !== 0) ? sorted[mid] : (sorted[mid - 1] + sorted[mid]) / 2;

    return {
      mean,
      std,
      median,
      min: sorted[0],
      max: sorted[n - 1],
      count: n
    };
  }

  /**
   * Generate an exact clean baseline dataset and its perturbed counterpart
   * Ensures the same underlying inlier points are shared across perturbation levels for a given seed.
   *
   * @param {string} datasetType 'blobs' | 'moons' | 'circles'
   * @param {Object} options
   * @param {number} options.inlierCount Number of inliers (e.g. 300)
   * @param {number} options.k Target cluster count
   * @param {number} options.noise Gaussian noise level
   * @param {number} options.outlierFraction Outlier fraction (0.0 to 0.3)
   * @param {number} options.seed PRNG seed
   */
  function generateControlledDataset(datasetType, options) {
    const { inlierCount = 300, k = 3, noise = 0.05, outlierFraction = 0.0, seed = 42 } = options;

    // Outlier count measured relative to inlier count to preserve exact inlier sample size
    const outlierCount = Math.round(inlierCount * outlierFraction);
    const totalN = inlierCount + outlierCount;

    // Actual fraction of total points passed to the generator
    const totalOutlierFraction = totalN > 0 ? (outlierCount / totalN) : 0;

    return Datasets.generateDataset(datasetType, {
      n: totalN,
      k,
      noise,
      outlierFraction: totalOutlierFraction,
      seed
    });
  }

  /**
   * Run a single paired experiment trial on identical generated data
   * Evaluates both K-Means and MST on exact same coordinates.
   */
  function runSingleTrial(datasetType, params) {
    const { inlierCount = 300, k = 3, noise = 0.05, outlierFraction = 0.0, seed = 42 } = params;
    const actualK = (datasetType === 'moons' || datasetType === 'circles') ? 2 : k;

    // 1. Generate data
    const dataset = generateControlledDataset(datasetType, {
      inlierCount,
      k: actualK,
      noise,
      outlierFraction,
      seed
    });

    // 2. Execute K-Means
    const kmStart = performance.now();
    const kmResult = KMeans.runKMeans(dataset.points, actualK, { seed, initMethod: 'kmeans++' });
    const kmRuntime = performance.now() - kmStart;
    const kmEval = Evaluation.evaluateClustering(dataset, kmResult.labels);

    // 3. Execute MST Clustering
    const mstStart = performance.now();
    const mstResult = MST.runMSTClustering(dataset.points, actualK);
    const mstRuntime = performance.now() - mstStart;
    const mstEval = Evaluation.evaluateClustering(dataset, mstResult.labels);

    return {
      datasetType,
      inlierCount: dataset.inliers.length,
      outlierCount: dataset.outliers.length,
      totalCount: dataset.points.length,
      k: actualK,
      noise,
      outlierFraction,
      seed,
      kmeans: {
        inlierARI: kmEval.inlierARI,
        overallARI: kmEval.overallARI,
        runtimeMs: kmRuntime,
        iterations: kmResult.iterations,
        converged: kmResult.converged,
        inertia: kmResult.inertia,
        predictedK: kmResult.centroids.length
      },
      mst: {
        inlierARI: mstEval.inlierARI,
        overallARI: mstEval.overallARI,
        runtimeMs: mstRuntime,
        cutsCount: mstResult.cutEdges.length,
        totalWeight: mstResult.totalWeight,
        predictedK: mstResult.k
      }
    };
  }

  /**
   * Robustness Experiment Runner Class
   */
  class RobustnessRunner {
    constructor() {
      this.isCancelled = false;
      this.isRunning = false;
      this.lastResults = null;
    }

    cancel() {
      this.isCancelled = true;
    }

    /**
     * Run full controlled robustness experiments:
     * - Generates matched clean baselines per seed (noise=0.00, outliers=0%)
     * - Executes parameter sweeps (noise sweep, outlier sweep)
     * - Calculates per-seed degradation: ΔARI = ARI_baseline - ARI_perturbed
     * - Aggregates means and standard deviations across seeds
     *
     * @param {Object} config
     * @param {string} [config.datasetType='blobs']
     * @param {number} [config.inlierCount=300]
     * @param {number} [config.k=3]
     * @param {Array<number>} [config.noiseLevels=[0.00, 0.05, 0.10, 0.20]]
     * @param {Array<number>} [config.outlierFractions=[0.00, 0.05, 0.10, 0.20]]
     * @param {Array<number>} [config.seeds=[11, 22, 33]]
     * @param {string} [config.sweepType='both'] 'noise' | 'outliers' | 'both'
     * @param {Function} [onProgress] callback: (progressFraction, statusText) => void
     * @returns {Promise<Object>} Aggregated robustness experiment results
     */
    async runExperiment(config = {}, onProgress = null) {
      const {
        datasetType = 'blobs',
        inlierCount = 300,
        k = (datasetType === 'moons' || datasetType === 'circles') ? 2 : 3,
        noiseLevels = [0.00, 0.05, 0.10, 0.20],
        outlierFractions = [0.00, 0.05, 0.10, 0.20],
        seeds = [11, 22, 33],
        sweepType = 'both',
        fixedNoiseForOutliers = 0.00
      } = config;

      if (this.isCancelled) {
        throw new Error('Experiment cancelled by user');
      }
      this.isRunning = true;

      const rawNoiseTrials = [];
      const rawOutlierTrials = [];
      const baselinesBySeed = new Map();

      // Determine total trials for progress calculation
      const doNoise = sweepType === 'noise' || sweepType === 'both';
      const doOutliers = sweepType === 'outliers' || sweepType === 'both';
      const totalSteps = seeds.length + (doNoise ? noiseLevels.length * seeds.length : 0) + (doOutliers ? outlierFractions.length * seeds.length : 0);
      let completedSteps = 0;

      const notify = async (msg) => {
        if (onProgress) {
          const frac = Math.min(1.0, completedSteps / Math.max(1, totalSteps));
          onProgress(frac, msg);
        }
        await yieldToEventLoop();
      };

      try {
        // Step 1: Compute Matched Clean Baselines for each seed (noise = 0.00, outliers = 0.0)
        for (const seed of seeds) {
          if (this.isCancelled) throw new Error('Experiment cancelled by user');
          await notify(`Computing clean baseline for seed ${seed}...`);

          const baseline = runSingleTrial(datasetType, {
            inlierCount,
            k,
            noise: 0.00,
            outlierFraction: 0.0,
            seed
          });
          baselinesBySeed.set(seed, baseline);
          completedSteps++;
        }

        // Step 2: Noise Sweep (keeping outliers fixed at 0%)
        if (doNoise) {
          for (const noise of noiseLevels) {
            for (const seed of seeds) {
              if (this.isCancelled) throw new Error('Experiment cancelled by user');
              await notify(`Noise sweep: σ = ${noise.toFixed(2)}, seed = ${seed}...`);

              let trial;
              if (noise === 0.00 && baselinesBySeed.has(seed)) {
                trial = baselinesBySeed.get(seed);
              } else {
                trial = runSingleTrial(datasetType, {
                  inlierCount,
                  k,
                  noise,
                  outlierFraction: 0.0,
                  seed
                });
              }

              // Calculate matched degradation relative to this seed's clean baseline
              const baseline = baselinesBySeed.get(seed);
              const kmDegradation = (baseline.kmeans.inlierARI || 0) - (trial.kmeans.inlierARI || 0);
              const mstDegradation = (baseline.mst.inlierARI || 0) - (trial.mst.inlierARI || 0);

              rawNoiseTrials.push({
                ...trial,
                baseline,
                kmDegradation: Math.max(0, kmDegradation),
                mstDegradation: Math.max(0, mstDegradation),
                kmeansDegradation: Math.max(0, kmDegradation),
                sweepType: 'noise'
              });
              completedSteps++;
            }
          }
        }

        // Step 3: Outlier Sweep (keeping noise fixed at controlled baseline level, default 0.00)
        const fixedNoise = (config.fixedNoiseForOutliers !== undefined) ? config.fixedNoiseForOutliers : 0.00;
        if (doOutliers) {
          for (const outlierFraction of outlierFractions) {
            for (const seed of seeds) {
              if (this.isCancelled) throw new Error('Experiment cancelled by user');
              await notify(`Outlier sweep: ${(outlierFraction * 100).toFixed(0)}% outliers, seed = ${seed}...`);

              let trial;
              // If zero outlier contamination and zero noise, reuse the clean baseline for exact numerical identity
              if (outlierFraction === 0.0 && fixedNoise === 0.00 && baselinesBySeed.has(seed)) {
                trial = baselinesBySeed.get(seed);
              } else {
                trial = runSingleTrial(datasetType, {
                  inlierCount,
                  k,
                  noise: fixedNoise,
                  outlierFraction,
                  seed
                });
              }

              // Compare against the clean baseline (seed's baseline with 0 outliers)
              const baseline = baselinesBySeed.get(seed);
              const kmDegradation = (baseline.kmeans.inlierARI || 0) - (trial.kmeans.inlierARI || 0);
              const mstDegradation = (baseline.mst.inlierARI || 0) - (trial.mst.inlierARI || 0);

              rawOutlierTrials.push({
                ...trial,
                baseline,
                kmDegradation: Math.max(0, kmDegradation),
                mstDegradation: Math.max(0, mstDegradation),
                kmeansDegradation: Math.max(0, kmDegradation),
                sweepType: 'outliers'
              });
              completedSteps++;
            }
          }
        }

        await notify('Aggregating statistical metrics...');

        // Step 4: Statistical Aggregation
        const aggregatedNoise = doNoise ? this.aggregateSweep(rawNoiseTrials, 'noise', noiseLevels) : [];
        const aggregatedOutliers = doOutliers ? this.aggregateSweep(rawOutlierTrials, 'outlierFraction', outlierFractions) : [];

        this.lastResults = {
          config,
          datasetType,
          inlierCount,
          k,
          seeds,
          sweepType,
          baselines: Array.from(baselinesBySeed.values()),
          rawNoiseTrials,
          rawOutlierTrials,
          aggregatedNoise,
          aggregatedOutliers,
          // Aliases for export manager and backwards compatibility:
          rawRuns: [...rawNoiseTrials, ...rawOutlierTrials],
          noiseSweep: aggregatedNoise,
          outlierSweep: aggregatedOutliers,
          timestamp: new Date().toISOString()
        };

        return this.lastResults;
      } finally {
        this.isRunning = false;
      }
    }

    /**
     * Group trials by parameter step and compute mean & standard deviation across seeds
     */
    aggregateSweep(trials, paramKey, stepValues) {
      const aggregated = [];

      for (const stepVal of stepValues) {
        const matches = trials.filter(t => Math.abs(t[paramKey] - stepVal) < 1e-6);
        if (matches.length === 0) continue;

        const kmInlierARIs = matches.map(m => m.kmeans.inlierARI ?? 0);
        const mstInlierARIs = matches.map(m => m.mst.inlierARI ?? 0);
        const kmOverallARIs = matches.map(m => m.kmeans.overallARI ?? 0);
        const mstOverallARIs = matches.map(m => m.mst.overallARI ?? 0);

        const kmDegradations = matches.map(m => m.kmDegradation ?? 0);
        const mstDegradations = matches.map(m => m.mstDegradation ?? 0);

        const kmRuntimes = matches.map(m => m.kmeans.runtimeMs);
        const mstRuntimes = matches.map(m => m.mst.runtimeMs);

        aggregated.push({
          stepValue: stepVal,
          paramKey,
          sampleCount: matches.length,
          kmeans: {
            inlierARI: computeStatistics(kmInlierARIs),
            overallARI: computeStatistics(kmOverallARIs),
            degradation: computeStatistics(kmDegradations),
            runtimeMs: computeStatistics(kmRuntimes)
          },
          mst: {
            inlierARI: computeStatistics(mstInlierARIs),
            overallARI: computeStatistics(mstOverallARIs),
            degradation: computeStatistics(mstDegradations),
            runtimeMs: computeStatistics(mstRuntimes)
          }
        });
      }

      return aggregated;
    }
  }

  window.MSTKMeans.Robustness = {
    RobustnessRunner,
    computeStatistics,
    generateControlledDataset,
    runSingleTrial
  };
})(window);
