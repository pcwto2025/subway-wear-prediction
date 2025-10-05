import { computed } from 'vue'
import { useI18n as vueUseI18n } from 'vue-i18n'

/**
 * Enhanced i18n composition API with additional utilities
 */
export function useI18n() {
  const i18n = vueUseI18n()

  /**
   * Format message with parameters
   * @param key Translation key
   * @param params Parameters object
   * @returns Formatted message
   */
  const tm = (key: string, params?: Record<string, any>) => {
    return i18n.t(key, params)
  }

  /**
   * Get current language
   */
  const currentLanguage = computed(() => i18n.locale.value)

  /**
   * Check if current language is Chinese
   */
  const isZhCN = computed(() => i18n.locale.value === 'zh-CN')

  /**
   * Check if current language is English
   */
  const isEnUS = computed(() => i18n.locale.value === 'en-US')

  /**
   * Switch language
   */
  const switchLanguage = (lang: 'zh-CN' | 'en-US') => {
    i18n.locale.value = lang
    localStorage.setItem('language', lang)

    // Update document title if needed
    updateDocumentLang(lang)
  }

  /**
   * Toggle between languages
   */
  const toggleLanguage = () => {
    const newLang = isZhCN.value ? 'en-US' : 'zh-CN'
    switchLanguage(newLang)
  }

  /**
   * Update HTML document lang attribute
   */
  const updateDocumentLang = (lang: string) => {
    document.documentElement.lang = lang === 'zh-CN' ? 'zh' : 'en'
  }

  /**
   * Format date based on locale
   */
  const formatDate = (date: Date | string, format?: string) => {
    const d = typeof date === 'string' ? new Date(date) : date
    const options: Intl.DateTimeFormatOptions = format === 'short'
      ? { year: 'numeric', month: '2-digit', day: '2-digit' }
      : { year: 'numeric', month: 'long', day: 'numeric' }

    return new Intl.DateTimeFormat(
      i18n.locale.value === 'zh-CN' ? 'zh-CN' : 'en-US',
      options
    ).format(d)
  }

  /**
   * Format number based on locale
   */
  const formatNumber = (num: number, options?: Intl.NumberFormatOptions) => {
    return new Intl.NumberFormat(
      i18n.locale.value === 'zh-CN' ? 'zh-CN' : 'en-US',
      options
    ).format(num)
  }

  /**
   * Format currency based on locale
   */
  const formatCurrency = (amount: number) => {
    return formatNumber(amount, {
      style: 'currency',
      currency: i18n.locale.value === 'zh-CN' ? 'CNY' : 'USD'
    })
  }

  return {
    ...i18n,
    tm,
    currentLanguage,
    isZhCN,
    isEnUS,
    switchLanguage,
    toggleLanguage,
    formatDate,
    formatNumber,
    formatCurrency
  }
}

/**
 * Get validation message
 */
export function useValidationMessage() {
  const { t } = vueUseI18n()

  return {
    required: (field: string) => t('validation.required', { field }),
    minLength: (field: string, min: number) => t('validation.minLength', { field, min }),
    maxLength: (field: string, max: number) => t('validation.maxLength', { field, max }),
    email: () => t('validation.email'),
    number: () => t('validation.number'),
    integer: () => t('validation.integer'),
    positive: () => t('validation.positive'),
    range: (min: number, max: number) => t('validation.range', { min, max }),
    pattern: () => t('validation.pattern'),
    unique: () => t('validation.unique'),
    passwordMatch: () => t('validation.passwordMatch')
  }
}