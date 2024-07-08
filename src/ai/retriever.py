from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from sqlalchemy.orm import DeclarativeBase, Session
from typing import Any, Optional
from db.models import Training
from db.trainings import get_trainings


class Retriever(BaseRetriever):
    content_model: DeclarativeBase = Training
    session: Session
    threshold: float = 0.5
    dataset: Optional[Any] = None
    embedding_llm: Optional[Any] = None
    embedding_column: str = "embedding"
    top_k: int = 5

    def _get_relevant_documents(self, query: str, ai_provider, *, run_manager):
        relevant_contents = self._get_most_relevant_contents_from_message(
            query,
            ai_provider=ai_provider,
            top=self.top_k,
            session=self.session,
            embeddings_llm=self.embedding_llm,
        )
        print(relevant_contents[0].score)
        return [
            Document(
                page_content=f"{content.solution}",
                metadata={
                    "context": content.context,
                    "problem": content.problem,
                    "score": content.score,
                },
            )
            for content in relevant_contents
        ]

    def _get_most_relevant_contents_from_message(
        self,
        ai_provider,
        message,
        top=5,
        session=None,
        embeddings_llm=None,
    ):
        message_embedding = ai_provider.generate_embedding(message, embeddings_llm)

        return get_trainings(session, top, message_embedding)
