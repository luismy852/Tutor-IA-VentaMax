import logging
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from models.schemas import ChatRequest, ChatResponse, ConversationResponse
from repositories.conversation_repository import ConversationRepository
from services.chat_service import ChatService
from api.dependencies import get_repository, get_chat_service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    repo: ConversationRepository = Depends(get_repository),
    service: ChatService = Depends(get_chat_service),
):
    session = await repo.get_session(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    if session["state"] != "chat":
        raise HTTPException(status_code=400, detail="Sesión aún en modo evaluación")

    response = await service.get_response(request.message, request.session_id)
    await repo.save(request.message, response, request.session_id)
    return ChatResponse(response=response)


async def _chat_stream_generator(
    session_id: str,
    message: str,
    service: ChatService,
    repo: ConversationRepository,
):
    full_response = ""
    async for chunk in service.get_response_stream(message, session_id):
        full_response += chunk
        encoded = chunk.replace('\n', '\\n')
        yield f"data: {encoded}\n\n"
    await repo.save(message, full_response, session_id)


@router.post("/chat/stream")
async def chat_stream(
    request: ChatRequest,
    repo: ConversationRepository = Depends(get_repository),
    service: ChatService = Depends(get_chat_service),
):
    session = await repo.get_session(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    if session["state"] not in ("chat", "simulacion"):
        raise HTTPException(status_code=400, detail="Sesión aún en modo evaluación")

    return StreamingResponse(
        _chat_stream_generator(request.session_id, request.message, service, repo),
        media_type="text/event-stream",
    )


@router.get("/history", response_model=list[ConversationResponse])
async def history(
    limit: int = 50,
    repo: ConversationRepository = Depends(get_repository),
):
    return await repo.get_all(limit=limit)


@router.get("/history/{session_id}", response_model=list[ConversationResponse])
async def get_history_by_session(
    session_id: str,
    limit: int = 50,
    repo: ConversationRepository = Depends(get_repository),
):
    return await repo.get_by_session_id(session_id, limit=limit)


@router.get(
    "/history/conversation/{conversation_id}", response_model=ConversationResponse
)
async def get_conversation(
    conversation_id: int,
    repo: ConversationRepository = Depends(get_repository),
):
    conv = await repo.get_by_id(conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")
    return conv
