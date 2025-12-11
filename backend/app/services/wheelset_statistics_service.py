"""
轮对统计服务层
"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from app.models.prediction import WheelsetStatistics as WheelsetStatisticsModel
from app.schemas.wheelset_statistics import WheelsetStatisticsCreate, WheelsetStatisticsUpdate


class WheelsetStatisticsService:
    """轮对统计服务类"""

    @staticmethod
    async def get_wheelset_statistics(db: AsyncSession, stat_id: UUID) -> Optional[WheelsetStatisticsModel]:
        """根据ID获取轮对统计数据"""
        result = await db.execute(
            select(WheelsetStatisticsModel).where(WheelsetStatisticsModel.id == stat_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_wheelset_statistics_by_vehicle_and_position(
        db: AsyncSession, 
        vehicle_id: UUID, 
        wheelset_position: str
    ) -> Optional[WheelsetStatisticsModel]:
        """根据车辆ID和轮对位置获取轮对统计数据"""
        result = await db.execute(
            select(WheelsetStatisticsModel)
            .where(
                and_(
                    WheelsetStatisticsModel.vehicle_id == vehicle_id,
                    WheelsetStatisticsModel.wheelset_position == wheelset_position
                )
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_wheelset_statistics_by_vehicle(
        db: AsyncSession, 
        vehicle_id: UUID, 
        skip: int = 0, 
        limit: int = 100
    ) -> tuple[List[WheelsetStatisticsModel], int]:
        """根据车辆ID获取轮对统计数据列表"""
        query = select(WheelsetStatisticsModel).where(WheelsetStatisticsModel.vehicle_id == vehicle_id)
        
        # 获取总数
        count_query = select(func.count()).select_from(
            select(WheelsetStatisticsModel)
            .where(WheelsetStatisticsModel.vehicle_id == vehicle_id)
            .subquery()
        )
        count_result = await db.execute(count_query)
        total = count_result.scalar_one()
        
        # 获取分页数据
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        statistics = result.scalars().all()
        
        return statistics, total

    @staticmethod
    async def create_wheelset_statistics(
        db: AsyncSession, 
        statistics_data: WheelsetStatisticsCreate
    ) -> WheelsetStatisticsModel:
        """创建轮对统计数据"""
        # 检查是否已存在相同车辆和位置的记录
        existing = await WheelsetStatisticsService.get_wheelset_statistics_by_vehicle_and_position(
            db, statistics_data.vehicle_id, statistics_data.wheelset_position
        )
        
        if existing:
            raise ValueError(f"Wheelset statistics for vehicle {statistics_data.vehicle_id} and position {statistics_data.wheelset_position} already exists")

        statistics = WheelsetStatisticsModel(**statistics_data.dict())
        db.add(statistics)
        await db.commit()
        await db.refresh(statistics)
        return statistics

    @staticmethod
    async def update_wheelset_statistics(
        db: AsyncSession, 
        stat_id: UUID, 
        statistics_data: WheelsetStatisticsUpdate
    ) -> Optional[WheelsetStatisticsModel]:
        """更新轮对统计数据"""
        statistics = await WheelsetStatisticsService.get_wheelset_statistics(db, stat_id)
        if not statistics:
            return None

        update_data = statistics_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(statistics, field, value)

        await db.commit()
        await db.refresh(statistics)
        return statistics

    @staticmethod
    async def delete_wheelset_statistics(db: AsyncSession, stat_id: UUID) -> bool:
        """删除轮对统计数据"""
        statistics = await WheelsetStatisticsService.get_wheelset_statistics(db, stat_id)
        if not statistics:
            return False

        await db.delete(statistics)
        await db.commit()
        return True

    @staticmethod
    async def get_all_wheelset_statistics(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None
    ) -> tuple[List[WheelsetStatisticsModel], int]:
        """获取所有轮对统计数据"""
        query = select(WheelsetStatisticsModel)
        
        if status:
            query = query.where(WheelsetStatisticsModel.status == status)
        
        # 获取总数
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await db.execute(count_query)
        total = count_result.scalar_one()
        
        # 获取分页数据
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        statistics = result.scalars().all()
        
        return statistics, total