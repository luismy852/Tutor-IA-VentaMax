import logging
from openai import AsyncOpenAI
from core.config import settings
from prompts.prompts import (
    CHAT_SYSTEM_PROMPT,
    SIMULATION_PROMPT,
    ANALYSIS_PROMPT,
    SIMULATION_FLAG,
    SIMULATION_END_FLAG,
)
from repositories.conversation_repository import ConversationRepository

logger = logging.getLogger(__name__)


class ChatService:

    def __init__(self, repository: ConversationRepository) -> None:
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.repository = repository

    async def get_response(
        self,
        message: str,
        session_id: str,
    ) -> str:
        system = CHAT_SYSTEM_PROMPT
        context = await self.repository.build_context(session_id)
        if context:
            system = f"{system}\n\nHistorial de la conversación:\n{context}"

        completion = await self.client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": message},
            ],
            temperature=0.8,
        )
        return completion.choices[0].message.content

    async def get_response_stream(
        self,
        message: str,
        session_id: str,
        system_prompt: str | None = None,
    ):
        session = await self.repository.get_session(session_id)
        system = system_prompt if system_prompt else CHAT_SYSTEM_PROMPT

        if session and session["state"] == "simulacion":
            system = SIMULATION_PROMPT

        context = await self.repository.build_context(session_id)
        if context:
            system = f"{system}\n\nHistorial de la conversación:\n{context}"

        stream = await self.client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": message},
            ],
            temperature=0.6,
            stream=True,
        )

        buffer = ""
        # Hold back enough chars so a flag split across chunks is never yielded prematurely
        hold = max(len(SIMULATION_FLAG), len(SIMULATION_END_FLAG))

        async for chunk in stream:
            content = chunk.choices[0].delta.content
            if not content:
                continue

            buffer += content

            if SIMULATION_FLAG in buffer:
                before = buffer.split(SIMULATION_FLAG)[0]
                if before:
                    yield before
                logger.info("Simulation ready for session %s", session_id)
                await self.repository.update_session_state(session_id, "simulacion")
                return

            if SIMULATION_END_FLAG in buffer:
                idx = buffer.find(SIMULATION_END_FLAG)
                before = buffer[:idx].rstrip()
                if before:
                    yield before
                yield "\n\n"

                analisis_completo = ""
                async for analysis_chunk in self._get_analysis_stream(session_id):
                    analisis_completo += analysis_chunk
                    yield analysis_chunk

                await self.repository.save_and_transition(
                    "analisis de venta", analisis_completo, session_id, "chat"
                )
                logger.info("Simulation ended for session %s", session_id)
                return

            # Yield only the portion far enough from the tail to not be a partial flag
            if len(buffer) > hold:
                yield buffer[:-hold]
                buffer = buffer[-hold:]

        # Stream ended with no flags — flush remaining buffer
        if buffer:
            yield buffer

    async def _get_analysis_stream(self, session_id: str):
        context = await self.repository.build_context(session_id)
        simulation = await self.repository.build_context_simulation(session_id)

        system = ANALYSIS_PROMPT
        if context:
            system = (
                f"{system}\n\nHistorial:\n{context}\n\nSimulacion de venta:\n{simulation}"
            )

        stream = await self.client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": system},
                {
                    "role": "user",
                    "content": "Genera el análisis de esta simulación de ventas.",
                },
            ],
            stream=True,
        )

        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
