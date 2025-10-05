-- =====================================================
-- 大修管理系统数据库迁移脚本
-- Overhaul Management System Database Migration
-- Version: 2.0
-- Date: 2024-01-26
-- =====================================================

-- 大修类型枚举
CREATE TYPE overhaul_type AS ENUM (
    'scheduled',    -- 计划大修
    'emergency',    -- 紧急大修
    'upgrade',      -- 升级改造
    'accident'      -- 事故维修
);

-- 大修状态枚举
CREATE TYPE overhaul_status AS ENUM (
    'planning',     -- 规划中
    'approved',     -- 已批准
    'in_progress',  -- 进行中
    'suspended',    -- 暂停
    'completed',    -- 已完成
    'cancelled'     -- 已取消
);

-- 大修级别枚举
CREATE TYPE overhaul_level AS ENUM (
    'A1',  -- A1级大修 (架修)
    'A2',  -- A2级大修 (大修)
    'A3',  -- A3级大修 (中修)
    'B1',  -- B1级检修
    'B2',  -- B2级检修
    'C1',  -- C1级检修
    'C2'   -- C2级检修
);

-- =====================================================
-- 大修计划表
-- =====================================================
CREATE TABLE IF NOT EXISTS overhaul_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_code VARCHAR(50) UNIQUE NOT NULL,  -- 大修计划编号
    vehicle_id UUID REFERENCES vehicles(id) ON DELETE CASCADE,
    train_number VARCHAR(20) NOT NULL,      -- 列车编号 (Tr01-Tr16)
    overhaul_type overhaul_type NOT NULL,
    overhaul_level overhaul_level NOT NULL,
    status overhaul_status DEFAULT 'planning',

    -- 时间计划
    planned_start_date DATE NOT NULL,
    planned_end_date DATE NOT NULL,
    actual_start_date DATE,
    actual_end_date DATE,

    -- 里程基准
    mileage_at_overhaul DECIMAL(12,2),     -- 大修时里程
    next_overhaul_mileage DECIMAL(12,2),   -- 下次大修里程

    -- 成本预算
    estimated_cost DECIMAL(12,2),          -- 预估成本
    actual_cost DECIMAL(12,2),             -- 实际成本
    currency VARCHAR(10) DEFAULT 'CNY',

    -- 承包信息
    contractor VARCHAR(200),               -- 承包商
    workshop VARCHAR(200),                 -- 检修车间
    responsible_person VARCHAR(100),       -- 负责人
    contact_phone VARCHAR(20),

    -- 审批信息
    approval_status VARCHAR(50),
    approved_by UUID REFERENCES users(id),
    approved_at TIMESTAMP,
    approval_notes TEXT,

    -- 其他信息
    description TEXT,
    technical_requirements TEXT,
    safety_requirements TEXT,
    quality_standards TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id),

    CONSTRAINT check_dates CHECK (planned_end_date > planned_start_date),
    CONSTRAINT check_mileage CHECK (next_overhaul_mileage > mileage_at_overhaul)
);

-- =====================================================
-- 大修项目表 (大修包含的具体维修项目)
-- =====================================================
CREATE TABLE IF NOT EXISTS overhaul_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    overhaul_plan_id UUID REFERENCES overhaul_plans(id) ON DELETE CASCADE,
    item_code VARCHAR(50) NOT NULL,        -- 项目编号
    item_name VARCHAR(200) NOT NULL,       -- 项目名称
    category VARCHAR(100),                 -- 项目类别

    -- 车厢信息
    carriage_number VARCHAR(50),           -- 车厢编号 (如: SL0101)
    component_type VARCHAR(100),           -- 部件类型

    -- 作业内容
    work_content TEXT,                     -- 作业内容
    technical_standard TEXT,               -- 技术标准
    inspection_method VARCHAR(200),        -- 检测方法

    -- 进度跟踪
    status VARCHAR(50) DEFAULT 'pending',  -- pending/in_progress/completed/skipped
    progress_percentage INTEGER DEFAULT 0,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,

    -- 质量控制
    quality_check_status VARCHAR(50),      -- 质检状态
    quality_inspector VARCHAR(100),        -- 质检员
    quality_check_date DATE,
    quality_notes TEXT,

    -- 成本信息
    labor_hours DECIMAL(8,2),             -- 工时
    material_cost DECIMAL(10,2),          -- 材料成本
    labor_cost DECIMAL(10,2),             -- 人工成本
    total_cost DECIMAL(10,2),             -- 总成本

    -- 备件信息
    spare_parts_used JSONB,               -- 使用的备件列表
    old_parts_disposal VARCHAR(200),      -- 旧件处理方式

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- 大修备件表
-- =====================================================
CREATE TABLE IF NOT EXISTS overhaul_spare_parts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    overhaul_plan_id UUID REFERENCES overhaul_plans(id) ON DELETE CASCADE,
    part_number VARCHAR(100) NOT NULL,     -- 备件号
    part_name VARCHAR(200) NOT NULL,       -- 备件名称
    category VARCHAR(100),                 -- 备件类别
    manufacturer VARCHAR(200),             -- 制造商

    -- 数量信息
    planned_quantity INTEGER NOT NULL,     -- 计划数量
    actual_quantity INTEGER,               -- 实际使用数量
    unit VARCHAR(20),                      -- 单位

    -- 成本信息
    unit_price DECIMAL(10,2),             -- 单价
    total_price DECIMAL(12,2),            -- 总价

    -- 库存信息
    stock_quantity INTEGER,                -- 库存数量
    warehouse_location VARCHAR(100),       -- 仓库位置

    -- 采购信息
    purchase_order_no VARCHAR(100),        -- 采购订单号
    supplier VARCHAR(200),                 -- 供应商
    delivery_date DATE,                    -- 交货日期

    -- 质量信息
    quality_certificate VARCHAR(200),      -- 质量证书
    warranty_period INTEGER,                -- 保修期(月)

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- 大修记录表 (历史记录)
-- =====================================================
CREATE TABLE IF NOT EXISTS overhaul_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    overhaul_plan_id UUID REFERENCES overhaul_plans(id),
    vehicle_id UUID REFERENCES vehicles(id),
    train_number VARCHAR(20) NOT NULL,
    overhaul_level overhaul_level NOT NULL,

    -- 执行信息
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    duration_days INTEGER,

    -- 里程信息
    mileage_before DECIMAL(12,2),         -- 大修前里程
    mileage_after DECIMAL(12,2),          -- 大修后里程
    mileage_interval DECIMAL(12,2),       -- 距上次大修里程

    -- 成本信息
    total_cost DECIMAL(12,2),
    labor_cost DECIMAL(10,2),
    material_cost DECIMAL(10,2),
    spare_parts_cost DECIMAL(10,2),

    -- 质量评估
    quality_score INTEGER,                 -- 质量评分 (0-100)
    performance_improvement TEXT,          -- 性能改善情况

    -- 问题记录
    problems_found TEXT,                   -- 发现的问题
    solutions_applied TEXT,                -- 采取的措施

    -- 文档附件
    report_url VARCHAR(500),              -- 大修报告URL
    photos JSONB,                          -- 照片列表
    documents JSONB,                       -- 文档列表

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id)
);

-- =====================================================
-- 大修标准表
-- =====================================================
CREATE TABLE IF NOT EXISTS overhaul_standards (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vehicle_type VARCHAR(50) NOT NULL,     -- 车辆类型
    overhaul_level overhaul_level NOT NULL,

    -- 周期标准
    mileage_interval DECIMAL(10,2),       -- 里程周期 (km)
    time_interval INTEGER,                 -- 时间周期 (月)
    whichever_first BOOLEAN DEFAULT true, -- 以先到为准

    -- 作业标准
    standard_duration_days INTEGER,        -- 标准工期
    required_items JSONB,                  -- 必修项目列表
    optional_items JSONB,                  -- 选修项目列表

    -- 成本标准
    standard_cost_min DECIMAL(10,2),      -- 标准成本下限
    standard_cost_max DECIMAL(10,2),      -- 标准成本上限

    -- 技术标准
    technical_requirements TEXT,
    quality_standards TEXT,
    acceptance_criteria TEXT,              -- 验收标准

    -- 适用范围
    applicable_from DATE,                  -- 生效日期
    applicable_to DATE,                    -- 失效日期

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- 创建索引
-- =====================================================
CREATE INDEX idx_overhaul_plans_vehicle ON overhaul_plans(vehicle_id);
CREATE INDEX idx_overhaul_plans_status ON overhaul_plans(status);
CREATE INDEX idx_overhaul_plans_dates ON overhaul_plans(planned_start_date, planned_end_date);
CREATE INDEX idx_overhaul_items_plan ON overhaul_items(overhaul_plan_id);
CREATE INDEX idx_overhaul_records_vehicle ON overhaul_records(vehicle_id);
CREATE INDEX idx_overhaul_records_dates ON overhaul_records(start_date, end_date);

-- =====================================================
-- 创建触发器更新时间戳
-- =====================================================
CREATE TRIGGER update_overhaul_plans_updated_at
    BEFORE UPDATE ON overhaul_plans
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_overhaul_items_updated_at
    BEFORE UPDATE ON overhaul_items
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- 插入初始大修标准数据
-- =====================================================
INSERT INTO overhaul_standards (
    vehicle_type, overhaul_level, mileage_interval, time_interval,
    standard_duration_days, standard_cost_min, standard_cost_max,
    technical_requirements
) VALUES
    ('passenger', 'A1', 1200000, 120, 45, 5000000, 8000000, 'A1级架修标准：全面解体检修，更换主要部件'),
    ('passenger', 'A2', 600000, 60, 30, 2000000, 3500000, 'A2级大修标准：重要部件检修，性能恢复'),
    ('passenger', 'A3', 300000, 36, 15, 800000, 1500000, 'A3级中修标准：关键系统检修'),
    ('passenger', 'B1', 150000, 18, 7, 300000, 500000, 'B1级检修标准：重点部件检查'),
    ('passenger', 'B2', 75000, 9, 3, 100000, 200000, 'B2级检修标准：常规检查维护'),
    ('special', 'A1', 800000, 96, 60, 8000000, 12000000, '特种车辆A1级大修标准'),
    ('special', 'A2', 400000, 48, 40, 4000000, 6000000, '特种车辆A2级大修标准');

-- =====================================================
-- 创建视图：大修计划概览
-- =====================================================
CREATE OR REPLACE VIEW overhaul_plan_overview AS
SELECT
    op.id,
    op.plan_code,
    op.train_number,
    v.vehicle_type,
    op.overhaul_level,
    op.status,
    op.planned_start_date,
    op.planned_end_date,
    op.actual_start_date,
    op.actual_end_date,
    CASE
        WHEN op.actual_end_date IS NOT NULL THEN op.actual_end_date - op.actual_start_date
        WHEN op.actual_start_date IS NOT NULL THEN CURRENT_DATE - op.actual_start_date
        ELSE op.planned_end_date - op.planned_start_date
    END AS duration_days,
    op.estimated_cost,
    op.actual_cost,
    op.contractor,
    op.workshop,
    COUNT(oi.id) AS total_items,
    COUNT(CASE WHEN oi.status = 'completed' THEN 1 END) AS completed_items,
    AVG(oi.progress_percentage) AS overall_progress
FROM overhaul_plans op
LEFT JOIN vehicles v ON op.vehicle_id = v.id
LEFT JOIN overhaul_items oi ON op.id = oi.overhaul_plan_id
GROUP BY op.id, v.vehicle_type;

-- =====================================================
-- 创建函数：计算下次大修时间
-- =====================================================
CREATE OR REPLACE FUNCTION calculate_next_overhaul(
    p_vehicle_id UUID,
    p_overhaul_level overhaul_level
) RETURNS TABLE (
    next_overhaul_date DATE,
    next_overhaul_mileage DECIMAL(12,2),
    days_remaining INTEGER,
    mileage_remaining DECIMAL(12,2)
) AS $$
DECLARE
    v_last_overhaul_date DATE;
    v_last_overhaul_mileage DECIMAL(12,2);
    v_current_mileage DECIMAL(12,2);
    v_time_interval INTEGER;
    v_mileage_interval DECIMAL(10,2);
BEGIN
    -- 获取最后一次大修信息
    SELECT end_date, mileage_after INTO v_last_overhaul_date, v_last_overhaul_mileage
    FROM overhaul_records
    WHERE vehicle_id = p_vehicle_id AND overhaul_level = p_overhaul_level
    ORDER BY end_date DESC
    LIMIT 1;

    -- 获取当前里程
    SELECT total_mileage INTO v_current_mileage
    FROM vehicles
    WHERE id = p_vehicle_id;

    -- 获取大修标准
    SELECT time_interval, mileage_interval
    INTO v_time_interval, v_mileage_interval
    FROM overhaul_standards
    WHERE overhaul_level = p_overhaul_level
    AND vehicle_type = (SELECT vehicle_type FROM vehicles WHERE id = p_vehicle_id)
    AND (applicable_to IS NULL OR applicable_to >= CURRENT_DATE)
    ORDER BY applicable_from DESC
    LIMIT 1;

    -- 计算下次大修时间
    RETURN QUERY
    SELECT
        v_last_overhaul_date + (v_time_interval || ' months')::INTERVAL AS next_overhaul_date,
        v_last_overhaul_mileage + v_mileage_interval AS next_overhaul_mileage,
        (v_last_overhaul_date + (v_time_interval || ' months')::INTERVAL - CURRENT_DATE)::INTEGER AS days_remaining,
        v_last_overhaul_mileage + v_mileage_interval - v_current_mileage AS mileage_remaining;
END;
$$ LANGUAGE plpgsql;

-- 授权
GRANT ALL ON ALL TABLES IN SCHEMA public TO subway_user;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO subway_user;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO subway_user;