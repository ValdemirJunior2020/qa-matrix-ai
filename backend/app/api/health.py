from fastapi import APIRouter, Depends
from ..security import current_user, require_admin
from ..services.ollama_service import health as ollama_health
from ..services.matrix_service import matrix_status
from ..config import settings
router=APIRouter(prefix="/health",tags=["health"])
@router.get("")
async def public_health():
    m=matrix_status(); o=await ollama_health()
    return {"status":"online","ai":"ready" if o["online"] else "offline","matrix":"ready" if m else "missing"}
@router.get("/details")
async def details(user:dict=Depends(require_admin)):
    m=matrix_status(); o=await ollama_health()
    return {"backend":"online","ollama":"online" if o["online"] else "offline","model":settings.ollama_model,"embed_model":settings.ollama_embed_model,"matrix_loaded":bool(m),"matrix_name":m.get("filename") if m else None,"index_ready":bool(m and m.get("index_ready")),"rule_count":m.get("rule_count") if m else 0}
