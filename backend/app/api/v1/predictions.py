"""预测相关API"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime
import random

router = APIRouter()


class PredictionRequest(BaseModel):
    vehicle_id: str
    prediction_horizon_days: int = 180


class WearPrediction(BaseModel):
    component_type: str
    component_position: str
    current_wear: float
    predicted_wear: float
    wear_rate: float  # mm per 10000km
    remaining_life_days: int
    remaining_life_mileage: float
    replacement_date: date
    confidence_score: float


class PredictionResponse(BaseModel):
    vehicle_id: str
    prediction_date: datetime
    risk_level: str
    overall_confidence: float
    predictions: List[WearPrediction]
    maintenance_recommendations: List[dict]


@router.post("/single", response_model=PredictionResponse)
async def predict_single_vehicle(request: PredictionRequest):
    """单车磨耗预测"""

    # 模拟预测结果
    predictions = [
        WearPrediction(
            component_type="wheelset",
            component_position="1A",
            current_wear=4.5,
            predicted_wear=6.8,
            wear_rate=0.15,
            remaining_life_days=120,
            remaining_life_mileage=50000,
            replacement_date=date(2024, 5, 15),
            confidence_score=0.92
        ),
        WearPrediction(
            component_type="brake_pad",
            component_position="前左",
            current_wear=35,
            predicted_wear=25,
            wear_rate=0.5,
            remaining_life_days=90,
            remaining_life_mileage=35000,
            replacement_date=date(2024, 4, 15),
            confidence_score=0.88
        ),
        WearPrediction(
            component_type="pantograph",
            component_position="前",
            current_wear=12,
            predicted_wear=8,
            wear_rate=0.3,
            remaining_life_days=150,
            remaining_life_mileage=60000,
            replacement_date=date(2024, 6, 20),
            confidence_score=0.85
        )
    ]

    # 生成维护建议
    recommendations = [
        {
            "priority": "high",
            "component": "制动片-前左",
            "action": "计划更换",
            "reason": "预计90天内达到最小厚度",
            "estimated_cost": 3000,
            "estimated_downtime_hours": 4
        },
        {
            "priority": "medium",
            "component": "轮对1A",
            "action": "镟修准备",
            "reason": "预计120天内需要镟修",
            "estimated_cost": 15000,
            "estimated_downtime_hours": 8
        }
    ]

    # 确定风险等级
    min_days = min(p.remaining_life_days for p in predictions)
    if min_days < 30:
        risk_level = "high"
    elif min_days < 60:
        risk_level = "medium"
    else:
        risk_level = "low"

    return PredictionResponse(
        vehicle_id=request.vehicle_id,
        prediction_date=datetime.now(),
        risk_level=risk_level,
        overall_confidence=0.88,
        predictions=predictions,
        maintenance_recommendations=recommendations
    )


class BatchPredictionRequest(BaseModel):
    vehicle_ids: List[str]
    prediction_horizon_days: int = 180


@router.post("/batch")
async def predict_batch_vehicles(request: BatchPredictionRequest):
    """批量车辆预测"""

    results = []
    for vehicle_id in request.vehicle_ids:
        # 模拟每辆车的预测
        single_request = PredictionRequest(
            vehicle_id=vehicle_id,
            prediction_horizon_days=request.prediction_horizon_days
        )
        result = await predict_single_vehicle(single_request)
        results.append(result)

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
    days: int = 90
):
    """获取磨耗趋势"""

    # 生成模拟趋势数据
    trend_data = []
    for i in range(days // 7):  # 每周一个数据点
        trend_data.append({
            "date": date(2024, 1, 1 + i * 7).isoformat(),
            "wear_value": 2.0 + i * 0.1 + random.uniform(-0.05, 0.05),
            "mileage": 100000 + i * 7 * 500
        })

    return {
        "vehicle_id": vehicle_id,
        "component_type": component_type,
        "trend_data": trend_data,
        "trend_line": {
            "slope": 0.015,  # mm/week
            "intercept": 2.0,
            "r2": 0.95
        },
        "prediction": {
            "next_week": 2.0 + (len(trend_data) + 1) * 0.1,
            "next_month": 2.0 + (len(trend_data) + 4) * 0.1
        }
    }