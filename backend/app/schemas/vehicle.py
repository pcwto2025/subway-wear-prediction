"""
车辆相关的Pydantic模型
"""
from pydantic import BaseModel
from typing import Optional
from datetime import date
from uuid import UUID


class VehicleBase(BaseModel):
    vehicle_code: str
    model: str
    line_number: str
    manufacture_date: date
    commissioning_date: date
    total_mileage: float
    status: str = "active"


class VehicleCreate(VehicleBase):
    pass


class VehicleUpdate(BaseModel):
    vehicle_code: Optional[str] = None
    model: Optional[str] = None
    line_number: Optional[str] = None
    manufacture_date: Optional[date] = None
    commissioning_date: Optional[date] = None
    total_mileage: Optional[float] = None
    status: Optional[str] = None


class Vehicle(VehicleBase):
    id: UUID
    
    class Config:
        from_attributes = True