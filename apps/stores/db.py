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


# Create a global instance
db_manager = DatabaseManager()

# Convenience functions for backward compatibility
def init_db():
    db_manager.init_db()


def close_db():
    db_manager.close_db()


def get_session():
    yield from db_manager.get_session()