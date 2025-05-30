from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class AdminCreate(BaseModel):
    email: EmailStr
    password: str

class AdminOut(BaseModel):
    id: int
    email: EmailStr

    class Config:
        orm_mode = True

class EmployeeCreate(BaseModel):
    nip: str = Field(..., min_length=3)
    name: str
    password: str

class EmployeeOut(BaseModel):
    id: int
    nip: str
    name: str

    class Config:
        orm_mode = True

class EmployeeUpdatePassword(BaseModel):
    password: str

class LoginRequest(BaseModel):
    nip_or_email: str
    password: str

class AttendanceCreate(BaseModel):
    latitude: float
    longitude: float
    mock_location: bool
    developer_mode: bool

class AttendanceOut(BaseModel):
    id: int
    employee_id: int
    check_in_time: datetime
    check_out_time: Optional[datetime]
    check_in_latitude: Optional[float]
    check_in_longitude: Optional[float]
    check_out_latitude: Optional[float]
    check_out_longitude: Optional[float]
    mock_location: bool
    developer_mode: bool

    class Config:
        orm_mode = True
