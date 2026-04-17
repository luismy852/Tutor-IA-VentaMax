import uuid
import logging
import aiosqlite
from core.config import settings
from domain.constants import HISTORY_LIMIT

logger = logging.getLogger(__name__)


class ConversationRepository:

    @property
    def _db(self) -> str:
        return settings.database_url

    async def init_db(self) -> None:
        async with aiosqlite.connect(self._db) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    state TEXT NOT NULL DEFAULT 'evaluacion',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    user_message TEXT NOT NULL,
                    ai_response TEXT NOT NULL,
                    modo TEXT NOT NULL DEFAULT 'evaluacion',
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES sessions(id)
                )
            """)
            await db.commit()

    async def create_session(self) -> str:
        session_id = str(uuid.uuid4())
        async with aiosqlite.connect(self._db) as db:
            await db.execute(
                "INSERT INTO sessions (id, state) VALUES (?, ?)",
                (session_id, "evaluacion"),
            )
            await db.commit()
        logger.info("Session created: %s", session_id)
        return session_id

    async def get_session(self, session_id: str) -> dict | None:
        async with aiosqlite.connect(self._db) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM sessions WHERE id = ?", (session_id,)
            ) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None

    async def update_session_state(self, session_id: str, new_state: str) -> None:
        async with aiosqlite.connect(self._db) as db:
            await db.execute(
                "UPDATE sessions SET state = ? WHERE id = ?",
                (new_state, session_id),
            )
            await db.commit()
        logger.info("Session %s → state '%s'", session_id, new_state)

    async def save(self, user_message: str, ai_response: str, session_id: str) -> None:
        session = await self.get_session(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")
        modo = session["state"]
        async with aiosqlite.connect(self._db) as db:
            await db.execute(
                "INSERT INTO conversations (session_id, user_message, ai_response, modo) VALUES (?, ?, ?, ?)",
                (session_id, user_message, ai_response, modo),
            )
            await db.commit()

    async def save_and_transition(
        self,
        user_message: str,
        ai_response: str,
        session_id: str,
        new_state: str,
    ) -> None:
        """Persists a conversation turn and transitions the session state atomically."""
        session = await self.get_session(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")
        modo = session["state"]
        async with aiosqlite.connect(self._db) as db:
            await db.execute(
                "INSERT INTO conversations (session_id, user_message, ai_response, modo) VALUES (?, ?, ?, ?)",
                (session_id, user_message, ai_response, modo),
            )
            await db.execute(
                "UPDATE sessions SET state = ? WHERE id = ?",
                (new_state, session_id),
            )
            await db.commit()
        logger.info("Session %s → state '%s' (atomic save)", session_id, new_state)

    async def get_all(self, limit: int = HISTORY_LIMIT) -> list[dict]:
        async with aiosqlite.connect(self._db) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM conversations ORDER BY id DESC LIMIT ?", (limit,)
            ) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def get_by_session_id(
        self, session_id: str, limit: int = HISTORY_LIMIT
    ) -> list[dict]:
        async with aiosqlite.connect(self._db) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM conversations WHERE session_id = ? ORDER BY id DESC LIMIT ?",
                (session_id, limit),
            ) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def get_by_id(self, conversation_id: int) -> dict | None:
        async with aiosqlite.connect(self._db) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM conversations WHERE id = ?", (conversation_id,)
            ) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None

    async def build_context(self, session_id: str) -> str:
        session = await self.get_session(session_id)
        if session and session["state"] == "simulacion":
            history = await self._get_simulation_history(session_id)
        else:
            history = await self.get_by_session_id(session_id)
        return self._format_history(history)

    async def build_context_simulation(self, session_id: str) -> str:
        history = await self._get_simulation_history(session_id)
        return self._format_history(history)

    async def _get_simulation_history(self, session_id: str) -> list[dict]:
        async with aiosqlite.connect(self._db) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM conversations WHERE session_id = ? AND modo = 'simulacion' ORDER BY id DESC LIMIT ?",
                (session_id, HISTORY_LIMIT),
            ) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    def _format_history(self, history: list[dict]) -> str:
        lines = [
            f"Usuario: {conv['user_message']}\nIA: {conv['ai_response']}"
            for conv in reversed(history)
        ]
        return "\n".join(lines).strip()
