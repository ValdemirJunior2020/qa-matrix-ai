import { useEffect, useState } from 'react'
import {
  MessageSquarePlus,
  MessagesSquare,
  FileSpreadsheet,
  Shield,
  Settings,
  Server,
  LogOut,
} from 'lucide-react'

import { useAuth } from './hooks/useAuth'
import { api } from './services/api'

import Login from './pages/Login'
import Chat from './pages/Chat'
import Admin from './pages/Admin'
import History from './pages/History'
import SettingsPage from './pages/Settings'

import SourcePanel from './components/SourcePanel'
import StatusPill from './components/StatusPill'

export default function App() {
  const { user, login, logout } = useAuth()

  const [page, setPage] = useState('chat')
  const [matrix, setMatrix] = useState(null)
  const [health, setHealth] = useState(null)
  const [source, setSource] = useState(null)

  useEffect(() => {
    if (!user) return

    let cancelled = false

    const loadAppData = async () => {
      try {
        const [matrixData, healthData] = await Promise.all([
          api.matrix(),
          api.health(),
        ])

        if (!cancelled) {
          setMatrix(matrixData)
          setHealth(healthData)
        }
      } catch (error) {
        console.error('Failed to load app data:', error)
      }
    }

    loadAppData()

    return () => {
      cancelled = true
    }
  }, [user, page])

  if (!user) {
    return <Login onLogin={login} />
  }

  const nav = [
    ['chat', MessageSquarePlus, 'New Chat'],
    ['history', MessagesSquare, 'Chat History'],
    ['matrix', FileSpreadsheet, 'Matrix'],
    ['admin', Shield, 'Admin'],
    ['settings', Settings, 'Settings'],
    ['status', Server, 'Server Status'],
  ]

  const openSource = async (sourceInfo) => {
    try {
      const data = await api.source(sourceInfo.record_id)
      setSource(data)
    } catch (error) {
      console.error('Failed to load source:', error)
      setSource(sourceInfo)
    }
  }

  const renderPage = () => {
    if (page === 'admin') {
      if (user.role === 'admin') {
        return <Admin />
      }

      return <Chat matrix={matrix} onSource={openSource} />
    }

    if (page === 'settings') {
      if (user.role === 'admin') {
        return <SettingsPage />
      }

      return <Chat matrix={matrix} onSource={openSource} />
    }

    if (page === 'history') {
      return <History onSource={openSource} />
    }

    if (page === 'status') {
      return <Admin />
    }

    return <Chat matrix={matrix} onSource={openSource} />
  }

  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="logo">
          <div>QA</div>

          <span>
            Matrix AI
            <small>PRIVATE SERVER</small>
          </span>
        </div>

        <nav>
          {nav.map(([id, Icon, label]) => (
            <button
              key={id}
              className={page === id ? 'active' : ''}
              onClick={() => setPage(id)}
              type="button"
            >
              <Icon size={18} />
              {label}
            </button>
          ))}
        </nav>

        <div className="sidebar-foot">
          <StatusPill
            ok={health?.status === 'online'}
            label={
              health?.status === 'online'
                ? 'Server online'
                : 'Server offline'
            }
          />

          <button onClick={logout} type="button">
            <LogOut size={17} />
            Sign out
          </button>

          <small>{user.email}</small>
        </div>
      </aside>

      <main className="workspace">
        {renderPage()}
      </main>

      <SourcePanel
        source={source}
        onClose={() => setSource(null)}
      />
    </div>
  )
}