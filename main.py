# main.py
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
import evaluator
from database import get_db, User
from auth import router as auth_router

app = FastAPI()

# Servir archivos estáticos: CSS, JS, imágenes
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configurar plantillas (HTML)
templates = Jinja2Templates(directory="templates")

# Incluir rutas de autenticación
app.include_router(auth_router, prefix="")

# Modelo para solicitudes de evaluación de movimientos
class MoveRequest(BaseModel):
    fen: str
    move: str  # en formato UCI, ej: e2e4

# Dependencia para obtener usuario actual
def get_current_user(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("session")
    if token in auth_router.active_sessions:
        username = auth_router.active_sessions[token]
        return db.query(User).filter(User.username == username).first()
    return None

# --- RUTA PRINCIPAL ---
@app.get("/")
def home(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "username": user.username if user else "Invitado",
        "elo": user.elo if user else 1200
    })
