"""
预测相关模型定义
"""
from sqlalchemy import Column, String, Integer, Float, Date, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from app.core.database import Base


class WearPrediction(Base):
    __tablename__ = "wear_predictions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vehicle_id = Column(UUID(as_uuid=True), ForeignKey("vehicles.id"), nullable=False)  # 关联车辆
    component_type = Column(String(50), nullable=False)  # 部件类型: wheelset, brake_pad, pantograph等
    component_position = Column(String(50), nullable=False)  # 部件位置
    current_wear = Column(Float, nullable=False)  # 当前磨耗值
    predicted_wear = Column(Float, nullable=False)  # 预测磨耗值
    wear_rate = Column(Float, nullable=False)  # 磨耗率 (mm per 10000km)
    remaining_life_days = Column(Integer, nullable=False)  # 剩余寿命(天)
    remaining_life_mileage = Column(Float, nullable=False)  # 剩余寿命(里程)
    replacement_date = Column(Date, nullable=False)  # 更换日期
    confidence_score = Column(Float, nullable=False)  # 置信度
    prediction_date = Column(DateTime(timezone=True), default=datetime.utcnow)  # 预测日期
    prediction_horizon_days = Column(Integer, default=180)  # 预测时间范围
    last_rewheeling_date = Column(Date)  # 上次镟修日期
    current_mileage = Column(Float)  # 当前里程
    next_rewheeling_mileage = Column(Float)  # 下次镟修里程
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class WearTrendData(Base):
    __tablename__ = "wear_trend_data"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vehicle_id = Column(UUID(as_uuid=True), ForeignKey("vehicles.id"), nullable=False)
    component_type = Column(String(50), nullable=False)
    date = Column(Date, nullable=False)  # 数据日期
    wear_value = Column(Float, nullable=False)  # 磨耗值
    mileage = Column(Float, nullable=False)  # 对应里程
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)


class PredictionResult(Base):
    __tablename__ = "prediction_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vehicle_id = Column(UUID(as_uuid=True), ForeignKey("vehicles.id"), nullable=False)
    risk_level = Column(String(20), default="low")  # high, medium, low
    overall_confidence = Column(Float, nullable=False)
    prediction_date = Column(DateTime(timezone=True), default=datetime.utcnow)
    total_predictions = Column(Integer, default=0)
    maintenance_priority = Column(String(20), default="low")  # high, medium, low
    next_maintenance_date = Column(Date)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class WheelsetStatistics(Base):
    __tablename__ = "wheelset_statistics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vehicle_id = Column(UUID(as_uuid=True), ForeignKey("vehicles.id"), nullable=False)
    wheelset_position = Column(String(20), nullable=False)  # 轮对位置，如1A, 1B, 2A等
    current_diameter = Column(Float, nullable=False)  # 当前直径(mm)
    flange_thickness = Column(Float)  # 轮缘厚度(mm)
    flange_height = Column(Float)  # 轮缘高度(mm)
    qr_value = Column(Float)  # QR值
    mileage_at_measurement = Column(Float)  # 测量时的里程
    last_rewheeling_date = Column(Date)  # 上次镟修日期
    next_rewheeling_mileage = Column(Float)  # 下次镟修计划里程
    wear_rate = Column(Float, default=0.0)  # 磨耗率
    status = Column(String(20), default="normal")  # normal, warning, critical
    inspection_date = Column(Date, nullable=False)  # 检查日期
    inspector = Column(String(100))  # 检查员
    notes = Column(Text)  # 备注
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)