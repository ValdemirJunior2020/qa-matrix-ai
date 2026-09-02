from pathlib import Path
import tempfile

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel, EmailStr, Field

from ..security import require_admin, hash_password
from ..config import settings
from ..database import db
from ..services.matrix_service import (
    replace_matrix,
    rebuild_active_index,
    matrix_status,
)
from ..services.settings_service import (
    get_runtime_settings,
    update_runtime_settings,
)

router = APIRouter(prefix="/admin", tags=["admin"])


class SettingsUpdate(BaseModel):
    ollama_model: str | None = Field(default=None, max_length=100)
    ollama_embed_model: str | None = Field(default=None, max_length=100)
    request_timeout_seconds: int | None = Field(
        default=None,
        ge=30,
        le=300,
    )


class CreateUserRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=256)
    role: str = Field(default="qa_user")


class UpdateUserRequest(BaseModel):
    active: bool | None = None
    role: str | None = None
    password: str | None = Field(
        default=None,
        min_length=8,
        max_length=256,
    )


@router.get("/settings")
def settings_get(user: dict = Depends(require_admin)):
    return get_runtime_settings()


@router.put("/settings")
def settings_put(
    body: SettingsUpdate,
    user: dict = Depends(require_admin),
):
    return update_runtime_settings(
        body.model_dump(exclude_none=True)
    )


@router.get("/matrix")
def info(user: dict = Depends(require_admin)):
    return matrix_status()


@router.post("/matrix/reindex")
def reindex(user: dict = Depends(require_admin)):
    try:
        return rebuild_active_index()
    except Exception:
        raise HTTPException(
            503,
            "Index rebuild failed. Confirm Ollama and the embedding model are running.",
        )


@router.post("/matrix/upload")
async def upload(
    file: UploadFile = File(...),
    user: dict = Depends(require_admin),
):
    if (
        not file.filename
        or not file.filename.lower().endswith(".xlsx")
    ):
        raise HTTPException(
            400,
            "Only .xlsx Matrix files are accepted",
        )

    total = 0

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".xlsx",
    ) as tmp:

        while chunk := await file.read(1024 * 1024):
            total += len(chunk)

            if total > settings.max_upload_mb * 1024 * 1024:
                raise HTTPException(
                    413,
                    "Matrix file is too large",
                )

            tmp.write(chunk)

        temp = Path(tmp.name)

    try:
        return replace_matrix(
            temp,
            file.filename,
        )

    except Exception:
        raise HTTPException(
            400,
            "Matrix validation or indexing failed; the existing active Matrix was kept unchanged.",
        )

    finally:
        temp.unlink(missing_ok=True)


# ============================================================
# USER MANAGEMENT
# ============================================================

@router.get("/users")
def list_users(
    user: dict = Depends(require_admin),
):
    with db() as conn:
        rows = conn.execute(
            """
            SELECT
                id,
                email,
                role,
                active,
                created_at
            FROM users
            ORDER BY created_at DESC
            """
        ).fetchall()

    return [
        {
            "id": row["id"],
            "email": row["email"],
            "role": row["role"],
            "active": bool(row["active"]),
            "created_at": row["created_at"],
        }
        for row in rows
    ]


@router.post("/users")
def create_user(
    body: CreateUserRequest,
    admin: dict = Depends(require_admin),
):

    email = body.email.strip().lower()

    if body.role not in {"admin", "qa_user"}:
        raise HTTPException(
            400,
            "Role must be admin or qa_user",
        )

    with db() as conn:

        existing = conn.execute(
            """
            SELECT id
            FROM users
            WHERE lower(email)=lower(?)
            """,
            (email,),
        ).fetchone()

        if existing:
            raise HTTPException(
                409,
                "A user with this email already exists.",
            )

        password_hash = hash_password(body.password)

        cursor = conn.execute(
            """
            INSERT INTO users (
                email,
                password_hash,
                role,
                active
            )
            VALUES (?, ?, ?, 1)
            """,
            (
                email,
                password_hash,
                body.role,
            ),
        )

        user_id = cursor.lastrowid

        conn.execute(
            """
            INSERT INTO audit_log (
                user_id,
                event,
                detail
            )
            VALUES (?, ?, ?)
            """,
            (
                admin["id"],
                "user_created",
                f"Created {email} as {body.role}",
            ),
        )

    return {
        "id": user_id,
        "email": email,
        "role": body.role,
        "active": True,
    }


@router.put("/users/{user_id}")
def update_user(
    user_id: int,
    body: UpdateUserRequest,
    admin: dict = Depends(require_admin),
):

    with db() as conn:

        existing = conn.execute(
            """
            SELECT *
            FROM users
            WHERE id=?
            """,
            (user_id,),
        ).fetchone()

        if not existing:
            raise HTTPException(
                404,
                "User not found.",
            )

        if body.role is not None:

            if body.role not in {
                "admin",
                "qa_user",
            }:
                raise HTTPException(
                    400,
                    "Role must be admin or qa_user",
                )

            conn.execute(
                """
                UPDATE users
                SET role=?
                WHERE id=?
                """,
                (
                    body.role,
                    user_id,
                ),
            )

        if body.active is not None:

            if (
                user_id == admin["id"]
                and body.active is False
            ):
                raise HTTPException(
                    400,
                    "You cannot deactivate your own admin account.",
                )

            conn.execute(
                """
                UPDATE users
                SET active=?
                WHERE id=?
                """,
                (
                    1 if body.active else 0,
                    user_id,
                ),
            )

        if body.password:

            conn.execute(
                """
                UPDATE users
                SET password_hash=?
                WHERE id=?
                """,
                (
                    hash_password(body.password),
                    user_id,
                ),
            )

        conn.execute(
            """
            INSERT INTO audit_log (
                user_id,
                event,
                detail
            )
            VALUES (?, ?, ?)
            """,
            (
                admin["id"],
                "user_updated",
                f"Updated user ID {user_id}",
            ),
        )

        updated = conn.execute(
            """
            SELECT
                id,
                email,
                role,
                active,
                created_at
            FROM users
            WHERE id=?
            """,
            (user_id,),
        ).fetchone()

    return {
        "id": updated["id"],
        "email": updated["email"],
        "role": updated["role"],
        "active": bool(updated["active"]),
        "created_at": updated["created_at"],
    }


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    admin: dict = Depends(require_admin),
):

    if user_id == admin["id"]:
        raise HTTPException(
            400,
            "You cannot delete your own admin account.",
        )

    with db() as conn:

        existing = conn.execute(
            """
            SELECT email
            FROM users
            WHERE id=?
            """,
            (user_id,),
        ).fetchone()

        if not existing:
            raise HTTPException(
                404,
                "User not found.",
            )

        conn.execute(
            """
            DELETE FROM users
            WHERE id=?
            """,
            (user_id,),
        )

        conn.execute(
            """
            INSERT INTO audit_log (
                user_id,
                event,
                detail
            )
            VALUES (?, ?, ?)
            """,
            (
                admin["id"],
                "user_deleted",
                f"Deleted {existing['email']}",
            ),
        )

    return {
        "ok": True,
    }