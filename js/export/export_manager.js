/**
 * MST vs K-Means Robustness Analysis
 * Module: Scientific Data & Figures Export Manager
 * Provides CSV, JSON, and PNG exports with spreadsheet formula injection protection
 * Pure Vanilla JavaScript - No dependencies
 */

(function (window) {
  'use strict';

  window.MSTKMeans = window.MSTKMeans || {};

  /**
   * Escape and sanitize a cell value for safe CSV output.
   * Defends against CSV/Spreadsheet Formula Injection (=, +, -, @).
   */
  function sanitizeCSVCell(value) {
    if (value === null || value === undefined) {
      return '';
    }

    let str = String(value);

    // Defense against CSV / Spreadsheet formula injection (CVE-2014-3524 / CWE-1236)
    // If cell begins with =, +, -, @, \t, or \r, prefix with a single quote unless it is a valid finite number
    const unsafeChars = ['=', '+', '-', '@', '\t', '\r'];
    const trimmed = str.trim();
    const isLegitNumber = trimmed !== '' && !isNaN(Number(trimmed)) && isFinite(Number(trimmed));

    if (!isLegitNumber && unsafeChars.some(char => str.startsWith(char))) {
      str = "'" + str;
    }

    // If cell contains commas, double quotes, or newlines, quote it and escape internal double quotes
    if (str.includes(',') || str.includes('"') || str.includes('\n') || str.includes('\r')) {
      return `"${str.replace(/"/g, '""')}"`;
    }

    return str;
  }

  /**
   * Convert header array and 2D row array into standard RFC 4180 CSV string
   */
  function toCSV(headers, rows) {
    const headerLine = headers.map(h => sanitizeCSVCell(h)).join(',');
    const rowLines = rows.map(row => row.map(cell => sanitizeCSVCell(cell)).join(','));
    return [headerLine, ...rowLines].join('\r\n');
  }

  /**
   * Trigger browser file download from Blob and safely revoke object URL
   */
  function downloadBlob(blob, filename) {
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    // Safely revoke object URL after browser handles download initiation
    setTimeout(() => {
      URL.revokeObjectURL(url);
    }, 1500);
  }

  /**
   * Trigger text file download (CSV or JSON)
   */
  function downloadText(content, filename, mimeType = 'text/csv;charset=utf-8') {
    const blob = new Blob([content], { type: mimeType });
    downloadBlob(blob, filename);
  }

  /**
   * Trigger Canvas export to high-resolution PNG
   */
  function exportCanvasAsPNG(canvas, filename = 'figure.png') {
    if (!canvas) {
      throw new Error('Canvas element not provided');
    }

    if (canvas.toBlob) {
      canvas.toBlob((blob) => {
        if (blob) {
          downloadBlob(blob, filename);
        } else {
          // Fallback to Data URL
          const dataUrl = canvas.toDataURL('image/png');
          const link = document.createElement('a');
          link.href = dataUrl;
          link.download = filename;
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
        }
      }, 'image/png');
    } else {
      const dataUrl = canvas.toDataURL('image/png');
      const link = document.createElement('a');
      link.href = dataUrl;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  }

  /**
   * A. Export Current Playground Dataset as CSV
   */
  function exportPlaygroundDatasetCSV(dataset, kmResult, mstResult) {
    if (!dataset || !dataset.points || !dataset.points.length) {
      throw new Error('No playground dataset available to export');
    }

    const headers = [
      'point_index',
      'x',
      'y',
      'ground_truth_label',
      'is_outlier',
      'kmeans_predicted_cluster',
      'mst_predicted_cluster'
    ];

    const kmLabels = (kmResult && kmResult.labels) || [];
    const mstLabels = (mstResult && mstResult.labels) || [];

    const rows = dataset.points.map((p, idx) => [
      idx,
      p.x.toFixed(6),
      p.y.toFixed(6),
      p.groundTruth !== undefined ? p.groundTruth : -1,
      p.isOutlier ? 1 : 0,
      kmLabels[idx] !== undefined ? kmLabels[idx] : -1,
      mstLabels[idx] !== undefined ? mstLabels[idx] : -1
    ]);

    const csv = toCSV(headers, rows);
    const filename = `mst_kmeans_dataset_${dataset.type || 'playground'}_n${dataset.points.length}.csv`;
    downloadText(csv, filename);
    return { filename, rowCount: rows.length };
  }

  /**
   * B. Export Current Playground Metrics as CSV
   */
  function exportPlaygroundMetricsCSV(session) {
    if (!session || !session.dataset) {
      throw new Error('No playground session metrics available to export');
    }

    const headers = [
      'dataset',
      'sample_count',
      'k',
      'noise',
      'outlier_fraction',
      'seed',
      'algorithm_name',
      'inlier_ari',
      'overall_ari',
      'runtime_ms',
      'algorithm_specific_metric',
      'convergence_or_components'
    ];

    const rows = [];

    // K-Means row
    if (session.kmeans) {
      rows.push([
        session.dataset.type,
        session.dataset.points.length,
        session.params.clusters,
        session.params.noise,
        session.params.outlierFraction,
        session.params.seed,
        'K-Means (Lloyd)',
        session.kmeansEval ? (session.kmeansEval.inlierARI !== null ? session.kmeansEval.inlierARI.toFixed(6) : 'N/A') : '',
        session.kmeansEval ? session.kmeansEval.overallARI.toFixed(6) : '',
        session.kmeans.runtimeMs.toFixed(3),
        `Inertia WCSS = ${session.kmeans.inertia.toFixed(4)}`,
        session.kmeans.converged ? `Converged in ${session.kmeans.iterations} iters` : `Iter limit (${session.kmeans.iterations})`
      ]);
    }

    // MST row
    if (session.mst) {
      rows.push([
        session.dataset.type,
        session.dataset.points.length,
        session.params.clusters,
        session.params.noise,
        session.params.outlierFraction,
        session.params.seed,
        'Euclidean MST Clustering',
        session.mstEval ? (session.mstEval.inlierARI !== null ? session.mstEval.inlierARI.toFixed(6) : 'N/A') : '',
        session.mstEval ? session.mstEval.overallARI.toFixed(6) : '',
        session.mst.runtimeMs.toFixed(3),
        `Total MST Weight = ${session.mst.totalWeight.toFixed(4)}`,
        `K=${session.mst.k} components (${session.mst.cutEdges.length} cut edges)`
      ]);
    }

    const csv = toCSV(headers, rows);
    const filename = `mst_kmeans_metrics_${session.dataset.type}_n${session.dataset.points.length}.csv`;
    downloadText(csv, filename);
    return { filename, rowCount: rows.length };
  }

  /**
   * C. Export Robustness Experiment Raw Observations as CSV
   */
  function exportRobustnessRawCSV(results) {
    const rawRuns = results?.rawRuns || (results ? (results.rawNoiseTrials || []).concat(results.rawOutlierTrials || []) : null);
    if (!rawRuns || !rawRuns.length) {
      throw new Error('No robustness experimental results available to export. Run Robustness Experiment first.');
    }

    const headers = [
      'dataset_family',
      'seed',
      'sample_count',
      'k',
      'noise_level',
      'outlier_fraction',
      'sweep_type',
      'algorithm',
      'inlier_ari',
      'matched_baseline_ari',
      'ari_degradation',
      'runtime_ms',
      'predicted_k'
    ];

    const rows = [];
    rawRuns.forEach(r => {
      const kmDeg = (r.kmeansDegradation !== undefined && r.kmeansDegradation !== null)
        ? r.kmeansDegradation
        : ((r.kmDegradation !== undefined && r.kmDegradation !== null) ? r.kmDegradation : null);
      const mstDeg = (r.mstDegradation !== undefined && r.mstDegradation !== null) ? r.mstDegradation : null;

      // K-Means entry
      rows.push([
        results.datasetType || r.datasetType,
        r.seed,
        r.totalCount,
        r.k,
        r.noise.toFixed(4),
        r.outlierFraction.toFixed(4),
        r.sweepType || 'general',
        'K-Means',
        (r.kmeans && r.kmeans.inlierARI !== null) ? r.kmeans.inlierARI.toFixed(6) : 'N/A',
        (r.baseline && r.baseline.kmeans && r.baseline.kmeans.inlierARI !== null) ? r.baseline.kmeans.inlierARI.toFixed(6) : 'N/A',
        kmDeg !== null ? kmDeg.toFixed(6) : 'N/A',
        (r.kmeans && r.kmeans.runtimeMs !== undefined) ? r.kmeans.runtimeMs.toFixed(3) : '0.000',
        (r.kmeans && r.kmeans.predictedK !== undefined) ? r.kmeans.predictedK : r.k
      ]);

      // MST entry
      rows.push([
        results.datasetType || r.datasetType,
        r.seed,
        r.totalCount,
        r.k,
        r.noise.toFixed(4),
        r.outlierFraction.toFixed(4),
        r.sweepType || 'general',
        'MST-Clustering',
        (r.mst && r.mst.inlierARI !== null) ? r.mst.inlierARI.toFixed(6) : 'N/A',
        (r.baseline && r.baseline.mst && r.baseline.mst.inlierARI !== null) ? r.baseline.mst.inlierARI.toFixed(6) : 'N/A',
        mstDeg !== null ? mstDeg.toFixed(6) : 'N/A',
        (r.mst && r.mst.runtimeMs !== undefined) ? r.mst.runtimeMs.toFixed(3) : '0.000',
        (r.mst && r.mst.predictedK !== undefined) ? r.mst.predictedK : r.k
      ]);
    });

    const csv = toCSV(headers, rows);
    const filename = `mst_kmeans_robustness_raw_${results.datasetType || 'experiment'}_runs${rawRuns.length}.csv`;
    downloadText(csv, filename);
    return { filename, rowCount: rows.length };
  }

  /**
   * D. Export Aggregated Robustness Statistics as CSV
   */
  function exportRobustnessAggregatedCSV(results) {
    const noiseData = results?.noiseSweep || results?.aggregatedNoise;
    const outlierData = results?.outlierSweep || results?.aggregatedOutliers;
    if (!results || (!noiseData && !outlierData)) {
      throw new Error('No aggregated robustness results available to export. Run Robustness Experiment first.');
    }

    const headers = [
      'parameter_group',
      'sweep_parameter_name',
      'sweep_value',
      'algorithm',
      'number_of_repetitions',
      'mean_inlier_ari',
      'std_inlier_ari',
      'mean_ari_degradation',
      'std_ari_degradation'
    ];

    const rows = [];
    const repCount = (results.seeds && results.seeds.length) || 3;

    // Noise sweep entries
    if (noiseData && noiseData.length) {
      noiseData.forEach(item => {
        const val = item.noise !== undefined ? item.noise : (item.stepValue !== undefined ? item.stepValue : 0);
        const kmARI = item.kmARI || (item.kmeans ? item.kmeans.inlierARI : { mean: 0, std: 0 });
        const kmDeg = item.kmDegradation || (item.kmeans ? item.kmeans.degradation : { mean: 0, std: 0 });
        const mstARI = item.mstARI || (item.mst ? item.mst.inlierARI : { mean: 0, std: 0 });
        const mstDeg = item.mstDegradation || (item.mst ? item.mst.degradation : { mean: 0, std: 0 });
        const nReps = item.sampleCount || repCount;

        // K-Means
        rows.push([
          'Noise Sweep (Outliers=0%)',
          'noise_sigma',
          val.toFixed(2),
          'K-Means',
          nReps,
          kmARI.mean.toFixed(6),
          kmARI.std.toFixed(6),
          kmDeg.mean.toFixed(6),
          kmDeg.std.toFixed(6)
        ]);

        // MST
        rows.push([
          'Noise Sweep (Outliers=0%)',
          'noise_sigma',
          val.toFixed(2),
          'MST-Clustering',
          nReps,
          mstARI.mean.toFixed(6),
          mstARI.std.toFixed(6),
          mstDeg.mean.toFixed(6),
          mstDeg.std.toFixed(6)
        ]);
      });
    }

    // Outlier sweep entries
    if (outlierData && outlierData.length) {
      outlierData.forEach(item => {
        const val = item.fraction !== undefined ? item.fraction : (item.stepValue !== undefined ? item.stepValue : 0);
        const kmARI = item.kmARI || (item.kmeans ? item.kmeans.inlierARI : { mean: 0, std: 0 });
        const kmDeg = item.kmDegradation || (item.kmeans ? item.kmeans.degradation : { mean: 0, std: 0 });
        const mstARI = item.mstARI || (item.mst ? item.mst.inlierARI : { mean: 0, std: 0 });
        const mstDeg = item.mstDegradation || (item.mst ? item.mst.degradation : { mean: 0, std: 0 });
        const nReps = item.sampleCount || repCount;

        // K-Means
        rows.push([
          'Outlier Contamination Sweep (Noise=0.00)',
          'outlier_fraction',
          `${Math.round(val * 100)}%`,
          'K-Means',
          nReps,
          kmARI.mean.toFixed(6),
          kmARI.std.toFixed(6),
          kmDeg.mean.toFixed(6),
          kmDeg.std.toFixed(6)
        ]);

        // MST
        rows.push([
          'Outlier Contamination Sweep (Noise=0.00)',
          'outlier_fraction',
          `${Math.round(val * 100)}%`,
          'MST-Clustering',
          nReps,
          mstARI.mean.toFixed(6),
          mstARI.std.toFixed(6),
          mstDeg.mean.toFixed(6),
          mstDeg.std.toFixed(6)
        ]);
      });
    }

    const csv = toCSV(headers, rows);
    const filename = `mst_kmeans_robustness_aggregated_${results.datasetType || 'experiment'}.csv`;
    downloadText(csv, filename);
    return { filename, rowCount: rows.length };
  }

  /**
   * E. Export Performance Benchmark Results as CSV
   */
  function exportBenchmarksCSV(results) {
    if (!results || !results.sampleSizes || !results.measurements) {
      throw new Error('No performance benchmark measurements available to export. Run Benchmarks first.');
    }

    const headers = [
      'sample_size',
      'algorithm',
      'trial_identifier',
      'execution_time_ms',
      'sample_mean_ms',
      'sample_std_ms',
      'sample_median_ms',
      'speedup_ratio_vs_mst',
      'hardware_platform',
      'hardware_concurrency_cores'
    ];

    const rows = [];
    const env = results.environment || {};

    results.sampleSizes.forEach(n => {
      const kmData = results.measurements.kmeans[n];
      const mstData = results.measurements.mst[n];
      const speedup = (mstData.mean / Math.max(kmData.mean, 1e-6)).toFixed(2);

      // Raw trials for K-Means
      kmData.trials.forEach((timeMs, tIdx) => {
        rows.push([
          n,
          'K-Means',
          `Trial ${tIdx + 1}`,
          timeMs.toFixed(4),
          kmData.mean.toFixed(4),
          kmData.std.toFixed(4),
          kmData.median.toFixed(4),
          speedup,
          env.platform || 'Browser',
          env.hardwareConcurrency || 'N/A'
        ]);
      });

      // Raw trials for MST
      mstData.trials.forEach((timeMs, tIdx) => {
        rows.push([
          n,
          'MST Prim Dense',
          `Trial ${tIdx + 1}`,
          timeMs.toFixed(4),
          mstData.mean.toFixed(4),
          mstData.std.toFixed(4),
          mstData.median.toFixed(4),
          '1.00',
          env.platform || 'Browser',
          env.hardwareConcurrency || 'N/A'
        ]);
      });
    });

    const csv = toCSV(headers, rows);
    const filename = `mst_kmeans_performance_benchmarks_${results.datasetType}.csv`;
    downloadText(csv, filename);
    return { filename, rowCount: rows.length };
  }

  /**
   * F. Export Reproducibility Information Recipe as JSON
   * Strictly includes public scientific metadata, no private tokens or filesystem paths
   */
  function exportReproducibilityJSON(appState) {
    const jsonDoc = {
      projectMetadata: {
        title: 'MST vs K-Means Robustness Analysis',
        leadStudent: 'Himanshu Gupta',
        allocationNumber: 19,
        partner: 'Parth Yadav',
        institution: 'Manav Rachna International Institute of Research and Studies',
        course: 'Pattern Matching Lab (BCS-DS-777)',
        timestamp: new Date().toISOString()
      },
      softwareEnvironment: {
        runtime: 'Client-Side JavaScript (Browser Native)',
        userAgent: navigator.userAgent,
        platform: navigator.platform,
        hardwareConcurrency: navigator.hardwareConcurrency || 'N/A',
        timerPrecision: typeof performance !== 'undefined' && typeof performance.now === 'function' ? 'High Resolution performance.now()' : 'Standard'
      },
      clusteringSpecifications: {
        kmeans: {
          algorithm: "Lloyd's Heuristic",
          initialization: 'K-Means++ (Probabilistic D^2 sampling)',
          distanceMetric: 'Squared Euclidean Distance',
          convergenceTolerance: 1e-5,
          emptyClusterReseed: 'Farthest Point Heuristic'
        },
        mst: {
          algorithm: "Prim's Dense Euclidean Minimum Spanning Tree",
          timeComplexity: 'O(N^2)',
          spaceComplexity: 'O(N)',
          clusterPartitioning: 'Removal of (K - 1) longest Euclidean edges',
          componentExtraction: 'Disjoint Set Union (Union-Find with path compression)'
        }
      },
      activePlaygroundState: appState.playground ? {
        dataset: appState.playground.dataset ? appState.playground.dataset.type : null,
        parameters: appState.playground.params || null,
        resultsSummary: {
          kmeansInlierARI: appState.playground.kmEval ? appState.playground.kmEval.inlierARI : null,
          mstInlierARI: appState.playground.mstEval ? appState.playground.mstEval.inlierARI : null,
          kmeansRuntimeMs: appState.playground.kmeans ? appState.playground.kmeans.runtimeMs : null,
          mstRuntimeMs: appState.playground.mst ? appState.playground.mst.runtimeMs : null
        }
      } : null,
      robustnessExperimentConfig: appState.robustness ? {
        datasetType: appState.robustness.datasetType,
        inlierCount: appState.robustness.inlierCount,
        k: appState.robustness.k,
        seeds: appState.robustness.seeds,
        noiseSweepSummary: appState.robustness.noiseSweep,
        outlierSweepSummary: appState.robustness.outlierSweep
      } : null,
      performanceBenchmarkConfig: appState.benchmarks ? {
        datasetType: appState.benchmarks.datasetType,
        k: appState.benchmarks.k,
        sampleSizes: appState.benchmarks.sampleSizes,
        repetitions: appState.benchmarks.repetitions,
        measurements: appState.benchmarks.measurements
      } : null
    };

    const jsonString = JSON.stringify(jsonDoc, null, 2);
    const filename = `mst_kmeans_reproducibility_recipe_${Date.now()}.json`;
    downloadText(jsonString, filename, 'application/json;charset=utf-8');
    return { filename, sizeBytes: jsonString.length };
  }

  window.MSTKMeans.ExportManager = {
    sanitizeCSVCell,
    toCSV,
    downloadBlob,
    downloadText,
    exportCanvasAsPNG,
    exportPlaygroundDatasetCSV,
    exportPlaygroundMetricsCSV,
    exportRobustnessRawCSV,
    exportRobustnessAggregatedCSV,
    exportBenchmarksCSV,
    exportReproducibilityJSON
  };
})(window);
