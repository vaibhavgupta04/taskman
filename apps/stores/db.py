from sqlmodel import create_engine, SQLModel, Session
import os


class DatabaseManager:
    def __init__(self, database_url: str = None):
        self.database_url = database_url or os.getenv(
            "DATABASE_URL", "sqlite:///./task_manager.db"
        )
        self.engine = create_engine(
            self.database_url, connect_args={"check_same_thread": False}
        )
    
    def init_db(self):
        SQLModel.metadata.create_all(self.engine)
    
    def close_db(self):
        self.engine.dispose()
    
    def get_session(self):
        with Session(self.engine) as session:
            yield session


db_manager = DatabaseManager()


def get_session():
    with Session(db_manager.engine) as session:
        yield session