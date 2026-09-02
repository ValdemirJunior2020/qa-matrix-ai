from fastapi import APIRouter, Depends

from ..security import require_admin
from ..services.ollama_service import health as ollama_health
from ..services.matrix_service import matrix_status
from ..services.ai_queue import ai_queue
from ..config import settings


router = APIRouter(
    prefix="/health",
    tags=["health"],
)


@router.get("")
async def public_health():
    """
    Lightweight health endpoint used by the frontend
    for automatic reconnect checks.
    """

    matrix = matrix_status()
    ollama = await ollama_health()

    return {
        "status": "online",
        "ai": "ready"
        if ollama["online"]
        else "offline",
        "matrix": "ready"
        if matrix
        else "missing",
    }


@router.get("/details")
async def details(
    user: dict = Depends(require_admin),
):
    """
    Admin-only detailed health information.
    """

    matrix = matrix_status()
    ollama = await ollama_health()

    queue = await ai_queue.status()

    return {
        "backend": "online",

        "ollama":
            "online"
            if ollama["online"]
            else "offline",

        "model":
            settings.ollama_model,

        "embed_model":
            settings.ollama_embed_model,

        "matrix_loaded":
            bool(matrix),

        "matrix_name":
            matrix.get("filename")
            if matrix
            else None,

        "index_ready":
            bool(
                matrix
                and matrix.get("index_ready")
            ),

        "rule_count":
            matrix.get("rule_count")
            if matrix
            else 0,

        "ai_queue": {
            "active":
                queue.active,

            "waiting":
                queue.waiting,

            "max_concurrent":
                queue.max_concurrent,

            "busy":
                queue.active
                >= queue.max_concurrent,
        },
    }


@router.get("/queue")
async def queue_status():
    """
    Queue status used by the React frontend.

    Example:

    {
        "active": 2,
        "waiting": 1,
        "max_concurrent": 2,
        "busy": true
    }
    """

    queue = await ai_queue.status()

    return {
        "active":
            queue.active,

        "waiting":
            queue.waiting,

        "max_concurrent":
            queue.max_concurrent,

        "busy":
            queue.active
            >= queue.max_concurrent,
    }