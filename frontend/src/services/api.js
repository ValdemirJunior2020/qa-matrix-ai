const BASE=(import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api').replace(/\/$/,'')
const token=()=>localStorage.getItem('qa_token')
async function req(path,options={}){
  const headers={...(options.body instanceof FormData?{}:{'Content-Type':'application/json'}),...(options.headers||{})}
  if(token()) headers.Authorization=`Bearer ${token()}`
  const r=await fetch(`${BASE}${path}`,{...options,headers})
  let data={}; try{data=await r.json()}catch{}
  if(!r.ok){ if(r.status===401){localStorage.removeItem('qa_token');localStorage.removeItem('qa_user')} throw new Error(data.detail||`Request failed (${r.status})`) }
  return data
}
export const api={
 login:(email,password)=>req('/auth/login',{method:'POST',body:JSON.stringify({email,password})}),
 health:()=>req('/health'), healthDetails:()=>req('/health/details'), matrix:()=>req('/matrix'),
 chat:(question,chat_id)=>req('/chat',{method:'POST',body:JSON.stringify({question,chat_id})}),
 source:(id)=>req(`/matrix/source/${id}`),
 upload:(file)=>{const f=new FormData();f.append('file',file);return req('/admin/matrix/upload',{method:'POST',body:f})},
 reindex:()=>req('/admin/matrix/reindex',{method:'POST'}),
 history:()=>req('/history'), historyChat:(id)=>req(`/history/${id}`),
 settings:()=>req('/admin/settings'), updateSettings:(data)=>req('/admin/settings',{method:'PUT',body:JSON.stringify(data)}),
}
