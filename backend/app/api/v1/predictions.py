"""预测相关API"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime
import random
from uuid import UUID

from app.core.database import get_db
from app.schemas.prediction import PredictionRequest, PredictionResponse, BatchPredictionRequest, WearTrendData
from app.services.prediction_service import PredictionService
from app.models.vehicle import Vehicle
from app.models.prediction import WearTrendData as WearTrendDataModel

router = APIRouter()


@router.post("/single", response_model=PredictionResponse)
async def predict_single_vehicle(
    request: PredictionRequest, 
    db: AsyncSession = Depends(get_db)
):
    """单车磨耗预测"""
    try:
        predictions, risk_level, overall_confidence, recommendations = await PredictionService.calculate_prediction(
            db, request.vehicle_id, request.prediction_horizon_days
        )

        return PredictionResponse(
            vehicle_id=request.vehicle_id,
            prediction_date=datetime.now(),
            risk_level=risk_level,
            overall_confidence=overall_confidence,
            predictions=predictions,
            maintenance_recommendations=recommendations
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@router.post("/batch")
async def predict_batch_vehicles(
    request: BatchPredictionRequest,
    db: AsyncSession = Depends(get_db)
):
    """批量车辆预测"""
    results = []
    for vehicle_id in request.vehicle_ids:
        try:
            # 为每辆车进行预测
            single_request = PredictionRequest(
                vehicle_id=vehicle_id,
                prediction_horizon_days=request.prediction_horizon_days
            )
            result = await predict_single_vehicle(single_request, db)
            results.append(result)
        except Exception:
            # 如果某辆车预测失败，记录错误但继续处理其他车辆
            continue

    return {
        "total": len(results),
        "predictions": results,
        "summary": {
            "high_risk": sum(1 for r in results if r.risk_level == "high"),
            "medium_risk": sum(1 for r in results if r.risk_level == "medium"),
            "low_risk": sum(1 for r in results if r.risk_level == "low")
        }
    }


@router.get("/trends")
async def get_wear_trends(
    vehicle_id: str,
    component_type: str,
    days: int = 90,
    db: AsyncSession = Depends(get_db)
):
    """获取磨耗趋势"""
    from uuid import UUID as uuid_lib
    from sqlalchemy import select
    
    try:
        # 尝试将vehicle_id转换为UUID
        uuid_vehicle_id = uuid_lib(vehicle_id)
    except ValueError:
        # 如果不是UUID格式，尝试通过vehicle_code查找
        vehicle_result = await db.execute(
            select(Vehicle).where(Vehicle.vehicle_code == vehicle_id)
        )
        vehicle = vehicle_result.scalar_one_or_none()
        if not vehicle:
            raise HTTPException(status_code=404, detail=f"Vehicle with ID or code {vehicle_id} not found")
        uuid_vehicle_id = vehicle.id

    # 获取数据库中的趋势数据
    trend_data = await PredictionService.get_wear_trend_data(
        db, uuid_vehicle_id, component_type, days
    )

    # 以字典格式返回数据
    result = []
    for trend in trend_data:
        result.append({
            "id": str(trend.id),
            "vehicle_id": str(trend.vehicle_id),
            "component_type": trend.component_type,
            "date": trend.date.isoformat(),
            "wear_value": trend.wear_value,
            "mileage": trend.mileage
        })

    return result