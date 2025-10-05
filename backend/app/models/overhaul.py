"""
大修管理数据模型
Overhaul Management Data Models
"""
from sqlalchemy import Column, String, Float, Integer, Date, DateTime, Text, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid
import enum
from datetime import datetime


class OverhaulType(str, enum.Enum):
    """大修类型"""
    SCHEDULED = "scheduled"      # 计划大修
    EMERGENCY = "emergency"      # 紧急大修
    UPGRADE = "upgrade"          # 升级改造
    ACCIDENT = "accident"        # 事故维修


class OverhaulStatus(str, enum.Enum):
    """大修状态"""
    PLANNING = "planning"        # 规划中
    APPROVED = "approved"        # 已批准
    IN_PROGRESS = "in_progress"  # 进行中
    SUSPENDED = "suspended"      # 暂停
    COMPLETED = "completed"      # 已完成
    CANCELLED = "cancelled"      # 已取消


class OverhaulLevel(str, enum.Enum):
    """大修级别"""
    A1 = "A1"  # A1级大修 (架修)
    A2 = "A2"  # A2级大修 (大修)
    A3 = "A3"  # A3级大修 (中修)
    B1 = "B1"  # B1级检修
    B2 = "B2"  # B2级检修
    C1 = "C1"  # C1级检修
    C2 = "C2"  # C2级检修


class OverhaulPlan(Base):
    """大修计划模型"""
    __tablename__ = "overhaul_plans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plan_code = Column(String(50), unique=True, nullable=False, index=True)
    vehicle_id = Column(UUID(as_uuid=True), ForeignKey("vehicles.id", ondelete="CASCADE"))
    train_number = Column(String(20), nullable=False)

    overhaul_type = Column(SQLEnum(OverhaulType), nullable=False)
    overhaul_level = Column(SQLEnum(OverhaulLevel), nullable=False)
    status = Column(SQLEnum(OverhaulStatus), default=OverhaulStatus.PLANNING)

    # 时间计划
    planned_start_date = Column(Date, nullable=False)
    planned_end_date = Column(Date, nullable=False)
    actual_start_date = Column(Date)
    actual_end_date = Column(Date)

    # 里程基准
    mileage_at_overhaul = Column(Float)
    next_overhaul_mileage = Column(Float)

    # 成本预算
    estimated_cost = Column(Float)
    actual_cost = Column(Float)
    currency = Column(String(10), default="CNY")

    # 承包信息
    contractor = Column(String(200))
    workshop = Column(String(200))
    responsible_person = Column(String(100))
    contact_phone = Column(String(20))

    # 审批信息
    approval_status = Column(String(50))
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    approved_at = Column(DateTime)
    approval_notes = Column(Text)

    # 其他信息
    description = Column(Text)
    technical_requirements = Column(Text)
    safety_requirements = Column(Text)
    quality_standards = Column(Text)

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    # 关系
    vehicle = relationship("Vehicle", backref="overhaul_plans")
    items = relationship("OverhaulItem", back_populates="overhaul_plan", cascade="all, delete-orphan")
    spare_parts = relationship("OverhaulSparePart", back_populates="overhaul_plan", cascade="all, delete-orphan")
    approver = relationship("User", foreign_keys=[approved_by])
    creator = relationship("User", foreign_keys=[created_by])
    updater = relationship("User", foreign_keys=[updated_by])


class OverhaulItem(Base):
    """大修项目模型"""
    __tablename__ = "overhaul_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    overhaul_plan_id = Column(UUID(as_uuid=True), ForeignKey("overhaul_plans.id", ondelete="CASCADE"))
    item_code = Column(String(50), nullable=False)
    item_name = Column(String(200), nullable=False)
    category = Column(String(100))

    # 车厢信息
    carriage_number = Column(String(50))
    component_type = Column(String(100))

    # 作业内容
    work_content = Column(Text)
    technical_standard = Column(Text)
    inspection_method = Column(String(200))

    # 进度跟踪
    status = Column(String(50), default="pending")
    progress_percentage = Column(Integer, default=0)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)

    # 质量控制
    quality_check_status = Column(String(50))
    quality_inspector = Column(String(100))
    quality_check_date = Column(Date)
    quality_notes = Column(Text)

    # 成本信息
    labor_hours = Column(Float)
    material_cost = Column(Float)
    labor_cost = Column(Float)
    total_cost = Column(Float)

    # 备件信息
    spare_parts_used = Column(JSON)
    old_parts_disposal = Column(String(200))

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    overhaul_plan = relationship("OverhaulPlan", back_populates="items")


class OverhaulSparePart(Base):
    """大修备件模型"""
    __tablename__ = "overhaul_spare_parts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    overhaul_plan_id = Column(UUID(as_uuid=True), ForeignKey("overhaul_plans.id", ondelete="CASCADE"))
    part_number = Column(String(100), nullable=False)
    part_name = Column(String(200), nullable=False)
    category = Column(String(100))
    manufacturer = Column(String(200))

    # 数量信息
    planned_quantity = Column(Integer, nullable=False)
    actual_quantity = Column(Integer)
    unit = Column(String(20))

    # 成本信息
    unit_price = Column(Float)
    total_price = Column(Float)

    # 库存信息
    stock_quantity = Column(Integer)
    warehouse_location = Column(String(100))

    # 采购信息
    purchase_order_no = Column(String(100))
    supplier = Column(String(200))
    delivery_date = Column(Date)

    # 质量信息
    quality_certificate = Column(String(200))
    warranty_period = Column(Integer)

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    overhaul_plan = relationship("OverhaulPlan", back_populates="spare_parts")


class OverhaulRecord(Base):
    """大修记录模型"""
    __tablename__ = "overhaul_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    overhaul_plan_id = Column(UUID(as_uuid=True), ForeignKey("overhaul_plans.id"))
    vehicle_id = Column(UUID(as_uuid=True), ForeignKey("vehicles.id"))
    train_number = Column(String(20), nullable=False)
    overhaul_level = Column(SQLEnum(OverhaulLevel), nullable=False)

    # 执行信息
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    duration_days = Column(Integer)

    # 里程信息
    mileage_before = Column(Float)
    mileage_after = Column(Float)
    mileage_interval = Column(Float)

    # 成本信息
    total_cost = Column(Float)
    labor_cost = Column(Float)
    material_cost = Column(Float)
    spare_parts_cost = Column(Float)

    # 质量评估
    quality_score = Column(Integer)
    performance_improvement = Column(Text)

    # 问题记录
    problems_found = Column(Text)
    solutions_applied = Column(Text)

    # 文档附件
    report_url = Column(String(500))
    photos = Column(JSON)
    documents = Column(JSON)

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    # 关系
    vehicle = relationship("Vehicle", backref="overhaul_records")
    plan = relationship("OverhaulPlan")
    creator = relationship("User")


class OverhaulStandard(Base):
    """大修标准模型"""
    __tablename__ = "overhaul_standards"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vehicle_type = Column(String(50), nullable=False)
    overhaul_level = Column(SQLEnum(OverhaulLevel), nullable=False)

    # 周期标准
    mileage_interval = Column(Float)
    time_interval = Column(Integer)
    whichever_first = Column(String(5), default="true")

    # 作业标准
    standard_duration_days = Column(Integer)
    required_items = Column(JSON)
    optional_items = Column(JSON)

    # 成本标准
    standard_cost_min = Column(Float)
    standard_cost_max = Column(Float)

    # 技术标准
    technical_requirements = Column(Text)
    quality_standards = Column(Text)
    acceptance_criteria = Column(Text)

    # 适用范围
    applicable_from = Column(Date)
    applicable_to = Column(Date)

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)