from __future__ import annotations
import json
from ..database import db
from .qa_engine import answer_question

async def chat(user_id:int, question:str, chat_id:int|None=None):
    with db() as conn:
        if chat_id is None:
            title=question[:70]
            cur=conn.execute("INSERT INTO chats(user_id,title) VALUES(?,?)",(user_id,title)); chat_id=cur.lastrowid
        else:
            own=conn.execute("SELECT id FROM chats WHERE id=? AND user_id=?",(chat_id,user_id)).fetchone()
            if not own: raise ValueError("Chat not found")
        conn.execute("INSERT INTO messages(chat_id,role,content) VALUES(?,?,?)",(chat_id,"user",question))
    result=await answer_question(question); result["chat_id"]=chat_id
    with db() as conn:
        conn.execute("INSERT INTO messages(chat_id,role,content,payload_json) VALUES(?,?,?,?)",(chat_id,"assistant",result["answer"],json.dumps(result)))
    return result
