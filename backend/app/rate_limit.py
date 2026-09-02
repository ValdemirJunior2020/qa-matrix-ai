from __future__ import annotations
import time
from collections import defaultdict, deque
from threading import Lock
from fastapi import HTTPException, Request

_lock=Lock(); _hits=defaultdict(deque)
LIMITS={
    "/api/auth/login": (10,60),
    "/api/chat": (30,60),
    "/api/admin/matrix/upload": (3,3600),
    "/api/admin/matrix/reindex": (5,3600),
}

def enforce_rate_limit(request: Request):
    path=request.url.path
    if path not in LIMITS: return
    limit,window=LIMITS[path]
    ip=request.headers.get("CF-Connecting-IP") or (request.client.host if request.client else "unknown")
    key=f"{ip}:{path}"; now=time.time()
    with _lock:
        q=_hits[key]
        while q and q[0] <= now-window: q.popleft()
        if len(q)>=limit: raise HTTPException(429,"Too many requests. Please try again later.")
        q.append(now)
