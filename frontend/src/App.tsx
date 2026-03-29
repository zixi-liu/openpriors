import { Routes, Route, Navigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import { ThemeProvider } from './context/ThemeContext.tsx'
import Sidebar from './components/Sidebar.tsx'
import CapturePage from './pages/CapturePage.tsx'
import PriorsPage from './pages/PriorsPage.tsx'
import SettingsPage from './pages/SettingsPage.tsx'

export default function App() {
  const [materials, setMaterials] = useState<{ id: string; title: string; isActive: boolean }[]>([])
  const [sessions] = useState<{ id: string; title: string; date: string }[]>([])

  // Load priors as materials for the sidebar
  useEffect(() => {
    fetch('/api/priors')
      .then(r => r.json())
      .then(data => {
        if (data.success && data.priors) {
          const uniqueSources = new Map<string, string>()
          for (const p of data.priors) {
            if (p.source_title && !uniqueSources.has(p.source_title)) {
              uniqueSources.set(p.source_title, p.id)
            }
          }
          setMaterials(
            Array.from(uniqueSources.entries()).map(([title, id]) => ({
              id,
              title,
              isActive: true,
            }))
          )
        }
      })
      .catch(() => {})
  }, [])

  const toggleMaterial = (id: string) => {
    setMaterials(prev =>
      prev.map(m => m.id === id ? { ...m, isActive: !m.isActive } : m)
    )
  }

  return (
    <ThemeProvider>
      <div className="h-screen flex" style={{ background: 'var(--op-bg)', color: 'var(--op-font-color)', fontFamily: 'var(--op-font-family)' }}>
        <Sidebar
          materials={materials}
          sessions={sessions}
          onToggleMaterial={toggleMaterial}
        />
        <main className="flex-1 overflow-auto">
          <Routes>
            <Route path="/" element={<Navigate to="/capture" />} />
            <Route path="/capture" element={<CapturePage />} />
            <Route path="/priors" element={<PriorsPage />} />
            <Route path="/settings" element={<SettingsPage />} />
          </Routes>
        </main>
      </div>
    </ThemeProvider>
  )
}
