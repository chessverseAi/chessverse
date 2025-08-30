# main.py
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
import evaluator
from database import get_db, User, engine, Base
from auth import router as auth_router
import time

# Crear tablas si no existen
Base.metadata.create_all(bind=engine)

app = FastAPI()

# ────── Servir archivos estáticos: CSS, JS, imágenes ──────
app.mount("/static", StaticFiles(directory="static"), name="static")

# ────── Configurar plantillas HTML ──────
templates = Jinja2Templates(directory="templates")

# ────── Incluir rutas de autenticación ──────
app.include_router(auth_router, prefix="/auth", tags=["auth"])

# ────── Modelo para evaluar movimientos ──────
class MoveRequest(BaseModel):
    fen: str
    move: str  # en formato UCI, ej: e2e4

# ────── Dependencia: obtener usuario actual ──────
def get_current_user(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("session_token")
    if not token:
        return None
    if hasattr(auth_router, "active_sessions") and token in auth_router.active_sessions:
        username = auth_router.active_sessions[token]
        return db.query(User).filter(User.username == username).first()
    return None

# ────── RUTA PRINCIPAL: página del tablero ──────
@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    username = user.username if user else "Invitado"
    elo = user.elo if user else 1200
    return templates.TemplateResponse("index.html", {
        "request": request,
        "username": username,
        "elo": elo
    })

# ────── RUTA: evaluar movimiento (para efecto visual) ──────
@app.post("/evaluate-move")
async def evaluate_move_endpoint(request: MoveRequest, db: Session = Depends(get_db)):
    try:
        result = evaluator.evaluate_move(request.fen, request.move)
        if "error" in result:
            return JSONResponse(status_code=404, content=result)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al evaluar movimiento: {str(e)}")

# ────── RUTA: salud (para verificar que el servidor funciona) ──────
@app.get("/health")
async def health():
    return {"status": "ok", "message": "ChessVerse está funcionando"}








