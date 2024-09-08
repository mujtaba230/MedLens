import { useState } from 'react'
import { rag } from '../services/api'

interface Message {
  role: 'user' | 'assistant'
  content: string
  sources?: { document_id: number; score: number }[]
  latency?: number
}

export default function SearchPage() {
  const [query, setQuery] = useState('')
  const [messages, setMessages] = useState<Message[]>([])
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!query.trim() || loading) return

    const userMsg: Message = { role: 'user', content: query }
    setMessages((prev) => [...prev, userMsg])
    setLoading(true)
    setQuery('')

    try {
      const res = await rag.query(userMsg.content)
      const data = res.data
      const assistantMsg: Message = {
        role: 'assistant',
        content: data.answer,
        sources: data.sources,
        latency: data.latency_ms,
      }
      setMessages((prev) => [...prev, assistantMsg])
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: err.response?.data?.detail || 'Query failed' },
      ])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <div className="card">
        <h2>Clinical Search (RAG)</h2>
        <form onSubmit={handleSubmit} style={{ display: 'flex', gap: 12 }}>
          <input
            className="input"
            style={{ marginBottom: 0, flex: 1 }}
            placeholder="Ask a clinical question..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <button type="submit" className="btn" disabled={loading}>
            {loading ? 'Searching...' : 'Ask'}
          </button>
        </form>
      </div>

      {messages.length > 0 && (
        <div className="card chat-container">
          {messages.map((m, i) => (
            <div key={i} className={`chat-message ${m.role}`}>
              <div style={{ whiteSpace: 'pre-wrap' }}>{m.content}</div>
              {m.sources && m.sources.length > 0 && (
                <div style={{ marginTop: 8, fontSize: '0.8rem', opacity: 0.7 }}>
                  Sources: {m.sources.map((s) => `Doc #${s.document_id} (score: ${s.score.toFixed(3)})`).join(', ')}
                  {m.latency !== undefined && ` · ${m.latency.toFixed(0)}ms`}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
