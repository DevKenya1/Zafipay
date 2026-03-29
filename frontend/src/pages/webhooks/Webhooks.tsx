import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { webhooksApi } from '../../lib/api'
import { useState } from 'react'
import { Plus, Globe } from 'lucide-react'

export default function Webhooks() {
  const qc = useQueryClient()
  const [showForm, setShowForm] = useState(false)
  const [url, setUrl] = useState('')
  const [secret, setSecret] = useState('')

  const { data: epData } = useQuery({ queryKey:['webhook-endpoints'], queryFn:()=>webhooksApi.listEndpoints() })
  const { data: dlData } = useQuery({ queryKey:['webhook-deliveries'], queryFn:()=>webhooksApi.listDeliveries() })

  const createMutation = useMutation({
    mutationFn: () => webhooksApi.createEndpoint({ url, events:['transaction.completed','transaction.failed','transaction.processing'] }),
    onSuccess: (res) => {
      setSecret(res.data.secret || '')
      setUrl('')
      setShowForm(false)
      qc.invalidateQueries({ queryKey:['webhook-endpoints'] })
    },
  })

  const raw = epData?.data
  const endpoints = Array.isArray(raw) ? raw : raw ? [raw] : []
  const deliveries = dlData?.data?.results || []

  const statusStyle: Record<string,{bg:string,color:string}> = {
    success:{ bg:'rgba(16,185,90,0.1)', color:'#10B95A' },
    failed:{ bg:'rgba(248,113,113,0.1)', color:'#F87171' },
    pending:{ bg:'rgba(237,247,241,0.06)', color:'rgba(237,247,241,0.4)' },
  }

  return (
    <div style={{padding:'36px 40px',minHeight:'100vh',background:'#0A0F0C',color:'#EDF7F1',fontFamily:'DM Sans,sans-serif'}}>
      <style>{`@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@400;500&display=swap');`}</style>

      <div style={{display:'flex',alignItems:'flex-start',justifyContent:'space-between',marginBottom:28}}>
        <div>
          <h2 style={{fontFamily:'Syne,sans-serif',fontSize:24,fontWeight:800,letterSpacing:-0.5,color:'#EDF7F1',marginBottom:4}}>Webhooks</h2>
          <p style={{fontSize:13,color:'rgba(237,247,241,0.3)'}}>Receive real-time payment events on your server</p>
        </div>
        <button onClick={()=>setShowForm(true)} style={{display:'flex',alignItems:'center',gap:7,padding:'10px 18px',background:'#10B95A',color:'#060A08',border:'none',borderRadius:10,fontSize:13,fontWeight:600,cursor:'pointer',fontFamily:'DM Sans,sans-serif'}}>
          <Plus size={14}/> Add endpoint
        </button>
      </div>

      {secret && (
        <div style={{marginBottom:20,padding:'16px 20px',background:'rgba(245,166,35,0.06)',border:'1px solid rgba(245,166,35,0.15)',borderRadius:14}}>
          <p style={{fontSize:12,fontWeight:500,color:'#F5A623',marginBottom:8}}>Save your webhook secret â€” shown only once</p>
          <code style={{fontSize:12,color:'rgba(237,247,241,0.6)',wordBreak:'break-all',display:'block',background:'rgba(237,247,241,0.03)',padding:'10px 12px',borderRadius:8}}>{secret}</code>
          <button onClick={()=>setSecret('')} style={{marginTop:8,fontSize:11,color:'rgba(245,166,35,0.7)',background:'none',border:'none',cursor:'pointer',padding:0}}>I have saved it Ã—</button>
        </div>
      )}

      {showForm && (
        <div style={{marginBottom:20,padding:'20px',background:'rgba(237,247,241,0.02)',border:'1px solid rgba(237,247,241,0.07)',borderRadius:14}}>
          <p style={{fontSize:13,fontWeight:500,color:'rgba(237,247,241,0.6)',marginBottom:12}}>New webhook endpoint</p>
          <div style={{display:'flex',gap:10}}>
            <input
              value={url}
              onChange={e=>setUrl(e.target.value)}
              placeholder="https://yourapp.com/webhook"
              style={{flex:1,background:'rgba(237,247,241,0.04)',border:'1px solid rgba(237,247,241,0.08)',borderRadius:10,padding:'11px 14px',fontSize:13,color:'#EDF7F1',outline:'none',fontFamily:'DM Sans,sans-serif'}}
            />
            <button onClick={()=>createMutation.mutate()} disabled={!url} style={{padding:'11px 20px',background:'#10B95A',color:'#060A08',border:'none',borderRadius:10,fontSize:13,fontWeight:600,cursor:'pointer',opacity:url?1:0.4}}>Create</button>
            <button onClick={()=>setShowForm(false)} style={{padding:'11px 16px',background:'rgba(237,247,241,0.05)',color:'rgba(237,247,241,0.4)',border:'none',borderRadius:10,fontSize:13,cursor:'pointer'}}>Cancel</button>
          </div>
          <p style={{fontSize:11,color:'rgba(237,247,241,0.25)',marginTop:8}}>Will subscribe to: transaction.completed, transaction.failed, transaction.processing</p>
        </div>
      )}

      <div style={{marginBottom:24}}>
        <p style={{fontSize:11,fontWeight:500,letterSpacing:'0.1em',textTransform:'uppercase',color:'rgba(237,247,241,0.25)',marginBottom:12}}>Endpoints ({endpoints.length})</p>
        <div style={{display:'flex',flexDirection:'column',gap:10}}>
          {endpoints.map((ep:any) => (
            <div key={ep.id} style={{background:'rgba(237,247,241,0.02)',border:'1px solid rgba(237,247,241,0.07)',borderRadius:14,padding:'18px 20px',display:'flex',alignItems:'flex-start',justifyContent:'space-between',gap:16}}>
              <div style={{display:'flex',alignItems:'flex-start',gap:12,minWidth:0}}>
                <div style={{width:32,height:32,borderRadius:8,background:'rgba(16,185,90,0.08)',display:'flex',alignItems:'center',justifyContent:'center',flexShrink:0}}>
                  <Globe size={14} color="#10B95A"/>
                </div>
                <div style={{minWidth:0}}>
                  <p style={{fontSize:13,fontWeight:500,color:'#EDF7F1',marginBottom:4,overflow:'hidden',textOverflow:'ellipsis',whiteSpace:'nowrap'}}>{ep.url}</p>
                  <p style={{fontSize:11,color:'rgba(237,247,241,0.25)'}}>{(ep.events||[]).join(' Â· ')}</p>
                </div>
              </div>
              <span style={{display:'inline-flex',alignItems:'center',gap:5,padding:'4px 10px',borderRadius:100,fontSize:11,fontWeight:500,flexShrink:0,background:ep.is_active?'rgba(16,185,90,0.1)':'rgba(237,247,241,0.06)',color:ep.is_active?'#10B95A':'rgba(237,247,241,0.3)'}}>
                <span style={{width:5,height:5,borderRadius:'50%',background:'currentColor',display:'inline-block'}}/>
                {ep.is_active?'Active':'Inactive'}
              </span>
            </div>
          ))}
          {endpoints.length===0 && <p style={{fontSize:13,color:'rgba(237,247,241,0.2)',padding:'24px 0'}}>No endpoints yet â€” add one above</p>}
        </div>
      </div>

      <div>
        <p style={{fontSize:11,fontWeight:500,letterSpacing:'0.1em',textTransform:'uppercase',color:'rgba(237,247,241,0.25)',marginBottom:12}}>Delivery log ({deliveries.length})</p>
        <div style={{background:'rgba(237,247,241,0.02)',border:'1px solid rgba(237,247,241,0.07)',borderRadius:14,overflow:'hidden'}}>
          <table style={{width:'100%',borderCollapse:'collapse',fontSize:13}}>
            <thead>
              <tr style={{borderBottom:'1px solid rgba(237,247,241,0.05)'}}>
                {['Event','Attempt','Response','Status','Date'].map(h=>(
                  <th key={h} style={{textAlign:'left',padding:'12px 16px',fontSize:11,fontWeight:500,color:'rgba(237,247,241,0.25)',letterSpacing:'0.08em',textTransform:'uppercase'}}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {deliveries.map((d:any,i:number) => (
                <tr key={d.id} style={{borderBottom:i<deliveries.length-1?'1px solid rgba(237,247,241,0.04)':'none'}}>
                  <td style={{padding:'13px 16px',fontWeight:500,color:'#EDF7F1'}}>{d.event_type}</td>
                  <td style={{padding:'13px 16px',color:'rgba(237,247,241,0.4)'}}>#{d.attempt_number}</td>
                  <td style={{padding:'13px 16px',color:'rgba(237,247,241,0.4)'}}>{d.response_status||'â€”'}</td>
                  <td style={{padding:'13px 16px'}}>
                    <span style={{display:'inline-flex',alignItems:'center',gap:5,padding:'3px 10px',borderRadius:100,fontSize:11,fontWeight:500,...(statusStyle[d.status]||statusStyle.pending)}}>
                      <span style={{width:5,height:5,borderRadius:'50%',background:'currentColor',display:'inline-block'}}/>
                      {d.status}
                    </span>
                  </td>
                  <td style={{padding:'13px 16px',color:'rgba(237,247,241,0.3)'}}>{new Date(d.created_at).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {deliveries.length===0&&<p style={{textAlign:'center',padding:'32px',color:'rgba(237,247,241,0.2)',fontSize:13}}>No deliveries yet</p>}
        </div>
      </div>
    </div>
  )
}