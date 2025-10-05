<template>
  <div class="overhaul-management">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>
        <el-icon><Tools /></el-icon>
        {{ $t('overhaul.title') || 'MMM-SL 大修管理系统' }}
      </h2>
      <div class="header-actions">
        <el-tag type="success">项目代码: MMM-SL</el-tag>
        <el-tag type="info">大修计划: {{ totalPlans }}</el-tag>
      </div>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-cards">
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic :title="$t('overhaul.stats.planning') || '规划中'" :value="stats.planning">
            <template #prefix>
              <el-icon color="#409EFF"><Calendar /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic :title="$t('overhaul.stats.inProgress') || '进行中'" :value="stats.in_progress">
            <template #prefix>
              <el-icon color="#E6A23C"><Loading /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic :title="$t('overhaul.stats.completed') || '已完成'" :value="stats.completed">
            <template #prefix>
              <el-icon color="#67C23A"><CircleCheck /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic
            :title="$t('overhaul.stats.totalCost') || '总成本'"
            :value="stats.total_cost"
            :formatter="formatCurrency"
          >
            <template #prefix>
              <el-icon color="#F56C6C"><Wallet /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
    </el-row>

    <!-- 搜索和操作栏 -->
    <el-card shadow="never" class="filter-card">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item :label="$t('overhaul.trainNumber') || '列车编号'">
          <el-select
            v-model="searchForm.train_number"
            placeholder="全部"
            clearable
            filterable
          >
            <el-option
              v-for="i in 16"
              :key="i"
              :label="`Tr${String(i).padStart(2, '0')}`"
              :value="`Tr${String(i).padStart(2, '0')}`"
            />
          </el-select>
        </el-form-item>

        <el-form-item :label="$t('overhaul.level') || '大修级别'">
          <el-select v-model="searchForm.overhaul_level" placeholder="全部" clearable>
            <el-option
              v-for="level in overhaulLevels"
              :key="level.value"
              :label="level.label"
              :value="level.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item :label="$t('overhaul.status') || '状态'">
          <el-select v-model="searchForm.status" placeholder="全部" clearable>
            <el-option
              v-for="status in overhaulStatuses"
              :key="status.value"
              :label="status.label"
              :value="status.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item :label="$t('overhaul.type') || '大修类型'">
          <el-select v-model="searchForm.overhaul_type" placeholder="全部" clearable>
            <el-option
              v-for="type in overhaulTypes"
              :key="type.value"
              :label="type.label"
              :value="type.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            {{ $t('common.search') || '搜索' }}
          </el-button>
          <el-button @click="handleReset">
            <el-icon><Refresh /></el-icon>
            {{ $t('common.reset') || '重置' }}
          </el-button>
        </el-form-item>
      </el-form>

      <div class="action-buttons">
        <el-button type="primary" @click="handleAddPlan">
          <el-icon><Plus /></el-icon>
          {{ $t('overhaul.createPlan') || '创建大修计划' }}
        </el-button>
        <el-button type="success" @click="handleSchedule">
          <el-icon><Calendar /></el-icon>
          {{ $t('overhaul.schedule') || '排程优化' }}
        </el-button>
        <el-button @click="handleStatistics">
          <el-icon><DataAnalysis /></el-icon>
          {{ $t('overhaul.statistics') || '统计分析' }}
        </el-button>
        <el-button @click="handleExport">
          <el-icon><Download /></el-icon>
          {{ $t('common.export') || '导出数据' }}
        </el-button>
      </div>
    </el-card>

    <!-- 大修计划列表 -->
    <el-card shadow="never" class="table-card">
      <el-tabs v-model="activeTab" @tab-click="handleTabChange">
        <el-tab-pane :label="$t('overhaul.listView') || '列表视图'" name="list">
          <el-table
            :data="planList"
            v-loading="loading"
            stripe
            border
            @selection-change="handleSelectionChange"
          >
            <el-table-column type="selection" width="55" />
            <el-table-column prop="plan_code" label="计划编号" width="120" fixed>
              <template #default="{ row }">
                <el-link type="primary" @click="handleViewPlan(row)">
                  {{ row.plan_code }}
                </el-link>
              </template>
            </el-table-column>
            <el-table-column prop="train_number" label="列车编号" width="100">
              <template #default="{ row }">
                <el-tag type="primary">{{ row.train_number }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="overhaul_level" label="大修级别" width="120">
              <template #default="{ row }">
                <el-tag :type="getLevelTagType(row.overhaul_level)">
                  {{ getLevelLabel(row.overhaul_level) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="overhaul_type" label="大修类型" width="100">
              <template #default="{ row }">
                {{ getTypeLabel(row.overhaul_type) }}
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusTagType(row.status)">
                  {{ getStatusLabel(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="planned_start_date" label="计划开始" width="120" />
            <el-table-column prop="planned_end_date" label="计划结束" width="120" />
            <el-table-column prop="duration_days" label="工期(天)" width="100">
              <template #default="{ row }">
                {{ row.duration_days || calculateDuration(row.planned_start_date, row.planned_end_date) }}
              </template>
            </el-table-column>
            <el-table-column prop="contractor" label="承包商" width="150" />
            <el-table-column prop="workshop" label="检修车间" width="150" />
            <el-table-column prop="estimated_cost" label="预估成本" width="120">
              <template #default="{ row }">
                {{ formatCurrency(row.estimated_cost || 0) }}
              </template>
            </el-table-column>
            <el-table-column prop="progress_percentage" label="进度" width="120">
              <template #default="{ row }">
                <el-progress
                  :percentage="row.progress_percentage || 0"
                  :status="getProgressStatus(row.progress_percentage)"
                />
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" size="small" @click="handleViewPlan(row)">
                  查看
                </el-button>
                <el-button size="small" @click="handleEditPlan(row)">
                  编辑
                </el-button>
                <el-dropdown trigger="click" class="action-dropdown">
                  <el-button size="small">
                    更多<el-icon class="el-icon--right"><arrow-down /></el-icon>
                  </el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item @click="handleApprovePlan(row)">
                        <el-icon><Check /></el-icon>批准
                      </el-dropdown-item>
                      <el-dropdown-item @click="handleStartPlan(row)">
                        <el-icon><VideoPlay /></el-icon>开始执行
                      </el-dropdown-item>
                      <el-dropdown-item @click="handleCompletePlan(row)">
                        <el-icon><Finished /></el-icon>完成
                      </el-dropdown-item>
                      <el-dropdown-item divided @click="handleDeletePlan(row)">
                        <el-icon><Delete /></el-icon>删除
                      </el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </template>
            </el-table-column>
          </el-table>

          <!-- 分页 -->
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            :total="total"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </el-tab-pane>

        <el-tab-pane :label="$t('overhaul.ganttView') || '甘特图视图'" name="gantt">
          <OverhaulGanttChart :plans="planList" />
        </el-tab-pane>

        <el-tab-pane :label="$t('overhaul.calendarView') || '日历视图'" name="calendar">
          <OverhaulCalendar :plans="planList" @plan-click="handleViewPlan" />
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 创建/编辑对话框 -->
    <OverhaulPlanDialog
      v-model="dialogVisible"
      :plan="currentPlan"
      :mode="dialogMode"
      @save="handleSavePlan"
    />

    <!-- 详情抽屉 -->
    <el-drawer
      v-model="detailDrawerVisible"
      :title="`大修计划详情 - ${currentPlan?.plan_code}`"
      size="70%"
    >
      <OverhaulPlanDetail
        v-if="currentPlan"
        :plan="currentPlan"
        @update="handleUpdatePlan"
      />
    </el-drawer>

    <!-- 统计分析对话框 -->
    <el-dialog
      v-model="statisticsDialogVisible"
      title="大修统计分析"
      width="90%"
      top="5vh"
    >
      <OverhaulStatistics :year="currentYear" />
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, defineAsyncComponent } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Tools,
  Calendar,
  Loading,
  CircleCheck,
  Wallet,
  Search,
  Refresh,
  Plus,
  Download,
  DataAnalysis,
  ArrowDown,
  Check,
  VideoPlay,
  Finished,
  Delete
} from '@element-plus/icons-vue'
import {
  OverhaulPlan,
  OverhaulStatus,
  OverhaulType,
  OverhaulLevel,
  OverhaulUtils,
  OverhaulStatistics as IOverhaulStatistics
} from '@/types/overhaul'
import { useI18n } from '@/composables/useI18n'

// 动态导入组件（将在后续创建）
const OverhaulPlanDialog = defineAsyncComponent(() => import('./OverhaulPlanDialog.vue'))
const OverhaulPlanDetail = defineAsyncComponent(() => import('./OverhaulPlanDetail.vue'))
const OverhaulGanttChart = defineAsyncComponent(() => import('./OverhaulGanttChart.vue'))
const OverhaulCalendar = defineAsyncComponent(() => import('./OverhaulCalendar.vue'))
const OverhaulStatistics = defineAsyncComponent(() => import('./OverhaulStatistics.vue'))

const { t } = useI18n()

// 状态
const loading = ref(false)
const dialogVisible = ref(false)
const dialogMode = ref<'create' | 'edit'>('create')
const detailDrawerVisible = ref(false)
const statisticsDialogVisible = ref(false)
const activeTab = ref('list')
const planList = ref<OverhaulPlan[]>([])
const currentPlan = ref<OverhaulPlan | null>(null)
const selectedPlans = ref<OverhaulPlan[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const currentYear = ref(new Date().getFullYear())

// 搜索表单
const searchForm = reactive({
  train_number: '',
  overhaul_level: '',
  status: '',
  overhaul_type: '',
  contractor: '',
  workshop: ''
})

// 统计数据
const stats = ref<IOverhaulStatistics>({
  total_plans: 0,
  planning: 0,
  in_progress: 0,
  completed: 0,
  total_cost: 0,
  average_duration: 0,
  on_time_rate: 0,
  cost_variance_rate: 0,
  by_level: {},
  by_type: {},
  upcoming_plans: []
})

// 选项列表
const overhaulLevels = [
  { value: OverhaulLevel.A1, label: 'A1级大修(架修)' },
  { value: OverhaulLevel.A2, label: 'A2级大修' },
  { value: OverhaulLevel.A3, label: 'A3级中修' },
  { value: OverhaulLevel.B1, label: 'B1级检修' },
  { value: OverhaulLevel.B2, label: 'B2级检修' },
  { value: OverhaulLevel.C1, label: 'C1级检修' },
  { value: OverhaulLevel.C2, label: 'C2级检修' }
]

const overhaulStatuses = [
  { value: OverhaulStatus.PLANNING, label: '规划中' },
  { value: OverhaulStatus.APPROVED, label: '已批准' },
  { value: OverhaulStatus.IN_PROGRESS, label: '进行中' },
  { value: OverhaulStatus.SUSPENDED, label: '暂停' },
  { value: OverhaulStatus.COMPLETED, label: '已完成' },
  { value: OverhaulStatus.CANCELLED, label: '已取消' }
]

const overhaulTypes = [
  { value: OverhaulType.SCHEDULED, label: '计划大修' },
  { value: OverhaulType.EMERGENCY, label: '紧急大修' },
  { value: OverhaulType.UPGRADE, label: '升级改造' },
  { value: OverhaulType.ACCIDENT, label: '事故维修' }
]

// 计算属性
const totalPlans = computed(() => planList.value.length)

// 工具函数
const getTypeLabel = (type: string) => OverhaulUtils.getTypeLabel(type as OverhaulType)
const getStatusLabel = (status: string) => OverhaulUtils.getStatusLabel(status as OverhaulStatus)
const getLevelLabel = (level: string) => OverhaulUtils.getLevelLabel(level as OverhaulLevel)
const getStatusTagType = (status: string) => OverhaulUtils.getStatusTagType(status as OverhaulStatus)
const getLevelTagType = (level: string) => OverhaulUtils.getLevelTagType(level as OverhaulLevel)
const calculateDuration = OverhaulUtils.calculateDuration
const formatCurrency = (value: number) => OverhaulUtils.formatCurrency(value)

const getProgressStatus = (percentage?: number) => {
  if (!percentage) return ''
  if (percentage >= 100) return 'success'
  if (percentage >= 80) return ''
  if (percentage >= 50) return 'warning'
  return 'exception'
}

// 事件处理
const handleSearch = async () => {
  loading.value = true
  try {
    // TODO: 调用API搜索
    await fetchOverhaulPlans()
  } finally {
    loading.value = false
  }
}

const handleReset = () => {
  Object.keys(searchForm).forEach(key => {
    searchForm[key as keyof typeof searchForm] = ''
  })
  handleSearch()
}

const handleAddPlan = () => {
  currentPlan.value = null
  dialogMode.value = 'create'
  dialogVisible.value = true
}

const handleEditPlan = (plan: OverhaulPlan) => {
  currentPlan.value = { ...plan }
  dialogMode.value = 'edit'
  dialogVisible.value = true
}

const handleViewPlan = (plan: OverhaulPlan) => {
  currentPlan.value = plan
  detailDrawerVisible.value = true
}

const handleDeletePlan = async (plan: OverhaulPlan) => {
  await ElMessageBox.confirm(
    `确定要删除大修计划 ${plan.plan_code} 吗？`,
    '删除确认',
    {
      type: 'warning'
    }
  )

  try {
    // TODO: 调用API删除
    const index = planList.value.findIndex(p => p.id === plan.id)
    if (index > -1) {
      planList.value.splice(index, 1)
      ElMessage.success('删除成功')
    }
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

const handleSavePlan = async (plan: OverhaulPlan) => {
  try {
    if (dialogMode.value === 'create') {
      // TODO: 调用API创建
      plan.id = Date.now().toString()
      planList.value.unshift(plan)
      ElMessage.success('创建成功')
    } else {
      // TODO: 调用API更新
      const index = planList.value.findIndex(p => p.id === plan.id)
      if (index > -1) {
        planList.value[index] = plan
      }
      ElMessage.success('更新成功')
    }
    dialogVisible.value = false
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const handleUpdatePlan = (plan: OverhaulPlan) => {
  const index = planList.value.findIndex(p => p.id === plan.id)
  if (index > -1) {
    planList.value[index] = plan
  }
}

const handleApprovePlan = async (plan: OverhaulPlan) => {
  await ElMessageBox.confirm(
    `确定要批准大修计划 ${plan.plan_code} 吗？`,
    '批准确认'
  )

  try {
    // TODO: 调用API批准
    plan.status = OverhaulStatus.APPROVED
    plan.approval_status = 'approved'
    plan.approved_at = new Date().toISOString()
    ElMessage.success('批准成功')
  } catch (error) {
    ElMessage.error('批准失败')
  }
}

const handleStartPlan = async (plan: OverhaulPlan) => {
  if (plan.status !== OverhaulStatus.APPROVED) {
    ElMessage.warning('请先批准计划')
    return
  }

  await ElMessageBox.confirm(
    `确定要开始执行大修计划 ${plan.plan_code} 吗？`,
    '执行确认'
  )

  try {
    // TODO: 调用API开始执行
    plan.status = OverhaulStatus.IN_PROGRESS
    plan.actual_start_date = new Date().toISOString().split('T')[0]
    ElMessage.success('已开始执行')
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const handleCompletePlan = async (plan: OverhaulPlan) => {
  if (plan.status !== OverhaulStatus.IN_PROGRESS) {
    ElMessage.warning('只能完成进行中的计划')
    return
  }

  await ElMessageBox.confirm(
    `确定要完成大修计划 ${plan.plan_code} 吗？`,
    '完成确认'
  )

  try {
    // TODO: 调用API完成
    plan.status = OverhaulStatus.COMPLETED
    plan.actual_end_date = new Date().toISOString().split('T')[0]
    ElMessage.success('已标记为完成')
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const handleSchedule = () => {
  ElMessage.info('排程优化功能开发中')
}

const handleStatistics = () => {
  statisticsDialogVisible.value = true
}

const handleExport = () => {
  ElMessage.info('导出功能开发中')
}

const handleSelectionChange = (selection: OverhaulPlan[]) => {
  selectedPlans.value = selection
}

const handleTabChange = () => {
  // 切换视图
}

const handleSizeChange = (val: number) => {
  pageSize.value = val
  handleSearch()
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  handleSearch()
}

// 获取大修计划列表
const fetchOverhaulPlans = async () => {
  try {
    // TODO: 调用API获取数据
    // 模拟数据
    planList.value = [
      {
        id: '1',
        plan_code: 'OH-2024-001',
        train_number: 'Tr01',
        overhaul_type: OverhaulType.SCHEDULED,
        overhaul_level: OverhaulLevel.A1,
        status: OverhaulStatus.IN_PROGRESS,
        planned_start_date: '2024-02-01',
        planned_end_date: '2024-03-15',
        actual_start_date: '2024-02-05',
        estimated_cost: 5000000,
        actual_cost: 4800000,
        contractor: '中车检修公司',
        workshop: '北辛安检修车间',
        responsible_person: '张工',
        contact_phone: '13800138000',
        progress_percentage: 75,
        mileage_at_overhaul: 1200000,
        description: 'Tr01列车A1级架修'
      },
      {
        id: '2',
        plan_code: 'OH-2024-002',
        train_number: 'Tr05',
        overhaul_type: OverhaulType.SCHEDULED,
        overhaul_level: OverhaulLevel.A2,
        status: OverhaulStatus.PLANNING,
        planned_start_date: '2024-03-01',
        planned_end_date: '2024-03-30',
        estimated_cost: 2500000,
        contractor: '地铁维保公司',
        workshop: '北辛安检修车间',
        responsible_person: '李工',
        contact_phone: '13900139000',
        progress_percentage: 0,
        mileage_at_overhaul: 600000,
        description: 'Tr05列车A2级大修'
      }
    ]

    total.value = planList.value.length
  } catch (error) {
    ElMessage.error('获取数据失败')
  }
}

// 获取统计数据
const fetchStatistics = async () => {
  try {
    // TODO: 调用API获取统计数据
    stats.value = {
      total_plans: 12,
      planning: 3,
      in_progress: 2,
      completed: 7,
      total_cost: 35000000,
      average_duration: 35,
      on_time_rate: 85,
      cost_variance_rate: -5,
      by_level: {
        A1: 2,
        A2: 3,
        A3: 4,
        B1: 3
      },
      by_type: {
        scheduled: 10,
        emergency: 1,
        upgrade: 1
      },
      upcoming_plans: []
    }
  } catch (error) {
    console.error('Failed to fetch statistics:', error)
  }
}

onMounted(() => {
  fetchOverhaulPlans()
  fetchStatistics()
})
</script>

<style scoped lang="scss">
.overhaul-management {
  padding: 20px;

  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;

    h2 {
      display: flex;
      align-items: center;
      gap: 10px;
      margin: 0;
    }

    .header-actions {
      display: flex;
      gap: 10px;
    }
  }

  .stats-cards {
    margin-bottom: 20px;
  }

  .filter-card {
    margin-bottom: 20px;

    .search-form {
      border-bottom: 1px solid #e4e7ed;
      padding-bottom: 10px;
      margin-bottom: 15px;
    }

    .action-buttons {
      display: flex;
      gap: 10px;
    }
  }

  .table-card {
    .el-pagination {
      margin-top: 20px;
      justify-content: flex-end;
    }

    .action-dropdown {
      margin-left: 10px;
    }
  }
}
</style>