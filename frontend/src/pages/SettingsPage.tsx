import { useState } from 'react'
import { RotateCcw } from 'lucide-react'
import { useTheme, DEFAULT_THEME } from '../context/ThemeContext.tsx'

const FONT_OPTIONS = [
  'Inter',
  'Georgia',
  'Merriweather',
  'Lora',
  'Roboto',
  'Source Sans 3',
  'Fira Sans',
  'IBM Plex Sans',
  'system-ui',
  'monospace',
]

const PRESET_BG_COLORS = [
  '#FDFBF7', '#FFFFFF', '#F0F0F0', '#1a1a2e', '#0d1117',
  '#FFF8E7', '#F0FFF4', '#EFF6FF', '#FDF2F8', '#FFFBEB',
]

const PRESET_FONT_COLORS = [
  '#1a1a1a', '#333333', '#4a4a4a', '#e0e0e0', '#c9d1d9',
  '#2d3748', '#1e3a5f', '#3c1361', '#134e4a', '#7c2d12',
]

export default function SettingsPage() {
  const { theme, setTheme } = useTheme()
  const [local, setLocal] = useState(theme)

  const update = (partial: Partial<typeof local>) => {
    const next = { ...local, ...partial }
    setLocal(next)
    setTheme(next)
  }

  const reset = () => {
    setLocal(DEFAULT_THEME)
    setTheme(DEFAULT_THEME)
  }

  return (
    <div className="max-w-2xl mx-auto px-6 py-10">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h2 className="font-serif text-2xl font-semibold" style={{ color: 'var(--op-font-color)' }}>
            Appearance
          </h2>
          <p className="text-sm mt-1" style={{ color: 'var(--op-font-color)', opacity: 0.5 }}>
            Customize background, font, and colors
          </p>
        </div>
        <button
          onClick={reset}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm border border-[#E8DFD0] hover:bg-[#F0EDE7] transition-colors"
          style={{ color: 'var(--op-font-color)' }}
        >
          <RotateCcw size={13} />
          Reset
        </button>
      </div>

      {/* Preview */}
      <div
        className="rounded-xl border border-[#E8DFD0] p-6 mb-8"
        style={{
          backgroundColor: local.bgColor,
          color: local.fontColor,
          fontFamily: `'${local.fontFamily}', sans-serif`,
        }}
      >
        <p className="text-xs uppercase tracking-wide mb-2" style={{ opacity: 0.4 }}>Preview</p>
        <h3 className="font-semibold text-lg mb-1">The Two-Minute Rule</h3>
        <p className="text-sm" style={{ opacity: 0.7 }}>
          If a task takes less than two minutes, do it immediately instead of scheduling it.
        </p>
      </div>

      <div className="space-y-8">
        {/* Background Color */}
        <div>
          <label className="text-xs font-medium uppercase tracking-wide mb-3 block" style={{ color: 'var(--op-font-color)', opacity: 0.5 }}>
            Background Color
          </label>
          <div className="flex items-center gap-3 flex-wrap">
            {PRESET_BG_COLORS.map(c => (
              <button
                key={c}
                onClick={() => update({ bgColor: c })}
                className={`w-8 h-8 rounded-full border-2 transition-transform hover:scale-110 ${
                  local.bgColor === c ? 'border-gray-900 scale-110' : 'border-[#E8DFD0]'
                }`}
                style={{ backgroundColor: c }}
              />
            ))}
            <input
              type="color"
              value={local.bgColor}
              onChange={e => update({ bgColor: e.target.value })}
              className="w-8 h-8 rounded-full cursor-pointer border-0 p-0"
            />
          </div>
        </div>

        {/* Font Color */}
        <div>
          <label className="text-xs font-medium uppercase tracking-wide mb-3 block" style={{ color: 'var(--op-font-color)', opacity: 0.5 }}>
            Font Color
          </label>
          <div className="flex items-center gap-3 flex-wrap">
            {PRESET_FONT_COLORS.map(c => (
              <button
                key={c}
                onClick={() => update({ fontColor: c })}
                className={`w-8 h-8 rounded-full border-2 transition-transform hover:scale-110 ${
                  local.fontColor === c ? 'border-gray-900 scale-110' : 'border-[#E8DFD0]'
                }`}
                style={{ backgroundColor: c }}
              />
            ))}
            <input
              type="color"
              value={local.fontColor}
              onChange={e => update({ fontColor: e.target.value })}
              className="w-8 h-8 rounded-full cursor-pointer border-0 p-0"
            />
          </div>
        </div>

        {/* Font Family */}
        <div>
          <label className="text-xs font-medium uppercase tracking-wide mb-3 block" style={{ color: 'var(--op-font-color)', opacity: 0.5 }}>
            Font
          </label>
          <div className="grid grid-cols-2 gap-2">
            {FONT_OPTIONS.map(f => (
              <button
                key={f}
                onClick={() => update({ fontFamily: f })}
                className={`px-4 py-2.5 rounded-lg text-sm text-left border transition-colors ${
                  local.fontFamily === f
                    ? 'border-gray-900 bg-gray-900 text-white'
                    : 'border-[#E8DFD0] hover:border-gray-400'
                }`}
                style={{ fontFamily: `'${f}', sans-serif`, color: local.fontFamily === f ? undefined : 'var(--op-font-color)' }}
              >
                {f}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
