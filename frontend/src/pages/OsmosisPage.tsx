import { useState, useRef, useEffect } from 'react'

interface Message {
  role: 'user' | 'assistant'
  content: string
  options?: Option[]
}

interface Option {
  title: string
  description: string
  type: string
}

export default function OsmosisPage() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [started, setStarted] = useState(false)
  const scrollRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' })
  }, [messages])

  const startSession = async () => {
    setStarted(true)
    setLoading(true)
    try {
      const res = await fetch('/api/osmosis/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          conversation: [],
          message: "I'd like to work on integrating some of my learnings into my life.",
        }),
      })
      const data = await res.json()
      if (data.success) {
        setMessages([{ role: 'assistant', content: data.message, options: data.options }])
      }
    } catch {
      setMessages([{ role: 'assistant', content: 'Could not connect to server.' }])
    } finally {
      setLoading(false)
      setTimeout(() => inputRef.current?.focus(), 100)
    }
  }

  const sendMessage = async () => {
    if (!input.trim() || loading) return
    const userMsg = input.trim()
    setInput('')

    const newMessages: Message[] = [...messages, { role: 'user', content: userMsg }]
    setMessages(newMessages)
    setLoading(true)

    try {
      // Build conversation for API (just role + content)
      const conversation = newMessages.map(m => ({ role: m.role, content: m.content }))

      const res = await fetch('/api/osmosis/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          conversation: conversation.slice(0, -1), // history without the last user msg
          message: userMsg,
        }),
      })
      const data = await res.json()
      if (data.success) {
        setMessages([...newMessages, { role: 'assistant', content: data.message, options: data.options }])
      }
    } catch {
      setMessages([...newMessages, { role: 'assistant', content: 'Something went wrong.' }])
    } finally {
      setLoading(false)
    }
  }

  const selectOption = (option: Option) => {
    setInput(`I'd like to: ${option.title}`)
    setTimeout(() => inputRef.current?.focus(), 50)
  }

  if (!started) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center max-w-md px-6">
          <h2 className="font-serif text-2xl font-semibold mb-3" style={{ color: 'var(--op-font-color)' }}>
            Osmosis Session
          </h2>
          <p className="text-sm mb-8" style={{ color: 'var(--op-font-color)', opacity: 0.5 }}>
            AI will explore your learning materials, find connections, and help you integrate knowledge into your daily life.
          </p>
          <button
            onClick={startSession}
            className="px-6 py-3 text-sm font-medium text-white bg-gray-900 rounded-lg hover:bg-gray-800 transition-colors"
          >
            Start Session
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="flex-1 flex flex-col h-full">
      {/* Messages */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto px-6 py-8 scrollbar-hide">
        <div className="max-w-2xl mx-auto space-y-6">
          {messages.map((msg, i) => (
            <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[80%] ${msg.role === 'user' ? '' : ''}`}>
                {/* Message */}
                <div
                  className={`rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                    msg.role === 'user'
                      ? 'bg-gray-900 text-white rounded-br-md'
                      : 'bg-[#F7F7F5] rounded-bl-md'
                  }`}
                  style={msg.role === 'assistant' ? { color: 'var(--op-font-color)' } : {}}
                >
                  {msg.content}
                </div>

                {/* Options */}
                {msg.options && msg.options.length > 0 && (
                  <div className="mt-3 space-y-2">
                    {msg.options.map((opt, j) => (
                      <button
                        key={j}
                        onClick={() => selectOption(opt)}
                        className="w-full text-left p-3 rounded-xl border border-[#E3E2E0] hover:bg-[#F7F7F5] transition-colors"
                      >
                        <p className="text-sm font-medium" style={{ color: 'var(--op-font-color)' }}>{opt.title}</p>
                        <p className="text-xs mt-0.5" style={{ color: 'var(--op-font-color)', opacity: 0.5 }}>{opt.description}</p>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex justify-start">
              <div className="bg-[#F7F7F5] rounded-2xl rounded-bl-md px-4 py-3">
                <div className="flex gap-1">
                  <span className="w-2 h-2 rounded-full bg-gray-400 animate-bounce" style={{ animationDelay: '0ms' }} />
                  <span className="w-2 h-2 rounded-full bg-gray-400 animate-bounce" style={{ animationDelay: '150ms' }} />
                  <span className="w-2 h-2 rounded-full bg-gray-400 animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Input */}
      <div className="border-t border-[#E3E2E0] px-6 py-4">
        <div className="max-w-2xl mx-auto flex gap-3">
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && sendMessage()}
            placeholder="Tell the agent what you'd like to work on..."
            disabled={loading}
            className="flex-1 text-sm px-4 py-3 rounded-xl border border-[#E3E2E0] focus:outline-none focus:border-gray-400 disabled:opacity-50"
            style={{ background: 'var(--op-bg)', color: 'var(--op-font-color)' }}
          />
          <button
            onClick={sendMessage}
            disabled={loading || !input.trim()}
            className="px-5 py-3 text-sm font-medium text-white bg-gray-900 rounded-xl hover:bg-gray-800 disabled:opacity-40 transition-colors"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  )
}
