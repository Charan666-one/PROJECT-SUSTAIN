from fastapi import APIRouter, Depends, HTTPException
from app.core.security import verify_password, create_access_token

router = APIRouter()

@router.post("/login")
async def login(credentials: dict):
    pass

@router.post("/register")
async def register_doctor(doctor_data: dict):
    pass

@router.post("/refresh")
async def refresh_token(token: str):
    pass
