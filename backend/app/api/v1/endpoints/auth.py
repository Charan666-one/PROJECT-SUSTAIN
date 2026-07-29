"""Authentication — doctor registration + login (JWT)."""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token
from app.models.admin.doctor import Doctor
from app.schemas.auth import DoctorRegister, DoctorLogin, Token, DoctorOut
from app.api.dependencies.auth import get_current_doctor

router = APIRouter()


@router.post("/register", response_model=DoctorOut, status_code=status.HTTP_201_CREATED)
async def register_doctor(data: DoctorRegister, db: AsyncSession = Depends(get_db)):
    existing = (await db.execute(select(Doctor).where(Doctor.email == data.email))).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=409, detail="A doctor with this email already exists")

    doctor = Doctor(
        full_name=data.full_name,
        email=data.email,
        phone=data.phone,
        password_hash=hash_password(data.password),
        registration_no=data.registration_no,
        qualifications=data.qualifications,
        clinic_name=data.clinic_name,
        clinic_address=data.clinic_address,
        languages=data.languages,
    )
    db.add(doctor)
    await db.commit()
    await db.refresh(doctor)
    return doctor


@router.post("/login", response_model=Token)
async def login(form: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    # OAuth2 form uses "username" — we treat it as the doctor's email.
    doctor = (await db.execute(select(Doctor).where(Doctor.email == form.username))).scalar_one_or_none()
    if not doctor or not verify_password(form.password, doctor.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    doctor.last_login = datetime.utcnow()
    await db.commit()
    return Token(access_token=create_access_token({"sub": str(doctor.id)}))


@router.post("/login-json", response_model=Token)
async def login_json(data: DoctorLogin, db: AsyncSession = Depends(get_db)):
    """JSON login for the SPA (avoids form-encoding on the frontend)."""
    doctor = (await db.execute(select(Doctor).where(Doctor.email == data.email))).scalar_one_or_none()
    if not doctor or not verify_password(data.password, doctor.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    doctor.last_login = datetime.utcnow()
    await db.commit()
    return Token(access_token=create_access_token({"sub": str(doctor.id)}))


@router.get("/me", response_model=DoctorOut)
async def me(doctor: Doctor = Depends(get_current_doctor)):
    return doctor
