// Theme initialization - runs before CSS is painted to prevent flickering
(() => {
  const key = 'chle-theme'
  const allowed = ['light', 'dark', 'system']
  const system = window.matchMedia('(prefers-color-scheme: dark)')
  let preference = 'system'
  try {
    const saved = localStorage.getItem(key)
    if (allowed.includes(saved)) preference = saved
  } catch { /* Storage unavailable */ }

  function apply() {
    const theme = preference === 'system' ? (system.matches ? 'dark' : 'light') : preference
    document.documentElement.dataset.theme = theme
    document.querySelector('meta[name="theme-color"]')?.setAttribute('content', theme === 'dark' ? '#10151e' : '#f4f6fa')
    document.querySelectorAll('[data-theme-choice]').forEach(button => {
      button.setAttribute('aria-pressed', String(button.dataset.themeChoice === preference))
    })
  }

  apply()
  system.addEventListener('change', () => { if (preference === 'system') apply() })
  window.addEventListener('storage', event => {
    if (event.key === key || event.key === null) {
      preference = allowed.includes(event.newValue) ? event.newValue : 'system'
      apply()
    }
  })
  document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('[data-theme-choice]').forEach(button => {
      button.addEventListener('click', () => {
        preference = button.dataset.themeChoice
        try { localStorage.setItem(key, preference) } catch {}
        apply()
      })
    })
    apply()
  })
})()
