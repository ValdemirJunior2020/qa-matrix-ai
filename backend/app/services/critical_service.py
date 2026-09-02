from __future__ import annotations
INSUFFICIENT="The Matrix does not provide enough information to determine this."
def evaluate_critical_rule(question:str,evidence:list[dict]):
    explicit=[r for r in evidence if bool(r.get("critical"))]
    if not explicit:return {"critical":False,"authoritative":False,"reason":INSUFFICIENT}
    r=explicit[0]
    return {"critical":True,"authoritative":True,"reason":r.get("critical_condition") or r.get("rule"),"record_id":r.get("id")}
