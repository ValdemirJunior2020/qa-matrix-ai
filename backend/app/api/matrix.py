from fastapi import APIRouter, Depends, HTTPException
from ..security import current_user
from ..services.matrix_service import matrix_status, source_record
router=APIRouter(prefix="/matrix",tags=["matrix"])
@router.get("")
def status(user:dict=Depends(current_user)):
    m=matrix_status()
    if not m: return {"loaded":False}
    return {"loaded":True,"filename":m["filename"],"sheet_count":m["sheet_count"],"rule_count":m["rule_count"],"index_ready":bool(m["index_ready"]),"activated_at":m["activated_at"]}
@router.get("/source/{record_id}")
def source(record_id:str,user:dict=Depends(current_user)):
    r=source_record(record_id)
    if not r: raise HTTPException(404,"Matrix source not found")
    return r
