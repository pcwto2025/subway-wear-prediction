<template>
  <div class="vehicle-management">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>
        <el-icon><Van /></el-icon>
        MMM-SL 地铁车辆管理系统
      </h2>
      <div class="header-actions">
        <el-tag type="success">项目代码: MMM-SL</el-tag>
        <el-tag type="info">车辆总数: {{ totalVehicles }}/16</el-tag>
      </div>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-cards">
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="运营中" :value="stats.inService">
            <template #prefix>
              <el-icon color="#67C23A"><CircleCheck /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="维护中" :value="stats.maintenance">
            <template #prefix>
              <el-icon color="#E6A23C"><Tools /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="备用" :value="stats.standby">
            <template #prefix>
              <el-icon color="#909399"><Clock /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="平均里程" :value="stats.avgMileage" suffix="km">
            <template #prefix>
              <el-icon color="#409EFF"><Odometer /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
    </el-row>

    <!-- 搜索和操作栏 -->
    <el-card shadow="never" class="filter-card">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="列车编号">
          <el-select
            v-model="searchForm.trainNumber"
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

        <el-form-item label="车辆类型">
          <el-select v-model="searchForm.vehicleType" placeholder="全部" clearable>
            <el-option label="客运车辆" value="passenger" />
            <el-option label="维护车辆" value="maintenance" />
            <el-option label="特种车辆" value="special" />
          </el-select>
        </el-form-item>

        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="全部" clearable>
            <el-option label="运营中" value="in_service" />
            <el-option label="维护中" value="maintenance" />
            <el-option label="备用" value="standby" />
            <el-option label="退役" value="retired" />
          </el-select>
        </el-form-item>

        <el-form-item label="运营线路">
          <el-input
            v-model="searchForm.line"
            placeholder="请输入线路"
            clearable
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="handleReset">
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
        </el-form-item>
      </el-form>

      <div class="action-buttons">
        <el-button type="primary" @click="handleAdd">
          <el-icon><Plus /></el-icon>
          新增车辆
        </el-button>
        <el-button type="success" @click="handleAddSpecial">
          <el-icon><Truck /></el-icon>
          新增特种车辆
        </el-button>
        <el-button @click="handleBatchOperation">
          <el-icon><Operation /></el-icon>
          批量操作
        </el-button>
        <el-button @click="handleExport">
          <el-icon><Download /></el-icon>
          导出数据
        </el-button>
      </div>
    </el-card>

    <!-- 车辆列表 -->
    <el-card shadow="never" class="table-card">
      <el-tabs v-model="activeTab" @tab-click="handleTabChange">
        <el-tab-pane label="列表视图" name="list">
          <el-table
            :data="vehicleList"
            v-loading="loading"
            stripe
            border
            @selection-change="handleSelectionChange"
          >
            <el-table-column type="selection" width="55" />
            <el-table-column prop="trainNumber" label="列车编号" width="100" fixed>
              <template #default="{ row }">
                <el-tag type="primary">{{ row.trainNumber }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="vehicleType" label="车辆类型" width="100">
              <template #default="{ row }">
                <el-tag :type="getVehicleTypeTag(row.vehicleType)">
                  {{ getVehicleTypeLabel(row.vehicleType) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="formation.formationType" label="编组" width="80" />
            <el-table-column prop="line" label="运营线路" width="100" />
            <el-table-column prop="depot" label="车辆段" width="120" />
            <el-table-column prop="manufacturer" label="制造商" width="100" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusTag(row.status)">
                  {{ getStatusLabel(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="totalMileage" label="总里程(km)" width="120">
              <template #default="{ row }">
                {{ row.totalMileage.toLocaleString() }}
              </template>
            </el-table-column>
            <el-table-column prop="commissionDate" label="投运日期" width="120" />
            <el-table-column prop="maintenanceLevel" label="维护等级" width="100">
              <template #default="{ row }">
                <el-tag size="small">{{ getMaintenanceLevelLabel(row.maintenanceLevel) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="nextMaintenanceDate" label="下次维护" width="120">
              <template #default="{ row }">
                <span :class="getMaintenanceDateClass(row.nextMaintenanceDate)">
                  {{ row.nextMaintenanceDate || '-' }}
                </span>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" size="small" @click="handleView(row)">
                  查看
                </el-button>
                <el-button size="small" @click="handleEdit(row)">
                  编辑
                </el-button>
                <el-button type="danger" size="small" @click="handleDelete(row)">
                  删除
                </el-button>
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

        <el-tab-pane label="编组视图" name="formation">
          <div class="formation-view">
            <el-row :gutter="20">
              <el-col :span="6" v-for="vehicle in vehicleList" :key="vehicle.id">
                <el-card shadow="hover" class="vehicle-card">
                  <div class="vehicle-card-header">
                    <el-tag type="primary">{{ vehicle.trainNumber }}</el-tag>
                    <el-tag :type="getStatusTag(vehicle.status)" size="small">
                      {{ getStatusLabel(vehicle.status) }}
                    </el-tag>
                  </div>
                  <div class="formation-diagram">
                    <div
                      v-for="(carriage, index) in vehicle.formation.carriages"
                      :key="index"
                      class="carriage-block"
                      :class="`carriage-${carriage.carriageType.toLowerCase()}`"
                    >
                      <span class="carriage-number">{{ carriage.carriageNumber }}</span>
                      <span class="carriage-type">{{ carriage.carriageType }}</span>
                    </div>
                  </div>
                  <div class="vehicle-info">
                    <p>线路: {{ vehicle.line }}</p>
                    <p>里程: {{ vehicle.totalMileage.toLocaleString() }} km</p>
                  </div>
                  <div class="vehicle-actions">
                    <el-button type="primary" size="small" @click="handleView(vehicle)">
                      详情
                    </el-button>
                    <el-button size="small" @click="handleEdit(vehicle)">
                      编辑
                    </el-button>
                  </div>
                </el-card>
              </el-col>
            </el-row>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 新增/编辑对话框 -->
    <VehicleFormDialog
      v-model="dialogVisible"
      :vehicle="currentVehicle"
      :existing-train-numbers="existingTrainNumbers"
      @save="handleSave"
    />

    <!-- 车辆详情抽屉 -->
    <el-drawer
      v-model="detailDrawerVisible"
      :title="`车辆详情 - ${currentVehicle?.trainNumber}`"
      size="60%"
    >
      <VehicleDetail v-if="currentVehicle" :vehicle="currentVehicle" />
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Van,
  CircleCheck,
  Tools,
  Clock,
  Odometer,
  Search,
  Refresh,
  Plus,
  Truck,
  Operation,
  Download
} from '@element-plus/icons-vue'
import VehicleFormDialog from '@/components/VehicleFormDialog.vue'
import VehicleDetail from '@/components/VehicleDetail.vue'
import type { Vehicle, VehicleSearchParams, VehicleType } from '@/types/vehicle'

// 模拟数据
const mockVehicles: Vehicle[] = [
  {
    id: '1',
    trainNumber: 'Tr01',
    projectCode: 'MMM-SL',
    vehicleType: 'passenger',
    formation: {
      formationType: '12编组',
      carriages: Array.from({ length: 12 }, (_, i) => ({
        carriageNumber: `SL01${String(i + 1).padStart(2, '0')}`,
        carriageType: i === 0 ? 'MC1' : i === 11 ? 'MC2' : i % 3 === 0 ? 'MP' : i % 2 === 0 ? 'M' : 'T',
        position: i + 1,
        status: 'in_service'
      }))
    },
    line: '1号线',
    depot: '北辛安车辆段',
    manufacturer: 'CRRC',
    manufactureDate: '2022-01-15',
    commissionDate: '2022-03-01',
    totalMileage: 45230.5,
    status: 'in_service',
    maintenanceLevel: 'monthly',
    lastMaintenanceDate: '2024-01-15',
    nextMaintenanceDate: '2024-02-15'
  },
  // ... 可以添加更多模拟数据
]

// 状态
const loading = ref(false)
const dialogVisible = ref(false)
const detailDrawerVisible = ref(false)
const activeTab = ref('list')
const vehicleList = ref<Vehicle[]>(mockVehicles)
const currentVehicle = ref<Vehicle | null>(null)
const selectedVehicles = ref<Vehicle[]>([])
const total = ref(16)
const currentPage = ref(1)
const pageSize = ref(10)

// 搜索表单
const searchForm = reactive<VehicleSearchParams>({
  trainNumber: '',
  vehicleType: undefined,
  status: undefined,
  line: ''
})

// 计算属性
const totalVehicles = computed(() => vehicleList.value.length)
const existingTrainNumbers = computed(() => vehicleList.value.map(v => v.trainNumber))

const stats = computed(() => ({
  inService: vehicleList.value.filter(v => v.status === 'in_service').length,
  maintenance: vehicleList.value.filter(v => v.status === 'maintenance').length,
  standby: vehicleList.value.filter(v => v.status === 'standby').length,
  avgMileage: Math.round(
    vehicleList.value.reduce((sum, v) => sum + v.totalMileage, 0) / vehicleList.value.length || 0
  )
}))

// 工具函数
const getVehicleTypeLabel = (type: string) => {
  const map: Record<string, string> = {
    passenger: '客运车辆',
    maintenance: '维护车辆',
    special: '特种车辆'
  }
  return map[type] || type
}

const getVehicleTypeTag = (type: string) => {
  const map: Record<string, string> = {
    passenger: 'primary',
    maintenance: 'warning',
    special: 'success'
  }
  return map[type] || 'info'
}

const getStatusLabel = (status: string) => {
  const map: Record<string, string> = {
    in_service: '运营中',
    maintenance: '维护中',
    standby: '备用',
    retired: '退役'
  }
  return map[status] || status
}

const getStatusTag = (status: string) => {
  const map: Record<string, string> = {
    in_service: 'success',
    maintenance: 'warning',
    standby: 'info',
    retired: 'danger'
  }
  return map[status] || 'info'
}

const getMaintenanceLevelLabel = (level: string) => {
  const map: Record<string, string> = {
    daily: '日检',
    weekly: '周检',
    monthly: '月检',
    quarterly: '季检',
    yearly: '年检'
  }
  return map[level] || level
}

const getMaintenanceDateClass = (date: string) => {
  if (!date) return ''
  const days = Math.floor((new Date(date).getTime() - Date.now()) / (1000 * 60 * 60 * 24))
  if (days < 0) return 'text-danger'
  if (days < 7) return 'text-warning'
  return ''
}

// 事件处理
const handleSearch = () => {
  loading.value = true
  // TODO: 调用API搜索
  setTimeout(() => {
    loading.value = false
    ElMessage.success('搜索完成')
  }, 1000)
}

const handleReset = () => {
  Object.keys(searchForm).forEach(key => {
    searchForm[key as keyof VehicleSearchParams] = undefined
  })
  handleSearch()
}

const handleAdd = () => {
  currentVehicle.value = null
  dialogVisible.value = true
}

const handleAddSpecial = () => {
  currentVehicle.value = {
    vehicleType: 'special'
  } as Vehicle
  dialogVisible.value = true
}

const handleEdit = (row: Vehicle) => {
  currentVehicle.value = { ...row }
  dialogVisible.value = true
}

const handleView = (row: Vehicle) => {
  currentVehicle.value = row
  detailDrawerVisible.value = true
}

const handleDelete = async (row: Vehicle) => {
  await ElMessageBox.confirm(
    `确定要删除列车 ${row.trainNumber} 吗？`,
    '删除确认',
    {
      type: 'warning'
    }
  )

  // TODO: 调用API删除
  const index = vehicleList.value.findIndex(v => v.id === row.id)
  if (index > -1) {
    vehicleList.value.splice(index, 1)
    ElMessage.success('删除成功')
  }
}

const handleSave = (vehicle: Vehicle) => {
  if (vehicle.id) {
    // 更新
    const index = vehicleList.value.findIndex(v => v.id === vehicle.id)
    if (index > -1) {
      vehicleList.value[index] = vehicle
    }
  } else {
    // 新增
    vehicle.id = Date.now().toString()
    vehicleList.value.push(vehicle)
  }
}

const handleBatchOperation = () => {
  if (selectedVehicles.value.length === 0) {
    ElMessage.warning('请先选择要操作的车辆')
    return
  }
  // TODO: 实现批量操作
}

const handleExport = () => {
  ElMessage.info('导出功能开发中')
}

const handleSelectionChange = (selection: Vehicle[]) => {
  selectedVehicles.value = selection
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

onMounted(() => {
  handleSearch()
})
</script>

<style scoped lang="scss">
.vehicle-management {
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
  }

  .formation-view {
    .vehicle-card {
      margin-bottom: 20px;

      .vehicle-card-header {
        display: flex;
        justify-content: space-between;
        margin-bottom: 15px;
      }

      .formation-diagram {
        display: flex;
        flex-wrap: wrap;
        gap: 4px;
        margin-bottom: 15px;
        padding: 10px;
        background: #f5f7fa;
        border-radius: 4px;

        .carriage-block {
          flex: 1 1 30%;
          padding: 4px;
          background: white;
          border: 1px solid #dcdfe6;
          border-radius: 2px;
          text-align: center;
          font-size: 10px;

          .carriage-number {
            display: block;
            font-weight: bold;
          }

          .carriage-type {
            display: block;
            color: #909399;
          }

          &.carriage-mc1,
          &.carriage-mc2 {
            background: #e6f7ff;
            border-color: #91d5ff;
          }

          &.carriage-mp {
            background: #f6ffed;
            border-color: #b7eb8f;
          }

          &.carriage-m {
            background: #fff7e6;
            border-color: #ffd591;
          }
        }
      }

      .vehicle-info {
        margin-bottom: 15px;

        p {
          margin: 5px 0;
          color: #606266;
        }
      }

      .vehicle-actions {
        display: flex;
        gap: 10px;
      }
    }
  }

  .text-danger {
    color: #f56c6c;
  }

  .text-warning {
    color: #e6a23c;
  }
}
</style>