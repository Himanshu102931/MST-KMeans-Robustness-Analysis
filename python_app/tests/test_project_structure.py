"""
test_project_structure.py
=========================
Project architecture, package structure, and Streamlit smoke tests.
Verifies internal module importability, file organization, and dashboard execution.
"""

import importlib
import pathlib
import sys
import pytest

# Ensure python_app root directory is available on sys.path
APP_DIR = pathlib.Path(__file__).resolve().parent.parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))


@pytest.mark.parametrize(
    "module_path",
    [
        "clustering_lab",
        "clustering_lab.algorithms",
        "clustering_lab.data",
        "clustering_lab.experiments",
        "clustering_lab.evaluation",
        "clustering_lab.visualization",
        "clustering_lab.utils",
    ],
)
def test_internal_packages_importable(module_path):
    """Verify that all internal clustering_lab packages and subpackages import cleanly."""
    try:
        mod = importlib.import_module(module_path)
        assert mod is not None
    except ImportError as exc:
        pytest.fail(f"Internal module '{module_path}' could not be imported: {exc}")


def test_directory_and_file_layout():
    """Verify standard directory and required file structure of python_app."""
    expected_files = [
        "app.py",
        "requirements.txt",
        "requirements-dev.txt",
        "README.md",
    ]
    for filename in expected_files:
        filepath = APP_DIR / filename
        assert filepath.is_file(), f"Expected file '{filename}' was not found in {APP_DIR}"

    expected_subpackages = [
        "algorithms",
        "data",
        "experiments",
        "evaluation",
        "visualization",
        "utils",
    ]
    for subpkg in expected_subpackages:
        init_file = APP_DIR / "clustering_lab" / subpkg / "__init__.py"
        assert init_file.is_file(), (
            f"Expected package initialization file missing at {init_file}"
        )

    # Verify Phase M2 algorithm implementations exist
    for algo_file in ["kmeans.py", "mst.py"]:
        algo_path = APP_DIR / "clustering_lab" / "algorithms" / algo_file
        assert algo_path.is_file(), f"Expected algorithm module missing at {algo_path}"

    # Verify Phase M3 data layer modules exist
    for data_file in ["dataset.py", "noise.py", "synthetic.py", "csv_loader.py", "config.py"]:
        data_path = APP_DIR / "clustering_lab" / "data" / data_file
        assert data_path.is_file(), f"Expected data module missing at {data_path}"


def test_minimal_streamlit_app_smoke():
    """Smoke test: execute minimal Streamlit app using official AppTest harness."""
    try:
        from streamlit.testing.v1 import AppTest
    except ImportError:
        pytest.skip("streamlit.testing.v1.AppTest is not available in current environment")

    app_path = APP_DIR / "app.py"
    assert app_path.is_file(), f"app.py not found at {app_path}"

    # Initialize and execute the Streamlit application in-memory
    at = AppTest.from_file(str(app_path))
    at.run()

    # Assert no unhandled runtime exceptions occurred
    assert not at.exception, (
        f"Streamlit application encountered unhandled exception(s): {at.exception}"
    )

    # Assert main title is rendered as expected
    assert len(at.title) > 0, "No title elements rendered by Streamlit application"
    assert at.title[0].value == "MST vs K-Means Robustness Analysis"


def test_utils_package_exports_canonical_math_helpers():
    """Verify that clustering_lab.utils exports compute_sample_std and math_helpers exists."""
    math_helpers_path = APP_DIR / "clustering_lab" / "utils" / "math_helpers.py"
    assert math_helpers_path.is_file(), f"Expected math_helpers module missing at {math_helpers_path}"

    import clustering_lab.utils as utils
    assert hasattr(utils, "compute_sample_std"), "clustering_lab.utils must export compute_sample_std"
    assert callable(utils.compute_sample_std)


def test_canonical_math_helper_sample_std_properties():
    """Verify mathematical properties of canonical compute_sample_std helper."""
    from clustering_lab.utils import compute_sample_std
    import numpy as np

    # 1. Known sample with independently calculated expected standard deviation
    # [2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0]
    # Sum = 40, Mean = 5.0, sum of squared differences = 32, N = 8, ddof = 1 -> variance = 32/7
    data = [2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0]
    expected_std = np.sqrt(32.0 / 7.0)
    assert compute_sample_std(data) == pytest.approx(expected_std, abs=1e-12)

    # 2. Constant data with zero variance
    assert compute_sample_std([7.0, 7.0, 7.0, 7.0]) == 0.0

    # 3. Single observation
    assert compute_sample_std([42.0]) == 0.0

    # 4. Empty observations
    assert compute_sample_std([]) == 0.0

    # 5. Floating-point data
    float_data = [1.5, 2.5, 3.5]
    # mean=2.5, diffs=[-1, 0, 1], sq_sum=2, ddof=1 -> var=2/2=1.0, std=1.0
    assert compute_sample_std(float_data) == pytest.approx(1.0, abs=1e-12)

    # 6. Appropriate ddof boundary behavior
    # ddof=0 -> population std
    pop_std = np.sqrt(2.0 / 3.0)
    assert compute_sample_std(float_data, ddof=0) == pytest.approx(pop_std, abs=1e-12)
    # len(data) <= ddof guard: 3 elements with ddof=3 or ddof=4 -> 0.0
    assert compute_sample_std(float_data, ddof=3) == 0.0
    assert compute_sample_std(float_data, ddof=4) == 0.0
