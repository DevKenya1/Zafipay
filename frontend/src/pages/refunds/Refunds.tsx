import { useQuery } from '@tanstack/react-query'
import { refundsApi } from '../../lib/api'
import { RotateCcw } from 'lucide-react'

const statusStyle: Record<string,{bg:string,color:string}> = {
  completed:{ bg:'rgba(16,185,90,0.1)', color:'#10B95A' },
  failed:{ bg:'rgba(248,113,113,0.1)', color:'#F87171' },
  pending:{ bg:'rgba(237,247,241,0.06)', color:'rgba(237,247,241,0.4)' },
  processing:{ bg:'rgba(99,91,255,0.1)', color:'#635BFF' },
}

export default function Refunds() {
  const { data, isLoading } = useQuery({ queryKey:['refunds'], queryFn:()=>refundsApi.list() })
  const refunds = data?.data?.results || []

  return (
    <div style={{padding:'36px 40px',minHeight:'100vh',background:'#0A0F0C',color:'#EDF7F1',fontFamily:'DM Sans,sans-serif'}}>
      <style>{`@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@400;500&display=swap');`}</style>

      <div style={{marginBottom:28}}>
        <h2 style={{fontFamily:'Syne,sans-serif',fontSize:24,fontWeight:800,letterSpacing:-0.5,color:'#EDF7F1',marginBottom:4}}>Refunds</h2>
        <p style={{fontSize:13,color:'rgba(237,247,241,0.3)'}}>
          {refunds.length} refund{refunds.length!==1?'s':''} · all providers
        </p>
      </div>

      {isLoading ? (
        <p style={{color:'rgba(237,247,241,0.3)',fontSize:14}}>Loading...</p>
      ) : refunds.length === 0 ? (
        <div style={{display:'flex',flexDirection:'column',alignItems:'center',justifyContent:'center',padding:'80px 0',gap:16}}>
          <div style={{width:56,height:56,borderRadius:16,background:'rgba(237,247,241,0.04)',border:'1px solid rgba(237,247,241,0.07)',display:'flex',alignItems:'center',justifyContent:'center'}}>
            <RotateCcw size={22} color="rgba(237,247,241,0.2)"/>
          </div>
          <p style={{fontSize:14,color:'rgba(237,247,241,0.25)',textAlign:'center'}}>No refunds yet</p>
          <p style={{fontSize:12,color:'rgba(237,247,241,0.15)',textAlign:'center',maxWidth:300}}>Refunds appear here once you process them from a completed transaction</p>
        </div>
      ) : (
        <div style={{background:'rgba(237,247,241,0.02)',border:'1px solid rgba(237,247,241,0.07)',borderRadius:16,overflow:'hidden'}}>
          <table style={{width:'100%',borderCollapse:'collapse',fontSize:13}}>
            <thead>
              <tr style={{borderBottom:'1px solid rgba(237,247,241,0.05)'}}>
                {['Transaction','Provider','Amount','Reason','Status','Date'].map(h=>(
                  <th key={h} style={{textAlign:'left',padding:'13px 16px',fontSize:11,fontWeight:500,color:'rgba(237,247,241,0.25)',letterSpacing:'0.08em',textTransform:'uppercase'}}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {refunds.map((r:any,i:number)=>(
                <tr key={r.id} style={{borderBottom:i<refunds.length-1?'1px solid rgba(237,247,241,0.04)':'none'}}>
                  <td style={{padding:'13px 16px'}}>
                    <code style={{fontSize:12,color:'rgba(237,247,241,0.5)',background:'rgba(237,247,241,0.04)',padding:'2px 8px',borderRadius:5}}>{r.transaction_ref?.slice(0,12)}...</code>
                  </td>
                  <td style={{padding:'13px 16px',color:'rgba(237,247,241,0.5)',textTransform:'capitalize'}}>{r.provider}</td>
                  <td style={{padding:'13px 16px',fontWeight:500,color:'#EDF7F1'}}>{r.amount}</td>
                  <td style={{padding:'13px 16px',color:'rgba(237,247,241,0.4)'}}>{r.reason||'—'}</td>
                  <td style={{padding:'13px 16px'}}>
                    <span style={{display:'inline-flex',alignItems:'center',gap:4,padding:'3px 10px',borderRadius:100,fontSize:11,fontWeight:500,...(statusStyle[r.status]||statusStyle.pending)}}>
                      <span style={{width:5,height:5,borderRadius:'50%',background:'currentColor',display:'inline-block'}}/>
                      {r.status}
                    </span>
                  </td>
                  <td style={{padding:'13px 16px',color:'rgba(237,247,241,0.3)'}}>{new Date(r.created_at).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}