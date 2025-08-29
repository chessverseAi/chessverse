# auth.py
from fastapi import APIRouter, Depends, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from database import get_db, User, hash_password
import secrets

router = APIRouter()
active_sessions = {}

@router.get("/register")
def get_register():
    return HTMLResponse("""
    <h2>📝 Registro</h2>
    <form action="/register" method="post">
        <input name="username" placeholder="Usuario" required><br><br>
        <input name="password" type="password" placeholder="Contraseña" required><br><br>
        <button type="submit">Registrar</button>
    </form>
    <p><a href="/login">¿Ya tienes cuenta? Inicia sesión</a></p>
    """)

@router.post("/register")
def register(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=400, detail="Usuario ya existe")
    hashed = hash_password(password)
    db_user = User(username=username, password_hash=hashed)
    db.add(db_user)
    db.commit()
    return RedirectResponse("/login", status_code=302)

@router.get("/login")
def get_login():
    return HTMLResponse("""
    <h2>🔐 Iniciar Sesión</h2>
    <form action="/login" method="post">
        <input name="username" placeholder="Usuario" required><br><br>
        <input name="password" type="password" placeholder="Contraseña" required><br><br>
        <button type="submit">Entrar</button>
    </form>
    <p><a href="/register">¿No tienes cuenta? Regístrate</a></p>
    """)

@router.post("/login")
def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == username).first()
    if not db_user or db_user.password_hash != hash_password(password):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    token = secrets.token_urlsafe(16)
    active_sessions[token] = db_user.username
    response = RedirectResponse("/", status_code=302)
    response.set_cookie(key="session", value=token)
    return response

@router.get("/leaderboard")
def leaderboard(db: Session = Depends(get_db)):
    users = db.query(User).order_by(User.elo.desc()).all()
    html = "<h2>🏆 Ranking Global</h2><ol>"
    for user in users:
        html += f"<li>{user.username} - {user.elo} ELO</li>"
    html += "</ol><p><a href='/'>Volver al tablero</a></p>"
    return HTMLResponse(html)