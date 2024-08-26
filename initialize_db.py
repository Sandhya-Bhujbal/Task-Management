from app.config import engine
from app.models import Base

# Create all tables
Base.metadata.create_all(engine)
