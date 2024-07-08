from .base import Base
from .session import engine
from .models import Training

Base.metadata.create_all(bind=engine)
