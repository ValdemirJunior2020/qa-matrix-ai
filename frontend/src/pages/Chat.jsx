import { useEffect, useRef, useState } from 'react'
import {
  Send,
  FileSpreadsheet,
  LoaderCircle,
} from 'lucide-react'

import { api } from '../services/api'
import AnswerCard from '../components/AnswerCard'

const starters = [
  'What does the Matrix say about refund delays?',
  'What should the agent do when a reservation is not found at check-in?',
  'When should the agent use Slack?',
  'What does the Ticket Matrix say about VIPRES?',
]

export default function Chat({ onSource, matrix }) {
  const [q, setQ] = useState('')
  const [messages, setMessages] = useState([])
  const [chatId, setChatId] = useState(null)
  const [busy, setBusy] = useState(false)

  const end = useRef(null)

  // FIXED: do not return scrollIntoView() from useEffect
  useEffect(() => {
    if (end.current) {
      end.current.scrollIntoView({
        behavior: 'smooth',
        block: 'end',
      })
    }
  }, [messages, busy])

  async function send(text = q) {
    const v = text.trim()

    if (!v || busy) return

    setQ('')

    setMessages((messages) => [
      ...messages,
      {
        role: 'user',
        text: v,
      },
    ])

    setBusy(true)

    try {
      const data = await api.chat(v, chatId)

      setChatId(data.chat_id)

      setMessages((messages) => [
        ...messages,
        {
          role: 'assistant',
          data,
        },
      ])
    } catch (error) {
      console.error('Chat request failed:', error)

      setMessages((messages) => [
        ...messages,
        {
          role: 'error',
          text: error?.message || 'Unable to contact the QA Matrix server.',
        },
      ])
    } finally {
      setBusy(false)
    }
  }

  function handleKeyDown(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault()
      send()
    }
  }

  return (
    <div className="chat-page">
      <div className="chat-head">
        <div>
          <span className="eyebrow">
            ACTIVE MATRIX
          </span>

          <h2>QA Matrix AI</h2>

          <p>
            <FileSpreadsheet size={15} />
            {matrix?.filename || 'Loading Matrix…'}
          </p>
        </div>
      </div>

      <div className="chat-scroll">
        {!messages.length && (
          <div className="welcome">
            <h1>
              Ask the Matrix, not a generic AI.
            </h1>

            <p>
              Answers are grounded in the active Excel Matrix
              and show the exact source cells.
            </p>

            <div className="starters">
              {starters.map((starter) => (
                <button
                  key={starter}
                  type="button"
                  onClick={() => send(starter)}
                  disabled={busy}
                >
                  {starter}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((message, index) => {
          if (message.role === 'user') {
            return (
              <div
                key={index}
                className="user-msg"
              >
                {message.text}
              </div>
            )
          }

          if (message.role === 'assistant') {
            return (
              <AnswerCard
                key={index}
                data={message.data}
                onSource={onSource}
              />
            )
          }

          return (
            <div
              key={index}
              className="error msg"
            >
              {message.text}
            </div>
          )
        })}

        {busy && (
          <div className="thinking">
            <LoaderCircle
              className="spin"
              size={18}
            />

            Checking the Matrix…
          </div>
        )}

        <div ref={end} />
      </div>

      <div className="composer">
        <textarea
          value={q}
          onChange={(event) => setQ(event.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask anything about the QA Matrix…"
          disabled={busy}
        />

        <button
          type="button"
          onClick={() => send()}
          disabled={busy || !q.trim()}
        >
          <Send size={18} />
        </button>

        <small>
          Enter to send · Shift+Enter for a new line
        </small>
      </div>
    </div>
  )
}