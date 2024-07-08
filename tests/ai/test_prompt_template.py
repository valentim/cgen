import pytest
from unittest.mock import patch
from ai.prompt_template import PromptTemplate


@pytest.fixture
@patch("ai.prompt_template.Settings")
def mock_settings(MockSettings):
    MockSettings.return_value.PROMPT_TEMPLATE = {
        "prompt": {
            "generate_code_template": """
$text

It must satisfy these test cases:
$test_cases

Note: Return only the function without any explanations or examples.

Details:
$details

Errors:
$errors

This code does not satisfy the test cases:
$bad_code
""",
            "generate_details_template": """
Details:
$details

Your task is to add a slight variation based on the details. Return a json in this format:
```
{"details": ["slight variation", ...]}
```
""",
        }
    }
    return MockSettings


@patch("ai.prompt_template.Settings")
def test_initialization_failure_no_generate_details_template(MockSettings):
    MockSettings.return_value.PROMPT_TEMPLATE = {
        "prompt": {
            "generate_code_template": """
$text

It must satisfy these test cases:
$test_cases

Note: Return only the function without any explanations or examples.

Details:
$details

Errors:
$errors

This code does not satisfy the test cases:
$bad_code
"""
        }
    }
    with pytest.raises(ValueError, match="Prompt template is not properly configured"):
        PromptTemplate()


def test_initialization_success(mock_settings):
    template = PromptTemplate()
    assert isinstance(template, PromptTemplate)


@patch("ai.prompt_template.Settings")
def test_initialization_failure_no_generate_code_template(MockSettings):
    MockSettings.return_value.PROMPT_TEMPLATE = {"prompt": {}}
    with pytest.raises(ValueError):
        PromptTemplate()


def test_render_generate_code(mock_settings):
    template = PromptTemplate()
    result = template.render(
        type="generate_code",
        text="Write a function named my_function",
        test_cases="\n- here\n- there",
        details="- here",
        errors="- here",
        bad_code="```python\nbad_code\n```",
    )
    expected = """
Write a function named my_function

It must satisfy these test cases:

- here
- there

Note: Return only the function without any explanations or examples.

Details:
- here

Errors:
- here

This code does not satisfy the test cases:
```python
bad_code
```
"""
    assert result.strip() == expected.strip()


def test_render_generate_details(mock_settings):
    template = PromptTemplate()
    result = template.render(
        type="generate_details",
        details="This function should add two numbers and return the result.",
    )
    expected = """
Details:
This function should add two numbers and return the result.

Your task is to add a slight variation based on the details. Return a json in this format:
```
{"details": ["slight variation", ...]}
```
"""
    assert result.strip() == expected.strip()


def test_render_invalid_type(mock_settings):
    template = PromptTemplate()
    with pytest.raises(ValueError):
        template.render(type="invalid_type")
