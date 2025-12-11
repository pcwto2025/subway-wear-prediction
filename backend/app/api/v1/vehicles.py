"""车辆管理API"""

from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import List, Optional
from datetime import date
from uuid import UUID
import uuid

from app.core.database import get_db
from app.schemas.vehicle import Vehicle as VehicleSchema, VehicleCreate, VehicleUpdate
from app.services.vehicle_service import VehicleService

router = APIRouter()


class VehicleList(BaseModel):
    items: List[VehicleSchema]
    total: int
    page: int
    page_size: int


@router.get("/", response_model=VehicleList)
async def get_vehicles(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    line_number: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """获取车辆列表"""
    skip = (page - 1) * page_size
    
    vehicles, total = await VehicleService.get_vehicles(
        db, skip=skip, limit=page_size, 
        line_number=line_number, status=status
    )

    return VehicleList(
        items=vehicles,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{vehicle_id}", response_model=VehicleSchema)
async def get_vehicle(vehicle_id: str, db: AsyncSession = Depends(get_db)):
    """获取车辆详情"""
    try:
        uuid_obj = UUID(vehicle_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid vehicle ID format")
        
    vehicle = await VehicleService.get_vehicle(db, uuid_obj)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle


@router.post("/", response_model=VehicleSchema)
async def create_vehicle(vehicle: VehicleCreate, db: AsyncSession = Depends(get_db)):
    """创建车辆"""
    try:
        created_vehicle = await VehicleService.create_vehicle(db, vehicle)
        return created_vehicle
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating vehicle: {str(e)}")


@router.put("/{vehicle_id}", response_model=VehicleSchema)
async def update_vehicle(vehicle_id: str, vehicle: VehicleUpdate, db: AsyncSession = Depends(get_db)):
    """更新车辆"""
    try:
        uuid_obj = UUID(vehicle_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid vehicle ID format")
        
    updated_vehicle = await VehicleService.update_vehicle(db, uuid_obj, vehicle)
    if not updated_vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return updated_vehicle


@router.delete("/{vehicle_id}")
async def delete_vehicle(vehicle_id: str, db: AsyncSession = Depends(get_db)):
    """删除车辆"""
    try:
        uuid_obj = UUID(vehicle_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid vehicle ID format")
        
    success = await VehicleService.delete_vehicle(db, uuid_obj)
    if not success:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return {"message": "Vehicle deleted successfully"}