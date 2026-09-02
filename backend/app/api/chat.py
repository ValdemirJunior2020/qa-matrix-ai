from fastapi import APIRouter, Depends, HTTPException
from ..schemas import ChatRequest
from ..security import current_user
from ..services.chat_service import chat
router=APIRouter(prefix="/chat",tags=["chat"])
@router.post("")
async def ask(body:ChatRequest,user:dict=Depends(current_user)):
    try: return await chat(user["id"],body.question,body.chat_id)
    except ValueError as e: raise HTTPException(404,str(e))
