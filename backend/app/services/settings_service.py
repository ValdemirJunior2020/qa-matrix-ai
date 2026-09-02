from __future__ import annotations
from ..database import db
from ..config import settings

ALLOWED={"ollama_model","ollama_embed_model","request_timeout_seconds"}

def load_runtime_settings():
    with db() as conn: rows=conn.execute("SELECT key,value FROM runtime_settings").fetchall()
    for r in rows:
        if r["key"] in ALLOWED:
            value=int(r["value"]) if r["key"]=="request_timeout_seconds" else r["value"]
            setattr(settings,r["key"],value)

def get_runtime_settings():
    return {"ollama_base_url":settings.ollama_base_url,"ollama_model":settings.ollama_model,"ollama_embed_model":settings.ollama_embed_model,"request_timeout_seconds":settings.request_timeout_seconds,"host":settings.host,"port":settings.port}

def update_runtime_settings(data:dict):
    for key,value in data.items():
        if key not in ALLOWED: continue
        if key=="request_timeout_seconds": value=max(30,min(300,int(value)))
        if key in {"ollama_model","ollama_embed_model"}:
            value=str(value).strip()
            if not value or len(value)>100: raise ValueError("Invalid model name")
        with db() as conn: conn.execute("INSERT INTO runtime_settings(key,value,updated_at) VALUES(?,?,CURRENT_TIMESTAMP) ON CONFLICT(key) DO UPDATE SET value=excluded.value,updated_at=CURRENT_TIMESTAMP",(key,str(value)))
        setattr(settings,key,value)
    return get_runtime_settings()
