import { useState, useRef } from 'react'
import ChatWindow from './components/ChatWindow'

export default function App() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const textareaRef = useRef(null)

  const sendMessage = async () => {
    const question = input.trim()
    if (!question || isLoading) return

    setMessages(prev => [...prev, { role: 'user', content: question }])
    setInput('')
    setIsLoading(true)

    try {
      const res = await fetch('/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question }),
      })

      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: 'Unknown error' }))
        const detail = err.detail?.error || err.detail || 'Request failed'
        setMessages(prev => [...prev, { role: 'assistant', data: { error: detail } }])
      } else {
        const data = await res.json()
        setMessages(prev => [...prev, { role: 'assistant', data }])
      }
    } catch {
      setMessages(prev => [...prev, { role: 'assistant', data: { error: 'Could not reach the server. Is the backend running?' } }])
    } finally {
      setIsLoading(false)
      textareaRef.current?.focus()
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <div className="flex flex-col h-screen max-w-3xl mx-auto">
      <header className="shrink-0 bg-white border-b border-slate-200 px-6 py-4 flex items-center gap-3 shadow-sm">
        <div className="h-8 w-8 rounded-full bg-blue-600 flex items-center justify-center text-white font-bold text-sm">
          FG
        </div>
        <div>
          <h1 className="font-semibold text-slate-900 leading-none">FinGuard RAG</h1>
          <p className="text-xs text-slate-500 mt-0.5">Indian financial regulations assistant</p>
        </div>
      </header>

      <ChatWindow messages={messages} isLoading={isLoading} />

      <div className="shrink-0 bg-white border-t border-slate-200 px-4 py-4">
        <div className="flex gap-2 items-end">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            rows={2}
            placeholder="Ask about home loans, insurance, UPI, mutual funds... (Enter to send, Shift+Enter for newline)"
            className="flex-1 resize-none rounded-xl border border-slate-300 px-3.5 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent placeholder:text-slate-400"
          />
          <button
            onClick={sendMessage}
            disabled={!input.trim() || isLoading}
            className="shrink-0 h-10 w-10 rounded-xl bg-blue-600 text-white flex items-center justify-center hover:bg-blue-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
              <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" />
            </svg>
          </button>
        </div>
        <p className="text-xs text-slate-400 mt-2 text-center">
          Every answer cites a source or admits uncertainty. Not financial advice.
        </p>
      </div>
    </div>
  )
}
