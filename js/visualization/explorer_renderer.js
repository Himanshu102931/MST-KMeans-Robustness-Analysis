/**
 * MST vs K-Means Robustness Analysis
 * Module: High-DPI Scientific Canvas Explorer Renderer
 * Renders interactive step-by-step visualizations for K-Means and Euclidean MST Prim's Clustering
 * Pure Vanilla JavaScript - No dependencies
 */

(function (window) {
  'use strict';

  window.MSTKMeans = window.MSTKMeans || {};
  const { setupCanvas, CLUSTER_COLORS } = window.MSTKMeans.Visualizer;

  const EXPLORER_COLORS = {
    bg: '#0f172a',
    grid: '#1e293b',
    unassignedPoint: '#64748b',
    unvisitedVertex: '#334155',
    inTreeVertex: '#38bdf8',       // Sky Blue
    activeEdge: '#f59e0b',         // Amber
    treeEdge: '#10b981',           // Emerald
    cutEdge: '#ef4444',            // Crimson Red
    candidateEdge: 'rgba(148, 163, 184, 0.18)',
    centroidShiftArrow: '#e11d48', // Bright Rose Red
    centroidFill: '#f8fafc',
    textMuted: '#94a3b8'
  };

  /**
   * Create coordinate mapper accounting for points and centroids
   */
  function createExplorerMapper(points, centroids = [], canvasWidth, canvasHeight, padding = 44) {
    let minX = Infinity, maxX = -Infinity;
    let minY = Infinity, maxY = -Infinity;

    const all = [...points, ...centroids];
    for (let i = 0; i < all.length; i++) {
      const p = all[i];
      if (p.x < minX) minX = p.x;
      if (p.x > maxX) maxX = p.x;
      if (p.y < minY) minY = p.y;
      if (p.y > maxY) maxY = p.y;
    }

    if (!isFinite(minX)) {
      minX = -1; maxX = 1; minY = -1; maxY = 1;
    }

    // Add 10% breathing room
    const spanX = Math.max(maxX - minX, 1e-4);
    const spanY = Math.max(maxY - minY, 1e-4);
    minX -= spanX * 0.08;
    maxX += spanX * 0.08;
    minY -= spanY * 0.08;
    maxY += spanY * 0.08;

    const effSpanX = maxX - minX;
    const effSpanY = maxY - minY;

    const availableW = canvasWidth - 2 * padding;
    const availableH = canvasHeight - 2 * padding;
    const scale = Math.min(availableW / effSpanX, availableH / effSpanY);

    const offsetX = padding + (availableW - effSpanX * scale) / 2;
    const offsetY = padding + (availableH - effSpanY * scale) / 2;

    return {
      toX: (x) => offsetX + (x - minX) * scale,
      toY: (y) => canvasHeight - (offsetY + (y - minY) * scale),
      scale
    };
  }

  /**
   * Draw subtle background grid
   */
  function drawGrid(ctx, width, height) {
    ctx.fillStyle = EXPLORER_COLORS.bg;
    ctx.fillRect(0, 0, width, height);

    ctx.strokeStyle = EXPLORER_COLORS.grid;
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
  }

  /**
   * Render K-Means step snapshot on canvas
   *
   * @param {HTMLCanvasElement} canvas
   * @param {Array<{x: number, y: number}>} points
   * @param {Object} step Trace step snapshot
   */
  function renderKMeansTraceStep(canvas, points, step) {
    if (!canvas || !step) return;
    const { ctx, width, height } = setupCanvas(canvas);
    drawGrid(ctx, width, height);

    const mapper = createExplorerMapper(points, step.centroids || [], width, height, 48);
    const actualK = step.centroids ? step.centroids.length : 0;

    // 1. Draw assignment connection lines (point to its assigned centroid)
    if (step.labels && step.labels.length === points.length && step.type !== 'init') {
      ctx.lineWidth = 1;
      for (let i = 0; i < points.length; i++) {
        const clusterIdx = step.labels[i];
        if (clusterIdx >= 0 && clusterIdx < actualK) {
          const pt = points[i];
          const ct = step.centroids[clusterIdx];
          const color = CLUSTER_COLORS[clusterIdx % CLUSTER_COLORS.length];

          ctx.strokeStyle = color;
          ctx.globalAlpha = 0.22;
          ctx.setLineDash([3, 3]);
          ctx.beginPath();
          ctx.moveTo(mapper.toX(pt.x), mapper.toY(pt.y));
          ctx.lineTo(mapper.toX(ct.x), mapper.toY(ct.y));
          ctx.stroke();
        }
      }
      ctx.setLineDash([]);
      ctx.globalAlpha = 1.0;
    }

    // 2. Draw centroid movement vector arrows (for update steps)
    if (step.type === 'update' && step.previousCentroids && step.previousCentroids.length) {
      for (let c = 0; c < actualK; c++) {
        const prev = step.previousCentroids[c];
        const curr = step.centroids[c];
        if (prev && curr) {
          const x1 = mapper.toX(prev.x);
          const y1 = mapper.toY(prev.y);
          const x2 = mapper.toX(curr.x);
          const y2 = mapper.toY(curr.y);
          const d = Math.hypot(x2 - x1, y2 - y1);

          if (d > 2) {
            // Arrow shaft
            ctx.save();
            ctx.strokeStyle = EXPLORER_COLORS.centroidShiftArrow;
            ctx.lineWidth = 2.5;
            ctx.setLineDash([4, 3]);
            ctx.beginPath();
            ctx.moveTo(x1, y1);
            ctx.lineTo(x2, y2);
            ctx.stroke();

            // Arrow head
            const angle = Math.atan2(y2 - y1, x2 - x1);
            const headLen = 8;
            ctx.setLineDash([]);
            ctx.fillStyle = EXPLORER_COLORS.centroidShiftArrow;
            ctx.beginPath();
            ctx.moveTo(x2, y2);
            ctx.lineTo(x2 - headLen * Math.cos(angle - Math.PI / 6), y2 - headLen * Math.sin(angle - Math.PI / 6));
            ctx.lineTo(x2 - headLen * Math.cos(angle + Math.PI / 6), y2 - headLen * Math.sin(angle + Math.PI / 6));
            ctx.closePath();
            ctx.fill();

            // Old centroid ghost marker
            ctx.strokeStyle = 'rgba(239, 68, 68, 0.4)';
            ctx.lineWidth = 1.5;
            ctx.beginPath();
            ctx.arc(x1, y1, 6, 0, 2 * Math.PI);
            ctx.stroke();
            ctx.restore();
          }
        }
      }
    }

    // 3. Draw Data Points
    for (let i = 0; i < points.length; i++) {
      const pt = points[i];
      const clusterIdx = step.labels ? step.labels[i] : -1;
      const cx = mapper.toX(pt.x);
      const cy = mapper.toY(pt.y);

      ctx.beginPath();
      ctx.arc(cx, cy, 6, 0, 2 * Math.PI);

      if (clusterIdx >= 0 && clusterIdx < actualK) {
        ctx.fillStyle = CLUSTER_COLORS[clusterIdx % CLUSTER_COLORS.length];
      } else {
        ctx.fillStyle = EXPLORER_COLORS.unassignedPoint;
      }
      ctx.fill();
      ctx.lineWidth = 1.5;
      ctx.strokeStyle = '#ffffff';
      ctx.stroke();

      // Point index label
      ctx.fillStyle = '#f8fafc';
      ctx.font = '9px monospace';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(i.toString(), cx, cy);
    }

    // 4. Draw Centroids as prominent diamonds
    if (step.centroids) {
      for (let c = 0; c < actualK; c++) {
        const ct = step.centroids[c];
        const cx = mapper.toX(ct.x);
        const cy = mapper.toY(ct.y);
        const color = CLUSTER_COLORS[c % CLUSTER_COLORS.length];

        ctx.save();
        // Outer glow
        ctx.shadowColor = color;
        ctx.shadowBlur = 10;

        // Diamond shape
        const r = 12;
        ctx.beginPath();
        ctx.moveTo(cx, cy - r);
        ctx.lineTo(cx + r, cy);
        ctx.lineTo(cx, cy + r);
        ctx.lineTo(cx - r, cy);
        ctx.closePath();

        ctx.fillStyle = color;
        ctx.fill();
        ctx.lineWidth = 2.5;
        ctx.strokeStyle = '#ffffff';
        ctx.stroke();

        ctx.shadowBlur = 0;
        // Inner centroid label: C1, C2, etc.
        ctx.fillStyle = '#ffffff';
        ctx.font = 'bold 9px monospace';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(`C${c + 1}`, cx, cy);
        ctx.restore();
      }
    }
  }

  /**
   * Render MST Prim's step snapshot on canvas
   *
   * @param {HTMLCanvasElement} canvas
   * @param {Array<{x: number, y: number}>} points
   * @param {Object} step Trace step snapshot
   */
  function renderMSTTraceStep(canvas, points, step) {
    if (!canvas || !step) return;
    const { ctx, width, height } = setupCanvas(canvas);
    drawGrid(ctx, width, height);

    const mapper = createExplorerMapper(points, [], width, height, 48);
    const n = points.length;
    const inTreeSet = new Set(step.inTreeVertices || []);
    const isCutApplied = step.type === 'cut_applied';
    const isCutSelection = step.type === 'cut_selection';

    // 1. Draw candidate frontier edges (in faint dotted lines)
    if (!isCutApplied && step.candidateEdges && step.candidateEdges.length) {
      ctx.lineWidth = 1;
      ctx.strokeStyle = EXPLORER_COLORS.candidateEdge;
      ctx.setLineDash([2, 3]);
      ctx.beginPath();
      for (let i = 0; i < step.candidateEdges.length; i++) {
        const edge = step.candidateEdges[i];
        const p1 = points[edge.u];
        const p2 = points[edge.v];
        if (p1 && p2) {
          ctx.moveTo(mapper.toX(p1.x), mapper.toY(p1.y));
          ctx.lineTo(mapper.toX(p2.x), mapper.toY(p2.y));
        }
      }
      ctx.stroke();
      ctx.setLineDash([]);
    }

    // 2. Draw accepted tree edges
    if (step.treeEdges && step.treeEdges.length) {
      for (let i = 0; i < step.treeEdges.length; i++) {
        const edge = step.treeEdges[i];
        const p1 = points[edge.u];
        const p2 = points[edge.v];
        if (!p1 || !p2) continue;

        const x1 = mapper.toX(p1.x);
        const y1 = mapper.toY(p1.y);
        const x2 = mapper.toX(p2.x);
        const y2 = mapper.toY(p2.y);

        if (isCutApplied && edge.isCut) {
          // Draw cut edges very faint dashed red with scissors indicator
          ctx.save();
          ctx.strokeStyle = 'rgba(239, 68, 68, 0.25)';
          ctx.lineWidth = 1.5;
          ctx.setLineDash([4, 4]);
          ctx.beginPath();
          ctx.moveTo(x1, y1);
          ctx.lineTo(x2, y2);
          ctx.stroke();

          // Cut scissors icon in middle
          const mx = (x1 + x2) / 2;
          const my = (y1 + y2) / 2;
          ctx.fillStyle = '#ef4444';
          ctx.font = '10px sans-serif';
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          ctx.fillText('✂', mx, my);
          ctx.restore();
        } else if (isCutSelection && edge.isCut) {
          // Highlight cut selection in bright crimson with thick dashed border
          ctx.save();
          ctx.strokeStyle = EXPLORER_COLORS.cutEdge;
          ctx.lineWidth = 3.5;
          ctx.setLineDash([6, 4]);
          ctx.beginPath();
          ctx.moveTo(x1, y1);
          ctx.lineTo(x2, y2);
          ctx.stroke();

          // Draw weight label badge
          const mx = (x1 + x2) / 2;
          const my = (y1 + y2) / 2;
          ctx.fillStyle = '#ef4444';
          ctx.font = 'bold 10px monospace';
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          ctx.fillText(`CUT: ${edge.weight.toFixed(2)}`, mx, my - 8);
          ctx.restore();
        } else {
          // Standard retained tree edge
          ctx.save();
          if (isCutApplied && step.labels) {
            // Color edge by component cluster
            const cIdx = step.labels[edge.u];
            ctx.strokeStyle = CLUSTER_COLORS[cIdx % CLUSTER_COLORS.length] || EXPLORER_COLORS.treeEdge;
            ctx.lineWidth = 2.4;
          } else {
            ctx.strokeStyle = EXPLORER_COLORS.treeEdge;
            ctx.lineWidth = 2.2;
          }
          ctx.beginPath();
          ctx.moveTo(x1, y1);
          ctx.lineTo(x2, y2);
          ctx.stroke();
          ctx.restore();
        }
      }
    }

    // 3. Highlight currently added edge (if during Prim's step)
    if (step.activeEdge && !isCutApplied && !isCutSelection) {
      const edge = step.activeEdge;
      const p1 = points[edge.u];
      const p2 = points[edge.v];
      if (p1 && p2) {
        ctx.save();
        ctx.strokeStyle = EXPLORER_COLORS.activeEdge;
        ctx.lineWidth = 3.5;
        ctx.beginPath();
        ctx.moveTo(mapper.toX(p1.x), mapper.toY(p1.y));
        ctx.lineTo(mapper.toX(p2.x), mapper.toY(p2.y));
        ctx.stroke();

        // Edge weight callout
        const mx = (mapper.toX(p1.x) + mapper.toX(p2.x)) / 2;
        const my = (mapper.toY(p1.y) + mapper.toY(p2.y)) / 2;
        ctx.fillStyle = '#fbbf24';
        ctx.font = 'bold 10px monospace';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(`w = ${edge.weight.toFixed(3)}`, mx, my - 8);
        ctx.restore();
      }
    }

    // 4. Draw Graph Vertices (Points)
    for (let i = 0; i < n; i++) {
      const pt = points[i];
      const cx = mapper.toX(pt.x);
      const cy = mapper.toY(pt.y);
      const inTree = inTreeSet.has(i);

      ctx.save();
      ctx.beginPath();
      ctx.arc(cx, cy, 7, 0, 2 * Math.PI);

      if (isCutApplied && step.labels) {
        const cIdx = step.labels[i];
        ctx.fillStyle = CLUSTER_COLORS[cIdx % CLUSTER_COLORS.length];
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 2.0;
      } else if (inTree) {
        ctx.fillStyle = (i === 0 && step.type === 'prim_init') ? '#f59e0b' : EXPLORER_COLORS.inTreeVertex;
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 1.8;
      } else {
        ctx.fillStyle = EXPLORER_COLORS.unvisitedVertex;
        ctx.strokeStyle = '#64748b';
        ctx.lineWidth = 1.2;
      }

      ctx.fill();
      ctx.stroke();

      // Vertex Index inside circle
      ctx.fillStyle = '#ffffff';
      ctx.font = 'bold 9px monospace';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(i.toString(), cx, cy);
      ctx.restore();
    }
  }

  window.MSTKMeans.ExplorerRenderer = {
    renderKMeansTraceStep,
    renderMSTTraceStep
  };
})(window);
