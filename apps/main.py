from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from apps.stores.db import db_manager
from apps.routes import users, tasks

app = FastAPI()


# CORS (open for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    db_manager.init_db()
    yield
    db_manager.close_db()



app = FastAPI(lifespan=lifespan)

app.include_router(users.router, tags=["users"])
app.include_router(tasks.router, tags=["tasks"])

@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}