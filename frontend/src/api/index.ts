import { request } from './request'

// 认证相关API
export const authApi = {
  login: (data: { username: string; password: string }) =>
    request({ url: '/auth/login', method: 'POST', data }),

  logout: () =>
    request({ url: '/auth/logout', method: 'POST' }),

  refresh: () =>
    request({ url: '/auth/refresh', method: 'POST' })
}

// 车辆管理API
export const vehicleApi = {
  getList: (params?: any) =>
    request({ url: '/vehicles', method: 'GET', params }),

  getDetail: (id: string) =>
    request({ url: `/vehicles/${id}`, method: 'GET' }),

  create: (data: any) =>
    request({ url: '/vehicles', method: 'POST', data }),

  update: (id: string, data: any) =>
    request({ url: `/vehicles/${id}`, method: 'PUT', data }),

  delete: (id: string) =>
    request({ url: `/vehicles/${id}`, method: 'DELETE' })
}

// 预测相关API
export const predictionApi = {
  single: (data: { vehicle_id: string; prediction_horizon_days: number }) =>
    request({ url: '/predictions/single', method: 'POST', data }),

  batch: (data: { vehicle_ids: string[]; prediction_horizon_days: number }) =>
    request({ url: '/predictions/batch', method: 'POST', data }),

  trends: (params: { vehicle_id: string; component_type: string; days?: number }) =>
    request({ url: '/predictions/trends', method: 'GET', params })
}

// 维护管理API
export const maintenanceApi = {
  getPlans: (params?: any) =>
    request({ url: '/maintenance/plans', method: 'GET', params }),

  createPlan: (data: any) =>
    request({ url: '/maintenance/plans', method: 'POST', data }),

  updatePlan: (id: string, data: any) =>
    request({ url: `/maintenance/plans/${id}`, method: 'PUT', data }),

  deletePlan: (id: string) =>
    request({ url: `/maintenance/plans/${id}`, method: 'DELETE' }),

  getSuggestions: (params?: any) =>
    request({ url: '/maintenance/suggestions', method: 'GET', params }),

  optimizeSchedule: (vehicle_ids: string[]) =>
    request({ url: '/maintenance/schedule-optimization', method: 'POST', data: vehicle_ids })
}

// 报表统计API
export const reportApi = {
  getDashboard: () =>
    request({ url: '/reports/dashboard', method: 'GET' }),

  getStatistics: (params?: any) =>
    request({ url: '/reports/statistics', method: 'GET', params }),

  getFleetOverview: () =>
    request({ url: '/reports/fleet-overview', method: 'GET' }),

  generateReport: (data: any) =>
    request({ url: '/reports/generate', method: 'POST', data }),

  downloadReport: (id: string) =>
    request({ url: `/reports/download/${id}`, method: 'GET' })
}