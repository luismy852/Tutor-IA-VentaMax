from fastapi import APIRouter, Depends, HTTPException
from models.schemas import SessionResponse, SessionStateUpdate
from repositories.conversation_repository import ConversationRepository
from api.dependencies import get_repository

router = APIRouter(prefix="/session", tags=["sessions"])


@router.post("", response_model=SessionResponse)
async def new_session(repo: ConversationRepository = Depends(get_repository)):
    session_id = await repo.create_session()
    return SessionResponse(session_id=session_id, state="evaluacion")


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session_info(
    session_id: str,
    repo: ConversationRepository = Depends(get_repository),
):
    session = await repo.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    return SessionResponse(session_id=session["id"], state=session["state"])


@router.put("/{session_id}/state")
async def update_state(
    session_id: str,
    request: SessionStateUpdate,
    repo: ConversationRepository = Depends(get_repository),
):
    session = await repo.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    await repo.update_session_state(session_id, request.state)
    return {"message": f"Estado actualizado a {request.state}"}
