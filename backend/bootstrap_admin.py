import argparse, getpass
from app.database import init_db, db
from app.security import hash_password

def main():
    p=argparse.ArgumentParser(); p.add_argument("--email",default="infojr.83@gmail.com"); p.add_argument("--password",default=None); args=p.parse_args()
    password=args.password or getpass.getpass("Admin password: ")
    if len(password)<8: raise SystemExit("Password must be at least 8 characters")
    init_db()
    with db() as conn:
        existing=conn.execute("SELECT id FROM users WHERE lower(email)=lower(?)",(args.email,)).fetchone()
        if existing: conn.execute("UPDATE users SET password_hash=?,role='admin',active=1 WHERE id=?",(hash_password(password),existing["id"]))
        else: conn.execute("INSERT INTO users(email,password_hash,role) VALUES(?,?,'admin')",(args.email,hash_password(password)))
    print(f"Admin ready: {args.email}")
if __name__=="__main__": main()
