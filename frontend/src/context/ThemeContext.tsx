import { createContext, useContext, useState, useEffect, ReactNode } from 'react'

interface ThemeSettings {
  bgColor: string
  fontColor: string
  fontFamily: string
}

interface ThemeContextType {
  theme: ThemeSettings
  setTheme: (theme: ThemeSettings) => void
}

const DEFAULT_THEME: ThemeSettings = {
  bgColor: '#FDFBF7',
  fontColor: '#1a1a1a',
  fontFamily: 'Inter',
}

const STORAGE_KEY = 'openpriors-theme'

const ThemeContext = createContext<ThemeContextType | null>(null)

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setThemeState] = useState<ThemeSettings>(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY)
      return stored ? { ...DEFAULT_THEME, ...JSON.parse(stored) } : DEFAULT_THEME
    } catch {
      return DEFAULT_THEME
    }
  })

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(theme))

    const root = document.documentElement
    root.style.setProperty('--op-bg', theme.bgColor)
    root.style.setProperty('--op-font-color', theme.fontColor)
    root.style.setProperty('--op-font-family', `'${theme.fontFamily}', sans-serif`)
  }, [theme])

  const setTheme = (next: ThemeSettings) => setThemeState(next)

  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  )
}

export function useTheme() {
  const ctx = useContext(ThemeContext)
  if (!ctx) throw new Error('useTheme must be used within ThemeProvider')
  return ctx
}

export { DEFAULT_THEME }
export type { ThemeSettings }
