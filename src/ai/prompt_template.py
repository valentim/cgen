from string import Template
from config.settings import Settings


class PromptTemplate:
    def __init__(self):
        prompt_template = Settings().PROMPT_TEMPLATE.get("prompt", {})

        if "generate_code_template" not in prompt_template:
            raise ValueError(
                "Prompt template is not properly configured. Please check the Readme for more information."
            )

        if "generate_details_template" not in prompt_template:
            raise ValueError(
                "Prompt template is not properly configured. Please check the Readme for more information."
            )

        self._generate_code_template = Template(
            prompt_template["generate_code_template"]
        )
        self._generate_details_template = Template(
            prompt_template["generate_details_template"]
        )

    def render(self, type, **kwargs) -> str:
        if type == "generate_code":
            return self._generate_code_template.safe_substitute(**kwargs)
        elif type == "generate_details":
            return self._generate_details_template.safe_substitute(**kwargs)
        else:
            raise ValueError(f"Invalid prompt type: {type}")
