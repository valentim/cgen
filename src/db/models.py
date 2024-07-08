from sqlalchemy import Column, Integer, Text, Float, DateTime, func
from pgvector.sqlalchemy import Vector
from .base import Base


class Training(Base):
    __tablename__ = "trainings"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, unique=True, nullable=True)
    problem = Column(Text, unique=True, nullable=False)
    solution = Column(Text, nullable=False)
    embedding = Column(Vector(1536), nullable=False)
    score = Column(Float, nullable=False)
    context = Column(Text, nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
