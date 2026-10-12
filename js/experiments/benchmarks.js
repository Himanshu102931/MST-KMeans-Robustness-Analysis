/**
 * MST vs K-Means Robustness Analysis
 * Module: Performance Benchmarking Engine
 * Empirically profiles execution time scaling across sample sizes N
 * Pure Vanilla JavaScript - No dependencies
 */

(function (window) {
  'use strict';

  window.MSTKMeans = window.MSTKMeans || {};
  const { Datasets, KMeans, MST } = window.MSTKMeans;
  const { computeStatistics } = window.MSTKMeans.Robustness;

  function yieldToEventLoop() {
    return new Promise(resolve => setTimeout(resolve, 0));
  }

  /**
   * Capture client environment and hardware capabilities safely
   */
  function getEnvironmentInfo() {
    return {
      userAgent: navigator.userAgent || 'Unknown Browser',
      platform: navigator.platform || 'Unknown OS',
      logicalCores: navigator.hardwareConcurrency || 'N/A',
      deviceMemory: navigator.deviceMemory ? `${navigator.deviceMemory} GB` : 'Unavailable',
      timerPrecision: 'performance.now() (~5µs resolution)'
    };
  }

  /**
   * Benchmark Runner Class
   */
  class BenchmarkRunner {
    constructor() {
      this.isCancelled = false;
      this.isRunning = false;
      this.lastResults = null;
    }

    cancel() {
      this.isCancelled = true;
    }

    /**
     * Run runtime scaling benchmark across dataset sizes
     *
     * @param {Object} config
     * @param {Array<number>} [config.sampleSizes=[100, 200, 400, 600]]
     * @param {number} [config.repetitions=5] Number of repeated timings per size
     * @param {string} [config.datasetType='blobs']
     * @param {number} [config.k=3]
     * @param {number} [config.seed=42]
     * @param {Function} [onProgress] callback: (fraction, statusText) => void
     * @returns {Promise<Object>}
     */
    async runBenchmark(config = {}, onProgress = null) {
      const {
        sampleSizes = [100, 200, 400, 600],
        repetitions = 5,
        datasetType = 'blobs',
        k = (datasetType === 'moons' || datasetType === 'circles') ? 2 : 3,
        seed = 42
      } = config;

      if (this.isCancelled) {
        throw new Error('Benchmark cancelled by user');
      }
      this.isRunning = true;

      const results = [];
      const totalSteps = sampleSizes.length * repetitions;
      let completedSteps = 0;

      const notify = async (msg) => {
        if (onProgress) {
          const frac = Math.min(1.0, completedSteps / Math.max(1, totalSteps));
          onProgress(frac, msg);
        }
        await yieldToEventLoop();
      };

      try {
        // 1. Warm-up Phase: run 1 throwaway execution per algorithm to trigger JIT optimization
        await notify('Warming up JIT compiler...');
        const warmupData = Datasets.generateDataset('blobs', { n: 100, k: 3, seed: 999 });
        KMeans.runKMeans(warmupData.points, 3, { seed: 999 });
        MST.runMSTClustering(warmupData.points, 3);
        await yieldToEventLoop();

        // 2. Timing Loop across sample sizes
        for (const n of sampleSizes) {
          const kmTimes = [];
          const mstTimes = [];

          for (let rep = 0; rep < repetitions; rep++) {
            if (this.isCancelled) throw new Error('Benchmark cancelled by user');

            await notify(`Benchmarking N = ${n} (trial ${rep + 1}/${repetitions})...`);

            // Generate dataset outside the timed region
            const trialSeed = (seed + rep * 17) % 100000;
            const dataset = Datasets.generateDataset(datasetType, {
              n,
              k,
              noise: 0.1,
              outlierFraction: 0.0,
              seed: trialSeed
            });

            // Isolate K-Means execution time
            const t0KM = performance.now();
            const kmRes = KMeans.runKMeans(dataset.points, k, { seed: trialSeed });
            const t1KM = performance.now();
            kmTimes.push(t1KM - t0KM);

            // Isolate MST execution time
            const t0MST = performance.now();
            const mstRes = MST.runMSTClustering(dataset.points, k);
            const t1MST = performance.now();
            mstTimes.push(t1MST - t0MST);

            completedSteps++;
            await yieldToEventLoop();
          }

          kmStats.trials = kmTimes;
          mstStats.trials = mstTimes;

          results.push({
            n,
            k,
            datasetType,
            repetitions,
            kmeans: kmStats,
            mst: mstStats,
            ratio: ratio,
            theoreticalRatio: (n * n) / (n * k * 10) // Theoretical O(N^2) vs O(N*K*I) scaling guideline
          });
        }

        const measurements = { kmeans: {}, mst: {} };
        results.forEach(r => {
          measurements.kmeans[r.n] = r.kmeans;
          measurements.mst[r.n] = r.mst;
        });

        this.lastResults = {
          config,
          datasetType,
          sampleSizes,
          repetitions,
          environment: getEnvironmentInfo(),
          results,
          measurements,
          timestamp: new Date().toISOString()
        };

        return this.lastResults;
      } finally {
        this.isRunning = false;
      }
    }
  }

  window.MSTKMeans.Benchmarks = {
    BenchmarkRunner,
    getEnvironmentInfo
  };
})(window);
