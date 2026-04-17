import json
import random
import logging
from domain.constants import QUESTION_COUNT, QUESTIONS_PATH
from repositories.conversation_repository import ConversationRepository

logger = logging.getLogger(__name__)


class EvaluationService:

    def __init__(self, repository: ConversationRepository) -> None:
        self.repository = repository
        self._questions: dict | None = None

    def _load_questions(self) -> dict:
        if self._questions is None:
            with open(QUESTIONS_PATH, "r", encoding="utf-8") as f:
                self._questions = json.load(f)
        return self._questions

    def get_random_questions(self) -> list[str]:
        data = self._load_questions()
        questions = []
        for i in range(1, QUESTION_COUNT + 1):
            options = data[f"pregunta{i}"]
            questions.append(random.choice(options))
        return questions

    async def save_response(
        self, session_id: str, question: str, response: str
    ) -> None:
        await self.repository.save(question, response, session_id)
        logger.info("Saved evaluation response for session %s", session_id)
