const BASE = (
  import.meta.env.VITE_API_BASE_URL ||
  'http://127.0.0.1:8000/api'
).replace(/\/$/, '')

const token = () =>
  localStorage.getItem('qa_token')


// ============================================================
// SMALL DELAY HELPER
// ============================================================

function sleep(ms) {
  return new Promise((resolve) => {
    setTimeout(resolve, ms)
  })
}


// ============================================================
// FETCH WITH RETRY
// ============================================================

async function fetchWithRetry(
  url,
  options = {},
  retries = 2
) {
  let lastError = null

  for (
    let attempt = 0;
    attempt <= retries;
    attempt++
  ) {
    try {
      const response = await fetch(
        url,
        options
      )

      return response
    } catch (error) {
      lastError = error

      if (attempt >= retries) {
        break
      }

      const delay =
        attempt === 0
          ? 1500
          : 3500

      await sleep(delay)
    }
  }

  throw (
    lastError ||
    new Error('Unable to reach the QA Matrix server.')
  )
}


// ============================================================
// MAIN REQUEST FUNCTION
// ============================================================

async function req(
  path,
  options = {}
) {
  const headers = {
    ...(options.body instanceof FormData
      ? {}
      : {
          'Content-Type':
            'application/json',
        }),

    ...(options.headers || {}),
  }

  const authToken = token()

  if (authToken) {
    headers.Authorization =
      `Bearer ${authToken}`
  }

  let response

  try {
    response = await fetchWithRetry(
      `${BASE}${path}`,
      {
        ...options,
        headers,
      },
      2
    )
  } catch (error) {
    console.error(
      `Network request failed: ${path}`,
      error
    )

    throw new Error(
      'QA Matrix server is offline or unreachable. Reconnecting…'
    )
  }

  let data = {}

  try {
    data = await response.json()
  } catch {
    data = {}
  }

  if (!response.ok) {
    if (response.status === 401) {
      localStorage.removeItem(
        'qa_token'
      )

      localStorage.removeItem(
        'qa_user'
      )
    }

    if (response.status === 429) {
      throw new Error(
        data.detail ||
        'Too many requests. Please wait a moment and try again.'
      )
    }

    if (
      response.status >= 500
    ) {
      throw new Error(
        data.detail ||
        'The QA Matrix server had a temporary problem.'
      )
    }

    throw new Error(
      data.detail ||
      `Request failed (${response.status})`
    )
  }

  return data
}


// ============================================================
// API
// ============================================================

export const api = {

  // ----------------------------------------------------------
  // AUTH
  // ----------------------------------------------------------

  login: (
    email,
    password
  ) =>
    req(
      '/auth/login',
      {
        method: 'POST',

        body: JSON.stringify({
          email,
          password,
        }),
      }
    ),


  // ----------------------------------------------------------
  // HEALTH / RECONNECT
  // ----------------------------------------------------------

  health: () =>
    req('/health'),


  healthDetails: () =>
    req('/health/details'),


  // IMPORTANT:
  // Your health router has prefix="/health",
  // so this endpoint is /api/health/queue
  queue: () =>
    req('/health/queue'),


  // ----------------------------------------------------------
  // MATRIX
  // ----------------------------------------------------------

  matrix: () =>
    req('/matrix'),


  source: (id) =>
    req(
      `/matrix/source/${id}`
    ),


  // ----------------------------------------------------------
  // CHAT
  // ----------------------------------------------------------

  chat: (
    question,
    chat_id
  ) =>
    req(
      '/chat',
      {
        method: 'POST',

        body: JSON.stringify({
          question,
          chat_id,
        }),
      }
    ),


  // ----------------------------------------------------------
  // MATRIX ADMIN
  // ----------------------------------------------------------

  upload: (file) => {
    const form =
      new FormData()

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


  // ----------------------------------------------------------
  // HISTORY
  // ----------------------------------------------------------

  history: () =>
    req('/history'),


  historyChat: (id) =>
    req(
      `/history/${id}`
    ),


  // ----------------------------------------------------------
  // SETTINGS
  // ----------------------------------------------------------

  settings: () =>
    req(
      '/admin/settings'
    ),


  updateSettings: (
    data
  ) =>
    req(
      '/admin/settings',
      {
        method: 'PUT',

        body: JSON.stringify(
          data
        ),
      }
    ),


  // ----------------------------------------------------------
  // USER MANAGEMENT
  // ----------------------------------------------------------

  users: () =>
    req(
      '/admin/users'
    ),


  createUser: (
    email,
    password,
    role = 'qa_user'
  ) =>
    req(
      '/admin/users',
      {
        method: 'POST',

        body: JSON.stringify({
          email,
          password,
          role,
        }),
      }
    ),


  updateUser: (
    id,
    data
  ) =>
    req(
      `/admin/users/${id}`,
      {
        method: 'PUT',

        body: JSON.stringify(
          data
        ),
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