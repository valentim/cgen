from injector import Module, provider, singleton
from sqlalchemy.orm import Session
from config.settings import Settings
from db.session import get_db
from openai import OpenAI
from ai.openai_provider import OpenAIProvider
from ai.prompt_template import PromptTemplate
from evaluation.code_executor import CodeExecutor
from evaluation.code_evaluator import CodeEvaluator
from tot.three_of_thoughts import TreeOfThoughts
from db.trainings import Trainings
from summarize_results import SummarizeResults

class DependencyContainer(Module):
    @singleton
    @provider
    def provide_settings(self) -> Settings:
        return Settings()

    @singleton
    @provider
    def provide_openai(self, settings: Settings) -> OpenAI:
        return OpenAI(api_key=settings.OPENAI_API_KEY)

    @singleton
    @provider
    def provide_prompt_template(self) -> PromptTemplate:
        return PromptTemplate()

    @singleton
    @provider
    def provide_ai_provider(self, openai: OpenAI, prompt_template: PromptTemplate) -> OpenAIProvider:
        return OpenAIProvider(openai, prompt_template)

    @singleton
    @provider
    def provide_code_executor(self) -> CodeExecutor:
        return CodeExecutor()

    @singleton
    @provider
    def provide_code_evaluator(self, code_executor: CodeExecutor) -> CodeEvaluator:
        return CodeEvaluator(code_executor)

    @singleton
    @provider
    def provide_tree_of_thoughts(self, ai_provider: OpenAIProvider, code_evaluator: CodeEvaluator, settings: Settings) -> TreeOfThoughts:
        return TreeOfThoughts(ai_provider, code_evaluator, max_depth=settings.THREE_MAX_DEPTH)

    @singleton
    @provider
    def provide_trainings(self, db: Session) -> Trainings:
        return Trainings(db)

    @singleton
    @provider
    def provide_db(self) -> Session:
        return next(get_db())

    @singleton
    @provider
    def provide_summarize_results(self, trainings: Trainings) -> SummarizeResults:
        return SummarizeResults(trainings)
