from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from apps.stores.db import db_manager


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
    # Startup
    db_manager.init_db()
    yield
    # Shutdown
    db_manager.close_db()


from apps.routes import users

app = FastAPI(lifespan=lifespan)

app.include_router(users.router, tags=["users"])

@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}