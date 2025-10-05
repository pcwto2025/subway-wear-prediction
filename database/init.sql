-- PostgreSQL初始化脚本
-- 地铁车辆磨耗预测系统数据库

-- 创建数据库（如果需要）
-- CREATE DATABASE subway_wear_db WITH ENCODING='UTF8';

-- 使用数据库
\c subway_wear_db;

-- 创建扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 创建枚举类型
CREATE TYPE vehicle_status AS ENUM ('active', 'maintenance', 'retired');
CREATE TYPE component_type AS ENUM ('wheel', 'brake', 'motor', 'bearing', 'pantograph', 'door', 'hvac', 'other');
CREATE TYPE maintenance_type AS ENUM ('preventive', 'corrective', 'predictive', 'emergency');
CREATE TYPE risk_level AS ENUM ('low', 'medium', 'high', 'critical');

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    is_superuser BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 车辆表
CREATE TABLE IF NOT EXISTS vehicles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    vehicle_number VARCHAR(50) UNIQUE NOT NULL,
    line VARCHAR(50) NOT NULL,
    manufacturer VARCHAR(100),
    model VARCHAR(100),
    manufacture_date DATE,
    commission_date DATE,
    total_mileage DECIMAL(12, 2) DEFAULT 0,
    status vehicle_status DEFAULT 'active',
    last_maintenance_date DATE,
    next_maintenance_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 组件表
CREATE TABLE IF NOT EXISTS components (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    vehicle_id UUID REFERENCES vehicles(id) ON DELETE CASCADE,
    component_type component_type NOT NULL,
    component_name VARCHAR(255) NOT NULL,
    serial_number VARCHAR(100),
    installation_date DATE,
    expected_lifetime_days INTEGER,
    current_wear_percentage DECIMAL(5, 2) DEFAULT 0,
    risk_level risk_level DEFAULT 'low',
    last_inspection_date DATE,
    next_inspection_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 磨耗记录表
CREATE TABLE IF NOT EXISTS wear_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    component_id UUID REFERENCES components(id) ON DELETE CASCADE,
    measurement_date TIMESTAMP WITH TIME ZONE NOT NULL,
    wear_value DECIMAL(10, 4) NOT NULL,
    temperature DECIMAL(5, 2),
    humidity DECIMAL(5, 2),
    load_factor DECIMAL(5, 2),
    speed_avg DECIMAL(6, 2),
    vibration_level DECIMAL(8, 4),
    notes TEXT,
    recorded_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 维护记录表
CREATE TABLE IF NOT EXISTS maintenance_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    vehicle_id UUID REFERENCES vehicles(id) ON DELETE CASCADE,
    component_id UUID REFERENCES components(id) ON DELETE SET NULL,
    maintenance_type maintenance_type NOT NULL,
    maintenance_date DATE NOT NULL,
    description TEXT,
    cost DECIMAL(10, 2),
    duration_hours DECIMAL(6, 2),
    performed_by VARCHAR(255),
    next_maintenance_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 预测记录表
CREATE TABLE IF NOT EXISTS predictions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    component_id UUID REFERENCES components(id) ON DELETE CASCADE,
    prediction_date TIMESTAMP WITH TIME ZONE NOT NULL,
    predicted_wear_date DATE,
    predicted_remaining_days INTEGER,
    confidence_score DECIMAL(3, 2),
    algorithm_version VARCHAR(50),
    input_features JSONB,
    prediction_result JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 告警表
CREATE TABLE IF NOT EXISTS alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    vehicle_id UUID REFERENCES vehicles(id) ON DELETE CASCADE,
    component_id UUID REFERENCES components(id) ON DELETE SET NULL,
    alert_type VARCHAR(50) NOT NULL,
    severity risk_level NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    is_acknowledged BOOLEAN DEFAULT false,
    acknowledged_by UUID REFERENCES users(id),
    acknowledged_at TIMESTAMP WITH TIME ZONE,
    is_resolved BOOLEAN DEFAULT false,
    resolved_by UUID REFERENCES users(id),
    resolved_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 系统配置表
CREATE TABLE IF NOT EXISTS system_configs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value JSONB NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX idx_vehicles_status ON vehicles(status);
CREATE INDEX idx_vehicles_line ON vehicles(line);
CREATE INDEX idx_components_vehicle_id ON components(vehicle_id);
CREATE INDEX idx_components_type ON components(component_type);
CREATE INDEX idx_components_risk_level ON components(risk_level);
CREATE INDEX idx_wear_records_component_id ON wear_records(component_id);
CREATE INDEX idx_wear_records_measurement_date ON wear_records(measurement_date);
CREATE INDEX idx_maintenance_records_vehicle_id ON maintenance_records(vehicle_id);
CREATE INDEX idx_maintenance_records_date ON maintenance_records(maintenance_date);
CREATE INDEX idx_predictions_component_id ON predictions(component_id);
CREATE INDEX idx_predictions_date ON predictions(prediction_date);
CREATE INDEX idx_alerts_vehicle_id ON alerts(vehicle_id);
CREATE INDEX idx_alerts_severity ON alerts(severity);
CREATE INDEX idx_alerts_is_resolved ON alerts(is_resolved);

-- 创建更新时间触发器
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_vehicles_updated_at BEFORE UPDATE ON vehicles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_components_updated_at BEFORE UPDATE ON components
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_maintenance_records_updated_at BEFORE UPDATE ON maintenance_records
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_system_configs_updated_at BEFORE UPDATE ON system_configs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 插入默认管理员用户 (密码: admin123)
INSERT INTO users (username, email, hashed_password, full_name, is_active, is_superuser)
VALUES (
    'admin',
    'admin@subway-wear.com',
    '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW',
    'System Administrator',
    true,
    true
) ON CONFLICT (username) DO NOTHING;

-- 插入系统配置
INSERT INTO system_configs (config_key, config_value, description)
VALUES
    ('wear_threshold', '{"wheel": 0.8, "brake": 0.7, "motor": 0.85, "bearing": 0.75}', '各组件磨耗阈值'),
    ('maintenance_interval', '{"preventive": 30, "predictive": 7}', '维护间隔天数'),
    ('alert_settings', '{"email_enabled": true, "sms_enabled": false}', '告警通知设置')
ON CONFLICT (config_key) DO NOTHING;

-- 插入示例数据
-- 插入示例车辆
INSERT INTO vehicles (vehicle_number, line, manufacturer, model, manufacture_date, commission_date, total_mileage, status)
VALUES
    ('SH001', 'Line 1', 'CRRC', 'Type-A', '2020-01-15', '2020-03-01', 125000.50, 'active'),
    ('SH002', 'Line 1', 'CRRC', 'Type-A', '2020-01-15', '2020-03-01', 118000.30, 'active'),
    ('SH003', 'Line 2', 'Siemens', 'Type-B', '2019-06-20', '2019-08-15', 156000.80, 'active'),
    ('SH004', 'Line 2', 'Siemens', 'Type-B', '2019-06-20', '2019-08-15', 145000.20, 'maintenance'),
    ('SH005', 'Line 3', 'Alstom', 'Type-C', '2021-03-10', '2021-05-01', 85000.60, 'active')
ON CONFLICT (vehicle_number) DO NOTHING;

-- 为每辆车插入组件
DO $$
DECLARE
    v_record RECORD;
    comp_id UUID;
BEGIN
    FOR v_record IN SELECT id, vehicle_number FROM vehicles LIMIT 5
    LOOP
        -- 轮对
        INSERT INTO components (vehicle_id, component_type, component_name, serial_number, installation_date, expected_lifetime_days, current_wear_percentage, risk_level)
        VALUES
            (v_record.id, 'wheel', 'Front Wheelset 1', v_record.vehicle_number || '-FW1', '2020-03-01', 1095, 35.5, 'low'),
            (v_record.id, 'wheel', 'Front Wheelset 2', v_record.vehicle_number || '-FW2', '2020-03-01', 1095, 38.2, 'low'),
            (v_record.id, 'wheel', 'Rear Wheelset 1', v_record.vehicle_number || '-RW1', '2020-03-01', 1095, 42.8, 'medium'),
            (v_record.id, 'wheel', 'Rear Wheelset 2', v_record.vehicle_number || '-RW2', '2020-03-01', 1095, 40.1, 'medium');

        -- 制动系统
        INSERT INTO components (vehicle_id, component_type, component_name, serial_number, installation_date, expected_lifetime_days, current_wear_percentage, risk_level)
        VALUES
            (v_record.id, 'brake', 'Brake Pad Set 1', v_record.vehicle_number || '-BP1', '2020-03-01', 730, 55.3, 'medium'),
            (v_record.id, 'brake', 'Brake Pad Set 2', v_record.vehicle_number || '-BP2', '2020-03-01', 730, 52.8, 'medium');

        -- 电机
        INSERT INTO components (vehicle_id, component_type, component_name, serial_number, installation_date, expected_lifetime_days, current_wear_percentage, risk_level)
        VALUES
            (v_record.id, 'motor', 'Traction Motor 1', v_record.vehicle_number || '-TM1', '2020-03-01', 1825, 25.6, 'low'),
            (v_record.id, 'motor', 'Traction Motor 2', v_record.vehicle_number || '-TM2', '2020-03-01', 1825, 26.8, 'low');

        -- 轴承
        INSERT INTO components (vehicle_id, component_type, component_name, serial_number, installation_date, expected_lifetime_days, current_wear_percentage, risk_level)
        VALUES
            (v_record.id, 'bearing', 'Main Bearing 1', v_record.vehicle_number || '-MB1', '2020-03-01', 1460, 30.2, 'low'),
            (v_record.id, 'bearing', 'Main Bearing 2', v_record.vehicle_number || '-MB2', '2020-03-01', 1460, 31.5, 'low');
    END LOOP;
END $$;

-- 插入磨耗记录示例
INSERT INTO wear_records (component_id, measurement_date, wear_value, temperature, humidity, load_factor, speed_avg)
SELECT
    c.id,
    CURRENT_TIMESTAMP - INTERVAL '1 day' * (10 - n),
    35.0 + random() * 10,
    20.0 + random() * 10,
    60.0 + random() * 20,
    0.7 + random() * 0.3,
    40.0 + random() * 20
FROM components c
CROSS JOIN generate_series(1, 10) n
WHERE c.component_type = 'wheel'
LIMIT 100;

-- 插入维护记录示例
INSERT INTO maintenance_records (vehicle_id, maintenance_type, maintenance_date, description, cost, duration_hours, performed_by)
SELECT
    v.id,
    (ARRAY['preventive', 'corrective', 'predictive'])[1 + floor(random() * 3)]::maintenance_type,
    CURRENT_DATE - INTERVAL '1 month' * n,
    '定期维护检查',
    1000 + random() * 5000,
    2 + random() * 6,
    'Maintenance Team ' || (1 + floor(random() * 3))
FROM vehicles v
CROSS JOIN generate_series(1, 3) n
LIMIT 15;

-- 创建视图：车辆概览
CREATE OR REPLACE VIEW vehicle_overview AS
SELECT
    v.id,
    v.vehicle_number,
    v.line,
    v.status,
    v.total_mileage,
    COUNT(DISTINCT c.id) as component_count,
    AVG(c.current_wear_percentage) as avg_wear_percentage,
    MAX(c.risk_level) as max_risk_level,
    v.last_maintenance_date,
    v.next_maintenance_date
FROM vehicles v
LEFT JOIN components c ON v.id = c.vehicle_id
GROUP BY v.id;

-- 创建视图：高风险组件
CREATE OR REPLACE VIEW high_risk_components AS
SELECT
    c.id,
    c.component_name,
    c.component_type,
    c.current_wear_percentage,
    c.risk_level,
    v.vehicle_number,
    v.line,
    c.next_inspection_date
FROM components c
JOIN vehicles v ON c.vehicle_id = v.id
WHERE c.risk_level IN ('high', 'critical')
   OR c.current_wear_percentage > 70
ORDER BY c.risk_level DESC, c.current_wear_percentage DESC;

-- 授权
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO subway_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO subway_user;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO subway_user;

-- 输出初始化完成信息
DO $$
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE '数据库初始化完成！';
    RAISE NOTICE '默认管理员账号：admin';
    RAISE NOTICE '默认密码：admin123';
    RAISE NOTICE '========================================';
END $$;