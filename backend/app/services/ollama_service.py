from __future__ import annotations
import httpx
from ..config import settings

async def health():
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            r=await client.get(f"{settings.ollama_base_url}/api/tags"); r.raise_for_status()
            names=[m.get("name") for m in r.json().get("models",[])]
            return {"online":True,"models":names,"model_ready":any((x or "").startswith(settings.ollama_model.split(":")[0]) for x in names)}
    except Exception as e:
        return {"online":False,"models":[],"model_ready":False,"error":"Ollama is not reachable locally."}

async def generate(system: str, user: str) -> str:
    payload={"model":settings.ollama_model,"stream":False,"messages":[{"role":"system","content":system},{"role":"user","content":user}],"options":{"temperature":0.1}}
    async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
        r=await client.post(f"{settings.ollama_base_url}/api/chat",json=payload); r.raise_for_status()
        return r.json().get("message",{}).get("content","").strip()
