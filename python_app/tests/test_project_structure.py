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
