"""
预测相关的Pydantic模型
"""
from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime
from uuid import UUID


class WearPredictionBase(BaseModel):
    vehicle_id: UUID
    component_type: str
    component_position: str
    current_wear: float
    predicted_wear: float
    wear_rate: float  # mm per 10000km
    remaining_life_days: int
    remaining_life_mileage: float
    replacement_date: date
    confidence_score: float
    prediction_horizon_days: Optional[int] = 180


class WearPredictionCreate(WearPredictionBase):
    pass


class WearPredictionUpdate(BaseModel):
    current_wear: Optional[float] = None
    predicted_wear: Optional[float] = None
    wear_rate: Optional[float] = None
    remaining_life_days: Optional[int] = None
    remaining_life_mileage: Optional[float] = None
    replacement_date: Optional[date] = None
    confidence_score: Optional[float] = None


class WearPrediction(WearPredictionBase):
    id: UUID
    prediction_date: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class PredictionRequest(BaseModel):
    vehicle_id: str
    prediction_horizon_days: int = 180


class PredictionResponse(BaseModel):
    vehicle_id: str
    prediction_date: datetime
    risk_level: str
    overall_confidence: float
    predictions: List[WearPrediction]
    maintenance_recommendations: List[dict]


class BatchPredictionRequest(BaseModel):
    vehicle_ids: List[str]
    prediction_horizon_days: int = 180


class WearTrendDataBase(BaseModel):
    vehicle_id: UUID
    component_type: str
    date: date
    wear_value: float
    mileage: float


class WearTrendDataCreate(WearTrendDataBase):
    pass


class WearTrendData(WearTrendDataBase):
    id: UUID
    
    class Config:
        from_attributes = True


class PredictionResultBase(BaseModel):
    vehicle_id: UUID
    risk_level: str
    overall_confidence: float
    total_predictions: int
    maintenance_priority: str
    next_maintenance_date: Optional[date] = None


class PredictionResultCreate(PredictionResultBase):
    pass


class PredictionResultUpdate(BaseModel):
    risk_level: Optional[str] = None
    overall_confidence: Optional[float] = None
    total_predictions: Optional[int] = None
    maintenance_priority: Optional[str] = None
    next_maintenance_date: Optional[date] = None


class PredictionResult(PredictionResultBase):
    id: UUID
    prediction_date: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class WheelsetStatisticsBase(BaseModel):
    vehicle_id: UUID
    wheelset_position: str
    current_diameter: float
    flange_thickness: Optional[float] = None
    flange_height: Optional[float] = None
    qr_value: Optional[float] = None
    mileage_at_measurement: Optional[float] = None
    last_rewheeling_date: Optional[date] = None
    next_rewheeling_mileage: Optional[float] = None
    wear_rate: Optional[float] = 0.0
    status: Optional[str] = "normal"
    inspection_date: date
    inspector: Optional[str] = None
    notes: Optional[str] = None


class WheelsetStatisticsCreate(WheelsetStatisticsBase):
    pass


class WheelsetStatisticsUpdate(BaseModel):
    current_diameter: Optional[float] = None
    flange_thickness: Optional[float] = None
    flange_height: Optional[float] = None
    qr_value: Optional[float] = None
    mileage_at_measurement: Optional[float] = None
    last_rewheeling_date: Optional[date] = None
    next_rewheeling_mileage: Optional[float] = None
    wear_rate: Optional[float] = None
    status: Optional[str] = None
    inspection_date: Optional[date] = None
    inspector: Optional[str] = None
    notes: Optional[str] = None


class WheelsetStatistics(WheelsetStatisticsBase):
    id: UUID
    
    class Config:
        from_attributes = True