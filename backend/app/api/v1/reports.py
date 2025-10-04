"""报表相关API"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import date, datetime
import random

router = APIRouter()


class DashboardData(BaseModel):
    total_vehicles: int
    active_vehicles: int
    vehicles_in_maintenance: int
    high_risk_vehicles: int
    total_predictions: int
    average_mileage: float
    upcoming_maintenance: List[dict]
    risk_distribution: dict
    recent_alerts: List[dict]


@router.get("/dashboard", response_model=DashboardData)
async def get_dashboard_data():
    """获取仪表板数据"""

    return DashboardData(
        total_vehicles=125,
        active_vehicles=118,
        vehicles_in_maintenance=7,
        high_risk_vehicles=12,
        total_predictions=450,
        average_mileage=156000,
        upcoming_maintenance=[
            {
                "vehicle_id": "SH-01-001",
                "date": date(2024, 2, 15).isoformat(),
                "type": "制动片更换",
                "priority": "high"
            },
            {
                "vehicle_id": "SH-02-005",
                "date": date(2024, 2, 18).isoformat(),
                "type": "轮对镟修",
                "priority": "medium"
            },
            {
                "vehicle_id": "SH-03-012",
                "date": date(2024, 2, 20).isoformat(),
                "type": "受电弓检查",
                "priority": "low"
            }
        ],
        risk_distribution={
            "critical": 2,
            "high": 10,
            "medium": 25,
            "low": 45,
            "minimal": 43
        },
        recent_alerts=[
            {
                "time": datetime.now().isoformat(),
                "level": "warning",
                "message": "车辆SH-01-001制动片磨耗接近阈值",
                "vehicle_id": "SH-01-001"
            },
            {
                "time": datetime.now().isoformat(),
                "level": "info",
                "message": "完成车辆SH-09-008定期检查",
                "vehicle_id": "SH-09-008"
            }
        ]
    )


@router.get("/statistics")
async def get_statistics(
    start_date: date = None,
    end_date: date = None,
    line_number: str = None
):
    """获取统计数据"""

    # 生成模拟统计数据
    statistics = {
        "period": {
            "start": start_date.isoformat() if start_date else "2024-01-01",
            "end": end_date.isoformat() if end_date else "2024-12-31"
        },
        "wear_statistics": {
            "wheelset": {
                "average_wear_rate": 0.15,  # mm/万km
                "max_wear_rate": 0.25,
                "min_wear_rate": 0.08,
                "total_replacements": 45
            },
            "brake_pad": {
                "average_wear_rate": 0.5,
                "max_wear_rate": 0.8,
                "min_wear_rate": 0.3,
                "total_replacements": 120
            },
            "pantograph": {
                "average_wear_rate": 0.3,
                "max_wear_rate": 0.5,
                "min_wear_rate": 0.2,
                "total_replacements": 30
            }
        },
        "maintenance_statistics": {
            "total_tasks": 350,
            "completed_tasks": 320,
            "on_time_completion_rate": 0.92,
            "average_downtime_hours": 6.5,
            "total_cost": 2850000
        },
        "prediction_accuracy": {
            "wheelset": 0.92,
            "brake_pad": 0.88,
            "pantograph": 0.85,
            "overall": 0.88
        },
        "cost_analysis": {
            "planned_maintenance_cost": 2100000,
            "unplanned_maintenance_cost": 750000,
            "cost_saving": 450000,
            "cost_per_km": 1.82
        }
    }

    return statistics


@router.post("/generate")
async def generate_report(
    report_type: str,  # monthly, quarterly, annual, custom
    start_date: date,
    end_date: date,
    include_sections: List[str] = None
):
    """生成报表"""

    # 模拟报表生成
    report = {
        "report_id": f"RPT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "type": report_type,
        "period": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        },
        "generated_at": datetime.now().isoformat(),
        "sections": include_sections or [
            "executive_summary",
            "wear_analysis",
            "maintenance_performance",
            "cost_analysis",
            "predictions_accuracy",
            "recommendations"
        ],
        "status": "generated",
        "download_url": f"/api/v1/reports/download/RPT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "file_size": random.randint(500000, 2000000),  # bytes
        "format": "PDF"
    }

    return report


@router.get("/download/{report_id}")
async def download_report(report_id: str):
    """下载报表"""

    # 实际应返回文件内容
    # 这里只返回模拟信息
    return {
        "message": f"Report {report_id} would be downloaded here",
        "file_name": f"{report_id}.pdf",
        "content_type": "application/pdf"
    }


@router.get("/fleet-overview")
async def get_fleet_overview():
    """获取车队概览"""

    lines = ["1号线", "2号线", "9号线", "10号线"]
    fleet_overview = []

    for line in lines:
        fleet_overview.append({
            "line_number": line,
            "total_vehicles": random.randint(20, 40),
            "active_vehicles": random.randint(18, 35),
            "average_mileage": random.randint(100000, 200000),
            "high_risk_vehicles": random.randint(0, 5),
            "maintenance_due": random.randint(1, 8),
            "performance_score": round(random.uniform(0.8, 0.95), 2)
        })

    return {
        "updated_at": datetime.now().isoformat(),
        "lines": fleet_overview,
        "summary": {
            "total_lines": len(lines),
            "total_vehicles": sum(l["total_vehicles"] for l in fleet_overview),
            "total_active": sum(l["active_vehicles"] for l in fleet_overview),
            "average_performance": round(
                sum(l["performance_score"] for l in fleet_overview) / len(fleet_overview), 2
            )
        }
    }