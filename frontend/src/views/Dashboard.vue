<template>
  <div class="dashboard-container">
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stat-cards">
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <el-statistic :value="dashboardData.total_vehicles">
            <template #title>
              <div class="stat-title">
                <el-icon><Van /></el-icon>
                <span>车辆总数</span>
              </div>
            </template>
          </el-statistic>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <el-statistic :value="dashboardData.active_vehicles">
            <template #title>
              <div class="stat-title">
                <el-icon><CircleCheck /></el-icon>
                <span>运行中</span>
              </div>
            </template>
          </el-statistic>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <el-statistic :value="dashboardData.vehicles_in_maintenance">
            <template #title>
              <div class="stat-title">
                <el-icon><Tools /></el-icon>
                <span>维护中</span>
              </div>
            </template>
          </el-statistic>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card high-risk">
          <el-statistic :value="dashboardData.high_risk_vehicles">
            <template #title>
              <div class="stat-title">
                <el-icon><Warning /></el-icon>
                <span>高风险</span>
              </div>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表和列表 -->
    <el-row :gutter="20" class="content-area">
      <!-- 风险分布图 -->
      <el-col :xs="24" :md="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>风险等级分布</span>
            </div>
          </template>
          <div ref="riskChartRef" class="chart-container"></div>
        </el-card>
      </el-col>

      <!-- 即将维护列表 -->
      <el-col :xs="24" :md="12">
        <el-card class="list-card">
          <template #header>
            <div class="card-header">
              <span>即将维护</span>
              <el-tag type="info" size="small">
                {{ dashboardData.upcoming_maintenance?.length || 0 }} 项
              </el-tag>
            </div>
          </template>
          <el-table
            :data="dashboardData.upcoming_maintenance"
            stripe
            style="width: 100%"
          >
            <el-table-column prop="vehicle_id" label="车辆编号" width="120" />
            <el-table-column prop="date" label="计划日期" width="120">
              <template #default="{ row }">
                {{ formatDate(row.date) }}
              </template>
            </el-table-column>
            <el-table-column prop="type" label="维护类型" />
            <el-table-column prop="priority" label="优先级" width="80">
              <template #default="{ row }">
                <el-tag :type="getPriorityType(row.priority)">
                  {{ getPriorityText(row.priority) }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <!-- 最近告警 -->
    <el-row :gutter="20" class="alert-area">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>最近告警</span>
              <el-button type="primary" size="small" text>
                查看全部
              </el-button>
            </div>
          </template>
          <el-timeline>
            <el-timeline-item
              v-for="(alert, index) in dashboardData.recent_alerts"
              :key="index"
              :timestamp="formatDateTime(alert.time)"
              :type="alert.level === 'warning' ? 'warning' : 'primary'"
              placement="top"
            >
              <el-card>
                <div class="alert-content">
                  <el-icon v-if="alert.level === 'warning'" color="#E6A23C">
                    <Warning />
                  </el-icon>
                  <el-icon v-else color="#409EFF">
                    <InfoFilled />
                  </el-icon>
                  <span>{{ alert.message }}</span>
                  <el-tag size="small">{{ alert.vehicle_id }}</el-tag>
                </div>
              </el-card>
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { reportApi } from '@/api'
import * as echarts from 'echarts'
import dayjs from 'dayjs'

const dashboardData = ref<any>({
  total_vehicles: 0,
  active_vehicles: 0,
  vehicles_in_maintenance: 0,
  high_risk_vehicles: 0,
  upcoming_maintenance: [],
  risk_distribution: {},
  recent_alerts: []
})

const riskChartRef = ref<HTMLElement>()
let riskChart: echarts.ECharts | null = null

// 获取仪表板数据
const fetchDashboardData = async () => {
  try {
    const data = await reportApi.getDashboard()
    dashboardData.value = data
    updateRiskChart()
  } catch (error) {
    console.error('Failed to fetch dashboard data:', error)
  }
}

// 更新风险分布图
const updateRiskChart = () => {
  if (!riskChartRef.value) return

  if (!riskChart) {
    riskChart = echarts.init(riskChartRef.value)
  }

  const data = dashboardData.value.risk_distribution
  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    legend: {
      bottom: '5%',
      left: 'center'
    },
    series: [
      {
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 20,
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        },
        data: [
          { value: data.critical || 0, name: '严重', itemStyle: { color: '#F56C6C' } },
          { value: data.high || 0, name: '高', itemStyle: { color: '#E6A23C' } },
          { value: data.medium || 0, name: '中等', itemStyle: { color: '#F4CA1C' } },
          { value: data.low || 0, name: '低', itemStyle: { color: '#67C23A' } },
          { value: data.minimal || 0, name: '极低', itemStyle: { color: '#409EFF' } }
        ]
      }
    ]
  }

  riskChart.setOption(option)
}

// 格式化日期
const formatDate = (date: string) => {
  return dayjs(date).format('YYYY-MM-DD')
}

const formatDateTime = (datetime: string) => {
  return dayjs(datetime).format('YYYY-MM-DD HH:mm:ss')
}

// 获取优先级类型
const getPriorityType = (priority: string) => {
  const types: Record<string, any> = {
    high: 'danger',
    medium: 'warning',
    low: 'success'
  }
  return types[priority] || 'info'
}

// 获取优先级文本
const getPriorityText = (priority: string) => {
  const texts: Record<string, string> = {
    high: '高',
    medium: '中',
    low: '低'
  }
  return texts[priority] || priority
}

// 窗口大小改变时重绘图表
const handleResize = () => {
  riskChart?.resize()
}

onMounted(() => {
  fetchDashboardData()
  window.addEventListener('resize', handleResize)

  // 定时刷新
  const timer = setInterval(fetchDashboardData, 30000)

  onUnmounted(() => {
    clearInterval(timer)
    window.removeEventListener('resize', handleResize)
    riskChart?.dispose()
  })
})
</script>

<style scoped>
.dashboard-container {
  padding: 0;
}

.stat-cards {
  margin-bottom: 20px;
}

.stat-card {
  height: 100%;
  transition: transform 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.stat-card.high-risk {
  border-left: 4px solid #f56c6c;
}

.stat-title {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #666;
  font-size: 14px;
}

.content-area {
  margin-bottom: 20px;
}

.chart-card,
.list-card {
  height: 400px;
}

.chart-container {
  height: 320px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.alert-area {
  margin-bottom: 20px;
}

.alert-content {
  display: flex;
  align-items: center;
  gap: 10px;
}

:deep(.el-statistic__number) {
  font-size: 32px;
  font-weight: bold;
  color: #333;
}

:deep(.el-card__header) {
  padding: 15px 20px;
  border-bottom: 1px solid #ebeef5;
}
</style>