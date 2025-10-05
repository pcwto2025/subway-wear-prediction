/**
 * MMM-SL地铁项目车辆数据类型定义
 */

// 车辆类型枚举
export enum VehicleType {
  PASSENGER = 'passenger', // 客运车辆
  MAINTENANCE = 'maintenance', // 维护车辆
  SPECIAL = 'special' // 特种车辆
}

// 车厢类型枚举
export enum CarriageType {
  MC1 = 'MC1', // 带司机室的动车
  MC2 = 'MC2', // 带司机室的动车
  M = 'M',     // 动车
  MP = 'MP',   // 带受电弓的动车
  T = 'T',     // 拖车
  TC = 'TC'    // 带司机室的拖车
}

// 车辆状态枚举
export enum VehicleStatus {
  IN_SERVICE = 'in_service',     // 运营中
  MAINTENANCE = 'maintenance',    // 维护中
  STANDBY = 'standby',           // 备用
  RETIRED = 'retired'            // 退役
}

// 单个车厢信息
export interface Carriage {
  id?: string
  carriageNumber: string        // 车厢编号 (如: SL0101)
  carriageType: CarriageType    // 车厢类型
  position: number              // 位置 (1-12)
  manufacturer?: string         // 制造商
  manufactureDate?: string     // 制造日期
  serialNumber?: string        // 序列号
  status: VehicleStatus        // 状态
}

// 列车编组信息
export interface TrainFormation {
  formationType: '6编组' | '8编组' | '12编组'
  carriages: Carriage[]
}

// MMM-SL项目车辆信息
export interface Vehicle {
  id?: string
  trainNumber: string           // 列车编号 (Tr01-Tr16)
  projectCode: string          // 项目代码 (MMM-SL)
  vehicleType: VehicleType    // 车辆类型
  formation: TrainFormation    // 编组信息
  line: string                // 运营线路
  depot?: string              // 车辆段
  manufacturer: string        // 制造商
  manufactureDate: string     // 制造日期
  commissionDate: string      // 投运日期
  totalMileage: number        // 总里程 (km)
  averageDailyMileage?: number // 日均里程 (km)
  status: VehicleStatus       // 车辆状态
  lastMaintenanceDate?: string // 上次维护日期
  nextMaintenanceDate?: string // 下次维护日期
  maintenanceLevel?: string   // 维护等级 (日检/周检/月检/年检)
  specialFeatures?: string[]  // 特殊功能 (预留给特种车辆)
  notes?: string             // 备注
  createdAt?: string
  updatedAt?: string
  createdBy?: string
  updatedBy?: string
}

// 特种维护车辆信息 (扩展接口)
export interface SpecialMaintenanceVehicle extends Vehicle {
  vehicleType: VehicleType.SPECIAL
  specialType: 'rail_grinding' | 'track_inspection' | 'rescue' | 'engineering' | 'cleaning'
  equipment: SpecialEquipment[]
  workCapability: WorkCapability
  certifications?: Certification[]
}

// 特种设备
export interface SpecialEquipment {
  name: string
  model: string
  manufacturer: string
  installDate: string
  lastInspectionDate: string
  nextInspectionDate: string
  status: 'normal' | 'maintenance' | 'fault'
}

// 作业能力
export interface WorkCapability {
  maxSpeed: number           // 最高速度 (km/h)
  workSpeed: number          // 作业速度 (km/h)
  dailyWorkCapacity: number  // 日作业能力
  workRange: string[]        // 作业范围
}

// 资质证书
export interface Certification {
  name: string
  issuer: string
  issueDate: string
  expiryDate: string
  certificateNumber: string
}

// 车辆搜索参数
export interface VehicleSearchParams {
  trainNumber?: string
  vehicleType?: VehicleType
  status?: VehicleStatus
  line?: string
  depot?: string
  dateFrom?: string
  dateTo?: string
  page?: number
  pageSize?: number
}

// 车辆统计信息
export interface VehicleStatistics {
  totalVehicles: number
  inServiceVehicles: number
  maintenanceVehicles: number
  standbyVehicles: number
  retiredVehicles: number
  averageMileage: number
  formationDistribution: {
    formation6: number
    formation8: number
    formation12: number
  }
  typeDistribution: {
    passenger: number
    maintenance: number
    special: number
  }
}

// 批量操作
export interface BatchOperation {
  action: 'update_status' | 'schedule_maintenance' | 'assign_line'
  vehicleIds: string[]
  params: any
}

// 车厢编号生成规则
export class CarriageNumberGenerator {
  /**
   * 生成车厢编号
   * @param trainNumber 列车号 (01-16)
   * @param position 位置 (1-12)
   * @param formationType 编组类型
   */
  static generate(trainNumber: number, position: number, formationType: '6编组' | '8编组' | '12编组'): string {
    const paddedTrain = trainNumber.toString().padStart(2, '0')
    const paddedPosition = position.toString().padStart(2, '0')

    // 根据MMM-SL项目规则生成编号
    // 奇数编组: N*2-1 (如: 01, 03, 05...)
    // 偶数编组: 2*N (如: 02, 04, 06...)
    let carriageCode: string

    if (position % 2 === 1) {
      // 奇数位置
      const n = Math.ceil(position / 2)
      carriageCode = `${paddedTrain}${(2 * n - 1).toString().padStart(2, '0')}`
    } else {
      // 偶数位置
      const n = position / 2
      carriageCode = `${paddedTrain}${(2 * n).toString().padStart(2, '0')}`
    }

    return `SL${carriageCode}`
  }

  /**
   * 批量生成编组车厢
   */
  static generateFormation(trainNumber: number, formationType: '12编组'): Carriage[] {
    const carriages: Carriage[] = []
    const positions = 12 // 12编组

    // 12编组典型配置: MC1+M+MP+T+T+MP+MP+T+T+MP+M+MC2
    const typeConfig = [
      CarriageType.MC1, CarriageType.M, CarriageType.MP,
      CarriageType.T, CarriageType.T, CarriageType.MP,
      CarriageType.MP, CarriageType.T, CarriageType.T,
      CarriageType.MP, CarriageType.M, CarriageType.MC2
    ]

    for (let i = 1; i <= positions; i++) {
      carriages.push({
        carriageNumber: this.generate(trainNumber, i, formationType),
        carriageType: typeConfig[i - 1],
        position: i,
        status: VehicleStatus.IN_SERVICE
      })
    }

    return carriages
  }
}

// 导出工具函数
export const VehicleUtils = {
  /**
   * 格式化列车编号
   */
  formatTrainNumber(num: number): string {
    return `Tr${num.toString().padStart(2, '0')}`
  },

  /**
   * 验证列车编号
   */
  validateTrainNumber(trainNumber: string): boolean {
    const regex = /^Tr(0[1-9]|1[0-6])$/
    return regex.test(trainNumber)
  },

  /**
   * 验证车厢编号
   */
  validateCarriageNumber(carriageNumber: string): boolean {
    const regex = /^SL\d{4}$/
    return regex.test(carriageNumber)
  },

  /**
   * 获取维护等级选项
   */
  getMaintenanceLevels() {
    return [
      { value: 'daily', label: '日检', interval: 1 },
      { value: 'weekly', label: '周检', interval: 7 },
      { value: 'monthly', label: '月检', interval: 30 },
      { value: 'quarterly', label: '季检', interval: 90 },
      { value: 'yearly', label: '年检', interval: 365 }
    ]
  }
}