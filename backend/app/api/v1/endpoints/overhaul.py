"""
大修管理API端点
Overhaul Management API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import List, Optional
from uuid import UUID
from datetime import date, datetime

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.overhaul import (
    OverhaulPlan, OverhaulItem, OverhaulSparePart,
    OverhaulRecord, OverhaulStandard
)
from app.schemas.overhaul import (
    OverhaulPlanCreate, OverhaulPlanUpdate, OverhaulPlanResponse,
    OverhaulItemCreate, OverhaulItemUpdate, OverhaulItemResponse,
    SparePartCreate, SparePartUpdate, SparePartResponse,
    OverhaulRecordCreate, OverhaulRecordResponse,
    OverhaulStandardCreate, OverhaulStandardResponse,
    OverhaulPlanQuery, OverhaulStatistics,
    OverhaulStatus, OverhaulType, OverhaulLevel
)

router = APIRouter(prefix="/api/v1/overhaul", tags=["overhaul"])


# ===================== Overhaul Plans =====================

@router.post("/plans", response_model=OverhaulPlanResponse)
async def create_overhaul_plan(
    plan: OverhaulPlanCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建大修计划"""
    # 检查计划编号是否已存在
    existing = await db.execute(
        select(OverhaulPlan).where(OverhaulPlan.plan_code == plan.plan_code)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Plan code {plan.plan_code} already exists"
        )

    # 创建大修计划
    db_plan = OverhaulPlan(
        **plan.dict(exclude={"items", "spare_parts"}),
        created_by=current_user.id,
        updated_by=current_user.id
    )
    db.add(db_plan)
    await db.flush()

    # 添加大修项目
    for item_data in plan.items or []:
        db_item = OverhaulItem(
            overhaul_plan_id=db_plan.id,
            **item_data.dict()
        )
        db.add(db_item)

    # 添加备件
    for part_data in plan.spare_parts or []:
        db_part = OverhaulSparePart(
            overhaul_plan_id=db_plan.id,
            **part_data.dict(),
            total_price=(part_data.planned_quantity * part_data.unit_price) if part_data.unit_price else None
        )
        db.add(db_part)

    await db.commit()
    await db.refresh(db_plan)

    # 加载关联数据
    result = await db.execute(
        select(OverhaulPlan)
        .options(
            selectinload(OverhaulPlan.items),
            selectinload(OverhaulPlan.spare_parts)
        )
        .where(OverhaulPlan.id == db_plan.id)
    )
    db_plan = result.scalar_one()

    response = OverhaulPlanResponse.from_orm(db_plan)
    response.calculate_fields()
    return response


@router.get("/plans", response_model=List[OverhaulPlanResponse])
async def get_overhaul_plans(
    query: OverhaulPlanQuery = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取大修计划列表"""
    stmt = select(OverhaulPlan).options(
        selectinload(OverhaulPlan.items),
        selectinload(OverhaulPlan.spare_parts)
    )

    # 应用过滤条件
    filters = []
    if query.train_number:
        filters.append(OverhaulPlan.train_number == query.train_number)
    if query.status:
        filters.append(OverhaulPlan.status == query.status)
    if query.overhaul_type:
        filters.append(OverhaulPlan.overhaul_type == query.overhaul_type)
    if query.overhaul_level:
        filters.append(OverhaulPlan.overhaul_level == query.overhaul_level)
    if query.contractor:
        filters.append(OverhaulPlan.contractor.ilike(f"%{query.contractor}%"))
    if query.workshop:
        filters.append(OverhaulPlan.workshop.ilike(f"%{query.workshop}%"))
    if query.start_date_from:
        filters.append(OverhaulPlan.planned_start_date >= query.start_date_from)
    if query.start_date_to:
        filters.append(OverhaulPlan.planned_start_date <= query.start_date_to)

    if filters:
        stmt = stmt.where(and_(*filters))

    # 分页
    stmt = stmt.offset((query.page - 1) * query.limit).limit(query.limit)
    stmt = stmt.order_by(OverhaulPlan.planned_start_date.desc())

    result = await db.execute(stmt)
    plans = result.scalars().all()

    responses = []
    for plan in plans:
        response = OverhaulPlanResponse.from_orm(plan)
        response.calculate_fields()
        responses.append(response)

    return responses


@router.get("/plans/{plan_id}", response_model=OverhaulPlanResponse)
async def get_overhaul_plan(
    plan_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取大修计划详情"""
    result = await db.execute(
        select(OverhaulPlan)
        .options(
            selectinload(OverhaulPlan.items),
            selectinload(OverhaulPlan.spare_parts)
        )
        .where(OverhaulPlan.id == plan_id)
    )
    plan = result.scalar_one_or_none()

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Overhaul plan not found"
        )

    response = OverhaulPlanResponse.from_orm(plan)
    response.calculate_fields()
    return response


@router.put("/plans/{plan_id}", response_model=OverhaulPlanResponse)
async def update_overhaul_plan(
    plan_id: UUID,
    update_data: OverhaulPlanUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新大修计划"""
    result = await db.execute(
        select(OverhaulPlan).where(OverhaulPlan.id == plan_id)
    )
    plan = result.scalar_one_or_none()

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Overhaul plan not found"
        )

    # 更新字段
    update_dict = update_data.dict(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(plan, field, value)

    # 处理审批
    if update_data.status == OverhaulStatus.APPROVED and plan.approval_status != "approved":
        plan.approved_by = current_user.id
        plan.approved_at = datetime.utcnow()
        plan.approval_status = "approved"

    plan.updated_by = current_user.id
    plan.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(plan)

    # 重新加载关联数据
    result = await db.execute(
        select(OverhaulPlan)
        .options(
            selectinload(OverhaulPlan.items),
            selectinload(OverhaulPlan.spare_parts)
        )
        .where(OverhaulPlan.id == plan_id)
    )
    plan = result.scalar_one()

    response = OverhaulPlanResponse.from_orm(plan)
    response.calculate_fields()
    return response


@router.delete("/plans/{plan_id}")
async def delete_overhaul_plan(
    plan_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除大修计划"""
    result = await db.execute(
        select(OverhaulPlan).where(OverhaulPlan.id == plan_id)
    )
    plan = result.scalar_one_or_none()

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Overhaul plan not found"
        )

    # 检查是否可以删除
    if plan.status not in [OverhaulStatus.PLANNING, OverhaulStatus.CANCELLED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete plan in current status"
        )

    await db.delete(plan)
    await db.commit()

    return {"message": "Overhaul plan deleted successfully"}


# ===================== Overhaul Items =====================

@router.post("/plans/{plan_id}/items", response_model=OverhaulItemResponse)
async def add_overhaul_item(
    plan_id: UUID,
    item: OverhaulItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """添加大修项目"""
    # 检查计划是否存在
    result = await db.execute(
        select(OverhaulPlan).where(OverhaulPlan.id == plan_id)
    )
    plan = result.scalar_one_or_none()

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Overhaul plan not found"
        )

    db_item = OverhaulItem(
        overhaul_plan_id=plan_id,
        **item.dict()
    )
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)

    return OverhaulItemResponse.from_orm(db_item)


@router.put("/items/{item_id}", response_model=OverhaulItemResponse)
async def update_overhaul_item(
    item_id: UUID,
    update_data: OverhaulItemUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新大修项目"""
    result = await db.execute(
        select(OverhaulItem).where(OverhaulItem.id == item_id)
    )
    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Overhaul item not found"
        )

    # 更新字段
    update_dict = update_data.dict(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(item, field, value)

    # 更新时间戳
    if update_data.status == "in_progress" and not item.started_at:
        item.started_at = datetime.utcnow()
    elif update_data.status == "completed" and not item.completed_at:
        item.completed_at = datetime.utcnow()
        item.progress_percentage = 100

    item.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(item)

    return OverhaulItemResponse.from_orm(item)


# ===================== Spare Parts =====================

@router.post("/plans/{plan_id}/spare-parts", response_model=SparePartResponse)
async def add_spare_part(
    plan_id: UUID,
    part: SparePartCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """添加备件"""
    # 检查计划是否存在
    result = await db.execute(
        select(OverhaulPlan).where(OverhaulPlan.id == plan_id)
    )
    plan = result.scalar_one_or_none()

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Overhaul plan not found"
        )

    db_part = OverhaulSparePart(
        overhaul_plan_id=plan_id,
        **part.dict(),
        total_price=(part.planned_quantity * part.unit_price) if part.unit_price else None
    )
    db.add(db_part)
    await db.commit()
    await db.refresh(db_part)

    return SparePartResponse.from_orm(db_part)


@router.put("/spare-parts/{part_id}", response_model=SparePartResponse)
async def update_spare_part(
    part_id: UUID,
    update_data: SparePartUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新备件"""
    result = await db.execute(
        select(OverhaulSparePart).where(OverhaulSparePart.id == part_id)
    )
    part = result.scalar_one_or_none()

    if not part:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Spare part not found"
        )

    # 更新字段
    update_dict = update_data.dict(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(part, field, value)

    part.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(part)

    return SparePartResponse.from_orm(part)


# ===================== Overhaul Records =====================

@router.post("/records", response_model=OverhaulRecordResponse)
async def create_overhaul_record(
    record: OverhaulRecordCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建大修记录"""
    # 计算派生字段
    duration_days = (record.end_date - record.start_date).days
    mileage_interval = None
    if record.mileage_before and record.mileage_after:
        mileage_interval = record.mileage_after - record.mileage_before

    db_record = OverhaulRecord(
        **record.dict(),
        duration_days=duration_days,
        mileage_interval=mileage_interval,
        created_by=current_user.id
    )
    db.add(db_record)

    # 如果关联计划，更新计划状态
    if record.overhaul_plan_id:
        result = await db.execute(
            select(OverhaulPlan).where(OverhaulPlan.id == record.overhaul_plan_id)
        )
        plan = result.scalar_one_or_none()
        if plan:
            plan.status = OverhaulStatus.COMPLETED
            plan.actual_end_date = record.end_date

    await db.commit()
    await db.refresh(db_record)

    return OverhaulRecordResponse.from_orm(db_record)


@router.get("/records", response_model=List[OverhaulRecordResponse])
async def get_overhaul_records(
    train_number: Optional[str] = None,
    vehicle_id: Optional[UUID] = None,
    level: Optional[OverhaulLevel] = None,
    start_date_from: Optional[date] = None,
    start_date_to: Optional[date] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取大修记录列表"""
    stmt = select(OverhaulRecord)

    # 应用过滤条件
    filters = []
    if train_number:
        filters.append(OverhaulRecord.train_number == train_number)
    if vehicle_id:
        filters.append(OverhaulRecord.vehicle_id == vehicle_id)
    if level:
        filters.append(OverhaulRecord.overhaul_level == level)
    if start_date_from:
        filters.append(OverhaulRecord.start_date >= start_date_from)
    if start_date_to:
        filters.append(OverhaulRecord.start_date <= start_date_to)

    if filters:
        stmt = stmt.where(and_(*filters))

    # 分页和排序
    stmt = stmt.offset((page - 1) * limit).limit(limit)
    stmt = stmt.order_by(OverhaulRecord.end_date.desc())

    result = await db.execute(stmt)
    records = result.scalars().all()

    return [OverhaulRecordResponse.from_orm(record) for record in records]


# ===================== Overhaul Standards =====================

@router.get("/standards", response_model=List[OverhaulStandardResponse])
async def get_overhaul_standards(
    vehicle_type: Optional[str] = None,
    level: Optional[OverhaulLevel] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取大修标准"""
    stmt = select(OverhaulStandard)

    filters = []
    if vehicle_type:
        filters.append(OverhaulStandard.vehicle_type == vehicle_type)
    if level:
        filters.append(OverhaulStandard.overhaul_level == level)

    # 只返回当前有效的标准
    filters.append(or_(
        OverhaulStandard.applicable_to.is_(None),
        OverhaulStandard.applicable_to >= date.today()
    ))

    if filters:
        stmt = stmt.where(and_(*filters))

    stmt = stmt.order_by(OverhaulStandard.overhaul_level)

    result = await db.execute(stmt)
    standards = result.scalars().all()

    return [OverhaulStandardResponse.from_orm(standard) for standard in standards]


# ===================== Statistics =====================

@router.get("/statistics", response_model=OverhaulStatistics)
async def get_overhaul_statistics(
    year: Optional[int] = None,
    month: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取大修统计信息"""
    # 基础查询
    stmt = select(OverhaulPlan)

    # 时间过滤
    if year:
        start_date = date(year, month or 1, 1)
        if month:
            # 特定月份
            import calendar
            last_day = calendar.monthrange(year, month)[1]
            end_date = date(year, month, last_day)
        else:
            # 整年
            end_date = date(year, 12, 31)

        stmt = stmt.where(
            OverhaulPlan.planned_start_date >= start_date,
            OverhaulPlan.planned_start_date <= end_date
        )

    result = await db.execute(stmt)
    plans = result.scalars().all()

    # 计算统计数据
    stats = OverhaulStatistics()
    stats.total_plans = len(plans)

    for plan in plans:
        # 状态统计
        if plan.status == OverhaulStatus.PLANNING:
            stats.planning += 1
        elif plan.status == OverhaulStatus.IN_PROGRESS:
            stats.in_progress += 1
        elif plan.status == OverhaulStatus.COMPLETED:
            stats.completed += 1

        # 成本统计
        if plan.actual_cost:
            stats.total_cost += plan.actual_cost

        # 级别统计
        level = plan.overhaul_level.value
        stats.by_level[level] = stats.by_level.get(level, 0) + 1

        # 类型统计
        type_name = plan.overhaul_type.value
        stats.by_type[type_name] = stats.by_type.get(type_name, 0) + 1

    # 计算平均工期
    completed_plans = [p for p in plans if p.status == OverhaulStatus.COMPLETED]
    if completed_plans:
        total_duration = sum(
            (p.actual_end_date - p.actual_start_date).days
            for p in completed_plans
            if p.actual_start_date and p.actual_end_date
        )
        stats.average_duration = total_duration / len(completed_plans)

        # 计算准时率
        on_time = sum(
            1 for p in completed_plans
            if p.actual_end_date <= p.planned_end_date
        )
        stats.on_time_rate = (on_time / len(completed_plans)) * 100

        # 计算成本偏差率
        with_cost = [p for p in completed_plans if p.estimated_cost and p.actual_cost]
        if with_cost:
            total_variance = sum(
                (p.actual_cost - p.estimated_cost) / p.estimated_cost * 100
                for p in with_cost
            )
            stats.cost_variance_rate = total_variance / len(with_cost)

    # 获取即将到来的计划
    upcoming_stmt = select(OverhaulPlan).where(
        OverhaulPlan.status == OverhaulStatus.PLANNING,
        OverhaulPlan.planned_start_date >= date.today()
    ).order_by(OverhaulPlan.planned_start_date).limit(5)

    upcoming_result = await db.execute(upcoming_stmt)
    upcoming_plans = upcoming_result.scalars().all()

    stats.upcoming_plans = [
        {
            "id": str(p.id),
            "plan_code": p.plan_code,
            "train_number": p.train_number,
            "overhaul_level": p.overhaul_level.value,
            "planned_start_date": p.planned_start_date.isoformat(),
            "planned_end_date": p.planned_end_date.isoformat()
        }
        for p in upcoming_plans
    ]

    return stats


# 添加必要的导入到文件顶部
from sqlalchemy.orm import selectinload