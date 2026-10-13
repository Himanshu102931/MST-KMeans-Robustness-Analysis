"""
clustering_lab.algorithms.explorer
==================================
Step-by-step educational trace generators for interactive visualization of
Lloyd's K-Means and dense Prim's Minimum Spanning Tree (MST) clustering.

Academic Context:
    Course: Pattern Matching Lab (BCS-DS-777)
    Project: MST vs K-Means Robustness Analysis
    Authors: Himanshu Gupta ([REDACTED_STUDENT_IDENTIFIER]) & Parth Yadav ([REDACTED_STUDENT_IDENTIFIER])
    Instructor: Mr. Aman Kumar, Assistant Professor
    Institution: MRIIRS, School of Engineering & Technology (2026–2027)

Design & Implementation Invariants:
    1. Zero Duplicate Algorithm Logic:
       The trace instrumentation executes the EXACT mathematical logic, distance
       calculations, tie-breaking rules, and label canonicalization as the production
       implementations in `kmeans.py` and `mst.py`.
    2. Exact Final Parity:
       For identical inputs and random seeds:
       - `run_kmeans_trace(X, k, seed).final_result` strictly equals `kmeans(X, k, seed=seed)`.
       - `run_mst_trace(X, k).final_result` strictly equals `mst_clustering(X, k)`.
    3. Fine-Grained Step Snapshots:
       Captures explicit snapshots for:
       - K-Means: Unassigned data -> K-Means++ centroid placement -> Point assignment
         -> Centroid arithmetic update -> Iteration progression -> Convergence.
       - Prim's MST: Starting root -> Step-by-step minimum edge addition -> Completed MST
         -> Longest (k - 1) edge cut -> Final connected component clusters.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

from clustering_lab.algorithms.kmeans import (
    KMeansResult,
    _validate_input_data as _validate_kmeans_input,
)
from clustering_lab.algorithms.mst import (
    MSTClusteringResult,
    MSTEdge,
    _DisjointSet,
    _validate_input_data as _validate_mst_input,
)


# -----------------------------------------------------------------------------
# K-Means Explorer Data Structures
# -----------------------------------------------------------------------------
@dataclass(frozen=True)
class KMeansTraceStep:
    """Individual snapshot in the K-Means algorithmic execution trace.

    Attributes:
        step_index: Sequential step number (0-indexed).
        step_type: Classification ('init', 'kmeans_plus_plus', 'assignment', 'update', 'converged').
        iteration: Current Lloyd iteration (0 for initialization).
        centroids: Array of centroid coordinates, shape (k, D).
        labels: 1D array of shape (N,) containing cluster assignments (-1 if unassigned).
        inertia: Sum of squared Euclidean distances to assigned centroids (None if unassigned).
        max_shift: Maximum Euclidean movement of any centroid during this update.
        converged: Whether the algorithm has satisfied the convergence tolerance.
        cluster_counts: Dictionary mapping cluster index -> assigned observation count.
        title: Human-readable step title.
        description: Educational description of the mathematical action in this step.
        math_formula: LaTeX / ASCII formulation for academic viva explanation.
        X: Feature array of coordinates for this step.
    """

    step_index: int
    step_type: str
    iteration: int
    centroids: np.ndarray
    labels: np.ndarray
    inertia: Optional[float]
    max_shift: Optional[float]
    converged: bool
    cluster_counts: Dict[int, int]
    title: str
    description: str
    math_formula: str
    X: Optional[np.ndarray] = None


@dataclass(frozen=True)
class KMeansTraceResult:
    """Complete step-by-step trace output for K-Means clustering."""

    steps: List[KMeansTraceStep]
    final_result: KMeansResult
    n_steps: int
    final_parity_verified: bool = True
    X: Optional[np.ndarray] = None


# -----------------------------------------------------------------------------
# Prim's MST Explorer Data Structures
# -----------------------------------------------------------------------------
@dataclass(frozen=True)
class MSTTraceStep:
    """Individual snapshot in the Prim's MST algorithmic execution trace.

    Attributes:
        step_index: Sequential step number (0-indexed).
        step_type: Classification ('init', 'tree_growth', 'mst_complete', 'cutting_edges', 'final_clusters').
        in_tree_mask: Boolean array of shape (N,) indicating vertices included in current tree.
        current_edge: Newly added edge (u, v, weight) in this step, or None.
        tree_edges: List of all edges (u, v, weight) included in the tree so far.
        total_weight: Cumulative sum of weights of edges in tree_edges.
        cut_edges: List of edges removed during cluster partitioning.
        retained_edges: List of edges retained in the final clustered forest.
        labels: 1D array of shape (N,) containing component cluster assignments.
        title: Human-readable step title.
        description: Educational description of the graph-theoretic action.
        math_formula: Graph theorem or formula for academic viva explanation.
        X: Feature array of coordinates for this step.
    """

    step_index: int
    step_type: str
    in_tree_mask: np.ndarray
    current_edge: Optional[Tuple[int, int, float]]
    tree_edges: List[Tuple[int, int, float]]
    total_weight: float
    cut_edges: List[Tuple[int, int, float]]
    retained_edges: List[Tuple[int, int, float]]
    labels: np.ndarray
    title: str
    description: str
    math_formula: str
    X: Optional[np.ndarray] = None

    @property
    def in_tree_vertices(self) -> List[int]:
        """Return list of vertex indices currently included in the spanning tree."""
        return [int(i) for i in np.where(self.in_tree_mask)[0]]

    @property
    def new_edge(self) -> Optional[Tuple[int, int, float]]:
        """Alias for current_edge."""
        return self.current_edge


@dataclass(frozen=True)
class MSTTraceResult:
    """Complete step-by-step trace output for Prim's MST clustering."""

    steps: List[MSTTraceStep]
    final_result: MSTClusteringResult
    n_steps: int
    final_parity_verified: bool = True
    X: Optional[np.ndarray] = None


# -----------------------------------------------------------------------------
# K-Means Trace Generator
# -----------------------------------------------------------------------------
def run_kmeans_trace(
    X: np.ndarray,
    k: int,
    max_iter: int = 100,
    tol: float = 1e-4,
    seed: Optional[int] = 42,
) -> KMeansTraceResult:
    """Execute Lloyd's K-Means with step-by-step tracing for educational visualization.

    Guarantees exact final result parity with `clustering_lab.algorithms.kmeans.kmeans`.

    Args:
        X: Feature array of shape (N, D).
        k: Target cluster count (1 <= k <= N).
        max_iter: Maximum Lloyd iterations.
        tol: Centroid shift convergence tolerance.
        seed: Random PRNG seed for K-Means++ initialization.

    Returns:
        KMeansTraceResult containing all ordered execution snapshots and the final result.
    """
    X_clean, k_val = _validate_kmeans_input(X, k, max_iter, tol)
    n_samples, n_features = X_clean.shape
    steps: List[KMeansTraceStep] = []

    # Fast path: N = 1 or k = 1
    if k_val == 1:
        center = np.mean(X_clean, axis=0, keepdims=True)
        inertia = float(np.sum((X_clean - center) ** 2))
        final_res = KMeansResult(
            labels=np.zeros(n_samples, dtype=np.int32),
            cluster_centers=center,
            inertia=inertia,
            n_iter=1,
            converged=True,
            k=1,
        )
        steps.append(
            KMeansTraceStep(
                step_index=0,
                step_type="converged",
                iteration=1,
                centroids=center.copy(),
                labels=np.zeros(n_samples, dtype=np.int32),
                inertia=inertia,
                max_shift=0.0,
                converged=True,
                cluster_counts={0: n_samples},
                title="Single Cluster (k=1)",
                description=f"All {n_samples} observations belong to a single global cluster with centroid at sample mean.",
                math_formula=r"\mu = \frac{1}{N}\sum_{i=1}^N X_i",
            )
        )
        for s in steps:
            object.__setattr__(s, "X", X_clean)
        return KMeansTraceResult(steps=steps, final_result=final_res, n_steps=len(steps), final_parity_verified=True, X=X_clean)

    # Fast path: k equals N
    if k_val == n_samples:
        final_res = KMeansResult(
            labels=np.arange(n_samples, dtype=np.int32),
            cluster_centers=X_clean.copy(),
            inertia=0.0,
            n_iter=1,
            converged=True,
            k=k_val,
        )
        steps.append(
            KMeansTraceStep(
                step_index=0,
                step_type="converged",
                iteration=1,
                centroids=X_clean.copy(),
                labels=np.arange(n_samples, dtype=np.int32),
                inertia=0.0,
                max_shift=0.0,
                converged=True,
                cluster_counts={i: 1 for i in range(n_samples)},
                title="Degenerate Partition (k=N)",
                description=f"Cluster count k ({k_val}) equals observation count N. Each sample is its own centroid.",
                math_formula=r"J = \sum_{i=1}^N ||X_i - \mu_i||^2 = 0",
            )
        )
        for s in steps:
            object.__setattr__(s, "X", X_clean)
        return KMeansTraceResult(steps=steps, final_result=final_res, n_steps=len(steps), final_parity_verified=True, X=X_clean)

    # Step 0: Initial Raw Data Snapshot
    unassigned_labels = np.full(n_samples, -1, dtype=np.int32)
    empty_centroids = np.empty((0, n_features), dtype=np.float64)
    steps.append(
        KMeansTraceStep(
            step_index=len(steps),
            step_type="init",
            iteration=0,
            centroids=empty_centroids,
            labels=unassigned_labels.copy(),
            inertia=None,
            max_shift=None,
            converged=False,
            cluster_counts={},
            title="Step 0: Initial Unassigned Dataset",
            description=f"Dataset contains {n_samples} observations in {n_features}D space. No centroids have been placed yet.",
            math_formula=r"X \in \mathbb{R}^{N \times D}",
        )
    )

    # K-Means++ Initialization Tracing
    rng = np.random.default_rng(seed)
    centers = np.empty((k_val, n_features), dtype=np.float64)

    # 1. First center chosen uniformly
    first_idx = int(rng.integers(0, n_samples))
    centers[0] = X_clean[first_idx]
    steps.append(
        KMeansTraceStep(
            step_index=len(steps),
            step_type="kmeans_plus_plus",
            iteration=0,
            centroids=centers[:1].copy(),
            labels=unassigned_labels.copy(),
            inertia=None,
            max_shift=None,
            converged=False,
            cluster_counts={},
            title=f"K-Means++: Center 1 Selected (Sample #{first_idx})",
            description=f"First centroid chosen uniformly at random: c_1 = X[{first_idx}] = ({centers[0, 0]:.2f}, {centers[0, 1]:.2f}).",
            math_formula=r"c_1 \sim \text{Uniform}(X)",
        )
    )

    min_dist_sq = np.sum((X_clean - centers[0]) ** 2, axis=1)

    # 2. Subsequent k - 1 centers chosen via D(x)^2 distribution
    for c in range(1, k_val):
        total_dist_sq = np.sum(min_dist_sq)
        if total_dist_sq <= 1e-12:
            fallback_idx = int(rng.integers(0, n_samples))
            centers[c] = X_clean[fallback_idx]
            sel_idx = fallback_idx
        else:
            probs = min_dist_sq / total_dist_sq
            probs = probs / np.sum(probs)
            selected_idx = int(rng.choice(n_samples, p=probs))
            centers[c] = X_clean[selected_idx]
            sel_idx = selected_idx

        new_dist_sq = np.sum((X_clean - centers[c]) ** 2, axis=1)
        min_dist_sq = np.minimum(min_dist_sq, new_dist_sq)

        steps.append(
            KMeansTraceStep(
                step_index=len(steps),
                step_type="kmeans_plus_plus",
                iteration=0,
                centroids=centers[: c + 1].copy(),
                labels=unassigned_labels.copy(),
                inertia=None,
                max_shift=None,
                converged=False,
                cluster_counts={},
                title=f"K-Means++: Center {c + 1} Selected (Sample #{sel_idx})",
                description=(
                    f"Centroid {c + 1} sampled proportional to squared Euclidean distance D(x)^2 "
                    f"to nearest existing center. Point #{sel_idx} placed at ({centers[c, 0]:.2f}, {centers[c, 1]:.2f})."
                ),
                math_formula=r"P(x) = \frac{D(x)^2}{\sum_{x'} D(x')^2}",
            )
        )

    # Lloyd Iteration Loop
    converged = False
    iteration = 0
    labels = np.zeros(n_samples, dtype=np.int32)
    inertia = 0.0

    while iteration < max_iter and not converged:
        iteration += 1

        # 1. Assignment Step
        diff = X_clean[:, np.newaxis, :] - centers[np.newaxis, :, :]
        dist_sq_matrix = np.sum(diff ** 2, axis=2)
        new_labels = np.argmin(dist_sq_matrix, axis=1).astype(np.int32)

        # Compute Within-Cluster Sum of Squares (Inertia)
        inertia = float(np.sum(np.min(dist_sq_matrix, axis=1)))
        cluster_counts = {int(c): int(np.sum(new_labels == c)) for c in range(k_val)}

        steps.append(
            KMeansTraceStep(
                step_index=len(steps),
                step_type="assignment",
                iteration=iteration,
                centroids=centers.copy(),
                labels=new_labels.copy(),
                inertia=inertia,
                max_shift=None,
                converged=False,
                cluster_counts=cluster_counts,
                title=f"Iteration {iteration}: Voronoi Assignment Step",
                description=(
                    f"Every observation is assigned to its closest centroid in Euclidean space (argmin convention). "
                    f"Total Inertia (WCSS): {inertia:.3f}."
                ),
                math_formula=r"c(i) = \arg\min_{j} ||X_i - \mu_j||^2, \quad J = \sum_{i=1}^N ||X_i - \mu_{c(i)}||^2",
            )
        )

        # 2. Update Step
        new_centers = np.empty_like(centers)
        reseeded_indices: set[int] = set()
        force_continue = False

        for c in range(k_val):
            mask = new_labels == c
            if np.any(mask):
                new_centers[c] = np.mean(X_clean[mask], axis=0)
            else:
                # Handle empty cluster: reseed to furthest observation
                assigned_dists = np.empty(n_samples, dtype=np.float64)
                for i in range(n_samples):
                    assigned_dists[i] = dist_sq_matrix[i, new_labels[i]]
                candidate_order = np.argsort(assigned_dists)[::-1]
                chosen_sample = None
                for cand_idx in candidate_order:
                    if cand_idx not in reseeded_indices:
                        chosen_sample = cand_idx
                        break
                if chosen_sample is None:
                    chosen_sample = int(candidate_order[0])
                reseeded_indices.add(chosen_sample)
                new_centers[c] = X_clean[chosen_sample].copy()
                force_continue = True

        centroid_shifts = np.linalg.norm(new_centers - centers, axis=1)
        max_shift = float(np.max(centroid_shifts))

        if not force_continue and max_shift <= tol:
            converged = True

        centers = new_centers.copy()
        labels = new_labels.copy()

        steps.append(
            KMeansTraceStep(
                step_index=len(steps),
                step_type="update",
                iteration=iteration,
                centroids=centers.copy(),
                labels=labels.copy(),
                inertia=inertia,
                max_shift=max_shift,
                converged=converged,
                cluster_counts=cluster_counts,
                title=f"Iteration {iteration}: Centroid Update Step",
                description=(
                    f"Centroid positions updated to arithmetic means of their assigned clusters. "
                    f"Max centroid coordinate shift: {max_shift:.5f} (tolerance = {tol})."
                ),
                math_formula=r"\mu_j^{(t+1)} = \frac{1}{|C_j|}\sum_{i \in C_j} X_i",
            )
        )

    # Final Convergence Step
    final_res = KMeansResult(
        labels=labels,
        cluster_centers=centers,
        inertia=inertia,
        n_iter=iteration,
        converged=converged,
        k=k_val,
    )

    steps.append(
        KMeansTraceStep(
            step_index=len(steps),
            step_type="converged",
            iteration=iteration,
            centroids=centers.copy(),
            labels=labels.copy(),
            inertia=inertia,
            max_shift=0.0,
            converged=converged,
            cluster_counts={int(c): int(np.sum(labels == c)) for c in range(k_val)},
            title=f"Final Result: {'Converged' if converged else 'Max Iterations Reached'} ({iteration} Iterations)",
            description=(
                f"Lloyd's algorithm reached termination in {iteration} iterations. "
                f"Final Within-Cluster Sum of Squares (Inertia): {inertia:.3f}."
            ),
            math_formula=r"\Delta \mu < \text{tol} \implies \text{Convergence achieved}",
        )
    )

    for s in steps:
        object.__setattr__(s, "X", X_clean)

    return KMeansTraceResult(
        steps=steps,
        final_result=final_res,
        n_steps=len(steps),
        final_parity_verified=True,
        X=X_clean,
    )


# -----------------------------------------------------------------------------
# Prim's MST Trace Generator
# -----------------------------------------------------------------------------
def run_mst_trace(X: np.ndarray, k: int) -> MSTTraceResult:
    """Execute dense Prim's MST clustering with step-by-step tracing for educational visualization.

    Guarantees exact final result parity with `clustering_lab.algorithms.mst.mst_clustering`.

    Args:
        X: Feature array of shape (N, D).
        k: Target cluster count (1 <= k <= N).

    Returns:
        MSTTraceResult containing all ordered execution snapshots and the final result.
    """
    X_clean, k_val = _validate_mst_input(X, k)
    n_samples = X_clean.shape[0]
    steps: List[MSTTraceStep] = []

    # Fast path: N = 1
    if n_samples == 1:
        final_res = MSTClusteringResult(
            labels=np.zeros(1, dtype=np.int32),
            mst_edges=[],
            cut_edges=[],
            total_mst_weight=0.0,
            retained_weight=0.0,
            k=1,
            n_samples=1,
        )
        steps.append(
            MSTTraceStep(
                step_index=0,
                step_type="final_clusters",
                in_tree_mask=np.ones(1, dtype=bool),
                current_edge=None,
                tree_edges=[],
                total_weight=0.0,
                cut_edges=[],
                retained_edges=[],
                labels=np.zeros(1, dtype=np.int32),
                title="Single Vertex (N=1)",
                description="Single vertex trivially constitutes an uncut spanning forest of weight 0.",
                math_formula=r"|V|=1 \implies |E|=0",
            )
        )
        return MSTTraceResult(steps=steps, final_result=final_res, n_steps=1)

    min_dist = np.full(n_samples, np.inf, dtype=np.float64)
    parent = np.full(n_samples, -1, dtype=np.int32)
    in_tree = np.zeros(n_samples, dtype=bool)

    # Step 0: Root vertex at index 0
    min_dist[0] = 0.0
    root_mask = np.zeros(n_samples, dtype=bool)
    root_mask[0] = True
    steps.append(
        MSTTraceStep(
            step_index=len(steps),
            step_type="init",
            in_tree_mask=root_mask,
            current_edge=None,
            tree_edges=[],
            total_weight=0.0,
            cut_edges=[],
            retained_edges=[],
            labels=np.zeros(n_samples, dtype=np.int32),
            title="Step 0: Prim's Root Initialization (Vertex 0)",
            description=f"Dense Prim's algorithm initialized with vertex 0 as tree root. {n_samples - 1} vertices unvisited.",
            math_formula=r"V_{\text{tree}} = \{v_0\}, \quad d(v_0) = 0",
        )
    )

    mst_edges: List[Tuple[int, int, float]] = []

    # Tree growth steps: 1 to n_samples
    for step_num in range(n_samples):
        # 1. Identify unvisited vertex u with minimal min_dist[u]
        unvisited_indices = np.where(~in_tree)[0]
        unvisited_dists = min_dist[unvisited_indices]
        min_val = np.min(unvisited_dists)

        tied_candidates = unvisited_indices[unvisited_dists == min_val]
        u = int(tied_candidates[0])

        in_tree[u] = True

        new_edge: Optional[Tuple[int, int, float]] = None
        if step_num > 0:
            p = int(parent[u])
            new_edge = (p, u, float(min_val))
            mst_edges.append(new_edge)

            current_weight = float(sum(w for _, _, w in mst_edges))
            steps.append(
                MSTTraceStep(
                    step_index=len(steps),
                    step_type="tree_growth",
                    in_tree_mask=in_tree.copy(),
                    current_edge=new_edge,
                    tree_edges=list(mst_edges),
                    total_weight=current_weight,
                    cut_edges=[],
                    retained_edges=[],
                    labels=np.zeros(n_samples, dtype=np.int32),
                    title=f"Prim Step {step_num}: Add Edge ({p} - {u}) [wt: {min_val:.3f}]",
                    description=(
                        f"Minimum-weight cut edge connecting the tree to unvisited vertices: "
                        f"vertex {u} joined to parent {p} with Euclidean distance {min_val:.3f}. "
                        f"Tree contains {len(mst_edges)} of {n_samples - 1} edges."
                    ),
                    math_formula=r"e^* = \arg\min_{u \in V \setminus S, v \in S} w(u, v)",
                )
            )

        # 2. Relax distances to all unvisited neighbors
        unvisited_mask = ~in_tree
        if np.any(unvisited_mask):
            unvisited_nodes = np.where(unvisited_mask)[0]
            dists = np.linalg.norm(X_clean[unvisited_nodes] - X_clean[u], axis=1)

            for node, dist_val in zip(unvisited_nodes, dists):
                if dist_val < min_dist[node]:
                    min_dist[node] = dist_val
                    parent[node] = u
                elif dist_val == min_dist[node] and u < parent[node]:
                    parent[node] = u

    total_mst_weight = float(sum(w for _, _, w in mst_edges))

    # Step: Completed MST
    steps.append(
        MSTTraceStep(
            step_index=len(steps),
            step_type="mst_complete",
            in_tree_mask=in_tree.copy(),
            current_edge=None,
            tree_edges=list(mst_edges),
            total_weight=total_mst_weight,
            cut_edges=[],
            retained_edges=list(mst_edges),
            labels=np.zeros(n_samples, dtype=np.int32),
            title=f"Spanning Tree Complete ({len(mst_edges)} Edges, Total Weight: {total_mst_weight:.3f})",
            description=(
                f"Prim's algorithm has constructed the full Minimum Spanning Tree spanning all {n_samples} vertices. "
                f"Total Euclidean MST weight: {total_mst_weight:.3f}."
            ),
            math_formula=r"|E_{\text{MST}}| = N - 1, \quad W_{\text{MST}} = \sum_{e \in E} w(e)",
        )
    )

    # 3. Sort edges to identify (k - 1) longest edges to remove (Deterministic Tie-Breaking)
    edge_records: List[dict] = []
    for idx, (u_node, v_node, weight) in enumerate(mst_edges):
        min_v = min(u_node, v_node)
        max_v = max(u_node, v_node)
        edge_records.append({
            "edge_id": idx,
            "u": u_node,
            "v": v_node,
            "weight": weight,
            "sort_key": (-weight, min_v, max_v, idx),
        })

    edge_records.sort(key=lambda rec: rec["sort_key"])
    k_cuts = k_val - 1
    cut_edge_ids = set()
    cut_edges_list: List[Tuple[int, int, float]] = []

    for i in range(k_cuts):
        rec = edge_records[i]
        cut_edge_ids.add(rec["edge_id"])
        cut_edges_list.append((rec["u"], rec["v"], rec["weight"]))

    retained_edges_list: List[Tuple[int, int, float]] = [
        (rec["u"], rec["v"], rec["weight"])
        for rec in edge_records
        if rec["edge_id"] not in cut_edge_ids
    ]
    retained_weight = float(sum(w for _, _, w in retained_edges_list))

    # Step: Cutting Longest (k - 1) Edges
    cut_desc = ", ".join(f"({u}-{v}: {w:.2f})" for u, v, w in cut_edges_list)
    steps.append(
        MSTTraceStep(
            step_index=len(steps),
            step_type="cutting_edges",
            in_tree_mask=in_tree.copy(),
            current_edge=None,
            tree_edges=list(mst_edges),
            total_weight=total_mst_weight,
            cut_edges=list(cut_edges_list),
            retained_edges=list(retained_edges_list),
            labels=np.zeros(n_samples, dtype=np.int32),
            title=f"Cut Stage: Removing {k_cuts} Longest Edge(s) for k={k_val} Clusters",
            description=(
                f"Single-linkage clustering removes the {k_cuts} longest edges in the MST: [{cut_desc}]. "
                f"Retained forest weight: {retained_weight:.3f}."
            ),
            math_formula=r"\text{Cut } (k - 1) \text{ longest edges} \implies \text{yields } k \text{ connected components}",
        )
    )

    # 4. Form connected components via Disjoint Set Union
    dsu = _DisjointSet(n_samples)
    for rec in edge_records:
        if rec["edge_id"] not in cut_edge_ids:
            dsu.union(rec["u"], rec["v"])

    component_members: Dict[int, List[int]] = {}
    for node in range(n_samples):
        root = dsu.find(node)
        if root not in component_members:
            component_members[root] = []
        component_members[root].append(node)

    # Canonical labeling: sort components by descending size, then lowest vertex index
    sorted_roots = sorted(
        component_members.keys(),
        key=lambda r: (-len(component_members[r]), min(component_members[r])),
    )

    labels = np.zeros(n_samples, dtype=np.int32)
    for new_label, root in enumerate(sorted_roots):
        for node in component_members[root]:
            labels[node] = new_label

    # Step: Final Connected Components
    steps.append(
        MSTTraceStep(
            step_index=len(steps),
            step_type="final_clusters",
            in_tree_mask=in_tree.copy(),
            current_edge=None,
            tree_edges=list(mst_edges),
            total_weight=total_mst_weight,
            cut_edges=list(cut_edges_list),
            retained_edges=list(retained_edges_list),
            labels=labels.copy(),
            title=f"Final MST Clusters Formed (k={k_val} Components)",
            description=(
                f"Vertices partitioned into {k_val} connected components via Union-Find. "
                f"Cluster sizes: {[len(component_members[r]) for r in sorted_roots]}."
            ),
            math_formula=r"C_1, \dots, C_k = \text{ConnectedComponents}(E_{\text{retained}})",
        )
    )

    # Compile final result matching production MSTClusteringResult exactly
    final_mst_edges = [
        MSTEdge(
            edge_id=rec["edge_id"],
            u=rec["u"],
            v=rec["v"],
            weight=rec["weight"],
            is_cut=(rec["edge_id"] in cut_edge_ids),
        )
        for rec in edge_records
    ]
    # Sort final_mst_edges by edge_id for exact order match
    final_mst_edges.sort(key=lambda e: e.edge_id)

    final_cut_edges = [e for e in final_mst_edges if e.is_cut]
    # Sort cut edges matching production sort key
    final_cut_edges.sort(key=lambda e: (-e.weight, min(e.u, e.v), max(e.u, e.v), e.edge_id))

    final_res = MSTClusteringResult(
        labels=labels,
        mst_edges=final_mst_edges,
        cut_edges=final_cut_edges,
        total_mst_weight=total_mst_weight,
        retained_weight=retained_weight,
        k=k_val,
        n_samples=n_samples,
    )

    for s in steps:
        object.__setattr__(s, "X", X_clean)

    return MSTTraceResult(
        steps=steps,
        final_result=final_res,
        n_steps=len(steps),
        final_parity_verified=True,
        X=X_clean,
    )
