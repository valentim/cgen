import os
import json
import toml
from typing import List
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class Settings:
    @property
    def ASSISTANT_NAME(self) -> str:
        return os.getenv("ASSISTANT_NAME", "Default Assistant Name")

    @property
    def ASSISTANT_INSTRUCTIONS(self) -> str:
        return os.getenv("ASSISTANT_INSTRUCTIONS", "Default Instructions")

    @property
    def ASSISTANT_INSTRUCTIONS_FOR_DETAILS(self) -> str:
        return os.getenv(
            "ASSISTANT_INSTRUCTIONS_FOR_DETAILS", "Default Instructions for Details"
        )

    @property
    def ASSISTANT_TOOLS(self) -> list:
        tools_str = os.getenv("ASSISTANT_TOOLS", '[{"type": "code_interpreter"}]')
        try:
            return json.loads(tools_str)
        except json.JSONDecodeError:
            raise ValueError("ASSISTANT_TOOLS environment variable is not a valid JSON")

    @property
    def ASSISTANT_MODEL(self) -> str:
        return os.getenv("ASSISTANT_MODEL", "default-model")

    @property
    def ASSISTANT_TEMPERATURE(self) -> float:
        return float(os.getenv("ASSISTANT_TEMPERATURE", 0.1))

    @property
    def ASSISTANT_MAX_TOKENS(self) -> int:
        return int(os.getenv("ASSISTANT_MAX_TOKENS", 2048))

    @property
    def ASSISTANT_TOP_P(self) -> int:
        return int(os.getenv("ASSISTANT_TOP_P", 1))

    @property
    def ASSISTANT_FREQUENCY_PENALTY(self) -> float:
        return float(os.getenv("ASSISTANT_FREQUENCY_PENALTY", 0))

    @property
    def ASSISTANT_PRESENCE_PENALTY(self) -> float:
        return float(os.getenv("ASSISTANT_PRESENCE_PENALTY", 0))

    @property
    def OPENAI_API_KEY(self) -> str | None:
        return os.getenv("OPENAI_API_KEY")

    @property
    def THREE_MAX_DEPTH(self) -> int:
        return int(os.getenv("THREE_MAX_DEPTH", 2))

    @property
    def BASE_VARIATIONS(self) -> List[str]:
        base_variations = os.getenv(
            "BASE_VARIATIONS", '["Use advanced programming techniques."]'
        )
        try:
            return json.loads(base_variations)
        except json.JSONDecodeError:
            raise ValueError("BASE_VARIATIONS environment variable is not a valid JSON")

    @property
    def LOGGING_LEVEL(self) -> str:
        return os.getenv("LOGGING_LEVEL", "INFO")

    @property
    def PROMPT_TEMPLATE(self) -> dict:
        prompt_template_path = os.getenv(
            "PROMPT_TEMPLATE_PATH", "datasets/prompt_template.toml"
        )

        try:
            config_path = Path(prompt_template_path)
            return toml.loads(config_path.read_text())
        except (FileNotFoundError, toml.TomlDecodeError) as e:
            raise ValueError(
                f"Failed to load the prompt template from {prompt_template_path}: {e}"
            )
