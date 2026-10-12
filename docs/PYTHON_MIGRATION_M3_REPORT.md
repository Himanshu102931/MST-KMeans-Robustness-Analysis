# Migration Phase M3 Completion Report
## Python Datasets, Noise/Outliers, CSV Import & Reproducibility

- **Project:** MST vs K-Means Robustness Analysis
- **Course:** Pattern Matching Lab (`BCS-DS-777`)
- **Institution:** Manav Rachna International Institute of Research and Studies (MRIIRS), School of Engineering & Technology
- **Degree:** B.Tech Computer Science & Engineering (AIML), 7th Semester (2026–2027)
- **Student Researchers:**
  - Himanshu Gupta (Roll No: `[REDACTED_STUDENT_IDENTIFIER]`)
  - Parth Yadav (Roll No: `[REDACTED_STUDENT_IDENTIFIER]`)
- **Active Branch:** `feature/python-streamlit-migration`
- **Baseline Checkpoint:** `91ab56c` (Phase M2 Verified CI: 43 tests passing on Python 3.12/Ubuntu)
- **Preserved Main Checkpoint:** `0864323` (Original Vanilla JavaScript Application & Viva Materials)
- **Date:** October 12, 2026

---

## 1. Executive Summary

Phase M3 establishes the complete, reproducible scientific data layer for the Python migration. It introduces:
1. Standardized, immutable data containers (`Dataset`).
2. Synthetic 2D generators for **Gaussian Blobs**, **Two Moons**, and **Concentric Circles**.
3. A decoupled contamination engine that independently applies Gaussian coordinate jitter and uniform bounding-box outliers via non-overlapping PRNG streams.
4. A secure, headless CSV dataset parser supporting custom 2D features and deterministic categorical label factorization.
5. A versioned JSON configuration schema (`1.0.0`) enabling bidirectional serialization, parameter validation, and round-trip reproducibility.
6. Targeted scientific documentation corrections in `ALGORITHM_SPECIFICATION.md` clarifying degenerate centroid geometry, cut property ties, single-linkage non-uniqueness, and non-convex inductive biases.

All legacy assets (Vanilla JavaScript web dashboard, HTML/CSS, research reports, and presentation slides) remain **strictly preserved and unmodified**.

---

## 2. Inventory of File Changes

### 2.1 New Files Created

| File Path | Description |
| :--- | :--- |
| `python_app/clustering_lab/data/dataset.py` | Standardized, immutable `Dataset` dataclass container with structural and range invariants ($1 \le N \le 10,000$). |
| `python_app/clustering_lab/data/noise.py` | Decoupled contamination engine: zero-mean Gaussian coordinate jitter and uniform bounding-box outlier generator. |
| `python_app/clustering_lab/data/synthetic.py` | Synthetic generators for Gaussian Blobs, Two Moons, and Concentric Circles returning validated `Dataset` objects. |
| `python_app/clustering_lab/data/csv_loader.py` | Headless, secure CSV parser supporting bytes/streams, column identifiers, categorical encoding, and DoS size limits. |
| `python_app/clustering_lab/data/config.py` | Versioned experiment configuration schema `1.0.0` with JSON serialization/deserialization and dataset factory. |
| `python_app/docs/DATASET_AND_REPRODUCIBILITY_SPECIFICATION.md` | Formal specification of dataset geometries, decoupled noise definitions, CSV standards, and PRNG reproducibility. |
| `python_app/tests/test_data.py` | Scientific test suite for synthetic generation, decoupled noise, outlier rounding, label preservation, and invariants (13 test functions). |
| `python_app/tests/test_data_io.py` | Test suite for CSV parsing (categorical/integer/unlabeled), error validation, and JSON configuration round-trip (8 test functions). |
| `docs/PYTHON_MIGRATION_M3_REPORT.md` | This Phase M3 completion audit report. |

### 2.2 Existing Files Modified

| File Path | Nature of Modification |
| :--- | :--- |
| `python_app/clustering_lab/data/__init__.py` | Exported public data layer API (`Dataset`, generators, contamination helpers, CSV loader, and config schema). |
| `python_app/tests/test_project_structure.py` | Extended `test_directory_and_file_layout` to verify physical presence of Phase M3 data modules. |
| `python_app/docs/ALGORITHM_SPECIFICATION.md` | Applied 5 targeted scientific corrections (degenerate centroids, cut property ties, single-linkage ties, non-convex biases). |
| `python_app/README.md` | Updated directory tree and marked Phase M3 deliverables completed. |

### 2.3 Preserved Files
- Legacy JavaScript web app (`index.html`, `js/`, `css/`, `results/`, `tests/`) untouched.
- Academic report and PowerPoint presentation (`docs/report/`, `docs/presentation/`) untouched.

---

## 3. Dataset Architectures & API Specifications

### 3.1 Standardized Data Container (`Dataset`)
- **Immutability:** `@dataclass(frozen=True)` preventing caller side-effects.
- **Attributes:**
  - `X`: `np.ndarray` of shape `(N, 2)` (finite `float64`).
  - `labels`: `Optional[np.ndarray]` of shape `(N,)` (`int32`), with `-1` for outliers, or `None` if unlabeled.
  - `inlier_mask`: `np.ndarray` of shape `(N,)` (`bool`).
  - `dataset_family`: `'blobs'`, `'moons'`, `'circles'`, or `'csv'`.
  - `seed`: Optional integer seed.
  - `params`: Generation hyperparameters dictionary.
  - `n_inliers`, `n_outliers`, `n_samples`: Explicit counts satisfying $N_{\text{inliers}} + N_{\text{outliers}} = N_{\text{samples}} = N$.
  - `clean_X`: Optional coordinates of inliers before noise addition for paired visualization.
  - `metadata`: Source information, cluster sizes, or categorical encodings.

### 3.2 Synthetic Data Generators (`synthetic.py`)
- **`generate_blobs(n_samples=300, n_clusters=3, cluster_std=0.4, radius=3.5, noise=0.0, outlier_rate=0.0, seed=42)`:**
  Centroids positioned symmetrically around a circle of radius $3.5$. Isotropic Gaussian dispersion.
- **`generate_moons(n_samples=300, noise=0.08, outlier_rate=0.0, seed=42)`:**
  Two interlocking crescent manifolds ($k=2$) parameterized with half-circle curves.
- **`generate_circles(n_samples=300, factor=0.45, noise=0.05, outlier_rate=0.0, seed=42)`:**
  Two nested circular rings ($k=2$) with inner/outer radius ratio `factor`.
- **`generate_synthetic_dataset(family, n_samples=300, seed=42, noise=0.0, outlier_rate=0.0, **kwargs)`:**
  Unified dispatcher.

---

## 4. Scientific Contamination Pipeline (`noise.py`)

### 4.1 Gaussian Noise (Inlier Perturbation)
- **Model:** $x_i^{\text{noisy}} = x_i^{\text{clean}} + \delta_i, \quad \delta_i \sim \mathcal{N}(0, \sigma^2 I_2)$.
- **Scale:** Absolute coordinate standard deviation ($\sigma \ge 0.0$).
- **Invariance:** Ground-truth cluster labels are strictly preserved for inliers.

### 4.2 Uniform Outliers (Background Perturbation)
- **Bounding Box:** Derived from inlier coordinates with $15\%$ proportional padding:
  $$\text{pad}_x = \max(0.15 \cdot (x_{\max} - x_{\min}), 0.5), \quad \text{pad}_y = \max(0.15 \cdot (y_{\max} - y_{\min}), 0.5)$$
- **Rate Definition:** $N_{\text{outliers}} = \text{round}(N_{\text{inliers}} \times \text{outlier\_rate})$ for rate in $[0.0, 1.0)$.
- **Label Convention:** Outliers receive label $-1$ and `inlier_mask = False`.

### 4.3 PRNG Decoupling Mechanism
- Master seed initializes `np.random.SeedSequence(seed)`.
- Spawns two independent streams: `rng_noise` and `rng_outliers`.
- Changing outlier contamination percentage leaves the noisy inliers bitwise unchanged.

---

## 5. CSV Import & JSON Schema Specifications

### 5.1 Headless CSV Loader (`csv_loader.py`)
- **Inputs:** Supports file paths, bytes, and `io.StringIO` / `io.BytesIO` streams.
- **Safety Limits:** Maximum 5 MB (`MAX_CSV_BYTES`) and maximum 10,000 rows (`MAX_SAFE_SAMPLES`).
- **Feature Columns:** Must specify exactly two distinct numerical column names or 0-based indices.
- **Label Encoding:** Integer labels preserved directly; categorical strings deterministically mapped via sorted unique classes into $[0, k-1]$ and stored in `metadata["label_encoding"]`.
- **Missing Labels:** Sets `labels = None`, `metadata["has_ground_truth"] = False`, `metadata["ari_available"] = False`.
- **Validation:** Strictly rejects missing files, empty files, missing columns, duplicate column headers, NaNs, and non-numeric content.

### 5.2 Versioned JSON Schema (`config.py`)
- **Schema Version:** `1.0.0` (validated on major version).
- **Attributes:** `dataset_family`, `n_samples` $[10, 5000]$, `n_clusters` $[1, 20]$ (enforced $2$ for moons/circles), `seed` $\ge 0$, `noise` $\ge 0.0$, `outlier_rate` $[0.0, 0.5]$, and `dataset_params`.
- **Round-Trip Stability:** Guaranteed bitwise equality: `ExperimentConfig.from_json(cfg.to_json()) == cfg`.
- **Safety Limit:** Maximum 100 KB JSON input.

---

## 6. Scientific Documentation Corrections in `ALGORITHM_SPECIFICATION.md`

1. **Degenerate Centroids ($U < k$):** Clarified that when distinct points $U < k$, it is mathematically impossible to produce $k$ non-empty clusters with pairwise distinct centroid coordinates; at least $k - U$ centroids must coincide with existing observations.
2. **MST Cut Property Ties:** Stated that when edges have strictly smaller weight, the crossing edge belongs to the unique MST; in the presence of equal-weight ties, at least one minimum-weight crossing edge belongs to some MST of $G$.
3. **Single-Linkage Equivalence under Ties:** Qualified that when edge weights are distinct, cutting $k - 1$ edges produces partitions identical to cutting single-linkage dendrograms; under ties, deterministic tie-breaking ensures a canonical, reproducible partition.
4. **Inductive Biases on Non-Convex Sets:** Replaced absolute failure/success assertions with scientifically accurate characterizations (K-Means is prone to systematic mispartitioning on non-globular manifolds due to linear Voronoi boundaries; MST is capable of capturing non-convex manifolds under favorable separation and low noise).
5. **Separation of Theory from Empirical Claims:** Theoretical properties are clearly distinguished from pending empirical sweeps.

---

## 7. Test Suite Architecture & Coverage

The test suite now encompasses 7 test modules:

1. **`test_data.py` (13 test functions):**
   - `test_blobs_generation_shapes_and_labels`: Verifies blobs output dimensions, cluster counts, and metadata.
   - `test_moons_generation_shapes_and_labels`: Verifies moons output dimensions, $k=2$, and inlier counts.
   - `test_circles_generation_shapes_and_labels`: Verifies circles output dimensions, $k=2$, and nested rings.
   - `test_exact_reproducibility_with_identical_seed`: Bitwise identical outputs across identical seeds.
   - `test_divergence_with_different_seeds`: Statistically distinct coordinates across differing seeds.
   - `test_outlier_rate_rounding_and_label_assignment`: Validates outlier count rounding (5%, 10%, 20%), label $-1$, and inlier mask.
   - `test_noisy_inlier_label_preservation`: Inlier labels strictly preserved after adding Gaussian jitter.
   - `test_decoupled_contamination_independence`: Validates that altering outlier rate does not change noisy inlier coordinates.
   - `test_zero_noise_and_zero_outlier_baseline`: Validates clean baseline (`clean_X == X`).
   - `test_duplicate_point_support_without_deduplication`: Verifies duplicate observations are preserved.
   - `test_invalid_parameter_rejection`: Asserts exceptions on negative noise, bad outlier rates, and bad cluster counts.
   - `test_dual_clustering_algorithms_interoperability`: Both custom K-Means and MST execute on generated datasets.
   - `test_input_immutability`: Asserts input feature arrays are not modified.

2. **`test_data_io.py` (8 test functions):**
   - `test_load_csv_with_integer_labels`: Verifies CSV loading with integer ground truth.
   - `test_load_csv_with_categorical_labels`: Verifies deterministic factorizing of categorical strings.
   - `test_load_csv_without_labels`: Verifies unlabeled CSV parsing and ARI availability flags.
   - `test_load_csv_by_integer_column_indices`: Verifies column selection by integer positions.
   - `test_load_csv_from_bytes_and_stringio`: Verifies parsing across bytes and StringIO streams.
   - `test_csv_validation_errors`: Validates rejection of empty inputs, missing columns, duplicate headers, NaNs, and non-numerics.
   - `test_experiment_config_roundtrip`: Verifies JSON serialization and round-trip fidelity.
   - `test_create_dataset_from_config`: Verifies dataset generation across blobs, moons, and circles from config.
   - `test_experiment_config_validation_rules`: Validates schema versions, parameter ranges, and malformed JSON.

3. **Existing Modules (Continued Verification):**
   - `test_kmeans.py` (10 test functions)
   - `test_mst.py` (10 test functions)
   - `test_reference_validation.py` (4 test functions)
   - `test_environment.py` (3 test functions)
   - `test_project_structure.py` (3 test functions)

---

## 8. State Verification Matrix

| Check / Requirement | Status | Verification Context |
| :--- | :---: | :--- |
| Python 3.12 AST & Bytecode Compilation | **VERIFIED** | Locally compiled all 19 Python modules via `py -3.12 -m py_compile` with exit code 0. |
| Zero Trailing Whitespace | **VERIFIED** | `git diff --check` executed with exit code 0 and zero warnings. |
| Filesystem & Package Structure | **VERIFIED** | All modules, subpackages, tests, and documentation confirmed present. |
| Local Preserved Application Integrity | **VERIFIED** | Zero changes made to JavaScript application, HTML, CSS, reports, or slides. |
| Full Scientific Pytest Execution | **PENDING** | Native scientific tests deferred to GitHub Actions Linux runner per Windows environment constraints. |

---

## 9. Current Git Status

```
On branch feature/python-streamlit-migration
Your branch is up to date with 'origin/feature/python-streamlit-migration'.

Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	modified:   python_app/README.md
	modified:   python_app/clustering_lab/data/__init__.py
	modified:   python_app/docs/ALGORITHM_SPECIFICATION.md
	modified:   python_app/tests/test_project_structure.py

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	docs/PYTHON_MIGRATION_M3_REPORT.md
	python_app/clustering_lab/data/config.py
	python_app/clustering_lab/data/csv_loader.py
	python_app/clustering_lab/data/dataset.py
	python_app/clustering_lab/data/noise.py
	python_app/clustering_lab/data/synthetic.py
	python_app/docs/DATASET_AND_REPRODUCIBILITY_SPECIFICATION.md
	python_app/tests/test_data.py
	python_app/tests/test_data_io.py

no changes added to commit (use "git add" and/or "git commit -a")
```

---

## 10. Recommended Next Steps

1. **User Review:** Inspect the created data modules, tests, and documentation.
2. **Commit Changes:**
   ```bash
   git add python_app/ docs/PYTHON_MIGRATION_M3_REPORT.md
   git commit -m "feat(data): implement reproducible synthetic generators, decoupled noise pipeline, CSV loader, and config schema"
   ```
3. **Push & Verify in CI:**
   ```bash
   git push origin feature/python-streamlit-migration
   ```
   Inspect GitHub Actions run on Ubuntu/Python 3.12 to verify all tests pass cleanly.
4. **Proceed to Phase M4:** Upon user approval, begin Phase M4 (Robustness Experiment Engine, Monte Carlo Noise Sweeps, and Evaluation Metrics).
