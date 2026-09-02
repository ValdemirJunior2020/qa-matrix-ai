import {useState} from 'react'
import {api} from '../services/api'
export function useAuth(){
 const [user,setUser]=useState(()=>{try{return JSON.parse(localStorage.getItem('qa_user'))}catch{return null}})
 async function login(email,password){const d=await api.login(email,password);localStorage.setItem('qa_token',d.access_token);localStorage.setItem('qa_user',JSON.stringify(d.user));setUser(d.user)}
 function logout(){localStorage.removeItem('qa_token');localStorage.removeItem('qa_user');setUser(null)}
 return {user,login,logout}
}
