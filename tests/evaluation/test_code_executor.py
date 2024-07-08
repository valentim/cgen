import pytest
import sys
import subprocess
from unittest.mock import patch
from evaluation.code_executor import CodeExecutor


@pytest.fixture
def code_executor():
    return CodeExecutor()


def test_identify_imports(code_executor):
    code = "import math\nimport sys"
    code_executor.identify_imports(code)
    assert code_executor.required_modules == ["math", "sys"]


def test_is_standard_library(code_executor):
    assert code_executor.is_standard_library("sys")
    assert not code_executor.is_standard_library("numpy")


@patch("evaluation.code_executor.subprocess.check_call")
def test_install_modules(mock_check_call, code_executor):
    code_executor.required_modules = ["numpy"]
    code_executor.install_modules()
    mock_check_call.assert_called_once_with(
        [sys.executable, "-m", "pip", "install", "numpy"]
    )


@patch("evaluation.code_executor.importlib.import_module")
def test_import_modules(mock_import_module, code_executor):
    code_executor.required_modules = ["math"]
    code_executor.import_modules()
    mock_import_module.assert_called_once_with("math")


@patch(
    "evaluation.code_executor.subprocess.check_call",
    side_effect=subprocess.CalledProcessError(1, "pip install"),
)
def test_install_modules_failure(mock_check_call, code_executor, caplog):
    code_executor.required_modules = ["invalid_module"]
    code_executor.install_modules()
    assert "Failed to install invalid_module" in caplog.text


@patch.object(CodeExecutor, "identify_imports")
@patch.object(CodeExecutor, "install_modules")
@patch.object(CodeExecutor, "import_modules")
def test_execute_test_success(
    mock_import_modules, mock_install_modules, mock_identify_imports, code_executor
):
    code = """
def add(a, b):
    return a + b
"""
    test_string = "assert add(1, 2) == 3"
    success, error = code_executor.execute_test(code, test_string)
    assert success
    assert error is None


@patch.object(CodeExecutor, "identify_imports")
@patch.object(CodeExecutor, "install_modules")
@patch.object(CodeExecutor, "import_modules")
def test_execute_test_failure(
    mock_import_modules, mock_install_modules, mock_identify_imports, code_executor
):
    code = """
def add(a, b):
    return a + b
"""
    test_string = "assert add(1, 2) == 4"
    success, error = code_executor.execute_test(code, test_string)
    assert not success
    assert "Test failed" in error


@patch.object(CodeExecutor, "identify_imports")
@patch.object(CodeExecutor, "install_modules")
@patch.object(CodeExecutor, "import_modules")
def test_execute_test_invalid_code(
    mock_import_modules, mock_install_modules, mock_identify_imports, code_executor
):
    code = """
def add(a, b):
    return a +
"""
    test_string = "assert add(1, 2) == 3"
    success, error = code_executor.execute_test(code, test_string)
    assert not success
    assert error == ["The code you provided was invalid"]


@patch.object(CodeExecutor, "identify_imports")
@patch.object(CodeExecutor, "install_modules")
@patch.object(CodeExecutor, "import_modules")
def test_execute_test_missing_equality(
    mock_import_modules, mock_install_modules, mock_identify_imports, code_executor
):
    code = """
def add(a, b):
    return a + b
"""
    test_string = "assert add(1, 2)"
    result = code_executor.execute_test(code, test_string)
    assert result == (False, ["The code you provided was invalid"])
