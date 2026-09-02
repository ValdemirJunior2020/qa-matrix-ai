function formatAnswer(text = '') {
  const lines = String(text).split('\n')

  return lines.map((line, index) => {
    // Matches:
    // 1. Step
    // 1.Step
    // 1) Step
    // 1-Step
    const match = line.match(/^(\d+)[\.\)\-]\s*(.*)$/)

    if (match) {
      return (
        <div key={index} className="answer-step">
          <span className="step-number">
            {match[1]}.
          </span>

          <span className="step-text">
            {match[2]}
          </span>
        </div>
      )
    }

    if (!line.trim()) {
      return (
        <div
          key={index}
          className="answer-space"
        />
      )
    }

    return (
      <div
        key={index}
        className="answer-line"
      >
        {line}
      </div>
    )
  })
}

export default function AnswerCard({
  data,
  onSource,
}) {
  return (
    <div className="answer-card">

      <div className="finding-grid">

        <div>
          <span>Category</span>
          <b>
            {data.category || 'Not determined'}
          </b>
        </div>

        <div>
          <span>Critical</span>
          <b>
            {data.critical
              ? 'Yes'
              : 'No / not supported'}
          </b>
        </div>

        <div>
          <span>Score Impact</span>
          <b>
            {data.score_impact || 'Not determined'}
          </b>
        </div>

        <div>
          <span>Confidence</span>
          <b>
            {data.confidence_label || 'Low'} ·{' '}
            {Math.round(
              (data.confidence || 0) * 100
            )}
            %
          </b>
        </div>

      </div>

      <section>

        <h4>Answer</h4>

        <div className="formatted-answer">
          {formatAnswer(data.answer)}
        </div>

      </section>

      {data.matrix_rule && (
        <section className="matrix-rule">

          <h4>Matrix Rule</h4>

          <p>
            {data.matrix_rule}
          </p>

        </section>
      )}

      {data.coaching && (
        <section>

          <h4>AI Recommendation</h4>

          <p>
            {data.coaching}
          </p>

        </section>
      )}

      {!!data.sources?.length && (
        <section>

          <h4>Matrix Evidence</h4>

          <div className="sources">

            {data.sources.map((source) => (
              <button
                key={source.record_id}
                type="button"
                onClick={() =>
                  onSource(source)
                }
              >

                <b>
                  {source.sheet}
                </b>

                <span>
                  {source.category || 'Matrix'} ·{' '}
                  {source.cell_range}
                </span>

                <small>
                  {source.excerpt}
                </small>

              </button>
            ))}

          </div>

        </section>
      )}

    </div>
  )
}