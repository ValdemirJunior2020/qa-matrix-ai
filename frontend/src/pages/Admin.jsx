import {
  useEffect,
  useState,
} from 'react'

import {
  Upload,
  RefreshCw,
  Server,
  Database,
  Brain,
  Users,
  UserPlus,
  Trash2,
  Power,
  KeyRound,
} from 'lucide-react'

import { api } from '../services/api'
import StatusPill from '../components/StatusPill'

export default function Admin() {

  const [health, setHealth] =
    useState(null)

  const [matrix, setMatrix] =
    useState(null)

  const [users, setUsers] =
    useState([])

  const [msg, setMsg] =
    useState('')

  const [busy, setBusy] =
    useState(false)

  const [email, setEmail] =
    useState('')

  const [password, setPassword] =
    useState('')

  const [role, setRole] =
    useState('qa_user')


  async function load() {
    try {

      const [
        healthData,
        matrixData,
        userData,
      ] = await Promise.all([
        api.healthDetails(),
        api.matrix(),
        api.users(),
      ])

      setHealth(healthData)
      setMatrix(matrixData)
      setUsers(userData)

    } catch (error) {

      setMsg(error.message)

    }
  }


  useEffect(() => {
    load()
  }, [])


  async function upload(event) {

    const file =
      event.target.files?.[0]

    if (!file) return

    setBusy(true)

    setMsg(
      'Validating and indexing new Matrix…'
    )

    try {

      await api.upload(file)

      setMsg(
        'New Matrix activated successfully.'
      )

      await load()

    } catch (error) {

      setMsg(error.message)

    } finally {

      setBusy(false)

      event.target.value = ''

    }
  }


  async function reindex() {

    setBusy(true)

    setMsg(
      'Rebuilding local semantic index…'
    )

    try {

      await api.reindex()

      setMsg(
        'Index rebuilt.'
      )

      await load()

    } catch (error) {

      setMsg(error.message)

    } finally {

      setBusy(false)

    }
  }


  async function createUser(event) {

    event.preventDefault()

    if (
      !email.trim() ||
      !password.trim()
    ) {
      return
    }

    setBusy(true)
    setMsg('Creating user…')

    try {

      await api.createUser(
        email.trim(),
        password,
        role,
      )

      setEmail('')
      setPassword('')
      setRole('qa_user')

      setMsg(
        'User created successfully.'
      )

      await load()

    } catch (error) {

      setMsg(error.message)

    } finally {

      setBusy(false)

    }
  }


  async function toggleUser(user) {

    setBusy(true)

    try {

      await api.updateUser(
        user.id,
        {
          active: !user.active,
        }
      )

      await load()

    } catch (error) {

      setMsg(error.message)

    } finally {

      setBusy(false)

    }
  }


  async function changeRole(
    user,
    newRole
  ) {

    setBusy(true)

    try {

      await api.updateUser(
        user.id,
        {
          role: newRole,
        }
      )

      await load()

    } catch (error) {

      setMsg(error.message)

    } finally {

      setBusy(false)

    }
  }


  async function resetPassword(user) {

    const newPassword =
      window.prompt(
        `Enter a new password for ${user.email}`
      )

    if (!newPassword) {
      return
    }

    if (
      newPassword.length < 8
    ) {
      setMsg(
        'Password must be at least 8 characters.'
      )

      return
    }

    setBusy(true)

    try {

      await api.updateUser(
        user.id,
        {
          password: newPassword,
        }
      )

      setMsg(
        `Password updated for ${user.email}.`
      )

    } catch (error) {

      setMsg(error.message)

    } finally {

      setBusy(false)

    }
  }


  async function deleteUser(user) {

    const confirmed =
      window.confirm(
        `Delete ${user.email}?`
      )

    if (!confirmed) {
      return
    }

    setBusy(true)

    try {

      await api.deleteUser(
        user.id
      )

      setMsg(
        `${user.email} deleted.`
      )

      await load()

    } catch (error) {

      setMsg(error.message)

    } finally {

      setBusy(false)

    }
  }


  return (
    <div className="admin-page">

      <div className="page-title">

        <div>

          <span className="eyebrow">
            SERVER CONTROL
          </span>

          <h2>Admin</h2>

        </div>

      </div>


      <div className="admin-grid">

        <article>

          <Server />

          <span>
            Backend
          </span>

          <b>
            {health?.backend ||
              'Checking…'}
          </b>

          <StatusPill
            ok={
              health?.backend ===
              'online'
            }
            label={
              health?.backend ===
              'online'
                ? 'Online'
                : 'Offline'
            }
          />

        </article>


        <article>

          <Brain />

          <span>
            Ollama
          </span>

          <b>
            {health?.model ||
              '—'}
          </b>

          <StatusPill
            ok={
              health?.ollama ===
              'online'
            }
            label={
              health?.ollama ||
              'Checking…'
            }
          />

        </article>


        <article>

          <Database />

          <span>
            Matrix Rules
          </span>

          <b>
            {matrix?.rule_count ??
              '—'}
          </b>

          <StatusPill
            ok={
              matrix?.index_ready
            }
            label={
              matrix?.index_ready
                ? 'Index ready'
                : 'Index pending'
            }
          />

        </article>

      </div>


      <div className="admin-card">

        <h3>
          Current Matrix
        </h3>

        <dl>

          <div>

            <dt>
              Filename
            </dt>

            <dd>
              {matrix?.filename ||
                'None loaded'}
            </dd>

          </div>


          <div>

            <dt>
              Sheets
            </dt>

            <dd>
              {matrix?.sheet_count ??
                '—'}
            </dd>

          </div>


          <div>

            <dt>
              Rules / records
            </dt>

            <dd>
              {matrix?.rule_count ??
                '—'}
            </dd>

          </div>


          <div>

            <dt>
              Activated
            </dt>

            <dd>
              {
                matrix?.activated_at
                  ? new Date(
                      matrix.activated_at
                    ).toLocaleString()
                  : '—'
              }
            </dd>

          </div>

        </dl>


        <div className="admin-actions">

          <label className="button">

            <Upload size={17} />

            Replace Matrix

            <input
              type="file"
              accept=".xlsx"
              hidden
              disabled={busy}
              onChange={upload}
            />

          </label>


          <button
            className="button secondary"
            disabled={busy}
            onClick={reindex}
          >

            <RefreshCw
              size={17}
            />

            Rebuild Index

          </button>

        </div>


        <p className="warning">

          A replacement becomes active
          only after validation and
          indexing succeed.

        </p>

      </div>


      <div className="admin-card">

        <h3>
          <Users size={18} />
          {' '}
          User Management
        </h3>


        <form
          className="user-create-form"
          onSubmit={createUser}
        >

          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={
              event =>
                setEmail(
                  event.target.value
                )
            }
            required
          />


          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={
              event =>
                setPassword(
                  event.target.value
                )
            }
            minLength={8}
            required
          />


          <select
            value={role}
            onChange={
              event =>
                setRole(
                  event.target.value
                )
            }
          >

            <option value="qa_user">
              QA User
            </option>

            <option value="admin">
              Admin
            </option>

          </select>


          <button
            className="button"
            type="submit"
            disabled={busy}
          >

            <UserPlus
              size={17}
            />

            Add User

          </button>

        </form>


        <div className="users-list">

          {users.map(user => (

            <div
              className="user-row"
              key={user.id}
            >

              <div className="user-info">

                <strong>
                  {user.email}
                </strong>

                <span>
                  {
                    user.active
                      ? 'Active'
                      : 'Disabled'
                  }
                </span>

              </div>


              <select
                value={user.role}
                disabled={busy}
                onChange={
                  event =>
                    changeRole(
                      user,
                      event.target.value
                    )
                }
              >

                <option value="qa_user">
                  QA User
                </option>

                <option value="admin">
                  Admin
                </option>

              </select>


              <button
                type="button"
                className="user-action"
                onClick={
                  () =>
                    resetPassword(user)
                }
                title="Reset password"
              >

                <KeyRound
                  size={16}
                />

              </button>


              <button
                type="button"
                className="user-action"
                onClick={
                  () =>
                    toggleUser(user)
                }
                title={
                  user.active
                    ? 'Disable user'
                    : 'Enable user'
                }
              >

                <Power
                  size={16}
                />

              </button>


              <button
                type="button"
                className="user-action danger"
                onClick={
                  () =>
                    deleteUser(user)
                }
                title="Delete user"
              >

                <Trash2
                  size={16}
                />

              </button>

            </div>

          ))}

        </div>


        {msg && (
          <div className="notice">
            {msg}
          </div>
        )}

      </div>

    </div>
  )
}