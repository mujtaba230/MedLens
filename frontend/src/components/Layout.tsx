import { Outlet, Link, useLocation } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'

export default function Layout() {
  const { user, logout } = useAuth()
  const location = useLocation()

  const navLink = (to: string, label: string) => (
    <Link
      to={to}
      className={location.pathname === to ? 'active' : ''}
    >
      {label}
    </Link>
  )

  return (
    <>
      <header className="navbar">
        <h1>Healthcare Doc Intelligence</h1>
        <nav>
          {navLink('/', 'Upload')}
          {navLink('/documents', 'Documents')}
          {navLink('/search', 'Search')}
          {(user?.role === 'admin' || user?.role === 'auditor') && navLink('/audit', 'Audit')}
          {user && (
            <span style={{ marginLeft: 20, fontSize: '0.85rem', opacity: 0.8 }}>
              {user.username} ({user.role}){' '}
              <button onClick={logout} style={{ background: 'none', border: 'none', color: '#4ecca3', cursor: 'pointer', textDecoration: 'underline' }}>
                Logout
              </button>
            </span>
          )}
        </nav>
      </header>
      <main className="container">
        <Outlet />
      </main>
    </>
  )
}
