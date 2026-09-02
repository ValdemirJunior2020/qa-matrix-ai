from __future__ import annotations
import hashlib, json, shutil, uuid
from datetime import datetime, timezone
from pathlib import Path
from ..config import settings
from ..database import db
from .excel_service import validate_xlsx
from .matrix_parser import parse_matrix
from .matrix_indexer import indexer


def _persist_records(conn, version_id:int, parsed:dict):
    for r in parsed["records"]:
        conn.execute("""INSERT INTO matrix_records(id,matrix_version_id,workbook,sheet,category,subcategory,rule,instructions,metadata_json,source_row_start,source_row_end,cell_range,score,critical,critical_condition) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (r["id"],version_id,r["workbook"],r["sheet"],r["category"],r["subcategory"],r["rule"],r["instructions"],json.dumps(r["fields"]),r["source_row_start"],r["source_row_end"],r["cell_range"],r["score"],int(r["critical"]),r["critical_condition"]))

def bootstrap_existing_matrix():
    active_dir=settings.matrix_dir/"active"; files=list(active_dir.glob("*.xlsx"))
    if not files: return
    path=files[0]; parsed=parse_matrix(path)
    with db() as conn:
        exists=conn.execute("SELECT id FROM matrix_versions WHERE sha256=?",(parsed["sha256"],)).fetchone()
        if exists:
            conn.execute("UPDATE matrix_versions SET active=0")
            conn.execute("UPDATE matrix_versions SET active=1,path=?,filename=?,sheet_count=?,rule_count=? WHERE id=?",(str(path),path.name,parsed["sheet_count"],parsed["rule_count"],exists["id"])); return
        conn.execute("UPDATE matrix_versions SET active=0")
        cur=conn.execute("INSERT INTO matrix_versions(filename,sha256,activated_at,sheet_count,rule_count,active,index_ready,path) VALUES(?,?,?,?,?,?,?,?)",(path.name,parsed["sha256"],datetime.now(timezone.utc).isoformat(),parsed["sheet_count"],parsed["rule_count"],1,0,str(path)))
        _persist_records(conn,cur.lastrowid,parsed)

def matrix_status():
    with db() as conn:
        row=conn.execute("SELECT * FROM matrix_versions WHERE active=1 LIMIT 1").fetchone()
    return dict(row) if row else None

def source_record(record_id:str):
    with db() as conn:
        row=conn.execute("SELECT * FROM matrix_records WHERE id=?",(record_id,)).fetchone()
    if not row: return None
    d=dict(row); d["metadata"]=json.loads(d["metadata_json"]); d.pop("metadata_json",None); return d

def rebuild_active_index():
    status=matrix_status()
    if not status: raise ValueError("No active Matrix")
    tmp=settings.index_dir/f"tmp-{uuid.uuid4().hex}"; target=settings.index_dir/"active"
    parsed=indexer.build(Path(status["path"]),tmp)
    backup=settings.index_dir/"previous"
    if backup.exists(): shutil.rmtree(backup)
    if target.exists(): target.rename(backup)
    tmp.rename(target)
    with db() as conn: conn.execute("UPDATE matrix_versions SET index_ready=1 WHERE id=?",(status["id"],))
    return {"status":"ready","rule_count":parsed["rule_count"]}

def replace_matrix(temp_path:Path, original_name:str):
    validate_xlsx(temp_path,settings.max_upload_mb)
    parsed=parse_matrix(temp_path)
    # Build new semantic index before changing active matrix.
    tmp_index=settings.index_dir/f"candidate-{uuid.uuid4().hex}"
    indexer.build(temp_path,tmp_index)
    archive=settings.matrix_dir/"archive"; archive.mkdir(parents=True,exist_ok=True)
    active=settings.matrix_dir/"active"; active.mkdir(parents=True,exist_ok=True)
    old=list(active.glob("*.xlsx"))
    for p in old: shutil.copy2(p,archive/f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{p.name}")
    safe_name=f"matrix-{parsed['sha256'][:12]}.xlsx"; new_path=active/safe_name; shutil.copy2(temp_path,new_path)
    with db() as conn:
        conn.execute("UPDATE matrix_versions SET active=0")
        cur=conn.execute("INSERT INTO matrix_versions(filename,sha256,activated_at,sheet_count,rule_count,active,index_ready,path) VALUES(?,?,?,?,?,?,?,?)",(original_name,parsed["sha256"],datetime.now(timezone.utc).isoformat(),parsed["sheet_count"],parsed["rule_count"],1,1,str(new_path)))
        _persist_records(conn,cur.lastrowid,parsed)
    target=settings.index_dir/"active"; prev=settings.index_dir/"previous"
    if prev.exists(): shutil.rmtree(prev)
    if target.exists(): target.rename(prev)
    tmp_index.rename(target)
    for p in old:
        try: p.unlink()
        except OSError: pass
    return matrix_status()
