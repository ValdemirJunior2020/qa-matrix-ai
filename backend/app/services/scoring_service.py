from __future__ import annotations

INSUFFICIENT = "The Matrix does not provide enough information to determine this."

def get_possible_score(records:list[dict], category:str|None=None):
    rows=[r for r in records if r.get("score") is not None and (not category or (r.get("category") or '').lower()==category.lower())]
    if not rows: return {"authoritative":False,"value":None,"message":INSUFFICIENT}
    return {"authoritative":True,"value":sum(float(r["score"]) for r in rows),"message":None}

def get_deduction(record:dict):
    if record.get("score") is None: return {"authoritative":False,"value":None,"message":INSUFFICIENT}
    return {"authoritative":True,"value":float(record["score"]),"message":None}

def calculate_category_score(records:list[dict], category:str):
    return get_possible_score(records,category)

def calculate_total_score(records:list[dict]):
    return get_possible_score(records)

def apply_critical(base_score:float|None, critical_rule:dict|None):
    if not critical_rule or not critical_rule.get("critical"):
        return {"authoritative":False,"value":base_score,"message":INSUFFICIENT}
    # Never assume a zero-out behavior merely because a rule is Critical.
    behavior=critical_rule.get("critical_condition") or ""
    if "zero" in behavior.lower() or "0" in behavior.lower():
        return {"authoritative":True,"value":0.0,"message":behavior}
    return {"authoritative":False,"value":base_score,"message":"The Matrix marks this Critical but does not explicitly define a zero-score behavior."}
