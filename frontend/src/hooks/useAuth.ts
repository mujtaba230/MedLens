import { useState, useEffect } from 'react'

interface User {
  username: string
  role: string
}

export function useAuth() {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (token) {
      try {
        const payload = JSON.parse(atob(token.split('.')[1]))
        setUser({ username: payload.sub, role: payload.role })
      } catch {
        localStorage.removeItem('token')
      }
    }
    setLoading(false)
  }, [])

  const login = (token: string) => {
    localStorage.setItem('token', token)
    const payload = JSON.parse(atob(token.split('.')[1]))
    setUser({ username: payload.sub, role: payload.role })
  }

  const logout = () => {
    localStorage.removeItem('token')
    setUser(null)
  }

  return { user, loading, login, logout }
}
