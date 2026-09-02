from __future__ import annotations

import json

from ..database import db
from .qa_engine import answer_question
from .ai_queue import ai_queue


async def chat(
    user_id: int,
    question: str,
    chat_id: int | None = None,
):
    # --------------------------------------------------------
    # CREATE / VALIDATE CHAT
    # --------------------------------------------------------

    with db() as conn:

        if chat_id is None:

            title = question[:70]

            cursor = conn.execute(
                """
                INSERT INTO chats(
                    user_id,
                    title
                )
                VALUES (?, ?)
                """,
                (
                    user_id,
                    title,
                ),
            )

            chat_id = cursor.lastrowid

        else:

            own = conn.execute(
                """
                SELECT id
                FROM chats
                WHERE id=?
                AND user_id=?
                """,
                (
                    chat_id,
                    user_id,
                ),
            ).fetchone()

            if not own:
                raise ValueError(
                    "Chat not found"
                )

        conn.execute(
            """
            INSERT INTO messages(
                chat_id,
                role,
                content
            )
            VALUES (?, ?, ?)
            """,
            (
                chat_id,
                "user",
                question,
            ),
        )

    # --------------------------------------------------------
    # AI QUEUE
    # --------------------------------------------------------

    await ai_queue.acquire()

    try:

        result = await answer_question(
            question
        )

    finally:

        await ai_queue.release()

    # --------------------------------------------------------
    # ATTACH CHAT ID
    # --------------------------------------------------------

    result["chat_id"] = chat_id

    # --------------------------------------------------------
    # SAVE ANSWER
    # --------------------------------------------------------

    with db() as conn:

        conn.execute(
            """
            INSERT INTO messages(
                chat_id,
                role,
                content,
                payload_json
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                chat_id,
                "assistant",
                result["answer"],
                json.dumps(
                    result,
                    ensure_ascii=False,
                ),
            ),
        )

    return result