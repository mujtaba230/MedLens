import { useState } from 'react'
import { useAuth } from '../hooks/useAuth'
import { auth } from '../services/api'

export default function LoginPage() {
  const [mode, setMode] = useState<'login' | 'register'>('login')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [email, setEmail] = useState('')
  const [role, setRole] = useState('doctor')
  const [error, setError] = useState('')
  const { login } = useAuth()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    try {
      if (mode === 'login') {
        const res = await auth.login(username, password)
        login(res.data.access_token)
      } else {
        await auth.register({ username, email, password, role })
        const res = await auth.login(username, password)
        login(res.data.access_token)
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Authentication failed')
    }
  }

  return (
    <div className="card login-form">
      <h2>{mode === 'login' ? 'Sign In' : 'Create Account'}</h2>
      {error && <p style={{ color: '#b91c1c', marginBottom: 12, fontSize: '0.9rem' }}>{error}</p>}
      <form onSubmit={handleSubmit}>
        <input
          className="input"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
        />
        {mode === 'register' && (
          <>
            <input
              className="input"
              placeholder="Email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
            <select className="input" value={role} onChange={(e) => setRole(e.target.value)}>
              <option value="doctor">Doctor</option>
              <option value="admin">Admin</option>
              <option value="auditor">Auditor</option>
            </select>
          </>
        )}
        <input
          className="input"
          placeholder="Password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        <button type="submit" className="btn" style={{ width: '100%' }}>
          {mode === 'login' ? 'Sign In' : 'Register'}
        </button>
      </form>
      <p style={{ marginTop: 16, textAlign: 'center', fontSize: '0.85rem' }}>
        {mode === 'login' ? (
          <>
            No account?{' '}
            <button onClick={() => setMode('register')} style={{ background: 'none', border: 'none', color: '#1e40af', cursor: 'pointer', textDecoration: 'underline' }}>
              Register
            </button>
          </>
        ) : (
          <>
            Have an account?{' '}
            <button onClick={() => setMode('login')} style={{ background: 'none', border: 'none', color: '#1e40af', cursor: 'pointer', textDecoration: 'underline' }}>
              Sign In
            </button>
          </>
        )}
      </p>
    </div>
  )
}
