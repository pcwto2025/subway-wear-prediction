"""
轮对统计相关的Pydantic模型
"""
from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime
from uuid import UUID


class WheelsetStatisticsBase(BaseModel):
    vehicle_id: UUID
    wheelset_position: str
    current_diameter: float
    flange_thickness: Optional[float] = None
    flange_height: Optional[float] = None
    qr_value: Optional[float] = None
    mileage_at_measurement: Optional[float] = None
    last_rewheeling_date: Optional[date] = None
    next_rewheeling_mileage: Optional[float] = None
    wear_rate: Optional[float] = 0.0
    status: Optional[str] = "normal"
    inspection_date: date
    inspector: Optional[str] = None
    notes: Optional[str] = None


class WheelsetStatisticsCreate(WheelsetStatisticsBase):
    pass


class WheelsetStatisticsUpdate(BaseModel):
    current_diameter: Optional[float] = None
    flange_thickness: Optional[float] = None
    flange_height: Optional[float] = None
    qr_value: Optional[float] = None
    mileage_at_measurement: Optional[float] = None
    last_rewheeling_date: Optional[date] = None
    next_rewheeling_mileage: Optional[float] = None
    wear_rate: Optional[float] = None
    status: Optional[str] = None
    inspection_date: Optional[date] = None
    inspector: Optional[str] = None
    notes: Optional[str] = None


class WheelsetStatistics(WheelsetStatisticsBase):
    id: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True