import pytest
from unittest.mock import patch, MagicMock
from ai.openai_provider import OpenAIProvider
from ai.prompt_template import PromptTemplate
import openai
import logging


@pytest.fixture
def openAiProvider():
    mock_client = MagicMock()
    with patch.object(
        OpenAIProvider, "create_or_get_assistant", return_value=MagicMock()
    ):
        return OpenAIProvider(client=mock_client, prompt_template=PromptTemplate())


@patch.object(OpenAIProvider, "_retry_with_backoff")
def test_get_prompt_details(mock_retry_with_backoff, openAiProvider):
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = (
        '{"details": ["variation1", "variation2"]}'
    )
    mock_retry_with_backoff.return_value = mock_response

    class MockPrompt:
        task = "task"
        details = ["detail1", "detail2"]

    prompt = MockPrompt()
    details = openAiProvider.get_prompt_details(prompt)

    assert details == ["variation1", "variation2"]


@patch.object(OpenAIProvider, "_retry_with_backoff")
def test_generate_code(mock_retry_with_backoff, openAiProvider):
    mock_thread = MagicMock()
    mock_retry_with_backoff.side_effect = [
        mock_thread,
        MagicMock(status="completed"),
        MagicMock(
            data=[
                MagicMock(
                    content=[
                        MagicMock(text=MagicMock(value="def add(a, b): return a + b"))
                    ]
                )
            ]
        ),
    ]

    class MockNode:
        class MockPrompt:
            task = "task"
            test_list = ["assert add(1, 2) == 3"]
            details = []
            errors = []

        prompt = MockPrompt()
        parent = None

    node = MockNode()
    code = openAiProvider.generate_code(node)

    assert code == "def add(a, b): return a + b"


def test_create_assistant(openAiProvider):
    openAiProvider._client.beta.assistants.create.return_value = MagicMock()

    with patch.object(OpenAIProvider, "list_assistants", return_value=[]):
        openAiProvider.create_assistant()

    openAiProvider._client.beta.assistants.create.assert_called_once_with(
        name="Python Developer Tutor",
        instructions="You are a personal Python developer tutor. Write code to answer questions.",
        tools=[{"type": "code_interpreter"}],
        model="gpt-4o",
    )


@pytest.mark.parametrize(
    "exception, exception_message",
    [
        (
            openai.RateLimitError(
                "Rate limit exceeded",
                response=MagicMock(request=MagicMock()),
                body=None,
            ),
            "Rate limit exceeded",
        ),
        (Exception("An unexpected error occurred"), "An unexpected error occurred"),
    ],
)
def test_retry_with_backoff(openAiProvider, exception, exception_message):
    mock_func = MagicMock(side_effect=exception)

    with pytest.raises(type(exception)):
        openAiProvider._retry_with_backoff(mock_func)

    if isinstance(exception, openai.RateLimitError):
        assert mock_func.call_count == 5
    else:
        assert mock_func.call_count == 1


def test_list_assistants_error(openAiProvider):
    openAiProvider._client.beta.assistants.list.side_effect = Exception("Error")
    assistants = openAiProvider.list_assistants()
    assert assistants == []


def test_get_prompt_details_error(openAiProvider):
    openAiProvider._client.chat.completions.create.side_effect = Exception("Error")
    with pytest.raises(Exception, match="Error"):
        openAiProvider.get_prompt_details(MagicMock())


def test_generate_code_error(openAiProvider):
    openAiProvider._client.beta.threads.create.side_effect = Exception("Error")
    with pytest.raises(Exception, match="Error"):
        openAiProvider.generate_code(MagicMock())


def test_list_assistants_exception(openAiProvider):
    openAiProvider._client.beta.assistants.list.side_effect = Exception("API Error")
    assistants = openAiProvider.list_assistants()
    assert assistants == []
    assert openAiProvider._client.beta.assistants.list.called


def test_logging_error_during_list_assistants(openAiProvider, caplog):
    openAiProvider._client.beta.assistants.list.side_effect = Exception("API Error")
    with caplog.at_level(logging.ERROR):
        assistants = openAiProvider.list_assistants()
    assert "An error occurred while listing assistants" in caplog.text
