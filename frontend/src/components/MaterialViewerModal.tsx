import { useState, useEffect } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

interface MaterialViewerModalProps {
  materialId: string
  onClose: () => void
}

interface Material {
  id: string
  title: string
  source_type: string
  content: string
  summary: string
  url: string
  author: string
  created_at: string
}

export default function MaterialViewerModal({ materialId, onClose }: MaterialViewerModalProps) {
  const [material, setMaterial] = useState<Material | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch(`/api/assets/materials/${materialId}`)
      .then(r => r.json())
      .then(data => {
        if (data.success) setMaterial(data.material)
      })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [materialId])

  const sourceTypeLabel: Record<string, { icon: string; label: string }> = {
    youtube: { icon: '🎬', label: 'YouTube' },
    url: { icon: '🌐', label: 'Article' },
    pdf: { icon: '📄', label: 'PDF' },
    text: { icon: '📝', label: 'Notes' },
    voice: { icon: '🎙️', label: 'Voice Reflection' },
    book: { icon: '📚', label: 'Book' },
  }

  const typeInfo = material ? (sourceTypeLabel[material.source_type] || sourceTypeLabel.text) : sourceTypeLabel.text

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-3xl w-full max-h-[80vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-[#E3E2E0]" style={{ background: 'var(--op-bg)' }}>
          <div>
            <h2 className="text-lg font-semibold" style={{ color: 'var(--op-font-color)' }}>
              {loading ? 'Loading...' : material?.title || 'Untitled'}
            </h2>
            {material && (
              <div className="flex items-center gap-2 mt-1">
                <span className="px-2 py-0.5 text-xs rounded" style={{ background: 'rgba(0,0,0,0.05)', color: 'var(--op-font-color)', opacity: 0.6 }}>
                  {typeInfo.icon} {typeInfo.label}
                </span>
                {material.author && (
                  <span className="text-xs" style={{ color: 'var(--op-font-color)', opacity: 0.4 }}>
                    by {material.author}
                  </span>
                )}
              </div>
            )}
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-lg hover:bg-[#00000008] transition-colors"
            style={{ color: 'var(--op-font-color)', opacity: 0.5 }}
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Summary */}
        {material?.summary && (
          <div className="px-4 py-2 border-b border-[#E3E2E0]" style={{ background: 'rgba(0,0,0,0.02)' }}>
            <p className="text-xs font-medium mb-1" style={{ color: 'var(--op-font-color)', opacity: 0.4 }}>Summary</p>
            <p className="text-sm" style={{ color: 'var(--op-font-color)', opacity: 0.7 }}>{material.summary}</p>
          </div>
        )}

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-4">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="w-5 h-5 border-2 border-gray-200 border-t-gray-500 rounded-full animate-spin" />
            </div>
          ) : material ? (
            <div className="prose prose-sm max-w-none" style={{ color: 'var(--op-font-color)' }}>
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {material.content}
              </ReactMarkdown>
            </div>
          ) : (
            <p className="text-sm text-center py-12" style={{ color: 'var(--op-font-color)', opacity: 0.4 }}>
              Material not found
            </p>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-3 border-t border-[#E3E2E0]" style={{ background: 'var(--op-bg)' }}>
          <div className="text-xs" style={{ color: 'var(--op-font-color)', opacity: 0.4 }}>
            {material?.url && (
              <a href={material.url} target="_blank" rel="noopener noreferrer"
                className="hover:underline flex items-center gap-1">
                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
                View original
              </a>
            )}
          </div>
          <button
            onClick={onClose}
            className="px-4 py-1.5 text-sm rounded-lg hover:bg-gray-100 transition-colors"
            style={{ color: 'var(--op-font-color)' }}
          >
            Close
          </button>
        </div>
      </div>
    </div>
  )
}
