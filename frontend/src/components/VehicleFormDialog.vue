<template>
  <el-dialog
    v-model="dialogVisible"
    :title="isEdit ? '编辑车辆信息' : '新增车辆信息'"
    width="90%"
    :close-on-click-modal="false"
    destroy-on-close
    @close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="formData"
      :rules="rules"
      label-width="140px"
      class="vehicle-form"
    >
      <!-- 基本信息 -->
      <el-card shadow="never" class="form-section">
        <template #header>
          <div class="card-header">
            <span>基本信息</span>
            <el-tag type="info">项目代码: MMM-SL</el-tag>
          </div>
        </template>

        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="车辆类型" prop="vehicleType">
              <el-select
                v-model="formData.vehicleType"
                placeholder="请选择车辆类型"
                @change="handleVehicleTypeChange"
              >
                <el-option label="客运车辆" value="passenger" />
                <el-option label="维护车辆" value="maintenance" />
                <el-option label="特种车辆" value="special" />
              </el-select>
            </el-form-item>
          </el-col>

          <el-col :span="8">
            <el-form-item label="列车编号" prop="trainNumber">
              <el-select
                v-model="formData.trainNumber"
                placeholder="请选择列车编号"
                filterable
                :disabled="isEdit"
              >
                <el-option
                  v-for="i in 16"
                  :key="i"
                  :label="`Tr${String(i).padStart(2, '0')}`"
                  :value="`Tr${String(i).padStart(2, '0')}`"
                  :disabled="isTrainNumberUsed(`Tr${String(i).padStart(2, '0')}`)"
                >
                  <span>{{ `Tr${String(i).padStart(2, '0')}` }}</span>
                  <span v-if="isTrainNumberUsed(`Tr${String(i).padStart(2, '0')}`)" class="text-gray-400">
                    (已使用)
                  </span>
                </el-option>
              </el-select>
            </el-form-item>
          </el-col>

          <el-col :span="8">
            <el-form-item label="运营线路" prop="line">
              <el-input v-model="formData.line" placeholder="如: 1号线" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="车辆段" prop="depot">
              <el-input v-model="formData.depot" placeholder="请输入车辆段" />
            </el-form-item>
          </el-col>

          <el-col :span="8">
            <el-form-item label="制造商" prop="manufacturer">
              <el-select
                v-model="formData.manufacturer"
                placeholder="请选择制造商"
                filterable
                allow-create
              >
                <el-option label="中车集团" value="CRRC" />
                <el-option label="西门子" value="Siemens" />
                <el-option label="阿尔斯通" value="Alstom" />
                <el-option label="庞巴迪" value="Bombardier" />
                <el-option label="川崎重工" value="Kawasaki" />
              </el-select>
            </el-form-item>
          </el-col>

          <el-col :span="8">
            <el-form-item label="车辆状态" prop="status">
              <el-select v-model="formData.status" placeholder="请选择状态">
                <el-option label="运营中" value="in_service" />
                <el-option label="维护中" value="maintenance" />
                <el-option label="备用" value="standby" />
                <el-option label="退役" value="retired" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="制造日期" prop="manufactureDate">
              <el-date-picker
                v-model="formData.manufactureDate"
                type="date"
                placeholder="选择日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
              />
            </el-form-item>
          </el-col>

          <el-col :span="8">
            <el-form-item label="投运日期" prop="commissionDate">
              <el-date-picker
                v-model="formData.commissionDate"
                type="date"
                placeholder="选择日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
              />
            </el-form-item>
          </el-col>

          <el-col :span="8">
            <el-form-item label="总里程(km)" prop="totalMileage">
              <el-input-number
                v-model="formData.totalMileage"
                :min="0"
                :precision="2"
                :step="100"
                placeholder="0.00"
              />
            </el-form-item>
          </el-col>
        </el-row>
      </el-card>

      <!-- 编组信息 -->
      <el-card shadow="never" class="form-section">
        <template #header>
          <div class="card-header">
            <span>编组信息</span>
            <el-button
              v-if="!isEdit"
              type="primary"
              size="small"
              @click="autoGenerateFormation"
            >
              自动生成12编组
            </el-button>
          </div>
        </template>

        <el-form-item label="编组类型" prop="formation.formationType">
          <el-radio-group v-model="formData.formation.formationType" @change="handleFormationChange">
            <el-radio-button label="6编组">6编组</el-radio-button>
            <el-radio-button label="8编组">8编组</el-radio-button>
            <el-radio-button label="12编组">12编组 (标准)</el-radio-button>
          </el-radio-group>
        </el-form-item>

        <el-table
          :data="formData.formation.carriages"
          border
          stripe
          max-height="300"
          class="carriage-table"
        >
          <el-table-column prop="position" label="位置" width="80" align="center" />
          <el-table-column prop="carriageNumber" label="车厢编号" width="120">
            <template #default="{ row }">
              <el-input
                v-model="row.carriageNumber"
                placeholder="SL****"
                size="small"
                :disabled="isEdit"
              />
            </template>
          </el-table-column>
          <el-table-column prop="carriageType" label="车厢类型" width="120">
            <template #default="{ row }">
              <el-select v-model="row.carriageType" size="small">
                <el-option label="MC1 (带司机室动车)" value="MC1" />
                <el-option label="MC2 (带司机室动车)" value="MC2" />
                <el-option label="M (动车)" value="M" />
                <el-option label="MP (带受电弓动车)" value="MP" />
                <el-option label="T (拖车)" value="T" />
                <el-option label="TC (带司机室拖车)" value="TC" />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column prop="manufacturer" label="制造商" width="150">
            <template #default="{ row }">
              <el-input v-model="row.manufacturer" placeholder="制造商" size="small" />
            </template>
          </el-table-column>
          <el-table-column prop="manufactureDate" label="制造日期" width="150">
            <template #default="{ row }">
              <el-date-picker
                v-model="row.manufactureDate"
                type="date"
                placeholder="选择日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                size="small"
              />
            </template>
          </el-table-column>
          <el-table-column prop="serialNumber" label="序列号" min-width="150">
            <template #default="{ row }">
              <el-input v-model="row.serialNumber" placeholder="序列号" size="small" />
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="120">
            <template #default="{ row }">
              <el-select v-model="row.status" size="small">
                <el-option label="运营中" value="in_service" />
                <el-option label="维护中" value="maintenance" />
                <el-option label="备用" value="standby" />
                <el-option label="退役" value="retired" />
              </el-select>
            </template>
          </el-table-column>
        </el-table>
      </el-card>

      <!-- 维护信息 -->
      <el-card shadow="never" class="form-section">
        <template #header>
          <span>维护信息</span>
        </template>

        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="维护等级" prop="maintenanceLevel">
              <el-select v-model="formData.maintenanceLevel" placeholder="请选择维护等级">
                <el-option label="日检" value="daily" />
                <el-option label="周检" value="weekly" />
                <el-option label="月检" value="monthly" />
                <el-option label="季检" value="quarterly" />
                <el-option label="年检" value="yearly" />
              </el-select>
            </el-form-item>
          </el-col>

          <el-col :span="8">
            <el-form-item label="上次维护日期">
              <el-date-picker
                v-model="formData.lastMaintenanceDate"
                type="date"
                placeholder="选择日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
              />
            </el-form-item>
          </el-col>

          <el-col :span="8">
            <el-form-item label="下次维护日期">
              <el-date-picker
                v-model="formData.nextMaintenanceDate"
                type="date"
                placeholder="选择日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="24">
            <el-form-item label="备注">
              <el-input
                v-model="formData.notes"
                type="textarea"
                :rows="3"
                placeholder="请输入备注信息"
              />
            </el-form-item>
          </el-col>
        </el-row>
      </el-card>

      <!-- 特种车辆专用信息 -->
      <el-card v-if="formData.vehicleType === 'special'" shadow="never" class="form-section">
        <template #header>
          <span>特种车辆信息</span>
        </template>

        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="特种类型" prop="specialType">
              <el-select v-model="formData.specialType" placeholder="请选择特种类型">
                <el-option label="钢轨打磨车" value="rail_grinding" />
                <el-option label="轨道检测车" value="track_inspection" />
                <el-option label="救援车" value="rescue" />
                <el-option label="工程车" value="engineering" />
                <el-option label="清洗车" value="cleaning" />
              </el-select>
            </el-form-item>
          </el-col>

          <el-col :span="8">
            <el-form-item label="最高速度(km/h)">
              <el-input-number v-model="formData.maxSpeed" :min="0" :max="200" />
            </el-form-item>
          </el-col>

          <el-col :span="8">
            <el-form-item label="作业速度(km/h)">
              <el-input-number v-model="formData.workSpeed" :min="0" :max="100" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="特殊功能">
          <el-checkbox-group v-model="formData.specialFeatures">
            <el-checkbox label="夜间作业">夜间作业</el-checkbox>
            <el-checkbox label="远程控制">远程控制</el-checkbox>
            <el-checkbox label="自动作业">自动作业</el-checkbox>
            <el-checkbox label="数据采集">数据采集</el-checkbox>
            <el-checkbox label="应急救援">应急救援</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
      </el-card>
    </el-form>

    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" @click="handleSubmit">
          {{ isEdit ? '更新' : '创建' }}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import {
  Vehicle,
  VehicleType,
  VehicleStatus,
  CarriageType,
  CarriageNumberGenerator,
  VehicleUtils
} from '@/types/vehicle'

const props = defineProps<{
  modelValue: boolean
  vehicle?: Vehicle
  existingTrainNumbers?: string[]
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'save': [vehicle: Vehicle]
}>()

const formRef = ref<FormInstance>()
const dialogVisible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const isEdit = computed(() => !!props.vehicle?.id)

// 表单数据
const formData = reactive<Vehicle>({
  trainNumber: '',
  projectCode: 'MMM-SL',
  vehicleType: VehicleType.PASSENGER,
  formation: {
    formationType: '12编组',
    carriages: []
  },
  line: '',
  depot: '',
  manufacturer: '',
  manufactureDate: '',
  commissionDate: '',
  totalMileage: 0,
  status: VehicleStatus.IN_SERVICE,
  maintenanceLevel: 'monthly',
  notes: '',
  // 特种车辆字段
  specialType: undefined,
  maxSpeed: undefined,
  workSpeed: undefined,
  specialFeatures: []
})

// 表单验证规则
const rules: FormRules = {
  vehicleType: [
    { required: true, message: '请选择车辆类型', trigger: 'change' }
  ],
  trainNumber: [
    { required: true, message: '请选择列车编号', trigger: 'change' },
    {
      validator: (rule, value, callback) => {
        if (!VehicleUtils.validateTrainNumber(value)) {
          callback(new Error('列车编号格式不正确'))
        } else {
          callback()
        }
      },
      trigger: 'change'
    }
  ],
  line: [
    { required: true, message: '请输入运营线路', trigger: 'blur' }
  ],
  manufacturer: [
    { required: true, message: '请选择制造商', trigger: 'change' }
  ],
  manufactureDate: [
    { required: true, message: '请选择制造日期', trigger: 'change' }
  ],
  commissionDate: [
    { required: true, message: '请选择投运日期', trigger: 'change' }
  ],
  status: [
    { required: true, message: '请选择车辆状态', trigger: 'change' }
  ],
  'formation.formationType': [
    { required: true, message: '请选择编组类型', trigger: 'change' }
  ]
}

// 检查列车编号是否已使用
const isTrainNumberUsed = (trainNumber: string): boolean => {
  if (isEdit.value && trainNumber === props.vehicle?.trainNumber) {
    return false
  }
  return props.existingTrainNumbers?.includes(trainNumber) || false
}

// 处理车辆类型变更
const handleVehicleTypeChange = (type: VehicleType) => {
  if (type === VehicleType.SPECIAL) {
    // 显示特种车辆的额外字段
    ElMessage.info('已切换到特种车辆模式，请填写额外信息')
  }
}

// 处理编组类型变更
const handleFormationChange = (formationType: string) => {
  const carriageCount = formationType === '6编组' ? 6 : formationType === '8编组' ? 8 : 12

  // 调整车厢数组长度
  if (formData.formation.carriages.length > carriageCount) {
    formData.formation.carriages = formData.formation.carriages.slice(0, carriageCount)
  } else {
    while (formData.formation.carriages.length < carriageCount) {
      formData.formation.carriages.push({
        carriageNumber: '',
        carriageType: CarriageType.T,
        position: formData.formation.carriages.length + 1,
        status: VehicleStatus.IN_SERVICE
      })
    }
  }
}

// 自动生成编组
const autoGenerateFormation = () => {
  if (!formData.trainNumber) {
    ElMessage.warning('请先选择列车编号')
    return
  }

  const trainNum = parseInt(formData.trainNumber.replace('Tr', ''))
  const carriages = CarriageNumberGenerator.generateFormation(trainNum, '12编组')

  // 复制制造商和日期到每个车厢
  carriages.forEach(carriage => {
    carriage.manufacturer = formData.manufacturer
    carriage.manufactureDate = formData.manufactureDate
  })

  formData.formation.carriages = carriages
  ElMessage.success('已自动生成12编组车厢编号')
}

// 提交表单
const handleSubmit = async () => {
  await formRef.value?.validate((valid) => {
    if (valid) {
      // 验证车厢编号
      const invalidCarriages = formData.formation.carriages.filter(
        c => c.carriageNumber && !VehicleUtils.validateCarriageNumber(c.carriageNumber)
      )

      if (invalidCarriages.length > 0) {
        ElMessage.error('存在无效的车厢编号，请检查')
        return
      }

      emit('save', { ...formData })
      ElMessage.success(isEdit.value ? '更新成功' : '创建成功')
      handleClose()
    }
  })
}

// 关闭对话框
const handleClose = () => {
  formRef.value?.resetFields()
  dialogVisible.value = false
}

// 监听vehicle属性变化，填充表单
watch(() => props.vehicle, (newVal) => {
  if (newVal && isEdit.value) {
    Object.assign(formData, newVal)
  }
}, { immediate: true })

// 初始化编组
watch(dialogVisible, (val) => {
  if (val && !isEdit.value) {
    handleFormationChange('12编组')
  }
})
</script>

<style scoped lang="scss">
.vehicle-form {
  .form-section {
    margin-bottom: 20px;

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
  }

  .carriage-table {
    margin-top: 10px;
  }

  .text-gray-400 {
    color: #909399;
    margin-left: 8px;
  }
}

.dialog-footer {
  padding: 20px;
  text-align: right;
}

:deep(.el-dialog__body) {
  max-height: 70vh;
  overflow-y: auto;
}
</style>