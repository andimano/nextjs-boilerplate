from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime
from math import radians, cos, sin, asin, sqrt

from backend.database import get_db
from backend.models import Attendance, Employee
from backend.schemas import AttendanceCreate

router = APIRouter()

# Fixed GPS points and radius in meters
LOCATION_POINTS = [
    {"lat": -4.01329, "lon": 119.62596, "radius": 100},
    {"lat": -4.03630, "lon": 119.63229, "radius": 100},
]

def haversine(lat1, lon1, lat2, lon2):
    # convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    # haversine formula
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371000  # Radius of earth in meters
    return c * r

def is_within_radius(lat, lon):
    for point in LOCATION_POINTS:
        distance = haversine(lat, lon, point["lat"], point["lon"])
        if distance <= point["radius"]:
            return True
    return False

@router.post("/checkin/{employee_id}")
async def check_in(employee_id: int, attendance: AttendanceCreate, db: AsyncSession = Depends(get_db)):
    if not is_within_radius(attendance.latitude, attendance.longitude):
        raise HTTPException(status_code=400, detail="You are not within the allowed attendance location radius.")

    new_attendance = Attendance(
        employee_id=employee_id,
        check_in_time=datetime.utcnow(),
        check_in_latitude=attendance.latitude,
        check_in_longitude=attendance.longitude,
        mock_location=attendance.mock_location,
        developer_mode=attendance.developer_mode,
    )
    db.add(new_attendance)
    await db.commit()
    await db.refresh(new_attendance)
    return {"message": "Check-in successful", "attendance_id": new_attendance.id}

@router.post("/checkout/{attendance_id}")
async def check_out(attendance_id: int, attendance: AttendanceCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Attendance).where(Attendance.id == attendance_id))
    attendance_record = result.scalars().first()
    if not attendance_record:
        raise HTTPException(status_code=404, detail="Attendance record not found.")

    if not is_within_radius(attendance.latitude, attendance.longitude):
        raise HTTPException(status_code=400, detail="You are not within the allowed attendance location radius.")

    attendance_record.check_out_time = datetime.utcnow()
    attendance_record.check_out_latitude = attendance.latitude
    attendance_record.check_out_longitude = attendance.longitude
    attendance_record.mock_location = attendance.mock_location
    attendance_record.developer_mode = attendance.developer_mode

    db.add(attendance_record)
    await db.commit()
    await db.refresh(attendance_record)
    return {"message": "Check-out successful"}
