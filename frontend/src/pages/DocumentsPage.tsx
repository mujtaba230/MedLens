import { useEffect, useState } from 'react'
import { documents, entities } from '../services/api'

interface Doc {
  id: number
  filename: string
  document_type: string
  status: string
  created_at: string
}

interface Entity {
  id: number
  entity_type: string
  text: string
  normalized_name: string | null
  confidence: number | null
  codes: { code_system: string; code: string; name: string | null }[]
}

export default function DocumentsPage() {
  const [docs, setDocs] = useState<Doc[]>([])
  const [selectedDoc, setSelectedDoc] = useState<number | null>(null)
  const [docEntities, setDocEntities] = useState<Entity[]>([])
  const [processing, setProcessing] = useState<number | null>(null)

  useEffect(() => {
    documents.list().then((res) => setDocs(res.data))
  }, [])

  const handleProcess = async (id: number) => {
    setProcessing(id)
    try {
      await documents.process(id)
      const updated = await documents.list()
      setDocs(updated.data)
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Processing failed')
    } finally {
      setProcessing(null)
    }
  }

  const handleExtract = async (id: number) => {
    try {
      const res = await entities.extract(id)
      setSelectedDoc(id)
      setDocEntities(res.data.entities)
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Extraction failed')
    }
  }

  const handleView = async (id: number) => {
    try {
      const res = await entities.get(id)
      setSelectedDoc(id)
      setDocEntities(res.data.entities)
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to load entities')
    }
  }

  const statusBadge = (status: string) => {
    const map: Record<string, string> = {
      pending: 'badge-yellow',
      ocr: 'badge-yellow',
      extracting: 'badge-yellow',
      mapping: 'badge-yellow',
      completed: 'badge-green',
      failed: 'badge-red',
    }
    return <span className={`badge ${map[status] || 'badge-blue'}`}>{status}</span>
  }

  return (
    <div>
      <div className="card">
        <h2>Documents</h2>
        <table className="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Filename</th>
              <th>Type</th>
              <th>Status</th>
              <th>Created</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {docs.map((d) => (
              <tr key={d.id}>
                <td>{d.id}</td>
                <td>{d.filename}</td>
                <td>{d.document_type}</td>
                <td>{statusBadge(d.status)}</td>
                <td>{new Date(d.created_at).toLocaleString()}</td>
                <td>
                  <button className="btn" style={{ padding: '6px 12px', fontSize: '0.8rem' }} onClick={() => handleProcess(d.id)} disabled={processing === d.id}>
                    {processing === d.id ? 'Processing...' : 'Process'}
                  </button>{' '}
                  <button className="btn btn-secondary" style={{ padding: '6px 12px', fontSize: '0.8rem' }} onClick={() => handleExtract(d.id)}>
                    Extract
                  </button>{' '}
                  <button className="btn" style={{ padding: '6px 12px', fontSize: '0.8rem' }} onClick={() => handleView(d.id)}>
                    View
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {selectedDoc !== null && (
        <div className="card">
          <h2>Extracted Entities (Doc #{selectedDoc})</h2>
          {docEntities.length === 0 ? (
            <p>No entities found. Run extraction first.</p>
          ) : (
            <div className="entity-list">
              {docEntities.map((e) => (
                <div key={e.id} className="entity-item">
                  <div>
                    <span className={`entity-type badge badge-blue`}>{e.entity_type}</span>
                    <div style={{ marginTop: 4, fontWeight: 500 }}>{e.text}</div>
                    {e.normalized_name && <div style={{ fontSize: '0.85rem', color: '#6b7280' }}>→ {e.normalized_name}</div>}
                    {e.codes.length > 0 && (
                      <div style={{ marginTop: 6 }}>
                        {e.codes.map((c, i) => (
                          <span key={i} className="code-tag">{c.code_system}: {c.code}</span>
                        ))}
                      </div>
                    )}
                  </div>
                  <span className="badge badge-green">{e.confidence ? `${(e.confidence * 100).toFixed(0)}%` : 'N/A'}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
