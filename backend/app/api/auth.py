from fastapi import APIRouter, HTTPException
from ..schemas import LoginRequest
from ..database import db
from ..security import verify_password, create_token
router=APIRouter(prefix="/auth",tags=["auth"])
@router.post("/login")
def login(body:LoginRequest):
    with db() as conn: row=conn.execute("SELECT * FROM users WHERE lower(email)=lower(?) AND active=1",(body.email,)).fetchone()
    if not row or not verify_password(body.password,row["password_hash"]): raise HTTPException(401,"Invalid email or password")
    user=dict(row); return {"access_token":create_token(user),"token_type":"bearer","user":{"id":user["id"],"email":user["email"],"role":user["role"]}}
