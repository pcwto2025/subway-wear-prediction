"""
大修管理数据模式
Overhaul Management Schemas
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from uuid import UUID
from enum import Enum


class OverhaulType(str, Enum):
    """大修类型"""
    SCHEDULED = "scheduled"
    EMERGENCY = "emergency"
    UPGRADE = "upgrade"
    ACCIDENT = "accident"


class OverhaulStatus(str, Enum):
    """大修状态"""
    PLANNING = "planning"
    APPROVED = "approved"
    IN_PROGRESS = "in_progress"
    SUSPENDED = "suspended"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class OverhaulLevel(str, Enum):
    """大修级别"""
    A1 = "A1"
    A2 = "A2"
    A3 = "A3"
    B1 = "B1"
    B2 = "B2"
    C1 = "C1"
    C2 = "C2"


# ===================== Overhaul Item Schemas =====================
class OverhaulItemBase(BaseModel):
    """大修项目基础模式"""
    item_code: str
    item_name: str
    category: Optional[str] = None
    carriage_number: Optional[str] = None
    component_type: Optional[str] = None
    work_content: Optional[str] = None
    technical_standard: Optional[str] = None
    inspection_method: Optional[str] = None


class OverhaulItemCreate(OverhaulItemBase):
    """创建大修项目"""
    pass


class OverhaulItemUpdate(BaseModel):
    """更新大修项目"""
    status: Optional[str] = None
    progress_percentage: Optional[int] = Field(None, ge=0, le=100)
    quality_check_status: Optional[str] = None
    quality_inspector: Optional[str] = None
    quality_check_date: Optional[date] = None
    quality_notes: Optional[str] = None
    labor_hours: Optional[float] = None
    material_cost: Optional[float] = None
    labor_cost: Optional[float] = None
    total_cost: Optional[float] = None
    spare_parts_used: Optional[List[Dict[str, Any]]] = None
    old_parts_disposal: Optional[str] = None


class OverhaulItemResponse(OverhaulItemBase):
    """大修项目响应"""
    id: UUID
    overhaul_plan_id: UUID
    status: str = "pending"
    progress_percentage: int = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    quality_check_status: Optional[str] = None
    quality_inspector: Optional[str] = None
    quality_check_date: Optional[date] = None
    quality_notes: Optional[str] = None
    labor_hours: Optional[float] = None
    material_cost: Optional[float] = None
    labor_cost: Optional[float] = None
    total_cost: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# ===================== Spare Part Schemas =====================
class SparePartBase(BaseModel):
    """备件基础模式"""
    part_number: str
    part_name: str
    category: Optional[str] = None
    manufacturer: Optional[str] = None
    planned_quantity: int = Field(..., gt=0)
    unit: Optional[str] = None
    unit_price: Optional[float] = None


class SparePartCreate(SparePartBase):
    """创建备件"""
    pass


class SparePartUpdate(BaseModel):
    """更新备件"""
    actual_quantity: Optional[int] = None
    stock_quantity: Optional[int] = None
    warehouse_location: Optional[str] = None
    purchase_order_no: Optional[str] = None
    supplier: Optional[str] = None
    delivery_date: Optional[date] = None
    quality_certificate: Optional[str] = None
    warranty_period: Optional[int] = None


class SparePartResponse(SparePartBase):
    """备件响应"""
    id: UUID
    overhaul_plan_id: UUID
    actual_quantity: Optional[int] = None
    total_price: Optional[float] = None
    stock_quantity: Optional[int] = None
    warehouse_location: Optional[str] = None
    purchase_order_no: Optional[str] = None
    supplier: Optional[str] = None
    delivery_date: Optional[date] = None
    quality_certificate: Optional[str] = None
    warranty_period: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# ===================== Overhaul Plan Schemas =====================
class OverhaulPlanBase(BaseModel):
    """大修计划基础模式"""
    plan_code: str = Field(..., description="大修计划编号")
    train_number: str = Field(..., pattern="^Tr(0[1-9]|1[0-6])$", description="列车编号")
    overhaul_type: OverhaulType
    overhaul_level: OverhaulLevel
    planned_start_date: date
    planned_end_date: date
    estimated_cost: Optional[float] = None
    contractor: Optional[str] = None
    workshop: Optional[str] = None
    responsible_person: Optional[str] = None
    contact_phone: Optional[str] = None
    description: Optional[str] = None
    technical_requirements: Optional[str] = None
    safety_requirements: Optional[str] = None
    quality_standards: Optional[str] = None

    @validator('planned_end_date')
    def validate_dates(cls, v, values):
        if 'planned_start_date' in values and v <= values['planned_start_date']:
            raise ValueError('planned_end_date must be after planned_start_date')
        return v


class OverhaulPlanCreate(OverhaulPlanBase):
    """创建大修计划"""
    vehicle_id: Optional[UUID] = None
    mileage_at_overhaul: Optional[float] = None
    next_overhaul_mileage: Optional[float] = None
    items: Optional[List[OverhaulItemCreate]] = []
    spare_parts: Optional[List[SparePartCreate]] = []


class OverhaulPlanUpdate(BaseModel):
    """更新大修计划"""
    status: Optional[OverhaulStatus] = None
    actual_start_date: Optional[date] = None
    actual_end_date: Optional[date] = None
    actual_cost: Optional[float] = None
    approval_status: Optional[str] = None
    approval_notes: Optional[str] = None
    contractor: Optional[str] = None
    workshop: Optional[str] = None
    responsible_person: Optional[str] = None
    contact_phone: Optional[str] = None


class OverhaulPlanResponse(OverhaulPlanBase):
    """大修计划响应"""
    id: UUID
    vehicle_id: Optional[UUID] = None
    status: OverhaulStatus = OverhaulStatus.PLANNING
    actual_start_date: Optional[date] = None
    actual_end_date: Optional[date] = None
    mileage_at_overhaul: Optional[float] = None
    next_overhaul_mileage: Optional[float] = None
    actual_cost: Optional[float] = None
    currency: str = "CNY"
    approval_status: Optional[str] = None
    approved_by: Optional[UUID] = None
    approved_at: Optional[datetime] = None
    approval_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None

    # 关联数据
    items: List[OverhaulItemResponse] = []
    spare_parts: List[SparePartResponse] = []

    # 计算字段
    duration_days: Optional[int] = None
    progress_percentage: Optional[float] = None
    cost_variance: Optional[float] = None

    class Config:
        orm_mode = True

    def calculate_fields(self):
        """计算派生字段"""
        # 计算工期
        if self.actual_start_date and self.actual_end_date:
            self.duration_days = (self.actual_end_date - self.actual_start_date).days
        elif self.planned_start_date and self.planned_end_date:
            self.duration_days = (self.planned_end_date - self.planned_start_date).days

        # 计算进度
        if self.items:
            total_progress = sum(item.progress_percentage for item in self.items)
            self.progress_percentage = total_progress / len(self.items)

        # 计算成本偏差
        if self.estimated_cost and self.actual_cost:
            self.cost_variance = self.actual_cost - self.estimated_cost


# ===================== Overhaul Record Schemas =====================
class OverhaulRecordBase(BaseModel):
    """大修记录基础模式"""
    train_number: str
    overhaul_level: OverhaulLevel
    start_date: date
    end_date: date
    mileage_before: Optional[float] = None
    mileage_after: Optional[float] = None
    total_cost: Optional[float] = None
    quality_score: Optional[int] = Field(None, ge=0, le=100)
    performance_improvement: Optional[str] = None
    problems_found: Optional[str] = None
    solutions_applied: Optional[str] = None


class OverhaulRecordCreate(OverhaulRecordBase):
    """创建大修记录"""
    overhaul_plan_id: Optional[UUID] = None
    vehicle_id: Optional[UUID] = None
    labor_cost: Optional[float] = None
    material_cost: Optional[float] = None
    spare_parts_cost: Optional[float] = None
    report_url: Optional[str] = None
    photos: Optional[List[str]] = None
    documents: Optional[List[Dict[str, str]]] = None


class OverhaulRecordResponse(OverhaulRecordBase):
    """大修记录响应"""
    id: UUID
    overhaul_plan_id: Optional[UUID] = None
    vehicle_id: Optional[UUID] = None
    duration_days: Optional[int] = None
    mileage_interval: Optional[float] = None
    labor_cost: Optional[float] = None
    material_cost: Optional[float] = None
    spare_parts_cost: Optional[float] = None
    report_url: Optional[str] = None
    photos: Optional[List[str]] = None
    documents: Optional[List[Dict[str, str]]] = None
    created_at: datetime
    created_by: Optional[UUID] = None

    class Config:
        orm_mode = True


# ===================== Overhaul Standard Schemas =====================
class OverhaulStandardBase(BaseModel):
    """大修标准基础模式"""
    vehicle_type: str
    overhaul_level: OverhaulLevel
    mileage_interval: Optional[float] = None
    time_interval: Optional[int] = None
    whichever_first: bool = True
    standard_duration_days: Optional[int] = None
    standard_cost_min: Optional[float] = None
    standard_cost_max: Optional[float] = None
    technical_requirements: Optional[str] = None
    quality_standards: Optional[str] = None
    acceptance_criteria: Optional[str] = None


class OverhaulStandardCreate(OverhaulStandardBase):
    """创建大修标准"""
    required_items: Optional[List[str]] = None
    optional_items: Optional[List[str]] = None
    applicable_from: Optional[date] = None
    applicable_to: Optional[date] = None


class OverhaulStandardResponse(OverhaulStandardBase):
    """大修标准响应"""
    id: UUID
    required_items: Optional[List[str]] = None
    optional_items: Optional[List[str]] = None
    applicable_from: Optional[date] = None
    applicable_to: Optional[date] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# ===================== Query Schemas =====================
class OverhaulPlanQuery(BaseModel):
    """大修计划查询参数"""
    train_number: Optional[str] = None
    status: Optional[OverhaulStatus] = None
    overhaul_type: Optional[OverhaulType] = None
    overhaul_level: Optional[OverhaulLevel] = None
    contractor: Optional[str] = None
    workshop: Optional[str] = None
    start_date_from: Optional[date] = None
    start_date_to: Optional[date] = None
    page: int = 1
    limit: int = 20


class OverhaulStatistics(BaseModel):
    """大修统计"""
    total_plans: int = 0
    planning: int = 0
    in_progress: int = 0
    completed: int = 0
    total_cost: float = 0
    average_duration: float = 0
    on_time_rate: float = 0
    cost_variance_rate: float = 0
    by_level: Dict[str, int] = {}
    by_type: Dict[str, int] = {}
    upcoming_plans: List[Dict[str, Any]] = []