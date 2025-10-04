"""维护管理API"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime
import uuid

router = APIRouter()


class MaintenancePlan(BaseModel):
    id: Optional[str] = None
    vehicle_id: str
    plan_date: date
    plan_type: str  # preventive, corrective, predictive
    priority: str  # urgent, high, medium, low
    component_type: str
    action_required: str
    estimated_cost: float
    estimated_downtime_hours: int
    status: str = "planned"  # planned, in_progress, completed, cancelled


class MaintenanceSuggestion(BaseModel):
    vehicle_id: str
    component: str
    current_condition: str
    recommended_action: str
    urgency: str
    estimated_cost: float
    reason: str


@router.get("/plans", response_model=List[MaintenancePlan])
async def get_maintenance_plans(
    vehicle_id: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    """获取维护计划列表"""

    # 模拟维护计划数据
    mock_plans = [
        MaintenancePlan(
            id=str(uuid.uuid4()),
            vehicle_id="vehicle-001",
            plan_date=date(2024, 2, 15),
            plan_type="predictive",
            priority="high",
            component_type="brake_pad",
            action_required="更换前轮制动片",
            estimated_cost=3500,
            estimated_downtime_hours=4,
            status="planned"
        ),
        MaintenancePlan(
            id=str(uuid.uuid4()),
            vehicle_id="vehicle-002",
            plan_date=date(2024, 2, 20),
            plan_type="preventive",
            priority="medium",
            component_type="wheelset",
            action_required="轮对镟修",
            estimated_cost=15000,
            estimated_downtime_hours=8,
            status="planned"
        ),
    ]

    # 过滤
    filtered = mock_plans
    if vehicle_id:
        filtered = [p for p in filtered if p.vehicle_id == vehicle_id]
    if status:
        filtered = [p for p in filtered if p.status == status]
    if priority:
        filtered = [p for p in filtered if p.priority == priority]

    # 分页
    start = (page - 1) * page_size
    end = start + page_size

    return filtered[start:end]


@router.post("/plans", response_model=MaintenancePlan)
async def create_maintenance_plan(plan: MaintenancePlan):
    """创建维护计划"""
    plan.id = str(uuid.uuid4())
    return plan


@router.put("/plans/{plan_id}", response_model=MaintenancePlan)
async def update_maintenance_plan(plan_id: str, plan: MaintenancePlan):
    """更新维护计划"""
    plan.id = plan_id
    return plan


@router.delete("/plans/{plan_id}")
async def delete_maintenance_plan(plan_id: str):
    """删除维护计划"""
    return {"message": f"Plan {plan_id} deleted successfully"}


@router.get("/suggestions", response_model=List[MaintenanceSuggestion])
async def get_maintenance_suggestions(
    vehicle_id: Optional[str] = None,
    urgency: Optional[str] = None
):
    """获取维护建议"""

    suggestions = [
        MaintenanceSuggestion(
            vehicle_id="vehicle-001",
            component="制动系统",
            current_condition="制动片厚度接近最小值",
            recommended_action="计划在2周内更换制动片",
            urgency="high",
            estimated_cost=3500,
            reason="基于磨耗预测，制动片将在30天内达到最小安全厚度"
        ),
        MaintenanceSuggestion(
            vehicle_id="vehicle-001",
            component="轮对",
            current_condition="轮径磨耗正常",
            recommended_action="下次大修时进行镟修",
            urgency="low",
            estimated_cost=15000,
            reason="当前磨耗率正常，预计3个月后需要镟修"
        ),
        MaintenanceSuggestion(
            vehicle_id="vehicle-002",
            component="受电弓",
            current_condition="碳滑板磨耗加速",
            recommended_action="增加检查频率，准备更换",
            urgency="medium",
            estimated_cost=5000,
            reason="检测到磨耗率异常增加，建议密切监控"
        ),
    ]

    # 过滤
    if vehicle_id:
        suggestions = [s for s in suggestions if s.vehicle_id == vehicle_id]
    if urgency:
        suggestions = [s for s in suggestions if s.urgency == urgency]

    return suggestions


@router.post("/schedule-optimization")
async def optimize_maintenance_schedule(vehicle_ids: List[str]):
    """优化维护计划"""

    # 模拟优化结果
    optimized_schedule = {
        "original_cost": 150000,
        "optimized_cost": 120000,
        "cost_saving": 30000,
        "original_downtime_hours": 48,
        "optimized_downtime_hours": 36,
        "schedule": [
            {
                "date": date(2024, 2, 15).isoformat(),
                "vehicles": ["vehicle-001", "vehicle-003"],
                "actions": ["制动片更换", "常规检查"],
                "total_hours": 8
            },
            {
                "date": date(2024, 2, 20).isoformat(),
                "vehicles": ["vehicle-002"],
                "actions": ["轮对镟修"],
                "total_hours": 8
            },
        ],
        "recommendations": [
            "合并相同类型的维护任务可减少停机时间",
            "建议采购备件以减少等待时间",
            "可考虑夜间维护以减少运营影响"
        ]
    }

    return optimized_schedule