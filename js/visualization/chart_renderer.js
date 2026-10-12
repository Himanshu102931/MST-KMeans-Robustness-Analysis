/**
 * MST vs K-Means Robustness Analysis
 * Module: High-DPI Scientific Canvas Chart Renderer
 * Renders Line Charts with Error Bars, Degradation Bar Charts, and Scaling Curves
 * Pure Vanilla JavaScript - No dependencies
 */

(function (window) {
  'use strict';

  window.MSTKMeans = window.MSTKMeans || {};
  const { setupCanvas } = window.MSTKMeans.Visualizer;

  const COLORS = {
    kmeans: '#F59E0B',      // Amber
    kmeansFill: 'rgba(245, 158, 11, 0.15)',
    mst: '#10B981',         // Emerald
    mstFill: 'rgba(16, 185, 129, 0.15)',
    grid: '#1e293b',
    axis: '#334155',
    text: '#94a3b8',
    textHighlight: '#f8fafc',
    bg: '#0f172a'
  };

  /**
   * Render an empty placeholder chart state
   */
  function renderEmptyState(canvas, message = 'Run experiment to render data-driven scientific chart') {
    const { ctx, width, height } = setupCanvas(canvas);
    ctx.fillStyle = COLORS.bg;
    ctx.fillRect(0, 0, width, height);

    ctx.strokeStyle = COLORS.grid;
    ctx.strokeRect(10, 10, width - 20, height - 20);

    ctx.fillStyle = '#64748b';
    ctx.font = '13px system-ui, sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(message, width / 2, height / 2);
  }

  /**
   * Render Line Chart with Error Bars (e.g. Inlier ARI vs Noise or Outliers)
   *
   * @param {HTMLCanvasElement} canvas
   * @param {Object} options
   * @param {string} options.title Chart title
   * @param {string} options.xLabel X-axis label
   * @param {string} options.yLabel Y-axis label
   * @param {Array<string|number>} options.xTicks Labels for X-axis
   * @param {Array<{mean: number, std: number}>} options.kmData K-Means data points
   * @param {Array<{mean: number, std: number}>} options.mstData MST data points
   * @param {number} [options.yMin=0.0]
   * @param {number} [options.yMax=1.0]
   */
  function renderLineChartWithErrorBars(canvas, options = {}) {
    const {
      title = 'Clustering Performance',
      xLabel = 'Perturbation Level',
      yLabel = 'Inlier ARI',
      xTicks = [],
      kmData = [],
      mstData = [],
      yMin = 0.0,
      yMax = 1.0
    } = options;

    if (!kmData.length && !mstData.length) {
      renderEmptyState(canvas, 'No experimental data available');
      return;
    }

    const { ctx, width, height } = setupCanvas(canvas);

    // Background
    ctx.fillStyle = COLORS.bg;
    ctx.fillRect(0, 0, width, height);

    const padLeft = 56;
    const padRight = 24;
    const padTop = 38;
    const padBottom = 48;

    const plotW = width - padLeft - padRight;
    const plotH = height - padTop - padBottom;

    // Title
    ctx.fillStyle = COLORS.textHighlight;
    ctx.font = 'bold 12px system-ui, sans-serif';
    ctx.textAlign = 'left';
    ctx.fillText(title, padLeft, 22);

    // Legend
    ctx.font = '11px system-ui, sans-serif';
    ctx.textAlign = 'right';
    // K-Means Legend
    ctx.fillStyle = COLORS.kmeans;
    ctx.fillRect(width - padRight - 145, 13, 10, 10);
    ctx.fillStyle = COLORS.text;
    ctx.fillText('K-Means (Mean ± 1σ)', width - padRight - 35, 21);
    // MST Legend
    ctx.fillStyle = COLORS.mst;
    ctx.fillRect(width - padRight - 26, 13, 10, 10);
    ctx.fillStyle = COLORS.text;
    ctx.fillText('MST', width - padRight, 21);

    // Y-Axis Grid & Ticks (5 horizontal intervals)
    const ySteps = 5;
    ctx.strokeStyle = COLORS.grid;
    ctx.lineWidth = 1;
    ctx.textAlign = 'right';
    ctx.font = '10px monospace';

    for (let i = 0; i <= ySteps; i++) {
      const frac = i / ySteps;
      const yVal = yMin + (1 - frac) * (yMax - yMin);
      const py = padTop + frac * plotH;

      ctx.beginPath();
      ctx.moveTo(padLeft, py);
      ctx.lineTo(width - padRight, py);
      ctx.stroke();

      ctx.fillStyle = COLORS.text;
      ctx.fillText(yVal.toFixed(2), padLeft - 8, py + 3);
    }

    // Y-Axis Title
    ctx.save();
    ctx.translate(14, padTop + plotH / 2);
    ctx.rotate(-Math.PI / 2);
    ctx.textAlign = 'center';
    ctx.font = '11px system-ui, sans-serif';
    ctx.fillStyle = COLORS.text;
    ctx.fillText(yLabel, 0, 0);
    ctx.restore();

    // X-Axis mapping helper
    const nPts = xTicks.length;
    const getX = (idx) => {
      if (nPts <= 1) return padLeft + plotW / 2;
      return padLeft + (idx / (nPts - 1)) * plotW;
    };
    const getY = (val) => {
      const clamped = Math.max(yMin, Math.min(yMax, val));
      const frac = (clamped - yMin) / (yMax - yMin);
      return padTop + (1 - frac) * plotH;
    };

    // Draw X-Ticks & Labels
    ctx.textAlign = 'center';
    ctx.font = '11px monospace';
    ctx.fillStyle = COLORS.text;
    for (let i = 0; i < nPts; i++) {
      const px = getX(i);
      ctx.fillText(`${xTicks[i]}`, px, height - padBottom + 18);
    }

    // X-Axis Title
    ctx.textAlign = 'center';
    ctx.font = '11px system-ui, sans-serif';
    ctx.fillStyle = COLORS.text;
    ctx.fillText(xLabel, padLeft + plotW / 2, height - 10);

    // Helper to draw series curve and error bars
    const drawSeries = (data, color, fillColor) => {
      if (!data || data.length === 0) return;

      // 1. Draw Connecting Line
      ctx.beginPath();
      ctx.strokeStyle = color;
      ctx.lineWidth = 2.2;
      for (let i = 0; i < data.length; i++) {
        const px = getX(i);
        const py = getY(data[i].mean);
        if (i === 0) ctx.moveTo(px, py);
        else ctx.lineTo(px, py);
      }
      ctx.stroke();

      // 2. Draw Error Bars (Whiskers: mean - std to mean + std)
      ctx.lineWidth = 1.4;
      ctx.strokeStyle = color;
      for (let i = 0; i < data.length; i++) {
        const px = getX(i);
        const mean = data[i].mean;
        const std = data[i].std || 0;
        const yTop = getY(Math.min(yMax, mean + std));
        const yBottom = getY(Math.max(yMin, mean - std));

        // Vertical error line
        ctx.beginPath();
        ctx.moveTo(px, yTop);
        ctx.lineTo(px, yBottom);
        ctx.stroke();

        // Top horizontal cap
        ctx.beginPath();
        ctx.moveTo(px - 4, yTop);
        ctx.lineTo(px + 4, yTop);
        ctx.stroke();

        // Bottom horizontal cap
        ctx.beginPath();
        ctx.moveTo(px - 4, yBottom);
        ctx.lineTo(px + 4, yBottom);
        ctx.stroke();
      }

      // 3. Draw Points
      for (let i = 0; i < data.length; i++) {
        const px = getX(i);
        const py = getY(data[i].mean);

        ctx.beginPath();
        ctx.arc(px, py, 4.5, 0, 2 * Math.PI);
        ctx.fillStyle = color;
        ctx.fill();
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 1.2;
        ctx.stroke();
      }
    };

    // Draw K-Means then MST series
    drawSeries(kmData, COLORS.kmeans, COLORS.kmeansFill);
    drawSeries(mstData, COLORS.mst, COLORS.mstFill);
  }

  /**
   * Render Comparative Degradation Grouped Bar Chart
   * Shows ΔARI = Baseline - Perturbed for K-Means vs MST side-by-side
   */
  function renderDegradationBarChart(canvas, options = {}) {
    const {
      title = 'ARI Degradation from Clean Baseline (Lower is More Robust)',
      xTicks = [],
      kmDegradation = [],
      mstDegradation = []
    } = options;

    if (!kmDegradation.length && !mstDegradation.length) {
      renderEmptyState(canvas, 'No degradation data available');
      return;
    }

    const { ctx, width, height } = setupCanvas(canvas);

    ctx.fillStyle = COLORS.bg;
    ctx.fillRect(0, 0, width, height);

    const padLeft = 56;
    const padRight = 24;
    const padTop = 38;
    const padBottom = 48;

    const plotW = width - padLeft - padRight;
    const plotH = height - padTop - padBottom;

    // Title
    ctx.fillStyle = COLORS.textHighlight;
    ctx.font = 'bold 12px system-ui, sans-serif';
    ctx.textAlign = 'left';
    ctx.fillText(title, padLeft, 22);

    // Legend
    ctx.font = '11px system-ui, sans-serif';
    ctx.textAlign = 'right';
    ctx.fillStyle = COLORS.kmeans;
    ctx.fillRect(width - padRight - 120, 13, 10, 10);
    ctx.fillStyle = COLORS.text;
    ctx.fillText('K-Means ΔARI', width - padRight - 40, 21);

    ctx.fillStyle = COLORS.mst;
    ctx.fillRect(width - padRight - 32, 13, 10, 10);
    ctx.fillStyle = COLORS.text;
    ctx.fillText('MST', width - padRight, 21);

    // Max degradation cap (typically in [0, 1])
    let maxVal = 0.5;
    kmDegradation.concat(mstDegradation).forEach(v => {
      if (v > maxVal) maxVal = v;
    });
    maxVal = Math.min(1.0, Math.ceil(maxVal * 5) / 5);

    // Y-Axis Grid
    const ySteps = 5;
    ctx.strokeStyle = COLORS.grid;
    ctx.lineWidth = 1;
    ctx.textAlign = 'right';
    ctx.font = '10px monospace';
    for (let i = 0; i <= ySteps; i++) {
      const frac = i / ySteps;
      const yVal = (1 - frac) * maxVal;
      const py = padTop + frac * plotH;

      ctx.beginPath();
      ctx.moveTo(padLeft, py);
      ctx.lineTo(width - padRight, py);
      ctx.stroke();

      ctx.fillStyle = COLORS.text;
      ctx.fillText(yVal.toFixed(2), padLeft - 8, py + 3);
    }

    // Y-Axis Label
    ctx.save();
    ctx.translate(14, padTop + plotH / 2);
    ctx.rotate(-Math.PI / 2);
    ctx.textAlign = 'center';
    ctx.font = '11px system-ui, sans-serif';
    ctx.fillStyle = COLORS.text;
    ctx.fillText('ΔARI Loss (Lower = Better)', 0, 0);
    ctx.restore();

    // Draw Grouped Bars
    const groupCount = xTicks.length;
    const groupWidth = plotW / groupCount;
    const barWidth = Math.min(22, (groupWidth - 16) / 2);

    for (let i = 0; i < groupCount; i++) {
      const groupCenterX = padLeft + i * groupWidth + groupWidth / 2;

      // X-Tick Label
      ctx.textAlign = 'center';
      ctx.font = '11px monospace';
      ctx.fillStyle = COLORS.text;
      ctx.fillText(xTicks[i], groupCenterX, height - padBottom + 18);

      // K-Means Bar (left of center)
      const kmVal = Math.max(0, kmDegradation[i] || 0);
      const kmHeight = (kmVal / maxVal) * plotH;
      const kmX = groupCenterX - barWidth - 2;
      const kmY = padTop + plotH - kmHeight;

      ctx.fillStyle = COLORS.kmeans;
      ctx.fillRect(kmX, kmY, barWidth, kmHeight);

      // MST Bar (right of center)
      const mstVal = Math.max(0, mstDegradation[i] || 0);
      const mstHeight = (mstVal / maxVal) * plotH;
      const mstX = groupCenterX + 2;
      const mstY = padTop + plotH - mstHeight;

      ctx.fillStyle = COLORS.mst;
      ctx.fillRect(mstX, mstY, barWidth, mstHeight);
    }

    // Baseline axis line
    ctx.beginPath();
    ctx.strokeStyle = COLORS.axis;
    ctx.lineWidth = 1.5;
    ctx.moveTo(padLeft, padTop + plotH);
    ctx.lineTo(width - padRight, padTop + plotH);
    ctx.stroke();
  }

  /**
   * Render Execution Time Scaling Line Chart (Benchmarks)
   */
  function renderRuntimeScalingChart(canvas, options = {}) {
    const {
      title = 'Execution Runtime vs Sample Size N (Empirical Scaling)',
      sampleSizes = [100, 200, 400, 600],
      kmTimes = [],
      mstTimes = []
    } = options;

    if (!kmTimes.length && !mstTimes.length) {
      renderEmptyState(canvas, 'Run performance benchmark to profile runtime scaling');
      return;
    }

    // Determine max runtime for dynamic scaling
    let maxT = 1.0;
    kmTimes.concat(mstTimes).forEach(item => {
      const val = (item.mean || 0) + (item.std || 0);
      if (val > maxT) maxT = val;
    });
    // Add 15% headroom
    maxT = Math.ceil(maxT * 1.15 * 10) / 10;

    const xTicks = sampleSizes.map(s => `N=${s}`);
    renderLineChartWithErrorBars(canvas, {
      title,
      xLabel: 'Sample Size (N Points)',
      yLabel: 'Runtime (ms)',
      xTicks,
      kmData: kmTimes,
      mstData: mstTimes,
      yMin: 0.0,
      yMax: maxT
    });
  }

  window.MSTKMeans.ChartRenderer = {
    renderEmptyState,
    renderLineChartWithErrorBars,
    renderDegradationBarChart,
    renderRuntimeScalingChart
  };
})(window);
