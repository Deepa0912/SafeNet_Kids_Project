"""
backend/routers/auth_router.py — Auth endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from ..database import get_db, Parent
from ..auth import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/api/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    username: str
    password: str
    email:    Optional[str] = None


@router.post("/register")
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(Parent).filter(Parent.username == body.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists.")
    parent = Parent(
        username   = body.username.strip(),
        email      = body.email,
        hashed_pw  = hash_password(body.password),
    )
    db.add(parent)
    db.commit()
    db.refresh(parent)
    token = create_access_token({"sub": parent.username})
    return {"access_token": token, "token_type": "bearer", "username": parent.username}


@router.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    parent = db.query(Parent).filter(Parent.username == form.username).first()
    if not parent or not verify_password(form.password, parent.hashed_pw):
        raise HTTPException(status_code=401, detail="Incorrect username or password.")
    token = create_access_token({"sub": parent.username})
    return {"access_token": token, "token_type": "bearer", "username": parent.username, "id": parent.id}


class ResetRequest(BaseModel):
    username:     str
    new_password: str


@router.post("/reset-password")
def reset_password(body: ResetRequest, db: Session = Depends(get_db)):
    parent = db.query(Parent).filter(Parent.username == body.username).first()
    if not parent:
        raise HTTPException(status_code=404, detail="User not found.")
    parent.hashed_pw = hash_password(body.new_password)
    db.commit()
    return {"status": "ok"}
