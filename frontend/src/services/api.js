const BASE = (
  import.meta.env.VITE_API_BASE_URL ||
  'http://127.0.0.1:8000/api'
).replace(/\/$/, '')

const token = () =>
  localStorage.getItem('qa_token')

async function req(path, options = {}) {
  const headers = {
    ...(options.body instanceof FormData
      ? {}
      : {
          'Content-Type': 'application/json',
        }),
    ...(options.headers || {}),
  }

  if (token()) {
    headers.Authorization = `Bearer ${token()}`
  }

  const response = await fetch(
    `${BASE}${path}`,
    {
      ...options,
      headers,
    }
  )

  let data = {}

  try {
    data = await response.json()
  } catch {}

  if (!response.ok) {
    if (response.status === 401) {
      localStorage.removeItem('qa_token')
      localStorage.removeItem('qa_user')
    }

    throw new Error(
      data.detail ||
      `Request failed (${response.status})`
    )
  }

  return data
}

export const api = {
  login: (email, password) =>
    req('/auth/login', {
      method: 'POST',
      body: JSON.stringify({
        email,
        password,
      }),
    }),

  health: () =>
    req('/health'),

  healthDetails: () =>
    req('/health/details'),

  matrix: () =>
    req('/matrix'),

  chat: (question, chat_id) =>
    req('/chat', {
      method: 'POST',
      body: JSON.stringify({
        question,
        chat_id,
      }),
    }),

  source: (id) =>
    req(`/matrix/source/${id}`),

  upload: (file) => {
    const form = new FormData()

    form.append(
      'file',
      file
    )

    return req(
      '/admin/matrix/upload',
      {
        method: 'POST',
        body: form,
      }
    )
  },

  reindex: () =>
    req(
      '/admin/matrix/reindex',
      {
        method: 'POST',
      }
    ),

  history: () =>
    req('/history'),

  historyChat: (id) =>
    req(`/history/${id}`),

  settings: () =>
    req('/admin/settings'),

  updateSettings: (data) =>
    req('/admin/settings', {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  // USER MANAGEMENT

  users: () =>
    req('/admin/users'),

  createUser: (
    email,
    password,
    role = 'qa_user'
  ) =>
    req('/admin/users', {
      method: 'POST',
      body: JSON.stringify({
        email,
        password,
        role,
      }),
    }),

  updateUser: (
    id,
    data
  ) =>
    req(
      `/admin/users/${id}`,
      {
        method: 'PUT',
        body: JSON.stringify(data),
      }
    ),

  deleteUser: (id) =>
    req(
      `/admin/users/${id}`,
      {
        method: 'DELETE',
      }
    ),
}