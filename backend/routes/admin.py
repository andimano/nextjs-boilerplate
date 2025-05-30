from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_
from passlib.context import CryptContext
from typing import List, Optional
from datetime import datetime

from backend.database import get_db
from backend.models import Employee, Attendance
from backend.schemas import EmployeeCreate, EmployeeOut, EmployeeUpdatePassword, AttendanceOut

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

@router.post("/employees", response_model=EmployeeOut)
async def create_employee(employee: EmployeeCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Employee).where(Employee.nip == employee.nip))
    existing_employee = result.scalars().first()
    if existing_employee:
        raise HTTPException(status_code=400, detail="Employee with this NIP already exists.")
    hashed_password = get_password_hash(employee.password)
    new_employee = Employee(nip=employee.nip, name=employee.name, hashed_password=hashed_password)
    db.add(new_employee)
    await db.commit()
    await db.refresh(new_employee)
    return new_employee

@router.get("/employees", response_model=List[EmployeeOut])
async def list_employees(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Employee))
    employees = result.scalars().all()
    return employees

@router.put("/employees/{employee_id}", response_model=EmployeeOut)
async def update_employee(employee_id: int, employee: EmployeeCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Employee).where(Employee.id == employee_id))
    existing_employee = result.scalars().first()
    if not existing_employee:
        raise HTTPException(status_code=404, detail="Employee not found.")
    existing_employee.nip = employee.nip
    existing_employee.name = employee.name
    if employee.password:
        existing_employee.hashed_password = get_password_hash(employee.password)
    db.add(existing_employee)
    await db.commit()
    await db.refresh(existing_employee)
    return existing_employee

@router.delete("/employees/{employee_id}")
async def delete_employee(employee_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Employee).where(Employee.id == employee_id))
    employee = result.scalars().first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found.")
    await db.delete(employee)
    await db.commit()
    return {"message": "Employee deleted successfully."}

@router.put("/employees/{employee_id}/password")
async def change_employee_password(employee_id: int, password_data: EmployeeUpdatePassword, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Employee).where(Employee.id == employee_id))
    employee = result.scalars().first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found.")
    employee.hashed_password = get_password_hash(password_data.password)
    db.add(employee)
    await db.commit()
    return {"message": "Password updated successfully."}

@router.get("/attendances", response_model=List[AttendanceOut])
async def get_attendance_records(employee_id: Optional[int] = None, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None, db: AsyncSession = Depends(get_db)):
    query = select(Attendance)
    filters = []
    if employee_id:
        filters.append(Attendance.employee_id == employee_id)
    if start_date:
        filters.append(Attendance.check_in_time >= start_date)
    if end_date:
        filters.append(Attendance.check_in_time <= end_date)
    if filters:
        query = query.where(and_(*filters))
    result = await db.execute(query)
    records = result.scalars().all()
    return records
