export default function AnswerCard({data,onSource}){return <div className="answer-card">
 <div className="finding-grid">
  <div><span>Category</span><b>{data.category||'Not determined'}</b></div>
  <div><span>Critical</span><b>{data.critical?'Yes':'No / not supported'}</b></div>
  <div><span>Score Impact</span><b>{data.score_impact||'Not determined'}</b></div>
  <div><span>Confidence</span><b>{data.confidence_label} · {Math.round((data.confidence||0)*100)}%</b></div>
 </div>
 <section><h4>Answer</h4><p>{data.answer}</p></section>
 {data.matrix_rule&&<section className="matrix-rule"><h4>Matrix Rule</h4><p>{data.matrix_rule}</p></section>}
 {data.coaching&&<section><h4>AI Recommendation</h4><p>{data.coaching}</p></section>}
 {!!data.sources?.length&&<section><h4>Matrix Evidence</h4><div className="sources">{data.sources.map(s=><button key={s.record_id} onClick={()=>onSource(s)}><b>{s.sheet}</b><span>{s.category||'Matrix'} · {s.cell_range}</span><small>{s.excerpt}</small></button>)}</div></section>}
 </div>}
