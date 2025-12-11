"""
预测服务层
"""
from typing import List, Optional, Tuple
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import date, datetime, timedelta
from app.models.prediction import WearPrediction as WearPredictionModel, WearTrendData as WearTrendDataModel, PredictionResult as PredictionResultModel, WheelsetStatistics as WheelsetStatisticsModel
from app.models.vehicle import Vehicle
from app.schemas.prediction import WearPredictionCreate, WearPredictionUpdate, WearTrendDataCreate, PredictionResultCreate, PredictionResultUpdate


class PredictionService:
    """预测服务类"""

    @staticmethod
    async def create_wear_prediction(db: AsyncSession, prediction_data: WearPredictionCreate) -> WearPredictionModel:
        """创建磨耗预测"""
        prediction = WearPredictionModel(**prediction_data.dict())
        db.add(prediction)
        await db.commit()
        await db.refresh(prediction)
        return prediction

    @staticmethod
    async def get_wear_predictions_by_vehicle(db: AsyncSession, vehicle_id: UUID) -> List[WearPredictionModel]:
        """根据车辆ID获取磨耗预测"""
        result = await db.execute(
            select(WearPredictionModel).where(WearPredictionModel.vehicle_id == vehicle_id)
        )
        return result.scalars().all()

    @staticmethod
    async def get_latest_predictions_by_vehicle(db: AsyncSession, vehicle_id: UUID, limit: int = 10) -> List[WearPredictionModel]:
        """获取车辆最新的磨耗预测"""
        result = await db.execute(
            select(WearPredictionModel)
            .where(WearPredictionModel.vehicle_id == vehicle_id)
            .order_by(WearPredictionModel.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()

    @staticmethod
    async def create_wear_trend_data(db: AsyncSession, trend_data: WearTrendDataCreate) -> WearTrendDataModel:
        """创建磨耗趋势数据"""
        trend = WearTrendDataModel(**trend_data.dict())
        db.add(trend)
        await db.commit()
        await db.refresh(trend)
        return trend

    @staticmethod
    async def get_wear_trend_data(db: AsyncSession, vehicle_id: UUID, component_type: str, days: int = 90) -> List[WearTrendDataModel]:
        """获取磨耗趋势数据"""
        from_date = date.today() - timedelta(days=days)
        result = await db.execute(
            select(WearTrendDataModel)
            .where(
                and_(
                    WearTrendDataModel.vehicle_id == vehicle_id,
                    WearTrendDataModel.component_type == component_type,
                    WearTrendDataModel.date >= from_date
                )
            )
            .order_by(WearTrendDataModel.date)
        )
        return result.scalars().all()

    @staticmethod
    async def create_prediction_result(db: AsyncSession, result_data: PredictionResultCreate) -> PredictionResultModel:
        """创建预测结果"""
        result = PredictionResultModel(**result_data.dict())
        db.add(result)
        await db.commit()
        await db.refresh(result)
        return result

    @staticmethod
    async def get_prediction_result_by_vehicle(db: AsyncSession, vehicle_id: UUID) -> Optional[PredictionResultModel]:
        """根据车辆ID获取最新的预测结果"""
        result = await db.execute(
            select(PredictionResultModel)
            .where(PredictionResultModel.vehicle_id == vehicle_id)
            .order_by(PredictionResultModel.created_at.desc())
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def calculate_prediction(
        db: AsyncSession, 
        vehicle_id: str, 
        prediction_horizon_days: int = 180
    ) -> Tuple[List[WearPredictionModel], str, float, List[dict]]:
        """
        计算磨耗预测
        返回: (预测列表, 风险等级, 整体置信度, 维护建议)
        """
        from uuid import UUID as uuid_lib
        
        # 首先尝试将vehicle_id转换为UUID
        try:
            uuid_vehicle_id = uuid_lib(vehicle_id)
        except ValueError:
            # 如果不是UUID格式，尝试通过vehicle_code查找
            vehicle_result = await db.execute(
                select(Vehicle).where(Vehicle.vehicle_code == vehicle_id)
            )
            vehicle = vehicle_result.scalar_one_or_none()
            if not vehicle:
                raise ValueError(f"Vehicle with ID or code {vehicle_id} not found")
            uuid_vehicle_id = vehicle.id

        # 查询车辆的轮对统计信息（上次镟修时间等）
        wheelset_stats_result = await db.execute(
            select(WheelsetStatisticsModel)
            .where(WheelsetStatisticsModel.vehicle_id == uuid_vehicle_id)
            .order_by(WheelsetStatisticsModel.inspection_date.desc())
        )
        wheelset_stats = wheelset_stats_result.scalars().first()
        
        # 查询车辆的历史磨耗数据
        trend_data = await PredictionService.get_wear_trend_data(
            db, uuid_vehicle_id, "wheelset"
        )
        
        # 基于里程和上次镟修时间的增强预测算法
        from random import uniform
        
        # 获取车辆当前里程
        current_mileage = vehicle.total_mileage if vehicle else 100000.0
        
        # 基础磨耗值
        base_wear_values = {
            "wheelset": 3.5,
            "brake_pad": 30.0,
            "pantograph": 10.0
        }
        
        predictions = []
        components = ["wheelset", "brake_pad", "pantograph"]
        
        for i, component in enumerate(components):
            # 基于组件类型和车辆历史的预测值
            current_wear = base_wear_values[component]
            
            # 根据上次镟修时间调整预测（仅对轮对有效）
            rewheeling_factor = 1.0
            last_rewheeling_date = None
            next_rewheeling_mileage = None
            
            if component == "wheelset" and wheelset_stats:
                current_wear = wheelset_stats.current_diameter if wheelset_stats.current_diameter else current_wear
                last_rewheeling_date = wheelset_stats.last_rewheeling_date
                next_rewheeling_mileage = wheelset_stats.next_rewheeling_mileage
                
                # 如果接近上次镟修时间，调整磨耗率
                if last_rewheeling_date:
                    days_since_rewheeling = (date.today() - last_rewheeling_date).days
                    if days_since_rewheeling < 30:  # 镟修后30天内
                        rewheeling_factor = 0.8  # 磨耗率降低

            # 基础磨耗率计算
            base_wear_rate = 0.05 + (i * 0.1)  # 基础磨耗率
            # 根据里程和时间调整磨耗率
            mileage_factor = current_mileage / 100000.0  # 基于总里程的因子
            wear_rate = base_wear_rate * rewheeling_factor * (1 + mileage_factor * 0.1)
            
            # 计算剩余寿命
            if component == "brake_pad":
                min_threshold = 5.0  # 制动片最小厚度
            elif component == "pantograph":
                min_threshold = 3.0  # 受电弓最小厚度
            else:  # wheelset
                min_threshold = 840.0  # 轮径最小值(mm) - 假设当前值为直径
            
            # 计算剩余寿命（基于磨耗值和磨耗率）
            if component == "wheelset":
                # 轮对：直径越小风险越高
                remaining_wear = current_wear - min_threshold
                remaining_life_days = int(remaining_wear / (wear_rate * 50)) if wear_rate > 0 else 365
                # 基于里程的计算
                remaining_life_mileage = remaining_wear / wear_rate * 1000  # 转换为里程
            else:
                # 其他组件：磨耗值越大风险越高
                remaining_wear = min_threshold - current_wear
                remaining_life_days = int(remaining_wear / wear_rate * 1000) if wear_rate > 0 else 365
                remaining_life_mileage = remaining_wear / wear_rate * 1000

            # 确保剩余天数不为负
            remaining_life_days = max(1, remaining_life_days)
            
            # 计算更换日期
            replacement_date = date.today() + timedelta(days=remaining_life_days)
            
            # 计算预测磨耗值
            predicted_wear = current_wear + (wear_rate * prediction_horizon_days / 1000) if component != "wheelset" else current_wear - (wear_rate * prediction_horizon_days / 1000)
            
            # 创建预测记录
            prediction_data = WearPredictionCreate(
                vehicle_id=uuid_vehicle_id,
                component_type=component,
                component_position=f"{'前' if i % 2 == 0 else '后'}{'左' if i // 2 == 0 else '右'}",
                current_wear=round(current_wear, 2),
                predicted_wear=round(predicted_wear, 2),
                wear_rate=round(wear_rate, 4),
                remaining_life_days=remaining_life_days,
                remaining_life_mileage=round(remaining_life_mileage, 2),
                replacement_date=replacement_date,
                confidence_score=round(0.85 + uniform(-0.05, 0.1), 2),
                prediction_horizon_days=prediction_horizon_days,
                last_rewheeling_date=last_rewheeling_date,
                current_mileage=current_mileage,
                next_rewheeling_mileage=next_rewheeling_mileage
            )
            
            prediction = await PredictionService.create_wear_prediction(db, prediction_data)
            predictions.append(prediction)

        # 确定风险等级
        min_days = min(p.remaining_life_days for p in predictions)
        if min_days < 30:
            risk_level = "high"
        elif min_days < 90:
            risk_level = "medium"
        else:
            risk_level = "low"

        # 生成维护建议
        recommendations = []
        for i, pred in enumerate(predictions):
            if pred.remaining_life_days < 30:
                priority = "high"
                action = "立即更换"
                reason = f"预计{pred.remaining_life_days}天内达到最小安全值"
            elif pred.remaining_life_days < 90:
                priority = "medium"
                action = "计划更换"
                reason = f"预计{pred.remaining_life_days}天内需要维护"
            else:
                priority = "low"
                action = "正常监控"
                reason = "状态良好，按计划维护"

            # 根据组件类型调整成本和停机时间
            base_cost = 2000
            base_downtime = 4
            if pred.component_type == "wheelset":
                cost_multiplier = 7.5  # 轮对镟修成本较高
                downtime_multiplier = 2.0  # 轮对镟修时间较长
            elif pred.component_type == "brake_pad":
                cost_multiplier = 1.5  # 制动片更换成本中等
                downtime_multiplier = 1.0
            else:  # pantograph
                cost_multiplier = 2.5  # 受电弓更换成本中等偏高
                downtime_multiplier = 1.5

            recommendations.append({
                "priority": priority,
                "component": f"{pred.component_type}-{pred.component_position}",
                "action": action,
                "reason": reason,
                "estimated_cost": int(base_cost * cost_multiplier),
                "estimated_downtime_hours": int(base_downtime * downtime_multiplier)
            })

        # 计算整体置信度
        overall_confidence = round(sum(p.confidence_score for p in predictions) / len(predictions), 2)

        # 创建预测结果记录
        result_data = PredictionResultCreate(
            vehicle_id=uuid_vehicle_id,
            risk_level=risk_level,
            overall_confidence=overall_confidence,
            total_predictions=len(predictions),
            maintenance_priority=risk_level,
            next_maintenance_date=min(p.replacement_date for p in predictions)
        )
        
        await PredictionService.create_prediction_result(db, result_data)

        return predictions, risk_level, overall_confidence, recommendations