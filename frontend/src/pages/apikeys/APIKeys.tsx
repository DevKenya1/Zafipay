import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiKeysApi } from '../../lib/api'
import { Plus, Copy, Trash2, Key } from 'lucide-react'

export default function APIKeys() {
  const qc = useQueryClient()
  const [name, setName] = useState('')
  const [createdKey, setCreatedKey] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [copied, setCopied] = useState(false)

  const { data, isLoading } = useQuery({ queryKey:['api-keys'], queryFn:()=>apiKeysApi.list() })

  const createMutation = useMutation({
    mutationFn: () => apiKeysApi.create({ name, scope:'full' }),
    onSuccess: (res) => {
      setCreatedKey(res.data.key)
      setName('')
      setShowForm(false)
      qc.invalidateQueries({ queryKey:['api-keys'] })
    },
  })

  const revokeMutation = useMutation({
    mutationFn: (id:string) => apiKeysApi.revoke(id),
    onSuccess: () => qc.invalidateQueries({ queryKey:['api-keys'] }),
  })

  const keys = data?.data || []

  const copy = (text:string) => {
    navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(()=>setCopied(false), 2000)
  }

  return (
    <div style={{padding:'36px 40px',minHeight:'100vh',background:'#0A0F0C',color:'#EDF7F1',fontFamily:'DM Sans,sans-serif'}}>
      <style>{`@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@400;500&display=swap');`}</style>

      <div style={{display:'flex',alignItems:'flex-start',justifyContent:'space-between',marginBottom:28}}>
        <div>
          <h2 style={{fontFamily:'Syne,sans-serif',fontSize:24,fontWeight:800,letterSpacing:-0.5,color:'#EDF7F1',marginBottom:4}}>API Keys</h2>
          <p style={{fontSize:13,color:'rgba(237,247,241,0.3)'}}>Authenticate your server-side API requests</p>
        </div>
        <button onClick={()=>setShowForm(true)} style={{display:'flex',alignItems:'center',gap:7,padding:'10px 18px',background:'#10B95A',color:'#060A08',border:'none',borderRadius:10,fontSize:13,fontWeight:600,cursor:'pointer',fontFamily:'DM Sans,sans-serif'}}>
          <Plus size={14}/> New key
        </button>
      </div>

      {createdKey && (
        <div style={{marginBottom:20,padding:'18px 20px',background:'rgba(245,166,35,0.05)',border:'1px solid rgba(245,166,35,0.15)',borderRadius:14}}>
          <p style={{fontSize:12,fontWeight:500,color:'#F5A623',marginBottom:10}}>Save this secret key — it will never be shown again</p>
          <div style={{display:'flex',alignItems:'center',gap:10}}>
            <code style={{flex:1,fontSize:12,color:'rgba(237,247,241,0.65)',background:'rgba(237,247,241,0.03)',padding:'10px 14px',borderRadius:8,wordBreak:'break-all',border:'1px solid rgba(237,247,241,0.06)'}}>{createdKey}</code>
            <button onClick={()=>copy(createdKey)} style={{padding:'10px 14px',background:'rgba(237,247,241,0.05)',border:'1px solid rgba(237,247,241,0.08)',borderRadius:8,color:copied?'#10B95A':'rgba(237,247,241,0.4)',cursor:'pointer',display:'flex',alignItems:'center',gap:6,fontSize:12,whiteSpace:'nowrap'}}>
              <Copy size={13}/>{copied?'Copied!':'Copy'}
            </button>
          </div>
          <button onClick={()=>setCreatedKey('')} style={{marginTop:10,fontSize:11,color:'rgba(245,166,35,0.6)',background:'none',border:'none',cursor:'pointer',padding:0}}>I have saved it ×</button>
        </div>
      )}

      {showForm && (
        <div style={{marginBottom:20,padding:'20px',background:'rgba(237,247,241,0.02)',border:'1px solid rgba(237,247,241,0.07)',borderRadius:14}}>
          <p style={{fontSize:13,fontWeight:500,color:'rgba(237,247,241,0.6)',marginBottom:12}}>Create new API key</p>
          <div style={{display:'flex',gap:10}}>
            <input
              value={name}
              onChange={e=>setName(e.target.value)}
              placeholder="e.g. Production server, Mobile app"
              style={{flex:1,background:'rgba(237,247,241,0.04)',border:'1px solid rgba(237,247,241,0.08)',borderRadius:10,padding:'11px 14px',fontSize:13,color:'#EDF7F1',outline:'none',fontFamily:'DM Sans,sans-serif'}}
            />
            <button onClick={()=>createMutation.mutate()} disabled={!name} style={{padding:'11px 20px',background:'#10B95A',color:'#060A08',border:'none',borderRadius:10,fontSize:13,fontWeight:600,cursor:'pointer',opacity:name?1:0.4}}>Generate</button>
            <button onClick={()=>setShowForm(false)} style={{padding:'11px 16px',background:'rgba(237,247,241,0.05)',color:'rgba(237,247,241,0.4)',border:'none',borderRadius:10,fontSize:13,cursor:'pointer'}}>Cancel</button>
          </div>
        </div>
      )}

      {isLoading ? (
        <p style={{color:'rgba(237,247,241,0.3)',fontSize:14}}>Loading...</p>
      ) : (
        <div style={{display:'flex',flexDirection:'column',gap:10}}>
          {keys.map((k:any) => (
            <div key={k.id} style={{background:'rgba(237,247,241,0.02)',border:'1px solid rgba(237,247,241,0.07)',borderRadius:14,padding:'18px 20px',display:'flex',alignItems:'center',justifyContent:'space-between',gap:16}}>
              <div style={{display:'flex',alignItems:'center',gap:12,minWidth:0}}>
                <div style={{width:36,height:36,borderRadius:9,background:k.is_active?'rgba(16,185,90,0.08)':'rgba(237,247,241,0.04)',display:'flex',alignItems:'center',justifyContent:'center',flexShrink:0}}>
                  <Key size={15} color={k.is_active?'#10B95A':'rgba(237,247,241,0.25)'}/>
                </div>
                <div>
                  <p style={{fontSize:14,fontWeight:500,color:k.is_active?'#EDF7F1':'rgba(237,247,241,0.3)',marginBottom:3}}>{k.name}</p>
                  <div style={{display:'flex',alignItems:'center',gap:10}}>
                    <code style={{fontSize:12,color:'rgba(237,247,241,0.3)',background:'rgba(237,247,241,0.04)',padding:'2px 8px',borderRadius:5}}>{k.prefix}••••••••••••</code>
                    <span style={{fontSize:11,color:'rgba(237,247,241,0.2)'}}>·</span>
                    <span style={{fontSize:11,color:'rgba(237,247,241,0.3)',textTransform:'capitalize'}}>{k.scope}</span>
                    {k.last_used_at && <>
                      <span style={{fontSize:11,color:'rgba(237,247,241,0.2)'}}>·</span>
                      <span style={{fontSize:11,color:'rgba(237,247,241,0.25)'}}>Last used {new Date(k.last_used_at).toLocaleDateString()}</span>
                    </>}
                  </div>
                </div>
              </div>
              <div style={{display:'flex',alignItems:'center',gap:10,flexShrink:0}}>
                <span style={{display:'inline-flex',alignItems:'center',gap:4,padding:'3px 10px',borderRadius:100,fontSize:11,fontWeight:500,background:k.is_active?'rgba(16,185,90,0.08)':'rgba(237,247,241,0.05)',color:k.is_active?'#10B95A':'rgba(237,247,241,0.3)'}}>
                  <span style={{width:5,height:5,borderRadius:'50%',background:'currentColor',display:'inline-block'}}/>
                  {k.is_active?'Active':'Revoked'}
                </span>
                {k.is_active && (
                  <button onClick={()=>revokeMutation.mutate(k.id)} style={{width:32,height:32,display:'flex',alignItems:'center',justifyContent:'center',background:'rgba(248,113,113,0.07)',border:'1px solid rgba(248,113,113,0.12)',borderRadius:8,cursor:'pointer',color:'#F87171'}}>
                    <Trash2 size={13}/>
                  </button>
                )}
              </div>
            </div>
          ))}
          {keys.length===0&&<p style={{fontSize:13,color:'rgba(237,247,241,0.2)',padding:'24px 0'}}>No API keys yet — create one above</p>}
        </div>
      )}
    </div>
  )
}