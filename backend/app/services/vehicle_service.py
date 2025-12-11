"""
车辆服务层
"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.vehicle import Vehicle
from app.schemas.vehicle import VehicleCreate, VehicleUpdate


class VehicleService:
    """车辆服务类"""

    @staticmethod
    async def get_vehicle(db: AsyncSession, vehicle_id: UUID) -> Optional[Vehicle]:
        """根据ID获取车辆"""
        result = await db.execute(select(Vehicle).where(Vehicle.id == vehicle_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_vehicle_by_code(db: AsyncSession, vehicle_code: str) -> Optional[Vehicle]:
        """根据车辆编号获取车辆"""
        result = await db.execute(select(Vehicle).where(Vehicle.vehicle_code == vehicle_code))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_vehicles(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        line_number: Optional[str] = None,
        status: Optional[str] = None
    ) -> tuple[List[Vehicle], int]:
        """获取车辆列表"""
        query = select(Vehicle)
        
        if line_number:
            query = query.where(Vehicle.line_number == line_number)
        if status:
            query = query.where(Vehicle.status == status)
        
        # 获取总数
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await db.execute(count_query)
        total = count_result.scalar_one()
        
        # 获取分页数据
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        vehicles = result.scalars().all()
        
        return vehicles, total

    @staticmethod
    async def create_vehicle(db: AsyncSession, vehicle_data: VehicleCreate) -> Vehicle:
        """创建车辆"""
        # 检查车辆编号是否已存在
        existing_vehicle = await VehicleService.get_vehicle_by_code(db, vehicle_data.vehicle_code)
        if existing_vehicle:
            raise ValueError(f"Vehicle with code {vehicle_data.vehicle_code} already exists")
        
        vehicle = Vehicle(
            vehicle_code=vehicle_data.vehicle_code,
            model=vehicle_data.model,
            line_number=vehicle_data.line_number,
            manufacture_date=vehicle_data.manufacture_date,
            commissioning_date=vehicle_data.commissioning_date,
            total_mileage=vehicle_data.total_mileage,
            status=vehicle_data.status
        )
        
        db.add(vehicle)
        await db.commit()
        await db.refresh(vehicle)
        
        return vehicle

    @staticmethod
    async def update_vehicle(db: AsyncSession, vehicle_id: UUID, vehicle_data: VehicleUpdate) -> Optional[Vehicle]:
        """更新车辆"""
        vehicle = await VehicleService.get_vehicle(db, vehicle_id)
        if not vehicle:
            return None
        
        update_data = vehicle_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(vehicle, field, value)
        
        await db.commit()
        await db.refresh(vehicle)
        
        return vehicle

    @staticmethod
    async def delete_vehicle(db: AsyncSession, vehicle_id: UUID) -> bool:
        """删除车辆"""
        vehicle = await VehicleService.get_vehicle(db, vehicle_id)
        if not vehicle:
            return False
        
        await db.delete(vehicle)
        await db.commit()
        
        return True