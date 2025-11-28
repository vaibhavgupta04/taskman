import requests
import sys

BASE_URL = "http://localhost:8000"

def verify():
    # 1. Register User
    username = "testuser_task"
    password = "password123"
    try:
        resp = requests.post(f"{BASE_URL}/register", json={"username": username, "password": password, "role": "member"})
        if resp.status_code == 200:
            print("User registered successfully")
        elif resp.status_code == 400 and "already registered" in resp.text:
            print("User already exists")
        else:
            print(f"Failed to register user: {resp.text}")
            return
    except Exception as e:
        print(f"Failed to connect: {e}")
        return

    # 2. Login
    resp = requests.post(f"{BASE_URL}/login", json={"username": username, "password": password})
    if resp.status_code != 200:
        print(f"Failed to login: {resp.text}")
        return
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("Logged in successfully")

    # 3. Create Task
    task_data = {
        "title": "Test Task",
        "description": "This is a test task",
        "status": "todo",
        "priority": "high"
    }
    resp = requests.post(f"{BASE_URL}/tasks/", json=task_data, headers=headers)
    if resp.status_code != 200:
        print(f"Failed to create task: {resp.text}")
        return
    task = resp.json()
    task_id = task["task_id"]
    print(f"Task created: {task_id}")

    # 4. List Tasks
    resp = requests.get(f"{BASE_URL}/tasks/", headers=headers)
    if resp.status_code != 200:
        print(f"Failed to list tasks: {resp.text}")
        return
    tasks = resp.json()
    print(f"Listed {len(tasks)} tasks")

    # 5. Update Task
    update_data = {"status": "in_progress"}
    resp = requests.put(f"{BASE_URL}/tasks/{task_id}", json=update_data, headers=headers)
    if resp.status_code != 200:
        print(f"Failed to update task: {resp.text}")
        return
    print("Task updated")

    # 7. Create Subtask
    subtask_data = {
        "title": "Subtask",
        "description": "This is a subtask",
        "status": "todo",
        "priority": "low"
    }
    resp = requests.post(f"{BASE_URL}/tasks/{task_id}/subtasks", json=subtask_data, headers=headers)
    if resp.status_code != 200:
        print(f"Failed to create subtask: {resp.text}")
        return
    print("Subtask created")

    # 8. Delete Task
    resp = requests.delete(f"{BASE_URL}/tasks/{task_id}", headers=headers)
    if resp.status_code != 200:
        print(f"Failed to delete task: {resp.text}")
        return
    print("Task deleted")

if __name__ == "__main__":
    verify()
