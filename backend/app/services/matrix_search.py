from __future__ import annotations
import json, math, re
from collections import Counter
from ..database import db

STOP={"the","a","an","is","are","to","of","and","or","what","does","about","this","that","in","on","for","it","should","agent"}

def _tokens(text: str):
    return [t for t in re.findall(r"[a-z0-9]+", text.lower()) if t not in STOP and len(t)>1]

def structured_search(query: str, limit: int = 8) -> list[dict]:
    q = Counter(_tokens(query))
    with db() as conn:
        mv = conn.execute("SELECT id FROM matrix_versions WHERE active=1 LIMIT 1").fetchone()
        if not mv: return []
        rows = conn.execute("SELECT * FROM matrix_records WHERE matrix_version_id=?", (mv["id"],)).fetchall()
    scored=[]
    for row in rows:
        d=dict(row); meta=json.loads(d["metadata_json"])
        hay=" ".join([d.get("sheet") or "", d.get("category") or "", d.get("subcategory") or "", d.get("rule") or "", d.get("instructions") or "", json.dumps(meta)])
        toks=Counter(_tokens(hay)); overlap=sum(min(q[t], toks[t]) for t in q)
        phrase_bonus=2.5 if query.lower() in hay.lower() else 0
        score=(overlap/max(1,len(q)))+phrase_bonus
        if score>0: scored.append((score,d,meta))
    scored.sort(key=lambda x:x[0], reverse=True)
    result=[]
    for score,d,meta in scored[:limit]:
        d["metadata"]=meta; d["structured_score"]=min(1.0, score)
        result.append(d)
    return result
