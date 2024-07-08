import json
import time
import random
import openai
from langchain_openai import OpenAIEmbeddings
from config.settings import Settings
from utils.logger import get_logger
from . import format_list
from typing import List, Callable, Any
from .prompt_template import PromptTemplate
from .prompt import Prompt
from tot.node import Node

_LOGGER = get_logger(__name__)
class OpenAIProvider:
    BASE_VARIATIONS = Settings().BASE_VARIATIONS
    EMBEDDINGS_LLM = OpenAIEmbeddings(openai_api_key=Settings().OPENAI_API_KEY)

    def __init__(self, client: openai.OpenAI, prompt_template: PromptTemplate):
        self._client: openai.OpenAI = client
        self._prompt_template: PromptTemplate = prompt_template
        self._assistant = self.create_or_get_assistant()

    def list_assistants(self) -> List[Any]:
        try:
            response = self._client.beta.assistants.list()
            return response.data
        except Exception as e:
            _LOGGER.error(f"An error occurred while listing assistants: {e}")
            return []

    def generate_embeddings(self, documents: List[str], embedding_llm_instance: OpenAIEmbeddings):
        return embedding_llm_instance.embed_documents(documents)

    def generate_embedding(self, document: str, embedding_llm_instance: OpenAIEmbeddings):
        return embedding_llm_instance.embed_query(document)

    def create_or_get_assistant(self) -> Any:
        assistants = self.list_assistants()
        for assistant in assistants:
            if assistant.name == Settings().ASSISTANT_NAME:
                _LOGGER.info(f"Assistant {Settings().ASSISTANT_NAME} already exists.")
                return assistant

        return self.create_assistant()

    def create_assistant(self) -> Any:
        assistant = self._client.beta.assistants.create(
            name=Settings().ASSISTANT_NAME,
            instructions=Settings().ASSISTANT_INSTRUCTIONS,
            tools=Settings().ASSISTANT_TOOLS,
            model=Settings().ASSISTANT_MODEL,
        )
        return assistant

    def get_prompt_details(self, prompt: Prompt) -> List[str]:
        prompt_message = self._prompt_template.render(
            "generate_details", details=format_list(prompt.details, prefix="- ")
        )

        response = self._retry_with_backoff(
            lambda: self._client.chat.completions.create(
                model=Settings().ASSISTANT_MODEL,
                response_format={"type": "json_object"},
                messages=[
                    {
                        "role": "system",
                        "content": [
                            {
                                "type": "text",
                                "text": Settings().ASSISTANT_INSTRUCTIONS_FOR_DETAILS,
                            }
                        ],
                    },
                    {
                        "role": "user",
                        "content": [{"type": "text", "text": prompt_message}],
                    },
                ],
                temperature=Settings().ASSISTANT_TEMPERATURE,
                max_tokens=Settings().ASSISTANT_MAX_TOKENS,
                top_p=Settings().ASSISTANT_TOP_P,
                frequency_penalty=Settings().ASSISTANT_FREQUENCY_PENALTY,
                presence_penalty=Settings().ASSISTANT_PRESENCE_PENALTY,
            )
        )

        response_json = json.loads(response.choices[0].message.content)
        details = response_json["details"]

        return details

    def generate_code(self, node: Node) -> str:
        prompt = node.prompt
        prompt_message = self._prompt_template.render(
            "generate_code",
            text=prompt.task,
            test_cases=format_list(prompt.test_list)
            if prompt.test_list
            else "No test cases available",
            details=format_list(prompt.details, prefix="- ")
            if prompt.details
            else "No details available",
            errors=format_list(prompt.errors, prefix="- ")
            if prompt.errors
            else "No errors available",
            bad_code=node.parent.code if node.parent and node.parent.code else "N/A",
        )

        thread = self._client.beta.threads.create()
        self._retry_with_backoff(
            lambda: self._client.beta.threads.messages.create(
                thread_id=thread.id, role="user", content=prompt_message
            )
        )

        assistant = self._assistant
        run = self._retry_with_backoff(
            lambda: self._client.beta.threads.runs.create_and_poll(
                thread_id=thread.id, assistant_id=assistant.id
            )
        )

        if run.status == "completed":
            messages = self._retry_with_backoff(
                lambda: self._client.beta.threads.messages.list(thread_id=thread.id)
            )

            try:
                for message in messages.data:
                    if message.content:
                        raw_code = message.content[0].text.value

                        return raw_code.strip("```python").strip("```")

                return ""
            except Exception as e:
                _LOGGER.error(f"An unexpected error ocurred to get messages: {e}")
                _LOGGER.error(messages)
                raise
        else:
            _LOGGER.error(f"Thread run failed with status: {run.status}")
            raise Exception(f"Thread run failed with status: {run.status}")

    def _retry_with_backoff(
        self, func: Callable[[], Any], max_retries=5, base_delay=1, max_delay=60
    ) -> Any:
        for retry in range(max_retries):
            try:
                return func()
            except openai.RateLimitError as e:
                if retry == max_retries - 1:
                    raise
                else:
                    delay = min(
                        base_delay * (2**retry) + random.uniform(0, 1), max_delay
                    )
                    _LOGGER.info(
                        f"Rate limit exceeded. Retrying in {delay:.2f} seconds... {e}"
                    )
                    time.sleep(delay)
            except Exception as e:
                _LOGGER.error(
                    f"An unexpected error occurred in OpenAI api integration: {e}"
                )
                raise
