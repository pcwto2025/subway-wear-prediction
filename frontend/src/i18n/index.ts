import { createI18n } from 'vue-i18n'
import zhCN from './locales/zh-CN.json'
import enUS from './locales/en-US.json'

// Get saved language or detect browser language
const savedLang = localStorage.getItem('language')
const browserLang = navigator.language.toLowerCase()
const defaultLang = savedLang || (browserLang.includes('zh') ? 'zh-CN' : 'en-US')

const i18n = createI18n({
  legacy: false, // Use composition API
  locale: defaultLang,
  fallbackLocale: 'en-US',
  messages: {
    'zh-CN': zhCN,
    'en-US': enUS
  }
})

export default i18n

export function useI18n() {
  return i18n.global
}