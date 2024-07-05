import ast
import subprocess
import sys
import importlib
from utils.logger import get_logger

_LOGGER = get_logger(__name__)


class CodeExecutor:
    def __init__(self):
        self.required_modules = []

    def identify_imports(self, code):
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self.required_modules.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                self.required_modules.append(node.module)

    def is_standard_library(self, module_name):
        try:
            spec = importlib.util.find_spec(module_name)
            return (
                spec is not None
                and spec.origin is not None
                and "site-packages" not in spec.origin
            )
        except ModuleNotFoundError:
            return False

    def install_modules(self):
        for module in self.required_modules:
            if not self.is_standard_library(module):
                try:
                    subprocess.check_call(
                        [sys.executable, "-m", "pip", "install", module]
                    )
                except subprocess.CalledProcessError as e:
                    _LOGGER.error(f"Failed to install {module}: {e}")
                else:
                    _LOGGER.info(f"Successfully installed {module}")

    def import_modules(self):
        for module in self.required_modules:
            if module:
                globals()[module] = importlib.import_module(module)

    def execute_test(self, code, test_string):
        try:
            self.identify_imports(code)
            self.install_modules()
            self.import_modules()

            test_string = test_string.replace("assert ", "").strip()
            if "==" not in test_string:
                raise ValueError(
                    "Test string must contain '==' to separate function and result."
                )

            func_call, expected_result = map(str.strip, test_string.split("=="))
            expected_result = ast.literal_eval(expected_result)

            parsed_call = ast.parse(func_call, mode="eval").body
            func_name = parsed_call.func.id
            func_args = [ast.literal_eval(arg) for arg in parsed_call.args]

            exec(code, globals())

            parsed_call = ast.parse(func_call, mode="eval").body
            func_name = parsed_call.func.id
            func_args = [ast.literal_eval(arg) for arg in parsed_call.args]

            result = eval(f"{func_name}(*{func_args})", globals())

            assert (
                result == expected_result
            ), f"Test failed: expected {expected_result}, got {result}"
            return (True, None)
        except AssertionError as e:
            _LOGGER.error(f"Test failed: {e}")
            return (False, str(e))
        except Exception as e:
            _LOGGER.error(f"An unexpected error occurred during the tests: {e}")
            return (False, ["The code you provided was invalid"])
