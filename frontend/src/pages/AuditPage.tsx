import { useEffect, useState } from 'react'
import { audit } from '../services/api'

interface Log {
  id: number
  username: string
  action: string
  resource_type: string | null
  resource_id: number | null
  query_text: string | null
  accessed_documents: number[]
  ip_address: string | null
  timestamp: string
}

export default function AuditPage() {
  const [logs, setLogs] = useState<Log[]>([])
  const [filterAction, setFilterAction] = useState('')

  useEffect(() => {
    audit.logs(filterAction ? { action: filterAction } : undefined).then((res) => setLogs(res.data))
  }, [filterAction])

  return (
    <div className="card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <h2>Audit Logs</h2>
        <select className="input" style={{ width: 160, marginBottom: 0 }} value={filterAction} onChange={(e) => setFilterAction(e.target.value)}>
          <option value="">All Actions</option>
          <option value="LOGIN">Login</option>
          <option value="UPLOAD">Upload</option>
          <option value="PROCESS">Process</option>
          <option value="EXTRACT">Extract</option>
          <option value="QUERY">Query</option>
          <option value="VIEW">View</option>
        </select>
      </div>
      <table className="table">
        <thead>
          <tr>
            <th>ID</th>
            <th>User</th>
            <th>Action</th>
            <th>Resource</th>
            <th>Query</th>
            <th>Docs</th>
            <th>IP</th>
            <th>Timestamp</th>
          </tr>
        </thead>
        <tbody>
          {logs.map((l) => (
            <tr key={l.id}>
              <td>{l.id}</td>
              <td>{l.username}</td>
              <td><span className="badge badge-blue">{l.action}</span></td>
              <td>{l.resource_type ? `${l.resource_type} #${l.resource_id}` : '-'}</td>
              <td style={{ maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {l.query_text || '-'}
              </td>
              <td>{l.accessed_documents.join(', ') || '-'}</td>
              <td>{l.ip_address || '-'}</td>
              <td>{new Date(l.timestamp).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
