/**
 * MST vs K-Means Robustness Analysis
 * Module: Euclidean Minimum Spanning Tree (MST) Clustering
 * Pure Vanilla JavaScript - No dependencies
 */

(function (window) {
  'use strict';

  window.MSTKMeans = window.MSTKMeans || {};

  /**
   * Disjoint Set Union (Union-Find) with path compression and rank optimization
   */
  class DisjointSet {
    constructor(size) {
      this.parent = new Int32Array(size);
      this.rank = new Int32Array(size);
      this.count = size;
      for (let i = 0; i < size; i++) {
        this.parent[i] = i;
      }
    }

    find(i) {
      let root = i;
      while (root !== this.parent[root]) {
        root = this.parent[root];
      }
      // Path compression
      let curr = i;
      while (curr !== root) {
        const next = this.parent[curr];
        this.parent[curr] = root;
        curr = next;
      }
      return root;
    }

    union(i, j) {
      const rootI = this.find(i);
      const rootJ = this.find(j);
      if (rootI === rootJ) return false;

      if (this.rank[rootI] < this.rank[rootJ]) {
        this.parent[rootI] = rootJ;
      } else if (this.rank[rootI] > this.rank[rootJ]) {
        this.parent[rootJ] = rootI;
      } else {
        this.parent[rootJ] = rootI;
        this.rank[rootI]++;
      }
      this.count--;
      return true;
    }
  }

  /**
   * Euclidean distance between two points
   */
  function euclideanDist(p1, p2) {
    const dx = p1.x - p2.x;
    const dy = p1.y - p2.y;
    return Math.sqrt(dx * dx + dy * dy);
  }

  /**
   * Compute Euclidean Minimum Spanning Tree using Prim's algorithm
   * Optimal O(N^2) time and O(N) space for dense complete Euclidean graphs
   * @param {Array<{x: number, y: number}>} points
   * @returns {Array<{id: number, u: number, v: number, weight: number}>}
   */
  function computeEuclideanMST(points) {
    const n = points.length;
    if (n < 2) return [];

    const minDist = new Float64Array(n).fill(Infinity);
    const parent = new Int32Array(n).fill(-1);
    const inTree = new Uint8Array(n);

    // Start with root at index 0
    minDist[0] = 0;
    const edges = [];

    for (let step = 0; step < n; step++) {
      // Find unvisited vertex with smallest minDist
      let u = -1;
      let minVal = Infinity;
      for (let i = 0; i < n; i++) {
        if (!inTree[i] && minDist[i] < minVal) {
          minVal = minDist[i];
          u = i;
        }
      }

      if (u === -1) break; // Should not happen in connected complete graph
      inTree[u] = 1;

      if (step > 0) {
        const p = parent[u];
        edges.push({
          id: step - 1,
          u: p,
          v: u,
          weight: minVal,
          isCut: false
        });
      }

      // Relax distances to all unvisited neighbors
      const pu = points[u];
      for (let v = 0; v < n; v++) {
        if (!inTree[v]) {
          const d = euclideanDist(pu, points[v]);
          if (d < minDist[v]) {
            minDist[v] = d;
            parent[v] = u;
          }
        }
      }
    }

    return edges;
  }

  /**
   * Execute MST-based clustering:
   * 1. Build Euclidean MST
   * 2. Remove the K - 1 longest edges
   * 3. Compute connected components
   * @param {Array<{x: number, y: number}>} points
   * @param {number} k Number of clusters
   * @returns {Object} MST clustering result
   */
  function runMSTClustering(points, k) {
    const startTime = performance.now();
    const n = points.length;

    if (n === 0) {
      return {
        labels: [],
        mstEdges: [],
        cutEdges: [],
        totalWeight: 0,
        k: 0,
        runtimeMs: 0
      };
    }

    const actualK = Math.max(1, Math.min(Math.floor(k), n));

    if (n === 1) {
      return {
        labels: [0],
        mstEdges: [],
        cutEdges: [],
        totalWeight: 0,
        k: 1,
        runtimeMs: performance.now() - startTime
      };
    }

    // 1. Build MST
    const mstEdges = computeEuclideanMST(points);
    let totalWeight = 0;
    for (let i = 0; i < mstEdges.length; i++) {
      totalWeight += mstEdges[i].weight;
    }

    // 2. Identify the K - 1 longest edges to cut
    // Sort a shallow copy by weight descending with deterministic secondary tie-break on edge id
    const sortedEdges = [...mstEdges].sort((a, b) => (b.weight - a.weight) || (a.id - b.id));
    const cutCount = Math.max(0, Math.min(actualK - 1, mstEdges.length));
    const cutEdges = [];

    const cutSet = new Set();
    for (let i = 0; i < cutCount; i++) {
      cutSet.add(sortedEdges[i].id);
      cutEdges.push(sortedEdges[i]);
    }

    // Flag isCut on the original edge records
    for (let i = 0; i < mstEdges.length; i++) {
      mstEdges[i].isCut = cutSet.has(mstEdges[i].id);
    }

    // 3. Form connected components using Disjoint Set Union
    const dsu = new DisjointSet(n);
    for (let i = 0; i < mstEdges.length; i++) {
      const edge = mstEdges[i];
      if (!edge.isCut) {
        dsu.union(edge.u, edge.v);
      }
    }

    // Map each root to a compact component label [0 ... actualK - 1]
    // Count sizes of components to assign labels by component size descending
    const rootCounts = new Map();
    for (let i = 0; i < n; i++) {
      const root = dsu.find(i);
      rootCounts.set(root, (rootCounts.get(root) || 0) + 1);
    }

    // Sort roots by component size descending for stable, consistent coloring (tie-break on root index)
    const sortedRoots = Array.from(rootCounts.keys()).sort((a, b) => {
      const diff = rootCounts.get(b) - rootCounts.get(a);
      return diff !== 0 ? diff : a - b;
    });

    const rootToCluster = new Map();
    sortedRoots.forEach((root, idx) => {
      rootToCluster.set(root, idx);
    });

    const labels = new Array(n);
    for (let i = 0; i < n; i++) {
      const root = dsu.find(i);
      labels[i] = rootToCluster.get(root);
    }

    const runtimeMs = performance.now() - startTime;

    return {
      labels,
      mstEdges,
      cutEdges,
      totalWeight,
      k: sortedRoots.length,
      runtimeMs
    };
  }

  /**
   * Generate step-by-step execution trace of MST construction and cluster cutting.
   * Every snapshot represents an authentic computational state.
   *
   * @param {Array<{x: number, y: number}>} points Point array
   * @param {number} k Number of clusters
   * @returns {{steps: Array<Object>, finalResult: Object}}
   */
  function generateMSTTrace(points, k) {
    const startTime = performance.now();
    const n = points.length;

    if (n === 0) {
      return {
        steps: [{
          stepIndex: 0,
          type: 'prim_init',
          inTreeVertices: [],
          treeEdges: [],
          candidateEdges: [],
          totalWeight: 0,
          cutEdges: [],
          retainedEdges: [],
          labels: [],
          explanation: 'Empty dataset: No vertices to span.'
        }],
        finalResult: {
          labels: [],
          mstEdges: [],
          cutEdges: [],
          totalWeight: 0,
          k: 0,
          runtimeMs: 0
        }
      };
    }

    const actualK = Math.max(1, Math.min(Math.floor(k), n));

    if (n === 1) {
      return {
        steps: [{
          stepIndex: 0,
          type: 'mst_complete',
          inTreeVertices: [0],
          treeEdges: [],
          candidateEdges: [],
          totalWeight: 0,
          cutEdges: [],
          retainedEdges: [],
          labels: [0],
          explanation: 'Single vertex: Spanning tree requires 0 edges.'
        }],
        finalResult: {
          labels: [0],
          mstEdges: [],
          cutEdges: [],
          totalWeight: 0,
          k: 1,
          runtimeMs: performance.now() - startTime
        }
      };
    }

    const minDist = new Float64Array(n).fill(Infinity);
    const parent = new Int32Array(n).fill(-1);
    const inTree = new Uint8Array(n);
    const steps = [];

    // Root at vertex 0
    minDist[0] = 0;
    const treeEdges = [];
    const inTreeList = [];

    // Step 0: Root vertex initialization
    inTree[0] = 1;
    inTreeList.push(0);

    // Initial relaxation from vertex 0 to all neighbors
    const candidateEdges = [];
    for (let v = 1; v < n; v++) {
      const d = euclideanDist(points[0], points[v]);
      minDist[v] = d;
      parent[v] = 0;
      candidateEdges.push({ u: 0, v, weight: d });
    }

    steps.push({
      stepIndex: 0,
      type: 'prim_init',
      root: 0,
      inTreeVertices: [...inTreeList],
      treeEdges: [],
      candidateEdges: candidateEdges.map(e => ({ ...e })),
      activeEdge: null,
      totalWeight: 0,
      cutEdges: [],
      retainedEdges: [],
      labels: new Array(n).fill(-1),
      explanation: `Step 1 — Prim's Root Initialization: Seeded spanning tree at vertex 0. Evaluated initial Euclidean distances to all ${n - 1} unvisited vertices.`
    });

    // Step 1 to n - 1: Greedily add shortest edge connecting tree to an unvisited vertex
    let runningWeight = 0;
    for (let step = 1; step < n; step++) {
      let u = -1;
      let minVal = Infinity;
      for (let i = 0; i < n; i++) {
        if (!inTree[i] && minDist[i] < minVal) {
          minVal = minDist[i];
          u = i;
        }
      }

      if (u === -1) break;
      const p = parent[u];
      inTree[u] = 1;
      inTreeList.push(u);

      const newEdge = {
        id: step - 1,
        u: p,
        v: u,
        weight: minVal,
        isCut: false
      };
      treeEdges.push(newEdge);
      runningWeight += minVal;

      // Relax distances from the newly added vertex u to remaining unvisited vertices
      const currentCandidates = [];
      const pu = points[u];
      for (let v = 0; v < n; v++) {
        if (!inTree[v]) {
          const d = euclideanDist(pu, points[v]);
          if (d < minDist[v]) {
            minDist[v] = d;
            parent[v] = u;
          }
          currentCandidates.push({ u: parent[v], v, weight: minDist[v] });
        }
      }

      steps.push({
        stepIndex: steps.length,
        type: 'prim_step',
        stepNumber: step,
        addedEdge: { ...newEdge },
        inTreeVertices: [...inTreeList],
        treeEdges: treeEdges.map(e => ({ ...e })),
        candidateEdges: currentCandidates.map(e => ({ ...e })),
        activeEdge: { ...newEdge },
        totalWeight: runningWeight,
        cutEdges: [],
        retainedEdges: treeEdges.map(e => ({ ...e })),
        labels: new Array(n).fill(-1),
        explanation: `Prim's Construction Step ${step}/${n - 1}: Accepted shortest frontier edge (${newEdge.u} ↔ ${newEdge.v}, weight: ${newEdge.weight.toFixed(3)}). Tree now connects ${inTreeList.length} vertices with cumulative weight ${runningWeight.toFixed(3)}.`
      });
    }

    // Spanning tree complete snapshot
    steps.push({
      stepIndex: steps.length,
      type: 'mst_complete',
      inTreeVertices: [...inTreeList],
      treeEdges: treeEdges.map(e => ({ ...e })),
      candidateEdges: [],
      activeEdge: null,
      totalWeight: runningWeight,
      cutEdges: [],
      retainedEdges: treeEdges.map(e => ({ ...e })),
      labels: new Array(n).fill(0),
      explanation: `Minimum Spanning Tree Complete: Exactly ${n - 1} Euclidean edges connect all ${n} vertices with minimal total weight (${runningWeight.toFixed(3)}). Ready for K-cluster partitioning.`
    });

    // 2. Identify the K - 1 longest edges to cut (deterministic tie-break on edge id)
    const sortedEdges = [...treeEdges].sort((a, b) => (b.weight - a.weight) || (a.id - b.id));
    const cutCount = Math.max(0, Math.min(actualK - 1, treeEdges.length));
    const cutEdges = [];
    const cutSet = new Set();

    for (let i = 0; i < cutCount; i++) {
      cutSet.add(sortedEdges[i].id);
      cutEdges.push(sortedEdges[i]);
    }

    for (let i = 0; i < treeEdges.length; i++) {
      treeEdges[i].isCut = cutSet.has(treeEdges[i].id);
    }

    const retainedEdges = treeEdges.filter(e => !e.isCut);

    if (cutCount > 0) {
      // Step: Cut selection preview
      steps.push({
        stepIndex: steps.length,
        type: 'cut_selection',
        inTreeVertices: [...inTreeList],
        treeEdges: treeEdges.map(e => ({ ...e })),
        candidateEdges: [],
        activeEdge: null,
        totalWeight: runningWeight,
        cutEdges: cutEdges.map(e => ({ ...e })),
        retainedEdges: retainedEdges.map(e => ({ ...e })),
        labels: new Array(n).fill(0),
        explanation: `Cluster Partitioning: Identified the ${cutCount} longest edge(s) in the MST for removal: [${cutEdges.map(e => `(${e.u}↔${e.v}: ${e.weight.toFixed(3)})`).join(', ')}]. Cutting these will decompose the tree into ${actualK} components.`
      });
    }

    // 3. Form connected components using Disjoint Set Union
    const dsu = new DisjointSet(n);
    for (let i = 0; i < treeEdges.length; i++) {
      const edge = treeEdges[i];
      if (!edge.isCut) {
        dsu.union(edge.u, edge.v);
      }
    }

    const rootCounts = new Map();
    for (let i = 0; i < n; i++) {
      const root = dsu.find(i);
      rootCounts.set(root, (rootCounts.get(root) || 0) + 1);
    }

    const sortedRoots = Array.from(rootCounts.keys()).sort((a, b) => {
      const diff = rootCounts.get(b) - rootCounts.get(a);
      return diff !== 0 ? diff : a - b;
    });

    const rootToCluster = new Map();
    sortedRoots.forEach((root, idx) => {
      rootToCluster.set(root, idx);
    });

    const labels = new Array(n);
    for (let i = 0; i < n; i++) {
      const root = dsu.find(i);
      labels[i] = rootToCluster.get(root);
    }

    // Step: Final cut applied and components colored
    steps.push({
      stepIndex: steps.length,
      type: 'cut_applied',
      inTreeVertices: [...inTreeList],
      treeEdges: treeEdges.map(e => ({ ...e })),
      candidateEdges: [],
      activeEdge: null,
      totalWeight: runningWeight,
      cutEdges: cutEdges.map(e => ({ ...e })),
      retainedEdges: retainedEdges.map(e => ({ ...e })),
      labels: Array.from(labels),
      k: sortedRoots.length,
      explanation: `Clustering Complete: Removed ${cutCount} longest edge(s). Graph is partitioned into ${sortedRoots.length} connected components. Vertices are colored by cluster.`
    });

    const runtimeMs = performance.now() - startTime;

    return {
      steps,
      finalResult: {
        labels: Array.from(labels),
        mstEdges: treeEdges,
        cutEdges,
        totalWeight: runningWeight,
        k: sortedRoots.length,
        runtimeMs
      }
    };
  }

  window.MSTKMeans.MST = {
    computeEuclideanMST,
    runMSTClustering,
    generateMSTTrace,
    DisjointSet,
    euclideanDist
  };
})(window);
