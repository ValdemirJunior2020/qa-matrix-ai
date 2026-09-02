import {X} from 'lucide-react'
export default function SourcePanel({source,onClose}){if(!source)return null;return <aside className="source-panel">
 <div className="panel-head"><div><span className="eyebrow">MATRIX SOURCE</span><h3>{source.workbook}</h3></div><button className="icon-btn" onClick={onClose}><X size={18}/></button></div>
 <div className="source-meta"><div><b>Sheet</b><span>{source.sheet}</span></div><div><b>Category</b><span>{source.category||'—'}</span></div><div><b>Cells</b><span>{source.cell_range||'—'}</span></div><div><b>Rows</b><span>{source.source_row_start||source.rows||'—'}</span></div></div>
 <div className="raw"><b>Raw extracted Matrix data</b><pre>{JSON.stringify(source.metadata||source,null,2)}</pre></div>
 </aside>}
