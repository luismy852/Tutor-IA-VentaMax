import logging
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from models.schemas import EvaluationRequest, EvaluationQuestion
from repositories.conversation_repository import ConversationRepository
from services.chat_service import ChatService
from services.evaluation_service import EvaluationService
from prompts.prompts import RETROALIMENTACION_PROMPT, RETROALIMENTACION_GENERAL_PROMPT
from domain.constants import QUESTION_COUNT
from api.dependencies import get_repository, get_chat_service, get_evaluation_service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["evaluation"])


@router.get("/questions")
async def get_questions(
    evaluation: EvaluationService = Depends(get_evaluation_service),
):
    return evaluation.get_random_questions()


async def _retroalimentacion_stream(
    context: str,
    session_id: str,
    question_num: int,
    chat: ChatService,
    repo: ConversationRepository,
):
    full_response = ""
    async for chunk in chat.get_response_stream(context, session_id, RETROALIMENTACION_GENERAL_PROMPT):
        full_response += chunk
        encoded = chunk.replace('\n', '\\n')
        yield f"data: {encoded}\n\n"

    if question_num == QUESTION_COUNT:
        await repo.save_and_transition("Retroalimentación", full_response, session_id, "chat")
        logger.info("Evaluation completed for session %s — transitioned to chat", session_id)
    else:
        await repo.save("Retroalimentación", full_response, session_id)
        logger.info("Retroalimentacion %d/%d saved for session %s", question_num, QUESTION_COUNT, session_id)


async def _retroalimentacion_general_stream(
    context: str,
    session_id: str,
    chat: ChatService,
    repo: ConversationRepository,
):
    full_response = ""
    async for chunk in chat.get_response_stream(context, session_id, RETROALIMENTACION_PROMPT):
        full_response += chunk
        encoded = chunk.replace('\n', '\\n')
        yield f"data: {encoded}\n\n"

    await repo.save_and_transition(
        "Retroalimentación general", full_response, session_id, "chat"
    )
    logger.info("General retroalimentacion completed for session %s", session_id)


@router.post("/retroalimentacion/{session_id}/{question}")
async def get_retroalimentacion(
    session_id: str,
    question: int,
    request: EvaluationQuestion,
    repo: ConversationRepository = Depends(get_repository),
    chat: ChatService = Depends(get_chat_service),
    evaluation: EvaluationService = Depends(get_evaluation_service),
):
    session = await repo.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")

    await evaluation.save_response(session_id, request.question, request.response)

    context = f"Pregunta: {request.question}\nRespuesta del vendedor: {request.response}"

    return StreamingResponse(
        _retroalimentacion_stream(context, session_id, question, chat, repo),
        media_type="text/event-stream",
    )


@router.post("/retroalimentacion")
async def get_retroalimentacion_general(
    request: EvaluationRequest,
    repo: ConversationRepository = Depends(get_repository),
    chat: ChatService = Depends(get_chat_service),
):
    session = await repo.get_session(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")

    context = "\n\n".join(
        f"Pregunta {i + 1}: {q}\nRespuesta {i + 1}: {r}"
        for i, (q, r) in enumerate(zip(request.questions, request.responses))
    )

    return StreamingResponse(
        _retroalimentacion_general_stream(context, request.session_id, chat, repo),
        media_type="text/event-stream",
    )
