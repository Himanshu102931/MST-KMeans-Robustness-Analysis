"""
test_environment.py
===================
Environment and dependency compatibility tests for python_app.
Verifies Python runtime version, required third-party scientific packages,
and core mathematical/data handling functionality.
"""

import importlib
import sys
import pytest


def test_python_version_compatibility():
    """Verify that runtime Python environment satisfies Python 3.12+ requirement."""
    assert sys.version_info >= (3, 12), (
        f"Python 3.12+ is required. Current runtime version: {sys.version}"
    )


@pytest.mark.parametrize(
    "package_name",
    [
        "streamlit",
        "numpy",
        "pandas",
        "scipy",
        "sklearn",
        "matplotlib",
        "plotly",
        "pytest",
    ],
)
def test_required_packages_importable(package_name):
    """Verify that all declared scientific and application packages can be imported."""
    try:
        module = importlib.import_module(package_name)
        assert module is not None
    except ImportError as exc:
        pytest.fail(f"Required package '{package_name}' could not be imported: {exc}")


def test_scientific_stack_sanity():
    """Verify basic operations across core numerical and data libraries."""
    import numpy as np
    import pandas as pd
    from scipy.spatial.distance import euclidean

    # NumPy basic array creation and vectorized arithmetic
    arr_a = np.array([1.0, 2.0, 3.0])
    arr_b = np.array([4.0, 6.0, 8.0])
    diff = arr_b - arr_a
    assert np.allclose(diff, np.array([3.0, 4.0, 5.0]))

    # SciPy Euclidean distance
    dist = euclidean(arr_a, arr_b)
    assert np.isclose(dist, np.sqrt(9.0 + 16.0 + 25.0))

    # Pandas DataFrame creation and column indexing
    df = pd.DataFrame({"x": arr_a, "y": arr_b, "label": [0, 0, 1]})
    assert df.shape == (3, 3)
    assert list(df.columns) == ["x", "y", "label"]
    assert df["x"].sum() == 6.0
