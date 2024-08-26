from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URI = 'mysql+pymysql://admin:admin@123@localhost/task_management_db'
engine = create_engine(DATABASE_URI)
Session = sessionmaker(bind=engine)

# Optionally, you can provide a function to get a new session
def get_session():
    return Session()
