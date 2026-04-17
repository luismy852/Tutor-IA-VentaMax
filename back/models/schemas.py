from pydantic import BaseModel
from datetime import datetime


class ChatRequest(BaseModel):
    message: str
    session_id: str


class ChatResponse(BaseModel):
    response: str


class ConversationResponse(BaseModel):
    id: int
    session_id: str
    user_message: str
    ai_response: str
    modo: str
    timestamp: datetime


class EvaluationRequest(BaseModel):
    session_id: str
    questions: list[str]
    responses: list[str]


class EvaluationQuestion(BaseModel):
    question: str
    response: str


class SessionResponse(BaseModel):
    session_id: str
    state: str


class SessionStateUpdate(BaseModel):
    state: str
