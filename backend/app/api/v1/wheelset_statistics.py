"""轮对统计相关API"""

from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID

from app.core.database import get_db
from app.schemas.wheelset_statistics import WheelsetStatistics, WheelsetStatisticsCreate, WheelsetStatisticsUpdate
from app.services.wheelset_statistics_service import WheelsetStatisticsService


router = APIRouter(prefix="/wheelset-statistics", tags=["wheelset-statistics"])


@router.get("/", response_model=List[WheelsetStatistics])
async def get_wheelset_statistics(
    vehicle_id: Optional[str] = Query(None, description="车辆ID"),
    status: Optional[str] = Query(None, description="状态"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """获取轮对统计数据"""
    if vehicle_id:
        try:
            vehicle_uuid = UUID(vehicle_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid vehicle ID format")
        
        statistics, total = await WheelsetStatisticsService.get_wheelset_statistics_by_vehicle(
            db, vehicle_uuid, skip=skip, limit=limit
        )
    else:
        statistics, total = await WheelsetStatisticsService.get_all_wheelset_statistics(
            db, skip=skip, limit=limit, status=status
        )
    
    return statistics


@router.get("/{stat_id}", response_model=WheelsetStatistics)
async def get_wheelset_statistic(stat_id: str, db: AsyncSession = Depends(get_db)):
    """获取轮对统计数据详情"""
    try:
        uuid_obj = UUID(stat_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid statistic ID format")
    
    statistics = await WheelsetStatisticsService.get_wheelset_statistics(db, uuid_obj)
    if not statistics:
        raise HTTPException(status_code=404, detail="Wheelset statistics not found")
    
    return statistics


@router.post("/", response_model=WheelsetStatistics)
async def create_wheelset_statistics(
    statistics: WheelsetStatisticsCreate, 
    db: AsyncSession = Depends(get_db)
):
    """创建轮对统计数据"""
    try:
        created_statistics = await WheelsetStatisticsService.create_wheelset_statistics(db, statistics)
        return created_statistics
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating wheelset statistics: {str(e)}")


@router.put("/{stat_id}", response_model=WheelsetStatistics)
async def update_wheelset_statistics(
    stat_id: str, 
    statistics: WheelsetStatisticsUpdate, 
    db: AsyncSession = Depends(get_db)
):
    """更新轮对统计数据"""
    try:
        uuid_obj = UUID(stat_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid statistic ID format")
    
    updated_statistics = await WheelsetStatisticsService.update_wheelset_statistics(
        db, uuid_obj, statistics
    )
    if not updated_statistics:
        raise HTTPException(status_code=404, detail="Wheelset statistics not found")
    
    return updated_statistics


@router.delete("/{stat_id}")
async def delete_wheelset_statistics(stat_id: str, db: AsyncSession = Depends(get_db)):
    """删除轮对统计数据"""
    try:
        uuid_obj = UUID(stat_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid statistic ID format")
    
    success = await WheelsetStatisticsService.delete_wheelset_statistics(db, uuid_obj)
    if not success:
        raise HTTPException(status_code=404, detail="Wheelset statistics not found")
    
    return {"message": "Wheelset statistics deleted successfully"}