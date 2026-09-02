import json
from fastapi import APIRouter,Depends,HTTPException
from ..database import db
from ..security import current_user
router=APIRouter(prefix="/history",tags=["history"])
@router.get("")
def list_history(user:dict=Depends(current_user)):
    with db() as conn: rows=conn.execute("SELECT id,title,created_at FROM chats WHERE user_id=? ORDER BY id DESC LIMIT 100",(user["id"],)).fetchall()
    return [dict(r) for r in rows]
@router.get("/{chat_id}")
def get_chat(chat_id:int,user:dict=Depends(current_user)):
    with db() as conn:
        chat=conn.execute("SELECT id,title,created_at FROM chats WHERE id=? AND user_id=?",(chat_id,user["id"])).fetchone()
        if not chat: raise HTTPException(404,"Chat not found")
        rows=conn.execute("SELECT role,content,payload_json,created_at FROM messages WHERE chat_id=? ORDER BY id",(chat_id,)).fetchall()
    out=[]
    for r in rows:
        d=dict(r)
        if d["payload_json"]:
            try:d["payload"]=json.loads(d["payload_json"])
            except: d["payload"]=None
        d.pop("payload_json",None);out.append(d)
    return {"chat":dict(chat),"messages":out}
