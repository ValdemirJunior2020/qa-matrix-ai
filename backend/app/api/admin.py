from pathlib import Path
import tempfile
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from ..security import require_admin
from ..config import settings
from ..services.matrix_service import replace_matrix,rebuild_active_index,matrix_status
from ..services.settings_service import get_runtime_settings,update_runtime_settings
from pydantic import BaseModel, Field
router=APIRouter(prefix="/admin",tags=["admin"])
class SettingsUpdate(BaseModel):
    ollama_model: str | None = Field(default=None,max_length=100)
    ollama_embed_model: str | None = Field(default=None,max_length=100)
    request_timeout_seconds: int | None = Field(default=None,ge=30,le=300)
@router.get("/settings")
def settings_get(user:dict=Depends(require_admin)): return get_runtime_settings()
@router.put("/settings")
def settings_put(body:SettingsUpdate,user:dict=Depends(require_admin)):
    return update_runtime_settings(body.model_dump(exclude_none=True))
@router.get("/matrix")
def info(user:dict=Depends(require_admin)): return matrix_status()
@router.post("/matrix/reindex")
def reindex(user:dict=Depends(require_admin)):
    try: return rebuild_active_index()
    except Exception as e: raise HTTPException(503,"Index rebuild failed. Confirm Ollama and the embedding model are running.")
@router.post("/matrix/upload")
async def upload(file:UploadFile=File(...),user:dict=Depends(require_admin)):
    if not file.filename or not file.filename.lower().endswith(".xlsx"): raise HTTPException(400,"Only .xlsx Matrix files are accepted")
    total=0
    with tempfile.NamedTemporaryFile(delete=False,suffix=".xlsx") as tmp:
        while chunk:=await file.read(1024*1024):
            total+=len(chunk)
            if total>settings.max_upload_mb*1024*1024: raise HTTPException(413,"Matrix file is too large")
            tmp.write(chunk)
        temp=Path(tmp.name)
    try: return replace_matrix(temp,file.filename)
    except Exception: raise HTTPException(400,"Matrix validation or indexing failed; the existing active Matrix was kept unchanged.")
    finally: temp.unlink(missing_ok=True)
