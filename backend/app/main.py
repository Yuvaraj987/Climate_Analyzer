from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.mongodb import connect_to_mongo, close_mongo_connection
from app.routes import hazards, regions


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    yield
    await close_mongo_connection()


app = FastAPI(
    title=settings.app_name,
    description="Historical climate hazard analysis API.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin, "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(regions.router, prefix=settings.api_prefix)
app.include_router(hazards.router, prefix=settings.api_prefix)


@app.get("/")
async def root():
    return {"message": "Climate Hazard Analyzer API", "docs": "/docs"}


@app.get("/health")
async def health():
    return {"status": "ok"}
