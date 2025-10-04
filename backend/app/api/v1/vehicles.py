"""车辆管理API"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import date
import uuid

router = APIRouter()


class Vehicle(BaseModel):
    id: Optional[str] = None
    vehicle_code: str
    model: str
    line_number: str
    manufacture_date: date
    commissioning_date: date
    total_mileage: float
    status: str = "active"


class VehicleList(BaseModel):
    items: List[Vehicle]
    total: int
    page: int
    page_size: int


# 模拟数据
mock_vehicles = [
    Vehicle(
        id=str(uuid.uuid4()),
        vehicle_code="SH-01-001",
        model="CRH380A",
        line_number="1号线",
        manufacture_date=date(2020, 1, 15),
        commissioning_date=date(2020, 3, 1),
        total_mileage=125000,
        status="active"
    ),
    Vehicle(
        id=str(uuid.uuid4()),
        vehicle_code="SH-02-005",
        model="CRH380B",
        line_number="2号线",
        manufacture_date=date(2019, 6, 20),
        commissioning_date=date(2019, 8, 1),
        total_mileage=185000,
        status="active"
    ),
]


@router.get("/", response_model=VehicleList)
async def get_vehicles(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    line_number: Optional[str] = None,
    status: Optional[str] = None
):
    """获取车辆列表"""
    filtered_vehicles = mock_vehicles

    if line_number:
        filtered_vehicles = [v for v in filtered_vehicles if v.line_number == line_number]
    if status:
        filtered_vehicles = [v for v in filtered_vehicles if v.status == status]

    # 分页
    start = (page - 1) * page_size
    end = start + page_size
    paginated = filtered_vehicles[start:end]

    return VehicleList(
        items=paginated,
        total=len(filtered_vehicles),
        page=page,
        page_size=page_size
    )


@router.get("/{vehicle_id}", response_model=Vehicle)
async def get_vehicle(vehicle_id: str):
    """获取车辆详情"""
    for vehicle in mock_vehicles:
        if vehicle.id == vehicle_id:
            return vehicle
    raise HTTPException(status_code=404, detail="Vehicle not found")


@router.post("/", response_model=Vehicle)
async def create_vehicle(vehicle: Vehicle):
    """创建车辆"""
    vehicle.id = str(uuid.uuid4())
    mock_vehicles.append(vehicle)
    return vehicle


@router.put("/{vehicle_id}", response_model=Vehicle)
async def update_vehicle(vehicle_id: str, vehicle: Vehicle):
    """更新车辆"""
    for i, v in enumerate(mock_vehicles):
        if v.id == vehicle_id:
            vehicle.id = vehicle_id
            mock_vehicles[i] = vehicle
            return vehicle
    raise HTTPException(status_code=404, detail="Vehicle not found")


@router.delete("/{vehicle_id}")
async def delete_vehicle(vehicle_id: str):
    """删除车辆"""
    for i, v in enumerate(mock_vehicles):
        if v.id == vehicle_id:
            mock_vehicles.pop(i)
            return {"message": "Vehicle deleted successfully"}
    raise HTTPException(status_code=404, detail="Vehicle not found")