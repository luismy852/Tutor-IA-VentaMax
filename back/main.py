from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from core.logging import setup_logging
from api.dependencies import get_repository
from routers import sessions, chat, evaluation

setup_logging()

app = FastAPI(title="VentaMax Tutor IA")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sessions.router)
app.include_router(chat.router)
app.include_router(evaluation.router)


@app.on_event("startup")
async def startup():
    repo = get_repository()
    await repo.init_db()
