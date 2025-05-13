from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager

from src.db.connection import init_db
from src.api.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):    
    init_db()
    yield
    print("server is stopping")


app = FastAPI(lifespan=lifespan)


app.include_router(router)
