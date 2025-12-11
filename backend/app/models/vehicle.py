"""
车辆模型定义
"""
from sqlalchemy import Column, String, Integer, Float, Date, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from app.core.database import Base


class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vehicle_code = Column(String(50), unique=True, nullable=False, index=True)
    model = Column(String(100), nullable=False)
    line_number = Column(String(20), nullable=False)
    manufacture_date = Column(Date, nullable=False)
    commissioning_date = Column(Date, nullable=False)
    total_mileage = Column(Float, default=0.0)
    status = Column(String(20), default="active")  # active, maintenance, retired
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    # 新增字段
    current_wear_values = Column(Text)  # JSON格式存储各部件磨耗值
    last_inspection_date = Column(Date)
    next_maintenance_date = Column(Date)