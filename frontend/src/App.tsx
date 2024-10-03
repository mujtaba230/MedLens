import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import LoginPage from './pages/LoginPage'
import UploadPage from './pages/UploadPage'
import SearchPage from './pages/SearchPage'
import DocumentsPage from './pages/DocumentsPage'
import AuditPage from './pages/AuditPage'
import { useAuth } from './hooks/useAuth'

function App() {
  const { user, loading } = useAuth()

  if (loading) {
    return <div className="container" style={{ marginTop: 40 }}>Loading...</div>
  }

  return (
    <Routes>
      <Route path="/login" element={!user ? <LoginPage /> : <Navigate to="/" />} />
      <Route element={<Layout />}>
        <Route path="/" element={user ? <UploadPage /> : <Navigate to="/login" />} />
        <Route path="/documents" element={user ? <DocumentsPage /> : <Navigate to="/login" />} />
        <Route path="/search" element={user ? <SearchPage /> : <Navigate to="/login" />} />
        <Route path="/audit" element={user && (user.role === 'admin' || user.role === 'auditor') ? <AuditPage /> : <Navigate to="/" />} />
      </Route>
    </Routes>
  )
}

export default App
