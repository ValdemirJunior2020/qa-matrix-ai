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

  const [serverOnline, setServerOnline] = useState(false)
  const [checkingServer, setCheckingServer] = useState(false)
  const [wasOffline, setWasOffline] = useState(false)

  // =========================================================
  // LOAD MATRIX WHEN USER LOGS IN
  // =========================================================

  useEffect(() => {
    if (!user) return

    let cancelled = false

    const loadMatrix = async () => {
      try {
        const matrixData = await api.matrix()

        if (!cancelled) {
          setMatrix(matrixData)
        }
      } catch (error) {
        console.error(
          'Failed to load Matrix:',
          error
        )
      }
    }

    loadMatrix()

    return () => {
      cancelled = true
    }
  }, [user])

  // =========================================================
  // SERVER HEALTH + AUTOMATIC RECONNECT
  // =========================================================

  useEffect(() => {
    if (!user) return

    let cancelled = false
    let timer = null

    const checkServer = async () => {
      if (cancelled) return

      setCheckingServer(true)

      try {
        const healthData =
          await api.health()

        if (cancelled) return

        setHealth(healthData)
        setServerOnline(true)

        // If server was previously offline
        // refresh Matrix data after reconnect.
        if (wasOffline) {
          try {
            const matrixData =
              await api.matrix()

            if (!cancelled) {
              setMatrix(matrixData)
            }
          } catch (error) {
            console.error(
              'Matrix refresh after reconnect failed:',
              error
            )
          }
        }

        setWasOffline(false)
      } catch (error) {
        if (cancelled) return

        console.warn(
          'QA Matrix server unavailable. Retrying...',
          error
        )

        setServerOnline(false)
        setWasOffline(true)

        setHealth({
          status: 'offline',
        })
      } finally {
        if (!cancelled) {
          setCheckingServer(false)
        }
      }
    }

    // Check immediately
    checkServer()

    // Then check every 5 seconds
    timer = setInterval(
      checkServer,
      5000
    )

    return () => {
      cancelled = true

      if (timer) {
        clearInterval(timer)
      }
    }
  }, [user, wasOffline])

  // =========================================================
  // LOGIN SCREEN
  // =========================================================

  if (!user) {
    return (
      <Login
        onLogin={login}
      />
    )
  }

  // =========================================================
  // NAVIGATION
  // =========================================================

  const normalNav = [
    [
      'chat',
      MessageSquarePlus,
      'New Chat',
    ],
    [
      'history',
      MessagesSquare,
      'Chat History',
    ],
    [
      'matrix',
      FileSpreadsheet,
      'Matrix',
    ],
    [
      'status',
      Server,
      'Server Status',
    ],
  ]

  const adminNav = [
    [
      'admin',
      Shield,
      'Admin',
    ],
    [
      'settings',
      Settings,
      'Settings',
    ],
  ]

  const nav =
    user.role === 'admin'
      ? [...normalNav, ...adminNav]
      : normalNav

  // =========================================================
  // SOURCE PANEL
  // =========================================================

  const openSource =
    async (sourceInfo) => {
      try {
        const data =
          await api.source(
            sourceInfo.record_id
          )

        setSource(data)
      } catch (error) {
        console.error(
          'Failed to load source:',
          error
        )

        setSource(sourceInfo)
      }
    }

  // =========================================================
  // PAGE RENDERER
  // =========================================================

  const renderPage = () => {
    if (
      page === 'admin' &&
      user.role === 'admin'
    ) {
      return <Admin />
    }

    if (
      page === 'settings' &&
      user.role === 'admin'
    ) {
      return <SettingsPage />
    }

    if (page === 'history') {
      return (
        <History
          onSource={openSource}
        />
      )
    }

    if (page === 'status') {
      if (user.role === 'admin') {
        return <Admin />
      }

      return (
        <div className="admin-page">
          <div className="page-title">
            <div>
              <span className="eyebrow">
                SERVER STATUS
              </span>

              <h2>
                QA Matrix AI
              </h2>
            </div>
          </div>

          <div className="admin-card">
            <h3>
              Server Connection
            </h3>

            <StatusPill
              ok={serverOnline}
              label={
                serverOnline
                  ? 'Server online'
                  : 'Server offline · reconnecting'
              }
            />

            <p>
              {serverOnline
                ? 'The private QA Matrix server is connected and ready.'
                : 'The server cannot be reached right now. QA Matrix AI will keep trying automatically every 5 seconds.'}
            </p>
          </div>
        </div>
      )
    }

    return (
      <Chat
        matrix={matrix}
        onSource={openSource}
      />
    )
  }

  // =========================================================
  // UI
  // =========================================================

  return (
    <div className="shell">

      <aside className="sidebar">

        <div className="logo">

          <div>
            QA
          </div>

          <span>
            Matrix AI

            <small>
              PRIVATE SERVER
            </small>
          </span>

        </div>

        <nav>

          {nav.map(
            ([
              id,
              Icon,
              label,
            ]) => (

              <button
                key={id}
                className={
                  page === id
                    ? 'active'
                    : ''
                }
                onClick={() =>
                  setPage(id)
                }
                type="button"
              >

                <Icon size={18} />

                {label}

              </button>
            )
          )}

        </nav>

        <div className="sidebar-foot">

          <StatusPill
            ok={serverOnline}
            label={
              serverOnline
                ? 'Server online'
                : checkingServer
                  ? 'Checking server…'
                  : 'Server offline · reconnecting'
            }
          />

          <button
            onClick={logout}
            type="button"
          >

            <LogOut size={17} />

            Sign out

          </button>

          <small>
            {user.email}
          </small>

        </div>

      </aside>

      <main className="workspace">
        {renderPage()}
      </main>

      <SourcePanel
        source={source}
        onClose={() =>
          setSource(null)
        }
      />

    </div>
  )
}