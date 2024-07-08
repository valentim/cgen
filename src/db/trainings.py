from sqlalchemy.orm import Session
from sqlalchemy import select, func
from .models import Training

def store_training(db: Session, task_id: int, problem: str, solution: str, embedding: list, score: float, context: str):
    existing_training = get_training_by_task_id(db, task_id)

    if existing_training:
        existing_training.task_id = task_id
        existing_training.solution = solution
        existing_training.embedding = embedding
        existing_training.score = score
        existing_training.context = context
        existing_training.updated_at = func.now()
    else:
        new_training = Training(task_id=task_id, problem=problem, solution=solution, embedding=embedding, score=score, context=context)
        db.add(new_training)
        db.commit()
        db.refresh(new_training)
        return new_training

    db.commit()
    db.refresh(existing_training)
    return existing_training

def get_trainings(db: Session, top: int, message_embedding: list):
    cosine_similarity_threshold = 0.5
    model = Training
    filters = [
        model.embedding.cosine_distance(message_embedding) < cosine_similarity_threshold,
    ]

    possible_contents = db.scalars(
        select(model)
        .filter(*filters)
        .order_by(getattr(model, 'embedding').cosine_distance(message_embedding))
        .limit(top)
    ).all()
    return possible_contents

def get_training_by_task_id(db: Session, task_id: str):
    return db.query(Training).filter(Training.task_id == task_id).first()

def get_all_trainings(db: Session):
    return db.query(Training).all()
