# Scientific Dataset & Reproducibility Specification
## MST vs K-Means Robustness Analysis — Phase M3

### Academic Context
- **Course:** Pattern Matching Lab (`BCS-DS-777`)
- **Institution:** Manav Rachna International Institute of Research and Studies (MRIIRS), School of Engineering & Technology
- **Degree:** B.Tech Computer Science & Engineering (AIML), 7th Semester (2026–2027)
- **Student Researchers:**
  - Himanshu Gupta (Roll No: `[REDACTED_STUDENT_IDENTIFIER]`)
  - Parth Yadav (Roll No: `[REDACTED_STUDENT_IDENTIFIER]`)
- **Package Location:** `python_app/clustering_lab/data/`

---

## 1. Overview and Scientific Motivation

Robustness benchmarking of clustering algorithms requires synthetic and empirical datasets whose geometric topologies and noise characteristics are strictly controlled and mathematically reproducible.

Phase M3 establishes the data layer for the Python research suite, featuring:
1. **Three Canonical Geometric Families:** Gaussian Blobs (convex/isotropic), Two Moons (non-convex entangled crescents), and Concentric Circles (nested non-convex rings).
2. **Decoupled Contamination Engine:** Independent, orthogonal control over inlier Gaussian jitter and uniform outlier contamination.
3. **Secure CSV Parser:** A headless parser for external empirical datasets with strict safety bounds.
4. **Versioned JSON Configuration Schema (`1.0.0`):** Full experiment specification export and import for guaranteed audit trails and cross-platform reproducibility.

---

## 2. Synthetic Dataset Families

### 2.1 Gaussian Blobs (`generate_blobs`)
- **Geometric Topology:** Linearly and convexly separable clusters generated from isotropic bivariate normal distributions.
- **Centroid Placement:** Centroids $\mu_0, \ldots, \mu_{k-1}$ are positioned symmetrically along a circle of radius $R = 3.5$:
  $$\mu_i = \left(R \cos\left(\frac{2\pi i}{k}\right), \; R \sin\left(\frac{2\pi i}{k}\right)\right)$$
- **Dispersion:** Points are drawn as $x \sim \mathcal{N}(\mu_i, \sigma_{\text{cluster}}^2 I_2)$ with default $\sigma_{\text{cluster}} = 0.4$.
- **Class Balance:** Samples are distributed equally across clusters ($N / k$ points per cluster).
- **Default Parameters:** $N = 300$, $k = 3$, $\sigma_{\text{cluster}} = 0.4$, $R = 3.5$.

### 2.2 Two Moons (`generate_moons`)
- **Geometric Topology:** Two non-convex, interlocking crescent manifolds that cannot be separated by linear hyperplanes.
- **Parametric Curve:**
  - Upper crescent (Cluster 0): $(\cos \theta, \sin \theta)$ for $\theta \in [0, \pi]$.
  - Lower crescent (Cluster 1): $(1 - \cos \theta, 1 - \sin \theta - 0.5)$ for $\theta \in [0, \pi]$.
- **Cluster Count:** Fixed at $k = 2$.
- **Default Parameters:** $N = 300$, base noise $\sigma = 0.08$.

### 2.3 Concentric Circles (`generate_circles`)
- **Geometric Topology:** Two nested concentric circular rings sharing the origin $(0, 0)$ as their center.
- **Parametric Curve:**
  - Outer ring (Cluster 0): Radius $r_{\text{outer}} = 1.0$, $(\cos \theta, \sin \theta)$ for $\theta \in [0, 2\pi)$.
  - Inner ring (Cluster 1): Radius $r_{\text{inner}} = \text{factor} \times r_{\text{outer}}$, $(\text{factor} \cos \theta, \text{factor} \sin \theta)$.
- **Separation Factor:** Ratio $r_{\text{inner}} / r_{\text{outer}} \in (0, 1)$, default $0.45$.
- **Cluster Count:** Fixed at $k = 2$.
- **Default Parameters:** $N = 300$, separation factor $= 0.45$, base noise $\sigma = 0.05$.

---

## 3. Contamination Pipeline & Decoupled PRNG Architecture

### 3.1 Gaussian Jitter (Inlier Perturbation)
- **Mathematical Model:**
  $$x_i^{\text{noisy}} = x_i^{\text{clean}} + \delta_i, \quad \delta_i \sim \mathcal{N}(0, \sigma^2 I_2)$$
- **Scale Convention:** $\sigma$ (`noise`) represents the **absolute coordinate standard deviation** (not normalized).
- **Label Invariance:** Adding Gaussian jitter does not alter the underlying cluster identity; ground-truth labels for inliers are strictly preserved.

### 3.2 Uniform Outliers (Background Contamination)
- **Bounding Box Calculation:** Derived from the clean inlier coordinate extents:
  $$x_{\min} = \min(X_{*, 0}), \; x_{\max} = \max(X_{*, 0}), \quad y_{\min} = \min(X_{*, 1}), \; y_{\max} = \max(X_{*, 1})$$
  with $15\%$ proportional padding added on each axis:
  $$\text{pad}_x = \max(0.15 \cdot (x_{\max} - x_{\min}), 0.5), \quad \text{pad}_y = \max(0.15 \cdot (y_{\max} - y_{\min}), 0.5)$$
- **Outlier Rate Definition:** Outlier count is defined strictly as a fraction of the original inlier count:
  $$N_{\text{outliers}} = \text{round}(N_{\text{inliers}} \times \text{outlier\_rate})$$
  Standard evaluation rates: $0\%$ ($0.0$), $5\%$ ($0.05$), $10\%$ ($0.10$), and $20\%$ ($0.20$).
- **Ground-Truth Label:** Injected outliers are explicitly assigned label **$-1$**.
- **Inlier Mask:** Boolean vector of length $N_{\text{total}}$ where inliers are `True` and outliers are `False`.

### 3.3 Decoupled Random Streams
To guarantee that parameter sweeps test strictly isolated variables:
- Master random seed initializes a `numpy.random.SeedSequence(seed)`.
- `SeedSequence.spawn(2)` forks two completely decoupled, non-overlapping PRNG streams:
  1. `rng_noise`: samples inlier Gaussian displacements.
  2. `rng_outliers`: samples uniform outlier spatial coordinates.
- **Scientific Consequence:** Changing the outlier rate (e.g. from $0\%$ to $20\%$) leaves the noisy inlier coordinates bitwise identical, ensuring valid paired statistical tests.

---

## 4. Standardized Dataset Container (`Dataset`)

```python
@dataclass(frozen=True)
class Dataset:
    X: np.ndarray             # Shape (N, 2), float64, finite coordinates
    labels: Optional[np.ndarray] # Shape (N,), int32, -1 for outliers, or None
    inlier_mask: np.ndarray   # Shape (N,), bool (True=inlier, False=outlier)
    dataset_family: str       # 'blobs', 'moons', 'circles', 'csv'
    seed: Optional[int]       # Master random seed or None
    params: Dict[str, Any]    # Hyperparameters used for generation
    n_inliers: int            # Count of inlier observations
    n_outliers: int           # Count of added outliers
    n_samples: int            # Total rows: N = n_inliers + n_outliers
    clean_X: Optional[np.ndarray] # Inliers before noise jitter (shape n_inliers, 2)
    metadata: Dict[str, Any]  # Source info, column headers, encodings
```

### Safety Invariants Enforced
- $N \ge 1$ and $N \le 10,000$ (enforces $O(N^2)$ memory safety for downstream MST processing).
- Rejects non-finite values (NaN, Inf) and dimension mismatches.
- Duplicate spatial coordinates are preserved as legitimate physical observations without silent deduplication.
- Caller data is copied to prevent unexpected mutation.

---

## 5. External CSV Import Specification

Module: `clustering_lab.data.csv_loader`

### Input Specifications & Limits
- **Source Types:** File path (string), raw bytes, or readable file-like streams (`io.StringIO`, `io.BytesIO`).
- **File Size Ceiling:** Maximum $5\text{ MB}$ (`5,242,880` bytes).
- **Row Ceiling:** Maximum $10,000$ observations.
- **Feature Selection:** Caller must specify exactly two distinct numerical column identifiers (`feature_cols`).
- **Label Handling:**
  - If a label column is provided:
    - Integer labels are preserved directly.
    - Categorical string labels are deterministically factorized according to sorted unique values:
      `sorted_classes = sorted(raw_labels.unique())`
      Mapping recorded in `metadata["label_encoding"]`.
  - If no label column is provided:
    - `labels` is set to `None`.
    - `metadata["has_ground_truth"] = False`.
    - `metadata["ari_available"] = False`.
- **Security Boundaries:** Zero code execution, zero `pickle` deserialization, zero disk writes.

---

## 6. Versioned Configuration Schema (`ExperimentConfig`)

- **Module:** `clustering_lab.data.config`
- **Current Version:** `1.0.0`

### JSON Structure Example
```json
{
  "schema_version": "1.0.0",
  "dataset_family": "blobs",
  "n_samples": 300,
  "n_clusters": 3,
  "seed": 42,
  "noise": 0.15,
  "outlier_rate": 0.10,
  "dataset_params": {
    "cluster_std": 0.4,
    "radius": 3.5
  }
}
```

### Validation Constraints
- `schema_version`: Must match major version `1.x.x`.
- `dataset_family`: Must be `'blobs'`, `'moons'`, or `'circles'`.
- `n_samples`: Integer in $[10, 5000]$.
- `n_clusters`: Integer in $[1, 20]$ (strictly enforced as $2$ for moons and circles).
- `seed`: Integer $\ge 0$.
- `noise`: Finite float $\ge 0.0$.
- `outlier_rate`: Float in $[0.0, 0.5]$.
- Max JSON size: $100\text{ KB}$.

---

## 7. Differences from Historical JavaScript Implementation

| Dimension | Legacy JavaScript Implementation | Python Phase M3 Implementation |
| :--- | :--- | :--- |
| **PRNG Engine** | Custom 32-bit linear congruential generator / Mulberry32 | Modern 64-bit NumPy PCG64 with `SeedSequence` stream spawning |
| **Stream Decoupling** | Single sequential PRNG call sequence (coupled draws) | Formally decoupled independent streams for noise and outliers |
| **Geometric Base Curves** | Custom trigonometric loops in `js/data/datasets.js` | Established `scikit-learn` generators + symmetric circular Gaussian centers |
| **Container Format** | JavaScript Object array of points `{id, x, y, isOutlier}` | Vectorized NumPy feature matrix $(N, 2)$ inside frozen `Dataset` dataclass |
| **Serialization** | Ad-hoc JSON stringification | Strict, versioned JSON schema (`ExperimentConfig`) with round-trip validation |
| **CSV Import** | Browser-only `FileReader` | Headless, UI-independent, secure parser with size limits and categorical encoding |
