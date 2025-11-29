
from fastapi.testclient import TestClient
from apps.main import app
from apps.auth.dependencies import get_current_user
from apps.models.users import User
from apps.stores.db import get_session, db_manager
from sqlmodel import Session, SQLModel, create_engine

# Setup in-memory DB for testing
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url)

def get_session_override():
    with Session(engine) as session:
        yield session

def get_current_user_override():
    return User(user_id=1, username="testuser", role="admin")

app.dependency_overrides[get_session] = get_session_override
app.dependency_overrides[get_current_user] = get_current_user_override

client = TestClient(app)

def test_bulk_update():
    # Create tables
    SQLModel.metadata.create_all(engine)
    
    # Create tasks
    task1_data = {"title": "Task 1", "status": "todo"}
    task2_data = {"title": "Task 2", "status": "todo"}
    
    res1 = client.post("/tasks/", json=task1_data)
    assert res1.status_code == 200
    t1 = res1.json()
    
    res2 = client.post("/tasks/", json=task2_data)
    assert res2.status_code == 200
    t2 = res2.json()
    
    print(f"Created tasks: {t1['task_id']}, {t2['task_id']}")
    
    # Bulk update
    bulk_update_data = {
        "task_ids": [t1['task_id'], t2['task_id']],
        "updates": {"status": "done"}
    }
    
    res_bulk = client.put("/tasks/bulk", json=bulk_update_data)
    if res_bulk.status_code != 200:
        print(f"Bulk update failed: {res_bulk.text}")
    assert res_bulk.status_code == 200
    updated_tasks = res_bulk.json()
    
    print(f"Updated {len(updated_tasks)} tasks")
    
    # Verify
    res_get1 = client.get(f"/tasks/{t1['task_id']}")
    res_get2 = client.get(f"/tasks/{t2['task_id']}")
    
    print(f"Task 1 status: {res_get1.json()['status']}")
    print(f"Task 2 status: {res_get2.json()['status']}")
    
    assert res_get1.json()['status'] == "done"
    assert res_get2.json()['status'] == "done"
    
    print("Verification Successful!")

if __name__ == "__main__":
    test_bulk_update()
