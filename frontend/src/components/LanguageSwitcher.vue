<template>
  <el-dropdown @command="handleCommand" placement="bottom">
    <span class="language-switcher">
      <el-icon class="el-icon--left">
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.94-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z" fill="currentColor"/>
        </svg>
      </el-icon>
      {{ currentLanguageName }}
      <el-icon class="el-icon--right"><arrow-down /></el-icon>
    </span>
    <template #dropdown>
      <el-dropdown-menu>
        <el-dropdown-item
          v-for="lang in languages"
          :key="lang.value"
          :command="lang.value"
          :disabled="lang.value === currentLanguage"
        >
          <span :class="{ 'font-bold': lang.value === currentLanguage }">
            {{ lang.label }}
          </span>
        </el-dropdown-item>
      </el-dropdown-menu>
    </template>
  </el-dropdown>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { ArrowDown } from '@element-plus/icons-vue'

const { locale, t } = useI18n()

const languages = [
  { value: 'zh-CN', label: '简体中文' },
  { value: 'en-US', label: 'English' }
]

const currentLanguage = computed(() => locale.value)
const currentLanguageName = computed(() => {
  const lang = languages.find(l => l.value === locale.value)
  return lang ? lang.label : 'Language'
})

const handleCommand = (lang: string) => {
  locale.value = lang
  localStorage.setItem('language', lang)

  // Update ElementPlus locale
  updateElementPlusLocale(lang)

  // Show success message
  ElMessage.success(
    lang === 'zh-CN' ? '语言切换成功' : 'Language changed successfully'
  )

  // Reload page to apply all changes (optional)
  // window.location.reload()
}

// Function to update ElementPlus locale dynamically
const updateElementPlusLocale = async (lang: string) => {
  const app = document.querySelector('#app')?.__vue_app__
  if (app) {
    if (lang === 'zh-CN') {
      const zhCn = await import('element-plus/dist/locale/zh-cn.mjs')
      app.config.globalProperties.$ELEMENT.locale = zhCn.default
    } else {
      const enUs = await import('element-plus/dist/locale/en.mjs')
      app.config.globalProperties.$ELEMENT.locale = enUs.default
    }
  }
}
</script>

<style scoped>
.language-switcher {
  display: inline-flex;
  align-items: center;
  cursor: pointer;
  padding: 0 12px;
  height: 32px;
  border-radius: 4px;
  transition: all 0.3s;
  color: var(--el-text-color-regular);
}

.language-switcher:hover {
  background-color: var(--el-fill-color-light);
  color: var(--el-color-primary);
}

.font-bold {
  font-weight: 600;
}
</style>