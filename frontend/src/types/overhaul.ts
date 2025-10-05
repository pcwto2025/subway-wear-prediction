/**
 * 大修管理类型定义
 * Overhaul Management Type Definitions
 */

// 大修类型
export enum OverhaulType {
  SCHEDULED = 'scheduled',   // 计划大修
  EMERGENCY = 'emergency',   // 紧急大修
  UPGRADE = 'upgrade',       // 升级改造
  ACCIDENT = 'accident'      // 事故维修
}

// 大修状态
export enum OverhaulStatus {
  PLANNING = 'planning',       // 规划中
  APPROVED = 'approved',       // 已批准
  IN_PROGRESS = 'in_progress', // 进行中
  SUSPENDED = 'suspended',     // 暂停
  COMPLETED = 'completed',     // 已完成
  CANCELLED = 'cancelled'      // 已取消
}

// 大修级别
export enum OverhaulLevel {
  A1 = 'A1',  // A1级大修 (架修)
  A2 = 'A2',  // A2级大修 (大修)
  A3 = 'A3',  // A3级大修 (中修)
  B1 = 'B1',  // B1级检修
  B2 = 'B2',  // B2级检修
  C1 = 'C1',  // C1级检修
  C2 = 'C2'   // C2级检修
}

// 大修项目
export interface OverhaulItem {
  id?: string
  overhaul_plan_id?: string
  item_code: string
  item_name: string
  category?: string
  carriage_number?: string
  component_type?: string
  work_content?: string
  technical_standard?: string
  inspection_method?: string
  status?: string
  progress_percentage?: number
  started_at?: string
  completed_at?: string
  quality_check_status?: string
  quality_inspector?: string
  quality_check_date?: string
  quality_notes?: string
  labor_hours?: number
  material_cost?: number
  labor_cost?: number
  total_cost?: number
  spare_parts_used?: any[]
  old_parts_disposal?: string
  created_at?: string
  updated_at?: string
}

// 备件信息
export interface SparePart {
  id?: string
  overhaul_plan_id?: string
  part_number: string
  part_name: string
  category?: string
  manufacturer?: string
  planned_quantity: number
  actual_quantity?: number
  unit?: string
  unit_price?: number
  total_price?: number
  stock_quantity?: number
  warehouse_location?: string
  purchase_order_no?: string
  supplier?: string
  delivery_date?: string
  quality_certificate?: string
  warranty_period?: number
  created_at?: string
  updated_at?: string
}

// 大修计划
export interface OverhaulPlan {
  id?: string
  plan_code: string
  vehicle_id?: string
  train_number: string
  overhaul_type: OverhaulType
  overhaul_level: OverhaulLevel
  status?: OverhaulStatus

  // 时间计划
  planned_start_date: string
  planned_end_date: string
  actual_start_date?: string
  actual_end_date?: string

  // 里程基准
  mileage_at_overhaul?: number
  next_overhaul_mileage?: number

  // 成本预算
  estimated_cost?: number
  actual_cost?: number
  currency?: string

  // 承包信息
  contractor?: string
  workshop?: string
  responsible_person?: string
  contact_phone?: string

  // 审批信息
  approval_status?: string
  approved_by?: string
  approved_at?: string
  approval_notes?: string

  // 其他信息
  description?: string
  technical_requirements?: string
  safety_requirements?: string
  quality_standards?: string

  // 关联数据
  items?: OverhaulItem[]
  spare_parts?: SparePart[]

  // 计算字段
  duration_days?: number
  progress_percentage?: number
  cost_variance?: number

  // 时间戳
  created_at?: string
  updated_at?: string
  created_by?: string
  updated_by?: string
}

// 大修记录
export interface OverhaulRecord {
  id?: string
  overhaul_plan_id?: string
  vehicle_id?: string
  train_number: string
  overhaul_level: OverhaulLevel

  // 执行信息
  start_date: string
  end_date: string
  duration_days?: number

  // 里程信息
  mileage_before?: number
  mileage_after?: number
  mileage_interval?: number

  // 成本信息
  total_cost?: number
  labor_cost?: number
  material_cost?: number
  spare_parts_cost?: number

  // 质量评估
  quality_score?: number
  performance_improvement?: string

  // 问题记录
  problems_found?: string
  solutions_applied?: string

  // 文档附件
  report_url?: string
  photos?: string[]
  documents?: any[]

  created_at?: string
  created_by?: string
}

// 大修标准
export interface OverhaulStandard {
  id?: string
  vehicle_type: string
  overhaul_level: OverhaulLevel

  // 周期标准
  mileage_interval?: number
  time_interval?: number
  whichever_first?: boolean

  // 作业标准
  standard_duration_days?: number
  required_items?: string[]
  optional_items?: string[]

  // 成本标准
  standard_cost_min?: number
  standard_cost_max?: number

  // 技术标准
  technical_requirements?: string
  quality_standards?: string
  acceptance_criteria?: string

  // 适用范围
  applicable_from?: string
  applicable_to?: string

  created_at?: string
  updated_at?: string
}

// 查询参数
export interface OverhaulPlanQuery {
  train_number?: string
  status?: OverhaulStatus
  overhaul_type?: OverhaulType
  overhaul_level?: OverhaulLevel
  contractor?: string
  workshop?: string
  start_date_from?: string
  start_date_to?: string
  page?: number
  limit?: number
}

// 统计信息
export interface OverhaulStatistics {
  total_plans: number
  planning: number
  in_progress: number
  completed: number
  total_cost: number
  average_duration: number
  on_time_rate: number
  cost_variance_rate: number
  by_level: Record<string, number>
  by_type: Record<string, number>
  upcoming_plans: any[]
}

// 工具函数
export const OverhaulUtils = {
  // 获取大修类型标签
  getTypeLabel(type: OverhaulType): string {
    const labels: Record<OverhaulType, string> = {
      [OverhaulType.SCHEDULED]: '计划大修',
      [OverhaulType.EMERGENCY]: '紧急大修',
      [OverhaulType.UPGRADE]: '升级改造',
      [OverhaulType.ACCIDENT]: '事故维修'
    }
    return labels[type] || type
  },

  // 获取大修状态标签
  getStatusLabel(status: OverhaulStatus): string {
    const labels: Record<OverhaulStatus, string> = {
      [OverhaulStatus.PLANNING]: '规划中',
      [OverhaulStatus.APPROVED]: '已批准',
      [OverhaulStatus.IN_PROGRESS]: '进行中',
      [OverhaulStatus.SUSPENDED]: '暂停',
      [OverhaulStatus.COMPLETED]: '已完成',
      [OverhaulStatus.CANCELLED]: '已取消'
    }
    return labels[status] || status
  },

  // 获取大修级别标签
  getLevelLabel(level: OverhaulLevel): string {
    const labels: Record<OverhaulLevel, string> = {
      [OverhaulLevel.A1]: 'A1级大修(架修)',
      [OverhaulLevel.A2]: 'A2级大修',
      [OverhaulLevel.A3]: 'A3级中修',
      [OverhaulLevel.B1]: 'B1级检修',
      [OverhaulLevel.B2]: 'B2级检修',
      [OverhaulLevel.C1]: 'C1级检修',
      [OverhaulLevel.C2]: 'C2级检修'
    }
    return labels[level] || level
  },

  // 获取状态标签类型
  getStatusTagType(status: OverhaulStatus): string {
    const types: Record<OverhaulStatus, string> = {
      [OverhaulStatus.PLANNING]: 'info',
      [OverhaulStatus.APPROVED]: 'warning',
      [OverhaulStatus.IN_PROGRESS]: 'primary',
      [OverhaulStatus.SUSPENDED]: 'danger',
      [OverhaulStatus.COMPLETED]: 'success',
      [OverhaulStatus.CANCELLED]: 'info'
    }
    return types[status] || 'info'
  },

  // 获取级别标签类型
  getLevelTagType(level: OverhaulLevel): string {
    if (level.startsWith('A')) return 'danger'
    if (level.startsWith('B')) return 'warning'
    return 'info'
  },

  // 计算工期
  calculateDuration(startDate: string, endDate: string): number {
    const start = new Date(startDate)
    const end = new Date(endDate)
    const diffTime = Math.abs(end.getTime() - start.getTime())
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  },

  // 计算成本偏差
  calculateCostVariance(estimated: number, actual: number): number {
    if (!estimated || estimated === 0) return 0
    return ((actual - estimated) / estimated) * 100
  },

  // 格式化货币
  formatCurrency(amount: number, currency = 'CNY'): string {
    return new Intl.NumberFormat('zh-CN', {
      style: 'currency',
      currency: currency
    }).format(amount)
  },

  // 获取即将到期的计划
  getUpcomingPlans(plans: OverhaulPlan[], days = 30): OverhaulPlan[] {
    const now = new Date()
    const future = new Date(now.getTime() + days * 24 * 60 * 60 * 1000)

    return plans.filter(plan => {
      if (plan.status !== OverhaulStatus.PLANNING) return false
      const planDate = new Date(plan.planned_start_date)
      return planDate >= now && planDate <= future
    }).sort((a, b) =>
      new Date(a.planned_start_date).getTime() - new Date(b.planned_start_date).getTime()
    )
  }
}