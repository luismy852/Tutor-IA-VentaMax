from functools import lru_cache
from repositories.conversation_repository import ConversationRepository
from services.chat_service import ChatService
from services.evaluation_service import EvaluationService


@lru_cache(maxsize=1)
def get_repository() -> ConversationRepository:
    return ConversationRepository()


@lru_cache(maxsize=1)
def get_chat_service() -> ChatService:
    return ChatService(get_repository())


@lru_cache(maxsize=1)
def get_evaluation_service() -> EvaluationService:
    return EvaluationService(get_repository())
