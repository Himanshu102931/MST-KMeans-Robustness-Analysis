/**
 * MST vs K-Means Robustness Analysis
 * Module: High-DPI Scientific Canvas Visualizer
 * Pure Vanilla JavaScript - No dependencies
 */

(function (window) {
  'use strict';

  window.MSTKMeans = window.MSTKMeans || {};

  // Curated accessible scientific color palette for clusters
  const CLUSTER_COLORS = [
    '#3B82F6', // Vibrant Blue
    '#10B981', // Emerald Green
    '#F59E0B', // Amber
    '#8B5CF6', // Purple
    '#EC4899', // Pink
    '#06B6D4', // Cyan
    '#F97316', // Orange
    '#14B8A6'  // Teal
  ];

  const OUTLIER_COLOR = '#EF4444'; // Red for injected outliers
  const OUTLIER_FILL = 'rgba(239, 68, 68, 0.25)';

  /**
   * Set up canvas for sharp rendering on High-DPI displays
   */
  function setupCanvas(canvas) {
    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();
    const width = rect.width || canvas.width || 400;
    const height = rect.height || canvas.height || 340;

    canvas.width = Math.floor(width * dpr);
    canvas.height = Math.floor(height * dpr);

    const ctx = canvas.getContext('2d');
    ctx.resetTransform?.();
    ctx.scale(dpr, dpr);
    return { ctx, width, height, dpr };
  }

  /**
   * Coordinate transformation helper to map data (x, y) to canvas (px, py)
   */
  function createCoordinateMapper(points, canvasWidth, canvasHeight, padding = 32) {
    let minX = Infinity, maxX = -Infinity;
    let minY = Infinity, maxY = -Infinity;

    for (let i = 0; i < points.length; i++) {
      const p = points[i];
      if (p.x < minX) minX = p.x;
      if (p.x > maxX) maxX = p.x;
      if (p.y < minY) minY = p.y;
      if (p.y > maxY) maxY = p.y;
    }

    if (!isFinite(minX)) {
      minX = -1; maxX = 1; minY = -1; maxY = 1;
    }

    const spanX = Math.max(maxX - minX, 1e-4);
    const spanY = Math.max(maxY - minY, 1e-4);

    const availableW = canvasWidth - 2 * padding;
    const availableH = canvasHeight - 2 * padding;

    // Preserve equal aspect ratio
    const scale = Math.min(availableW / spanX, availableH / spanY);

    const offsetX = padding + (availableW - spanX * scale) / 2;
    const offsetY = padding + (availableH - spanY * scale) / 2;

    return {
      toCanvasX: (x) => offsetX + (x - minX) * scale,
      // Invert Y so positive Y is upwards
      toCanvasY: (y) => canvasHeight - (offsetY + (y - minY) * scale),
      scale,
      bounds: { minX, maxX, minY, maxY }
    };
  }

  /**
   * Draw subtle background grid and axes
   */
  function drawGrid(ctx, width, height) {
    ctx.save();
    ctx.fillStyle = '#0f172a'; // Deep dark scientific background
    ctx.fillRect(0, 0, width, height);

    ctx.strokeStyle = '#1e293b';
    ctx.lineWidth = 1;

    const step = 40;
    ctx.beginPath();
    for (let x = step; x < width; x += step) {
      ctx.moveTo(x, 0);
      ctx.lineTo(x, height);
    }
    for (let y = step; y < height; y += step) {
      ctx.moveTo(0, y);
      ctx.lineTo(width, y);
    }
    ctx.stroke();
    ctx.restore();
  }

  /**
   * Render Ground Truth Scatter Plot
   */
  function renderGroundTruth(canvas, dataset) {
    const { ctx, width, height } = setupCanvas(canvas);
    drawGrid(ctx, width, height);

    const points = dataset.points;
    if (!points || points.length === 0) return;

    const mapper = createCoordinateMapper(points, width, height);

    // 1. Draw Inliers
    for (let i = 0; i < points.length; i++) {
      const p = points[i];
      if (p.isOutlier) continue;

      const cx = mapper.toCanvasX(p.x);
      const cy = mapper.toCanvasY(p.y);
      const color = CLUSTER_COLORS[p.groundTruth % CLUSTER_COLORS.length] || '#64748B';

      ctx.beginPath();
      ctx.arc(cx, cy, 4.5, 0, 2 * Math.PI);
      ctx.fillStyle = color;
      ctx.fill();
      ctx.lineWidth = 1.5;
      ctx.strokeStyle = '#ffffff';
      ctx.stroke();
    }

    // 2. Draw Outliers (highlighted in red with dashed ring / distinct mark)
    for (let i = 0; i < points.length; i++) {
      const p = points[i];
      if (!p.isOutlier) continue;

      const cx = mapper.toCanvasX(p.x);
      const cy = mapper.toCanvasY(p.y);

      // Distinct halo
      ctx.beginPath();
      ctx.arc(cx, cy, 7, 0, 2 * Math.PI);
      ctx.fillStyle = OUTLIER_FILL;
      ctx.fill();
      ctx.strokeStyle = OUTLIER_COLOR;
      ctx.lineWidth = 1.5;
      ctx.stroke();

      // Center point
      ctx.beginPath();
      ctx.arc(cx, cy, 3, 0, 2 * Math.PI);
      ctx.fillStyle = OUTLIER_COLOR;
      ctx.fill();
    }
  }

  /**
   * Render K-Means Clustering Results
   */
  function renderKMeans(canvas, dataset, kmeansResult) {
    const { ctx, width, height } = setupCanvas(canvas);
    drawGrid(ctx, width, height);

    const points = dataset.points;
    if (!points || points.length === 0 || !kmeansResult) return;

    const mapper = createCoordinateMapper(points, width, height);
    const labels = kmeansResult.labels;
    const centroids = kmeansResult.centroids || [];

    // 1. Draw points colored by predicted cluster
    for (let i = 0; i < points.length; i++) {
      const p = points[i];
      const clusterIdx = labels[i];
      const color = CLUSTER_COLORS[clusterIdx % CLUSTER_COLORS.length] || '#94A3B8';

      const cx = mapper.toCanvasX(p.x);
      const cy = mapper.toCanvasY(p.y);

      ctx.beginPath();
      ctx.arc(cx, cy, 4.5, 0, 2 * Math.PI);
      ctx.fillStyle = color;
      ctx.fill();
      ctx.lineWidth = 1.2;
      ctx.strokeStyle = '#ffffff';
      ctx.stroke();
    }

    // 2. Draw Centroids prominently
    for (let c = 0; c < centroids.length; c++) {
      const centroid = centroids[c];
      const cx = mapper.toCanvasX(centroid.x);
      const cy = mapper.toCanvasY(centroid.y);
      const color = CLUSTER_COLORS[c % CLUSTER_COLORS.length] || '#F59E0B';

      // Outer glow ring
      ctx.beginPath();
      ctx.arc(cx, cy, 11, 0, 2 * Math.PI);
      ctx.fillStyle = 'rgba(255, 255, 255, 0.2)';
      ctx.fill();
      ctx.strokeStyle = '#ffffff';
      ctx.lineWidth = 2;
      ctx.stroke();

      // Inner diamond / cross
      ctx.beginPath();
      ctx.arc(cx, cy, 7, 0, 2 * Math.PI);
      ctx.fillStyle = color;
      ctx.fill();

      // Cross marker in center
      ctx.strokeStyle = '#ffffff';
      ctx.lineWidth = 2.5;
      ctx.beginPath();
      ctx.moveTo(cx - 4, cy);
      ctx.lineTo(cx + 4, cy);
      ctx.moveTo(cx, cy - 4);
      ctx.lineTo(cx, cy + 4);
      ctx.stroke();
    }
  }

  /**
   * Render MST Clustering Results
   */
  function renderMST(canvas, dataset, mstResult) {
    const { ctx, width, height } = setupCanvas(canvas);
    drawGrid(ctx, width, height);

    const points = dataset.points;
    if (!points || points.length === 0 || !mstResult) return;

    const mapper = createCoordinateMapper(points, width, height);
    const { labels, mstEdges } = mstResult;

    // 1. Draw Kept MST Edges (subtle solid lines)
    ctx.lineWidth = 1.2;
    ctx.strokeStyle = 'rgba(148, 163, 184, 0.45)';
    ctx.setLineDash([]);
    ctx.beginPath();
    for (let i = 0; i < mstEdges.length; i++) {
      const edge = mstEdges[i];
      if (!edge.isCut) {
        const p1 = points[edge.u];
        const p2 = points[edge.v];
        ctx.moveTo(mapper.toCanvasX(p1.x), mapper.toCanvasY(p1.y));
        ctx.lineTo(mapper.toCanvasX(p2.x), mapper.toCanvasY(p2.y));
      }
    }
    ctx.stroke();

    // 2. Draw Cut Edges (the K-1 longest removed edges) in dashed crimson
    ctx.lineWidth = 2.5;
    ctx.strokeStyle = '#EF4444';
    ctx.setLineDash([4, 4]);
    ctx.beginPath();
    for (let i = 0; i < mstEdges.length; i++) {
      const edge = mstEdges[i];
      if (edge.isCut) {
        const p1 = points[edge.u];
        const p2 = points[edge.v];
        ctx.moveTo(mapper.toCanvasX(p1.x), mapper.toCanvasY(p1.y));
        ctx.lineTo(mapper.toCanvasX(p2.x), mapper.toCanvasY(p2.y));
      }
    }
    ctx.stroke();
    ctx.setLineDash([]); // Reset line dash

    // 3. Draw Points colored by connected component
    for (let i = 0; i < points.length; i++) {
      const p = points[i];
      const compIdx = labels[i];
      const color = CLUSTER_COLORS[compIdx % CLUSTER_COLORS.length] || '#94A3B8';

      const cx = mapper.toCanvasX(p.x);
      const cy = mapper.toCanvasY(p.y);

      ctx.beginPath();
      ctx.arc(cx, cy, 4.5, 0, 2 * Math.PI);
      ctx.fillStyle = color;
      ctx.fill();
      ctx.lineWidth = 1.2;
      ctx.strokeStyle = '#ffffff';
      ctx.stroke();
    }
  }

  window.MSTKMeans.Visualizer = {
    CLUSTER_COLORS,
    OUTLIER_COLOR,
    renderGroundTruth,
    renderKMeans,
    renderMST,
    setupCanvas
  };
})(window);
