"""
clustering_lab.data.csv_loader
==============================
Secure, UI-independent CSV dataset parser for empirical benchmark imports.

Key Design & Safety Features:
    - Accepts file paths, file-like objects (BytesIO / StringIO), or raw bytes.
    - Strict size limit (<= 5 MB) and row limit (<= 10,000 rows) to prevent DoS.
    - Selects exactly two numerical feature dimensions for 2D clustering.
    - Optional ground-truth label column with deterministic categorical encoding.
    - Validates NaN, Inf, empty content, missing columns, and duplicate headers.
    - Strictly preserves row alignment; never invents synthetic labels or outliers.
    - Safe execution: no unpickling, no code evaluation, no temporary disk writes.
"""

from __future__ import annotations

import io
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd

from clustering_lab.data.dataset import MAX_SAFE_SAMPLES, Dataset, create_dataset

MAX_CSV_BYTES: int = 5 * 1024 * 1024  # 5 Megabytes


def load_dataset_from_csv(
    source: Union[str, bytes, io.IOBase],
    feature_cols: Union[Tuple[str, str], List[str], Tuple[int, int], List[int]],
    label_col: Optional[Union[str, int]] = None,
    dataset_name: str = "custom_csv",
) -> Dataset:
    """Parse and validate an external CSV file into a standardized Dataset.

    Args:
        source: CSV file path (str), raw CSV bytes, or readable file-like stream.
        feature_cols: Identifiers (names or 0-based column indices) of exactly two
            numerical feature columns.
        label_col: Optional identifier of the ground-truth cluster label column.
        dataset_name: Human-readable identifier for metadata records.

    Returns:
        Standardized, immutable Dataset instance.

    Raises:
        ValueError: If size limits, dimensionality, contents, or values are invalid.
        KeyError: If specified column names do not exist in the CSV.
        TypeError: If feature columns cannot be converted to finite float64.
    """
    # 1. Enforce safe buffer handling and size limits
    if isinstance(source, bytes):
        if len(source) == 0:
            raise ValueError("CSV input is empty (0 bytes).")
        if len(source) > MAX_CSV_BYTES:
            raise ValueError(f"CSV file size ({len(source)} bytes) exceeds safety limit of {MAX_CSV_BYTES} bytes (5 MB).")
        stream = io.BytesIO(source)
    elif isinstance(source, io.IOBase):
        # Inspect size if seekable
        if hasattr(source, "seek") and hasattr(source, "tell"):
            try:
                source.seek(0, io.SEEK_END)
                size = source.tell()
                source.seek(0)
                if size == 0:
                    raise ValueError("CSV input stream is empty (0 bytes).")
                if size > MAX_CSV_BYTES:
                    raise ValueError(f"CSV stream size ({size} bytes) exceeds safety limit of {MAX_CSV_BYTES} bytes.")
            except (io.UnsupportedOperation, AttributeError):
                pass
        stream = source
    elif isinstance(source, str):
        # Could be raw CSV text or a file path
        # Check if it looks like a path or a multiline string
        if "\n" not in source and ("/" in source or "\\" in source or source.endswith(".csv")):
            import os
            if not os.path.isfile(source):
                raise ValueError(f"Specified CSV file path does not exist: {source}")
            file_size = os.path.getsize(source)
            if file_size == 0:
                raise ValueError(f"CSV file '{source}' is empty (0 bytes).")
            if file_size > MAX_CSV_BYTES:
                raise ValueError(f"CSV file '{source}' ({file_size} bytes) exceeds limit of {MAX_CSV_BYTES} bytes.")
            stream = source
        else:
            if len(source.strip()) == 0:
                raise ValueError("CSV input string is empty.")
            if len(source.encode("utf-8")) > MAX_CSV_BYTES:
                raise ValueError("CSV input string exceeds maximum size limit of 5 MB.")
            stream = io.StringIO(source)
    else:
        raise TypeError(f"Unsupported CSV source type: {type(source).__name__}.")

    # 2. Parse using pandas with safe options
    try:
        df = pd.read_csv(stream)
    except Exception as exc:
        raise ValueError(f"Failed to parse CSV tabular data: {exc}") from exc

    if df.empty or df.shape[0] == 0:
        raise ValueError("Parsed CSV contains zero data rows.")

    if df.shape[0] > MAX_SAFE_SAMPLES:
        raise ValueError(
            f"CSV contains {df.shape[0]} rows, exceeding safe limit of {MAX_SAFE_SAMPLES}. "
            "Downsample the dataset before importing for 2D clustering robustness analysis."
        )

    # Check for duplicate column headers
    col_list = list(df.columns)
    if len(col_list) != len(set(col_list)):
        raise ValueError(f"CSV contains duplicate column headers: {col_list}.")

    # 3. Resolve feature column identifiers
    if not isinstance(feature_cols, (tuple, list)) or len(feature_cols) != 2:
        raise ValueError(f"'feature_cols' must specify exactly two column identifiers, got {feature_cols}.")

    resolved_feature_names: List[str] = []
    for col_id in feature_cols:
        if isinstance(col_id, int):
            if col_id < 0 or col_id >= len(df.columns):
                raise KeyError(f"Feature column index {col_id} is out of bounds for CSV with {len(df.columns)} columns.")
            resolved_feature_names.append(str(df.columns[col_id]))
        elif isinstance(col_id, str):
            if col_id not in df.columns:
                raise KeyError(f"Feature column '{col_id}' not found in CSV. Available columns: {list(df.columns)}.")
            resolved_feature_names.append(col_id)
        else:
            raise TypeError(f"Column identifier must be str or int, got {type(col_id).__name__}.")

    if resolved_feature_names[0] == resolved_feature_names[1]:
        raise ValueError(f"Feature columns must be distinct. Received duplicate column: '{resolved_feature_names[0]}'.")

    # 4. Extract and validate numerical features
    try:
        X_df = df[resolved_feature_names].astype(np.float64)
    except (ValueError, TypeError) as exc:
        raise TypeError(
            f"Feature columns {resolved_feature_names} contain non-numerical values that cannot be parsed as floats: {exc}"
        ) from exc

    X = X_df.to_numpy(dtype=np.float64)
    if not np.isfinite(X).all():
        raise ValueError(
            f"Feature columns {resolved_feature_names} contain non-finite values (NaN, null, or Inf). "
            "Clean missing and non-finite records prior to import."
        )

    # 5. Extract and resolve labels if requested
    labels: Optional[np.ndarray] = None
    label_encoding: Optional[Dict[Any, int]] = None
    resolved_label_name: Optional[str] = None

    if label_col is not None:
        if isinstance(label_col, int):
            if label_col < 0 or label_col >= len(df.columns):
                raise KeyError(f"Label column index {label_col} is out of bounds.")
            resolved_label_name = str(df.columns[label_col])
        elif isinstance(label_col, str):
            if label_col not in df.columns:
                raise KeyError(f"Label column '{label_col}' not found in CSV. Available columns: {list(df.columns)}.")
            resolved_label_name = label_col
        else:
            raise TypeError(f"Label column identifier must be str or int, got {type(label_col).__name__}.")

        raw_labels = df[resolved_label_name]
        if raw_labels.isna().any():
            raise ValueError(f"Ground-truth label column '{resolved_label_name}' contains missing (NaN/null) values.")

        # Check if already integer
        if pd.api.types.is_integer_dtype(raw_labels):
            labels = raw_labels.to_numpy(dtype=np.int32)
        else:
            # Deterministically factorize categorical labels by sorted unique values
            unique_classes = sorted(raw_labels.unique(), key=lambda v: str(v))
            label_encoding = {val: idx for idx, val in enumerate(unique_classes)}
            labels = np.array([label_encoding[v] for v in raw_labels], dtype=np.int32)

    # 6. Construct inlier mask
    # All imported records are considered valid inliers unless an explicit label of -1 was supplied
    n_samples = X.shape[0]
    if labels is not None and np.any(labels == -1):
        inlier_mask = (labels != -1)
    else:
        inlier_mask = np.ones(n_samples, dtype=bool)

    metadata: Dict[str, Any] = {
        "source_name": dataset_name,
        "feature_columns": resolved_feature_names,
        "label_column": resolved_label_name,
        "has_ground_truth": labels is not None,
        "ari_available": labels is not None,
        "total_csv_columns": len(df.columns),
    }
    if label_encoding is not None:
        metadata["label_encoding"] = {str(k): v for k, v in label_encoding.items()}

    params: Dict[str, Any] = {
        "feature_cols": resolved_feature_names,
        "label_col": resolved_label_name,
    }

    return create_dataset(
        X=X,
        labels=labels,
        inlier_mask=inlier_mask,
        dataset_family="csv",
        seed=None,
        params=params,
        clean_X=None,
        metadata=metadata,
    )
