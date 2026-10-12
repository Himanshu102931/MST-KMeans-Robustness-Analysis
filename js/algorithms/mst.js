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

    // Assemble the N - 1 MST edges
    const edges = [];
    for (let i = 1; i < n; i++) {
      const u = parent[i];
      const v = i;
      edges.push({
        id: i - 1,
        u,
        v,
        weight: euclideanDist(points[u], points[v]),
        isCut: false
      });
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
    // Sort a shallow copy by weight descending
    const sortedEdges = [...mstEdges].sort((a, b) => b.weight - a.weight);
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

    // Sort roots by component size descending for stable, consistent coloring
    const sortedRoots = Array.from(rootCounts.keys()).sort((a, b) => {
      return rootCounts.get(b) - rootCounts.get(a);
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

  window.MSTKMeans.MST = {
    computeEuclideanMST,
    runMSTClustering,
    DisjointSet,
    euclideanDist
  };
})(window);
