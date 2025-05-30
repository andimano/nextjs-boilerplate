from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta

from backend.database import get_db
from backend.models import Admin, Employee
from backend.schemas import LoginRequest

SECRET_KEY = "your_secret_key_here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/login")
async def login(login_data: LoginRequest, db: AsyncSession = Depends(get_db)):
    nip_or_email = login_data.nip_or_email
    password = login_data.password

    # Try to find admin by email
    result = await db.execute(select(Admin).where(Admin.email == nip_or_email))
    admin = result.scalars().first()
    if admin and verify_password(password, admin.hashed_password):
        access_token = create_access_token(data={"sub": admin.email, "role": "admin"})
        return {"access_token": access_token, "token_type": "bearer", "role": "admin"}

    # Try to find employee by nip
    result = await db.execute(select(Employee).where(Employee.nip == nip_or_email))
    employee = result.scalars().first()
    if employee and verify_password(password, employee.hashed_password):
        access_token = create_access_token(data={"sub": employee.nip, "role": "employee"})
        return {"access_token": access_token, "token_type": "bearer", "role": "employee"}

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
