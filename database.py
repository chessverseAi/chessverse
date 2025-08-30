# database.py
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os

# ───────────────────────────────────────────────
# 1. Configuración de la base de datos
# Usa SQLite para simplicidad (perfecto para desarrollo)
# ───────────────────────────────────────────────
DATABASE_URL = "sqlite:///./users.db"

# Crear el motor de base de datos
# connect_args={"check_same_thread": False} → necesario para SQLite en FastAPI
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Sesión local para dependencias
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para definir modelos
Base = declarative_base()


# ───────────────────────────────────────────────
# 2. Modelo: Usuario
# Almacena: username, contraseña hasheada y ELO
# ───────────────────────────────────────────────
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    elo = Column(Integer, default=1200)


# ───────────────────────────────────────────────
# 3. Dependencia: obtener sesión de base de datos
# Se usa en rutas con Depends(get_db)
# ───────────────────────────────────────────────
def get_db():
    """
    Dependencia de FastAPI para inyectar la sesión de base de datos.
    Asegura que la sesión se cierre después de usarla.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ───────────────────────────────────────────────
# 4. Función opcional: crear tablas
# Útil si ejecutas scripts o necesitas inicializar
# ───────────────────────────────────────────────
def create_tables():
    """
    Crea todas las tablas en la base de datos si no existen.
    Llámalo al inicio del main.py.
    """
    Base.metadata.create_all(bind=engine)
