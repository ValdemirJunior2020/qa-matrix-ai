export default function StatusPill({ok,label}){return <span className={`status ${ok?'ok':'bad'}`}><i/>{label}</span>}
