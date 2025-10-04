<template>
  <div class="maintenance-container">
    <!-- Header -->
    <div class="page-header">
      <h1>维护管理</h1>
      <div class="header-actions">
        <el-button type="primary" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>
          创建维护计划
        </el-button>
        <el-button @click="exportData">
          <el-icon><Download /></el-icon>
          导出报表
        </el-button>
      </div>
    </div>

    <!-- Tabs -->
    <el-tabs v-model="activeTab" @tab-click="handleTabChange">
      <el-tab-pane label="维护计划" name="plans">
        <!-- Filter Bar -->
        <div class="filter-bar">
          <el-select v-model="filterStatus" placeholder="状态筛选" clearable>
            <el-option label="待执行" value="pending" />
            <el-option label="进行中" value="in_progress" />
            <el-option label="已完成" value="completed" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
          <el-select v-model="filterPriority" placeholder="优先级筛选" clearable>
            <el-option label="紧急" value="urgent" />
            <el-option label="高" value="high" />
            <el-option label="中" value="medium" />
            <el-option label="低" value="low" />
          </el-select>
          <el-date-picker
            v-model="filterDateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
          />
          <el-button type="primary" @click="fetchMaintenancePlans">查询</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </div>

        <!-- Plans Table -->
        <el-table
          :data="maintenancePlans"
          v-loading="loading"
          style="width: 100%"
          @selection-change="handleSelectionChange"
        >
          <el-table-column type="selection" width="55" />
          <el-table-column prop="plan_id" label="计划编号" width="120" />
          <el-table-column prop="vehicle_number" label="车辆编号" width="120" />
          <el-table-column label="维护类型" width="120">
            <template #default="scope">
              <el-tag :type="getTypeTagType(scope.row.type)">
                {{ getMaintenanceTypeName(scope.row.type) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="优先级" width="100">
            <template #default="scope">
              <el-tag :type="getPriorityTagType(scope.row.priority)">
                {{ getPriorityName(scope.row.priority) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="scheduled_date" label="计划日期" width="120" />
          <el-table-column label="状态" width="100">
            <template #default="scope">
              <el-tag :type="getStatusTagType(scope.row.status)">
                {{ getStatusName(scope.row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="estimated_hours" label="预计工时(h)" width="120" />
          <el-table-column prop="estimated_cost" label="预计成本(元)" width="120" />
          <el-table-column label="操作" fixed="right" width="200">
            <template #default="scope">
              <el-button link type="primary" @click="viewPlanDetail(scope.row)">
                查看
              </el-button>
              <el-button
                link
                type="primary"
                @click="editPlan(scope.row)"
                v-if="scope.row.status === 'pending'"
              >
                编辑
              </el-button>
              <el-button
                link
                type="success"
                @click="executePlan(scope.row)"
                v-if="scope.row.status === 'pending'"
              >
                执行
              </el-button>
              <el-button
                link
                type="danger"
                @click="cancelPlan(scope.row)"
                v-if="scope.row.status === 'pending'"
              >
                取消
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- Pagination -->
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="totalCount"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </el-tab-pane>

      <el-tab-pane label="维护历史" name="history">
        <!-- History Table -->
        <el-table :data="maintenanceHistory" v-loading="loading" style="width: 100%">
          <el-table-column prop="record_id" label="记录编号" width="120" />
          <el-table-column prop="vehicle_number" label="车辆编号" width="120" />
          <el-table-column label="维护类型" width="120">
            <template #default="scope">
              <el-tag>{{ getMaintenanceTypeName(scope.row.type) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="executed_date" label="执行日期" width="120" />
          <el-table-column prop="actual_hours" label="实际工时(h)" width="120" />
          <el-table-column prop="actual_cost" label="实际成本(元)" width="120" />
          <el-table-column prop="technician" label="技术人员" width="120" />
          <el-table-column label="结果" width="100">
            <template #default="scope">
              <el-tag :type="scope.row.result === 'success' ? 'success' : 'warning'">
                {{ scope.row.result === 'success' ? '成功' : '部分完成' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="notes" label="备注" min-width="200" show-overflow-tooltip />
          <el-table-column label="操作" fixed="right" width="100">
            <template #default="scope">
              <el-button link type="primary" @click="viewHistoryDetail(scope.row)">
                详情
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="维护日历" name="calendar">
        <div class="calendar-container">
          <el-calendar v-model="calendarDate">
            <template #date-cell="{ data }">
              <div class="calendar-cell">
                <div class="date">{{ data.day.split('-')[2] }}</div>
                <div class="events">
                  <div
                    v-for="event in getDateEvents(data.day)"
                    :key="event.id"
                    class="event-item"
                    :class="'event-' + event.priority"
                    @click="viewPlanDetail(event)"
                  >
                    {{ event.vehicle_number }}
                  </div>
                </div>
              </div>
            </template>
          </el-calendar>
        </div>
      </el-tab-pane>

      <el-tab-pane label="统计分析" name="statistics">
        <div class="statistics-container">
          <el-row :gutter="20">
            <el-col :span="12">
              <div class="chart-card">
                <h3>月度维护统计</h3>
                <div id="monthlyChart" style="height: 300px;"></div>
              </div>
            </el-col>
            <el-col :span="12">
              <div class="chart-card">
                <h3>维护类型分布</h3>
                <div id="typeChart" style="height: 300px;"></div>
              </div>
            </el-col>
          </el-row>
          <el-row :gutter="20" style="margin-top: 20px;">
            <el-col :span="12">
              <div class="chart-card">
                <h3>成本趋势分析</h3>
                <div id="costChart" style="height: 300px;"></div>
              </div>
            </el-col>
            <el-col :span="12">
              <div class="chart-card">
                <h3>工时效率分析</h3>
                <div id="efficiencyChart" style="height: 300px;"></div>
              </div>
            </el-col>
          </el-row>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- Create/Edit Dialog -->
    <el-dialog
      v-model="showCreateDialog"
      :title="isEdit ? '编辑维护计划' : '创建维护计划'"
      width="600px"
    >
      <el-form :model="planForm" :rules="planRules" ref="planFormRef" label-width="100px">
        <el-form-item label="车辆编号" prop="vehicle_number">
          <el-select v-model="planForm.vehicle_number" placeholder="请选择车辆">
            <el-option
              v-for="vehicle in vehicleList"
              :key="vehicle.number"
              :label="vehicle.number"
              :value="vehicle.number"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="维护类型" prop="type">
          <el-select v-model="planForm.type" placeholder="请选择维护类型">
            <el-option label="日常检修" value="routine" />
            <el-option label="定期保养" value="scheduled" />
            <el-option label="故障维修" value="repair" />
            <el-option label="大修" value="overhaul" />
          </el-select>
        </el-form-item>
        <el-form-item label="优先级" prop="priority">
          <el-radio-group v-model="planForm.priority">
            <el-radio label="urgent">紧急</el-radio>
            <el-radio label="high">高</el-radio>
            <el-radio label="medium">中</el-radio>
            <el-radio label="low">低</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="计划日期" prop="scheduled_date">
          <el-date-picker
            v-model="planForm.scheduled_date"
            type="date"
            placeholder="选择日期"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item label="预计工时" prop="estimated_hours">
          <el-input-number v-model="planForm.estimated_hours" :min="0" :step="0.5" />
        </el-form-item>
        <el-form-item label="预计成本" prop="estimated_cost">
          <el-input-number v-model="planForm.estimated_cost" :min="0" :step="100" />
        </el-form-item>
        <el-form-item label="维护内容" prop="description">
          <el-input
            type="textarea"
            v-model="planForm.description"
            :rows="4"
            placeholder="请输入维护内容描述"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="submitPlanForm">确定</el-button>
      </template>
    </el-dialog>

    <!-- Detail Dialog -->
    <el-dialog v-model="showDetailDialog" title="维护计划详情" width="700px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="计划编号">
          {{ currentPlan.plan_id }}
        </el-descriptions-item>
        <el-descriptions-item label="车辆编号">
          {{ currentPlan.vehicle_number }}
        </el-descriptions-item>
        <el-descriptions-item label="维护类型">
          <el-tag>{{ getMaintenanceTypeName(currentPlan.type) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="优先级">
          <el-tag :type="getPriorityTagType(currentPlan.priority)">
            {{ getPriorityName(currentPlan.priority) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="计划日期">
          {{ currentPlan.scheduled_date }}
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusTagType(currentPlan.status)">
            {{ getStatusName(currentPlan.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="预计工时">
          {{ currentPlan.estimated_hours }} 小时
        </el-descriptions-item>
        <el-descriptions-item label="预计成本">
          ¥{{ currentPlan.estimated_cost }}
        </el-descriptions-item>
        <el-descriptions-item label="创建时间" :span="2">
          {{ currentPlan.created_at }}
        </el-descriptions-item>
        <el-descriptions-item label="维护内容" :span="2">
          {{ currentPlan.description || '暂无描述' }}
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Download } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import dayjs from 'dayjs'
import api from '@/api'

// State
const activeTab = ref('plans')
const loading = ref(false)
const showCreateDialog = ref(false)
const showDetailDialog = ref(false)
const isEdit = ref(false)

// Filters
const filterStatus = ref('')
const filterPriority = ref('')
const filterDateRange = ref<[string, string] | null>(null)

// Pagination
const currentPage = ref(1)
const pageSize = ref(20)
const totalCount = ref(0)

// Data
const maintenancePlans = ref<any[]>([])
const maintenanceHistory = ref<any[]>([])
const vehicleList = ref<any[]>([])
const selectedPlans = ref<any[]>([])
const currentPlan = ref<any>({})
const calendarDate = ref(new Date())

// Form
const planFormRef = ref()
const planForm = reactive({
  vehicle_number: '',
  type: '',
  priority: 'medium',
  scheduled_date: '',
  estimated_hours: 4,
  estimated_cost: 5000,
  description: ''
})

const planRules = {
  vehicle_number: [
    { required: true, message: '请选择车辆', trigger: 'change' }
  ],
  type: [
    { required: true, message: '请选择维护类型', trigger: 'change' }
  ],
  priority: [
    { required: true, message: '请选择优先级', trigger: 'change' }
  ],
  scheduled_date: [
    { required: true, message: '请选择计划日期', trigger: 'change' }
  ],
  estimated_hours: [
    { required: true, message: '请输入预计工时', trigger: 'blur' }
  ],
  estimated_cost: [
    { required: true, message: '请输入预计成本', trigger: 'blur' }
  ]
}

// Charts
let monthlyChart: echarts.ECharts | null = null
let typeChart: echarts.ECharts | null = null
let costChart: echarts.ECharts | null = null
let efficiencyChart: echarts.ECharts | null = null

// Methods
const fetchMaintenancePlans = async () => {
  loading.value = true
  try {
    const params: any = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    if (filterStatus.value) params.status = filterStatus.value
    if (filterPriority.value) params.priority = filterPriority.value
    if (filterDateRange.value) {
      params.start_date = filterDateRange.value[0]
      params.end_date = filterDateRange.value[1]
    }

    const response = await api.maintenance.getPlans(params)
    maintenancePlans.value = response.data.items
    totalCount.value = response.data.total
  } catch (error) {
    console.error('Failed to fetch maintenance plans:', error)
    // Use mock data
    maintenancePlans.value = generateMockPlans()
    totalCount.value = 50
  } finally {
    loading.value = false
  }
}

const fetchMaintenanceHistory = async () => {
  loading.value = true
  try {
    const response = await api.maintenance.getHistory({
      page: 1,
      page_size: 50
    })
    maintenanceHistory.value = response.data.items
  } catch (error) {
    console.error('Failed to fetch maintenance history:', error)
    // Use mock data
    maintenanceHistory.value = generateMockHistory()
  } finally {
    loading.value = false
  }
}

const fetchVehicles = async () => {
  try {
    const response = await api.vehicles.getList({ page: 1, page_size: 100 })
    vehicleList.value = response.data.items
  } catch (error) {
    console.error('Failed to fetch vehicles:', error)
    // Use mock data
    vehicleList.value = [
      { number: 'A001', model: 'CRH380A' },
      { number: 'A002', model: 'CRH380A' },
      { number: 'B001', model: 'CRH380B' },
      { number: 'B002', model: 'CRH380B' }
    ]
  }
}

const generateMockPlans = () => {
  const plans = []
  const statuses = ['pending', 'in_progress', 'completed', 'cancelled']
  const types = ['routine', 'scheduled', 'repair', 'overhaul']
  const priorities = ['urgent', 'high', 'medium', 'low']

  for (let i = 1; i <= 20; i++) {
    plans.push({
      plan_id: `MP${String(i).padStart(5, '0')}`,
      vehicle_number: `A${String(Math.ceil(Math.random() * 10)).padStart(3, '0')}`,
      type: types[Math.floor(Math.random() * types.length)],
      priority: priorities[Math.floor(Math.random() * priorities.length)],
      scheduled_date: dayjs().add(Math.floor(Math.random() * 30), 'day').format('YYYY-MM-DD'),
      status: statuses[Math.floor(Math.random() * statuses.length)],
      estimated_hours: Math.floor(Math.random() * 20) + 2,
      estimated_cost: Math.floor(Math.random() * 50000) + 5000,
      created_at: dayjs().subtract(Math.floor(Math.random() * 7), 'day').format('YYYY-MM-DD HH:mm:ss'),
      description: '例行维护检查，包括制动系统、转向架、电气系统等'
    })
  }
  return plans
}

const generateMockHistory = () => {
  const history = []
  const types = ['routine', 'scheduled', 'repair', 'overhaul']

  for (let i = 1; i <= 30; i++) {
    history.push({
      record_id: `MR${String(i).padStart(5, '0')}`,
      vehicle_number: `A${String(Math.ceil(Math.random() * 10)).padStart(3, '0')}`,
      type: types[Math.floor(Math.random() * types.length)],
      executed_date: dayjs().subtract(Math.floor(Math.random() * 60), 'day').format('YYYY-MM-DD'),
      actual_hours: Math.floor(Math.random() * 20) + 2,
      actual_cost: Math.floor(Math.random() * 50000) + 5000,
      technician: `技术员${Math.ceil(Math.random() * 5)}`,
      result: Math.random() > 0.2 ? 'success' : 'partial',
      notes: '维护工作已完成，所有系统运行正常'
    })
  }
  return history
}

const handleTabChange = () => {
  if (activeTab.value === 'plans') {
    fetchMaintenancePlans()
  } else if (activeTab.value === 'history') {
    fetchMaintenanceHistory()
  } else if (activeTab.value === 'statistics') {
    initCharts()
  }
}

const handleSelectionChange = (selection: any[]) => {
  selectedPlans.value = selection
}

const handleSizeChange = () => {
  fetchMaintenancePlans()
}

const handleCurrentChange = () => {
  fetchMaintenancePlans()
}

const resetFilters = () => {
  filterStatus.value = ''
  filterPriority.value = ''
  filterDateRange.value = null
  fetchMaintenancePlans()
}

const viewPlanDetail = (row: any) => {
  currentPlan.value = row
  showDetailDialog.value = true
}

const editPlan = (row: any) => {
  isEdit.value = true
  Object.assign(planForm, row)
  showCreateDialog.value = true
}

const executePlan = async (row: any) => {
  try {
    await ElMessageBox.confirm('确认要执行该维护计划吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await api.maintenance.executePlan(row.plan_id)
    ElMessage.success('维护计划已开始执行')
    fetchMaintenancePlans()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('执行失败，请重试')
    }
  }
}

const cancelPlan = async (row: any) => {
  try {
    await ElMessageBox.confirm('确认要取消该维护计划吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await api.maintenance.cancelPlan(row.plan_id)
    ElMessage.success('维护计划已取消')
    fetchMaintenancePlans()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('取消失败，请重试')
    }
  }
}

const viewHistoryDetail = (row: any) => {
  // Show history detail
  ElMessage.info('查看维护历史详情：' + row.record_id)
}

const submitPlanForm = async () => {
  try {
    await planFormRef.value.validate()

    if (isEdit.value) {
      await api.maintenance.updatePlan(currentPlan.value.plan_id, planForm)
      ElMessage.success('维护计划更新成功')
    } else {
      await api.maintenance.createPlan(planForm)
      ElMessage.success('维护计划创建成功')
    }

    showCreateDialog.value = false
    fetchMaintenancePlans()
    resetForm()
  } catch (error) {
    console.error('Failed to submit plan:', error)
    ElMessage.error('操作失败，请重试')
  }
}

const resetForm = () => {
  planForm.vehicle_number = ''
  planForm.type = ''
  planForm.priority = 'medium'
  planForm.scheduled_date = ''
  planForm.estimated_hours = 4
  planForm.estimated_cost = 5000
  planForm.description = ''
  isEdit.value = false
}

const exportData = () => {
  ElMessage.success('正在导出维护报表...')
  // Implement export functionality
}

const getDateEvents = (date: string) => {
  return maintenancePlans.value.filter(plan =>
    plan.scheduled_date === date && plan.status === 'pending'
  )
}

const initCharts = () => {
  // Monthly maintenance chart
  if (!monthlyChart) {
    monthlyChart = echarts.init(document.getElementById('monthlyChart')!)
  }
  monthlyChart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: ['1月', '2月', '3月', '4月', '5月', '6月']
    },
    yAxis: { type: 'value', name: '维护次数' },
    series: [{
      data: [120, 150, 180, 160, 140, 170],
      type: 'bar',
      itemStyle: { color: '#409EFF' }
    }]
  })

  // Type distribution chart
  if (!typeChart) {
    typeChart = echarts.init(document.getElementById('typeChart')!)
  }
  typeChart.setOption({
    tooltip: { trigger: 'item' },
    legend: { orient: 'vertical', left: 'left' },
    series: [{
      type: 'pie',
      radius: '50%',
      data: [
        { value: 335, name: '日常检修' },
        { value: 310, name: '定期保养' },
        { value: 234, name: '故障维修' },
        { value: 135, name: '大修' }
      ]
    }]
  })

  // Cost trend chart
  if (!costChart) {
    costChart = echarts.init(document.getElementById('costChart')!)
  }
  costChart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: ['1月', '2月', '3月', '4月', '5月', '6月']
    },
    yAxis: { type: 'value', name: '成本(万元)' },
    series: [{
      data: [45, 52, 48, 55, 51, 58],
      type: 'line',
      smooth: true,
      itemStyle: { color: '#67C23A' }
    }]
  })

  // Efficiency chart
  if (!efficiencyChart) {
    efficiencyChart = echarts.init(document.getElementById('efficiencyChart')!)
  }
  efficiencyChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['预计工时', '实际工时'] },
    xAxis: {
      type: 'category',
      data: ['1月', '2月', '3月', '4月', '5月', '6月']
    },
    yAxis: { type: 'value', name: '工时(h)' },
    series: [
      {
        name: '预计工时',
        type: 'line',
        data: [320, 350, 380, 360, 340, 370]
      },
      {
        name: '实际工时',
        type: 'line',
        data: [300, 340, 365, 350, 335, 355]
      }
    ]
  })
}

// Helper functions
const getMaintenanceTypeName = (type: string) => {
  const types: Record<string, string> = {
    routine: '日常检修',
    scheduled: '定期保养',
    repair: '故障维修',
    overhaul: '大修'
  }
  return types[type] || type
}

const getPriorityName = (priority: string) => {
  const priorities: Record<string, string> = {
    urgent: '紧急',
    high: '高',
    medium: '中',
    low: '低'
  }
  return priorities[priority] || priority
}

const getStatusName = (status: string) => {
  const statuses: Record<string, string> = {
    pending: '待执行',
    in_progress: '进行中',
    completed: '已完成',
    cancelled: '已取消'
  }
  return statuses[status] || status
}

const getTypeTagType = (type: string) => {
  const types: Record<string, string> = {
    routine: '',
    scheduled: 'success',
    repair: 'warning',
    overhaul: 'danger'
  }
  return types[type] || ''
}

const getPriorityTagType = (priority: string) => {
  const types: Record<string, string> = {
    urgent: 'danger',
    high: 'warning',
    medium: '',
    low: 'info'
  }
  return types[priority] || ''
}

const getStatusTagType = (status: string) => {
  const types: Record<string, string> = {
    pending: 'warning',
    in_progress: '',
    completed: 'success',
    cancelled: 'info'
  }
  return types[status] || ''
}

// Lifecycle
onMounted(() => {
  fetchMaintenancePlans()
  fetchVehicles()
})
</script>

<style scoped>
.maintenance-container {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h1 {
  font-size: 24px;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.filter-bar {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.el-table {
  margin-bottom: 20px;
}

.calendar-container {
  padding: 20px;
  background: white;
  border-radius: 8px;
}

.calendar-cell {
  height: 80px;
  padding: 4px;
}

.calendar-cell .date {
  font-weight: bold;
  margin-bottom: 4px;
}

.calendar-cell .events {
  max-height: 50px;
  overflow-y: auto;
}

.event-item {
  font-size: 12px;
  padding: 2px 4px;
  margin: 2px 0;
  border-radius: 3px;
  cursor: pointer;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.event-urgent {
  background-color: #f56c6c;
  color: white;
}

.event-high {
  background-color: #e6a23c;
  color: white;
}

.event-medium {
  background-color: #409eff;
  color: white;
}

.event-low {
  background-color: #909399;
  color: white;
}

.statistics-container {
  padding: 20px;
}

.chart-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.chart-card h3 {
  margin-top: 0;
  margin-bottom: 20px;
  font-size: 18px;
}
</style>