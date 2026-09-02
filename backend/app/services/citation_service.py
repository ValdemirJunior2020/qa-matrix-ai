from __future__ import annotations

def source_from_record(r: dict) -> dict:
    excerpt=(r.get("instructions") or r.get("rule") or "").strip()
    if len(excerpt)>500: excerpt=excerpt[:497]+"..."
    return {"record_id":r["id"],"workbook":r["workbook"],"sheet":r["sheet"],"category":r.get("category"),"cell_range":r.get("cell_range"),"rows":str(r.get("source_row_start") or ""),"excerpt":excerpt}
