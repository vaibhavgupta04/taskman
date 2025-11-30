# TaskMan - Task Management API

FastAPI-based task management system with authentication, role-based access control, and advanced filtering.

## Running the Application

### 1. Run Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn apps.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Run via Docker

```bash
# Start the application
docker-compose up

# Stop the application
docker-compose down
```

- The API will be available at `http://localhost:8000`
- NOTE : Added .env for local testing (Not Ideal to keep .env in repo for Production) 
## API Endpoints

### Authentication
- `POST /register` - Register a new user
- `POST /login` - Login and get access token
- `DELETE /users/{user_id}` - Deactivate a user (admin only)

### Tasks
- `POST /tasks/` - Create a task
- `GET /tasks/{task_id}` - Get task by ID
- `PUT /tasks/{task_id}` - Update a task
- `DELETE /tasks/{task_id}` - Delete a task (admin only)
- `PUT /tasks/bulk` - Bulk update tasks
- `POST /tasks/{task_id}/assign/{user_id}` - Assign user to task
- `POST /tasks/{task_id}/subtasks` - Create a subtask

### Features
- `GET /tasks/` - List tasks (with filtering)
- `GET /features/task-distribution` - Get task distribution by user
- `GET /features/overdue-tasks` - Get overdue tasks summary

### Documentation
- Swagger UI: `http://localhost:8000/docs`
- Postman Collection : `TaskMan.postman_collection.json`

### Improvements
- Using Elasticsearch for search functionality
- Using SQL for database in Docker
- Using design patterns for better code organization Domain Driven Design
- Using multi-stage Dockerfile for better performance

