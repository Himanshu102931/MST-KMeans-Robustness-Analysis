"""
clustering_lab.algorithms.mst
=============================
Independent, from-scratch implementation of Euclidean Minimum Spanning Tree (MST)
clustering using Prim's algorithm, deterministic tie-breaking, and Union-Find.

Academic Context:
    Course: Pattern Matching Lab (BCS-DS-777)
    Project: MST vs K-Means Robustness Analysis
    Authors: Himanshu Gupta ([REDACTED_STUDENT_IDENTIFIER]) & Parth Yadav ([REDACTED_STUDENT_IDENTIFIER])
    Institution: MRIIRS, School of Engineering & Technology (2026–2027)

Design & Implementation Principles:
    - Complete Euclidean Graph representation: every observation is a vertex;
      edge weights correspond to Euclidean distances ||X_u - X_v||_2.
    - Dense Prim's algorithm achieving O(N^2) time and O(N) auxiliary space.
    - Zero-weight edges for coincident / duplicated observations are natively supported.
    - Deterministic tie-breaking on vertex relaxation and longest-edge cutting.
    - Single-linkage graph cut: cutting the (k - 1) longest tree edges creates
      exactly k connected components.
    - Disjoint Set Union (Union-Find) with path compression and rank optimization.
    - Explicit separation of total MST weight and retained forest weight.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple
import numpy as np


@dataclass(frozen=True)
class MSTEdge:
    """Representation of an undirected edge in the Minimum Spanning Tree.

    Attributes:
        edge_id: Original sequential identifier assigned during Prim construction.
        u: Index of the source vertex in the observation array X.
        v: Index of the destination vertex in the observation array X.
        weight: Euclidean distance ||X_u - X_v||_2.
        is_cut: Boolean flag indicating if this edge was removed to form clusters.
    """

    edge_id: int
    u: int
    v: int
    weight: float
    is_cut: bool


@dataclass(frozen=True)
class MSTClusteringResult:
    """Immutable result object produced by Euclidean MST clustering.

    Attributes:
        labels: 1D array of shape (N,) containing integer cluster labels in [0, k-1].
        mst_edges: Complete list of N - 1 MST edges before cutting (for N >= 2).
        cut_edges: List of k - 1 longest edges that were removed during partitioning.
        total_mst_weight: Sum of weights of all N - 1 edges in the uncut MST.
        retained_weight: Sum of weights of edges remaining in the clustered forest.
        k: Number of connected components (clusters).
        n_samples: Total number of observations N.
    """

    labels: np.ndarray
    mst_edges: List[MSTEdge]
    cut_edges: List[MSTEdge]
    total_mst_weight: float
    retained_weight: float
    k: int
    n_samples: int


class _DisjointSet:
    """Disjoint Set Union (DSU / Union-Find) with path compression and union by rank."""

    def __init__(self, size: int) -> None:
        self.parent = np.arange(size, dtype=np.int32)
        self.rank = np.zeros(size, dtype=np.int32)
        self.num_components = size

    def find(self, i: int) -> int:
        """Find representative root of element i with full path compression."""
        root = i
        while root != self.parent[root]:
            root = int(self.parent[root])

        # Second pass: compress path
        curr = i
        while curr != root:
            next_node = int(self.parent[curr])
            self.parent[curr] = root
            curr = next_node
        return root

    def union(self, i: int, j: int) -> bool:
        """Merge sets containing i and j. Returns True if merged, False if already connected."""
        root_i = self.find(i)
        root_j = self.find(j)
        if root_i == root_j:
            return False

        # Union by rank
        if self.rank[root_i] < self.rank[root_j]:
            self.parent[root_i] = root_j
        elif self.rank[root_i] > self.rank[root_j]:
            self.parent[root_j] = root_i
        else:
            self.parent[root_j] = root_i
            self.rank[root_i] += 1

        self.num_components -= 1
        return True


def _validate_input_data(X: np.ndarray, k: int) -> Tuple[np.ndarray, int]:
    """Validate numerical array and target cluster count k."""
    if not isinstance(k, (int, np.integer)):
        raise TypeError(f"Number of clusters 'k' must be an integer, got {type(k).__name__}.")
    k = int(k)

    try:
        X_arr = np.asarray(X, dtype=np.float64)
    except (ValueError, TypeError) as exc:
        raise ValueError(f"Input X could not be converted to float64 array: {exc}") from exc

    if X_arr.ndim != 2:
        raise ValueError(f"Input X must be a 2D array of shape (N, D), got {X_arr.ndim}D shape {X_arr.shape}.")

    n_samples, n_features = X_arr.shape
    if n_samples < 1:
        raise ValueError(f"Input array X must contain at least 1 sample, got shape {X_arr.shape}.")
    if n_features < 1:
        raise ValueError(f"Input array X must contain at least 1 feature dimension, got shape {X_arr.shape}.")

    if not np.isfinite(X_arr).all():
        raise ValueError("Input array X contains non-finite values (NaN or Inf). Only finite numerical values are permitted.")

    if k < 1:
        raise ValueError(f"Number of clusters 'k' must be at least 1, got {k}.")
    if k > n_samples:
        raise ValueError(f"Number of clusters 'k' ({k}) cannot exceed number of samples N ({n_samples}).")

    return X_arr.copy(), k


def _compute_euclidean_mst_prim(X: np.ndarray) -> List[Tuple[int, int, float]]:
    """Compute Euclidean Minimum Spanning Tree using dense Prim's algorithm.

    Complexity:
        Time: O(N^2)
        Space: O(N) auxiliary space (no dense N x N matrix stored in memory)

    Deterministic Tie-Breaking:
        When multiple unvisited vertices have identical minimum distance to the growing tree,
        the vertex with the lowest index is selected.

    Returns:
        List of tuples (u, v, weight) representing the N - 1 tree edges.
    """
    n_samples = X.shape[0]
    if n_samples < 2:
        return []

    min_dist = np.full(n_samples, np.inf, dtype=np.float64)
    parent = np.full(n_samples, -1, dtype=np.int32)
    in_tree = np.zeros(n_samples, dtype=bool)

    # Root Prim's tree at index 0
    min_dist[0] = 0.0
    mst_edges: List[Tuple[int, int, float]] = []

    for step in range(n_samples):
        # 1. Identify unvisited vertex u with minimal min_dist[u]
        # Deterministic: lowest index wins when distances are equal
        unvisited_indices = np.where(~in_tree)[0]
        unvisited_dists = min_dist[unvisited_indices]
        min_val = np.min(unvisited_dists)

        # In case of tie, select the first unvisited index achieving min_val
        tied_candidates = unvisited_indices[unvisited_dists == min_val]
        u = int(tied_candidates[0])

        in_tree[u] = True

        if step > 0:
            p = int(parent[u])
            mst_edges.append((p, u, float(min_val)))

        # 2. Relax distances to all unvisited neighbors
        unvisited_mask = ~in_tree
        if np.any(unvisited_mask):
            unvisited_nodes = np.where(unvisited_mask)[0]
            # Compute Euclidean distances from u to all unvisited nodes
            dists = np.linalg.norm(X[unvisited_nodes] - X[u], axis=1)

            for node, dist_val in zip(unvisited_nodes, dists):
                if dist_val < min_dist[node]:
                    min_dist[node] = dist_val
                    parent[node] = u
                elif dist_val == min_dist[node] and u < parent[node]:
                    # Deterministic secondary tie-break: prefer lower parent index
                    parent[node] = u

    return mst_edges


def mst_clustering(X: np.ndarray, k: int) -> MSTClusteringResult:
    """Perform Euclidean MST clustering by cutting the (k - 1) longest tree edges.

    Mathematical Method:
        1. Models X as a complete Euclidean weighted graph G = (V, E).
        2. Constructs the exact Minimum Spanning Tree T = (V, E_T) with |E_T| = N - 1
           using dense Prim's algorithm.
        3. Identifies the k - 1 longest edges in E_T and removes them.
           This corresponds to a single-linkage hierarchical clustering cut at threshold
           equal to the (k - 1)-th longest edge weight.
        4. Partitions V into k connected components via Disjoint Set Union.

    Deterministic Tie-Breaking on Cuts:
        When edge weights are tied, secondary sorting criteria are:
            (weight DESC, min(u, v) ASC, max(u, v) ASC, edge_id ASC)
        guaranteeing stable, deterministic cuts across platforms.

    Label Assignment:
        Components are canonically indexed from 0 to k - 1 in descending order
        of component cardinality (cluster size). In case of identical size,
        the component containing the smaller minimum vertex index receives
        the lower label.

    Args:
        X: Feature array of shape (N, D).
        k: Desired number of clusters (1 <= k <= N).

    Returns:
        MSTClusteringResult containing labels, edge lists, and weights.
    """
    X_clean, k_val = _validate_input_data(X, k)
    n_samples = X_clean.shape[0]

    # Special case: N = 1
    if n_samples == 1:
        return MSTClusteringResult(
            labels=np.zeros(1, dtype=np.int32),
            mst_edges=[],
            cut_edges=[],
            total_mst_weight=0.0,
            retained_weight=0.0,
            k=1,
            n_samples=1,
        )

    # 1. Build MST using Prim's algorithm
    raw_edges = _compute_euclidean_mst_prim(X_clean)
    total_mst_weight = float(sum(w for _, _, w in raw_edges))

    # 2. Sort edges to identify the (k - 1) longest edges to remove
    # Secondary tie-break: lower vertex indices, then edge creation order
    # To sort by weight DESC, we negate the weight in the sort key
    edge_records: List[dict] = []
    for edge_id, (u, v, w) in enumerate(raw_edges):
        u_norm, v_norm = min(u, v), max(u, v)
        edge_records.append({
            "edge_id": edge_id,
            "u": u,
            "v": v,
            "weight": w,
            "u_norm": u_norm,
            "v_norm": v_norm,
        })

    # Sort descending by weight, then ascending by u_norm, v_norm, edge_id
    sorted_records = sorted(
        edge_records,
        key=lambda r: (-r["weight"], r["u_norm"], r["v_norm"], r["edge_id"]),
    )

    cut_count = k_val - 1
    cut_edge_ids = {r["edge_id"] for r in sorted_records[:cut_count]}

    # Build final MSTEdge objects
    constructed_mst_edges: List[MSTEdge] = []
    constructed_cut_edges: List[MSTEdge] = []
    retained_weight = 0.0

    for rec in edge_records:
        is_cut = rec["edge_id"] in cut_edge_ids
        edge_obj = MSTEdge(
            edge_id=rec["edge_id"],
            u=rec["u"],
            v=rec["v"],
            weight=rec["weight"],
            is_cut=is_cut,
        )
        constructed_mst_edges.append(edge_obj)
        if is_cut:
            constructed_cut_edges.append(edge_obj)
        else:
            retained_weight += rec["weight"]

    # 3. Form connected components using Disjoint Set Union
    dsu = _DisjointSet(n_samples)
    for edge in constructed_mst_edges:
        if not edge.is_cut:
            dsu.union(edge.u, edge.v)

    # 4. Map components to canonical labels [0, ..., k - 1]
    # Collect members for each root
    component_members: dict[int, list[int]] = {}
    for i in range(n_samples):
        root = dsu.find(i)
        if root not in component_members:
            component_members[root] = []
        component_members[root].append(i)

    # Sort roots: primary by size DESC, secondary by min vertex index ASC
    sorted_roots = sorted(
        component_members.keys(),
        key=lambda r: (-len(component_members[r]), min(component_members[r])),
    )

    root_to_label = {root: label for label, root in enumerate(sorted_roots)}
    labels = np.array([root_to_label[dsu.find(i)] for i in range(n_samples)], dtype=np.int32)

    return MSTClusteringResult(
        labels=labels,
        mst_edges=constructed_mst_edges,
        cut_edges=constructed_cut_edges,
        total_mst_weight=total_mst_weight,
        retained_weight=retained_weight,
        k=len(sorted_roots),
        n_samples=n_samples,
    )


class MSTClustering:
    """Object-oriented estimator interface for Euclidean MST clustering.

    Conforms to standard estimator patterns (fit, fit_predict).
    """

    def __init__(self, n_clusters: int = 2) -> None:
        self.n_clusters = n_clusters

        # Fitted attributes
        self.labels_: Optional[np.ndarray] = None
        self.mst_edges_: Optional[List[MSTEdge]] = None
        self.cut_edges_: Optional[List[MSTEdge]] = None
        self.total_mst_weight_: Optional[float] = None
        self.retained_weight_: Optional[float] = None
        self.k_: Optional[int] = None
        self.n_samples_: Optional[int] = None

    def fit(self, X: np.ndarray) -> "MSTClustering":
        """Fit Euclidean MST clustering model to feature array X."""
        result = mst_clustering(X=X, k=self.n_clusters)
        self.labels_ = result.labels
        self.mst_edges_ = result.mst_edges
        self.cut_edges_ = result.cut_edges
        self.total_mst_weight_ = result.total_mst_weight
        self.retained_weight_ = result.retained_weight
        self.k_ = result.k
        self.n_samples_ = result.n_samples
        return self

    def fit_predict(self, X: np.ndarray) -> np.ndarray:
        """Fit model and return cluster assignments."""
        return self.fit(X).labels_
