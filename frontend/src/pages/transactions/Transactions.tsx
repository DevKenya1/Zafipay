import { useQuery } from '@tanstack/react-query'
import { transactionsApi } from '../../lib/api'

const statusStyle: Record<string,{bg:string,color:string}> = {
  completed: { bg:'rgba(16,185,90,0.1)', color:'#10B95A' },
  failed:    { bg:'rgba(248,113,113,0.1)', color:'#F87171' },
  processing:{ bg:'rgba(99,91,255,0.1)', color:'#635BFF' },
  pending:   { bg:'rgba(237,247,241,0.07)', color:'rgba(237,247,241,0.4)' },
  refunded:  { bg:'rgba(245,166,35,0.1)', color:'#F5A623' },
}

const providerColor: Record<string,string> = {
  mpesa:'#00A651', airtel:'#FF0000', stripe:'#635BFF',
  flutterwave:'#F5A623', paypal:'#009CDE',
}

export default function Transactions() {
  const { data, isLoading } = useQuery({
    queryKey: ['transactions'],
    queryFn: () => transactionsApi.list(),
  })

  const transactions = data?.data?.results || []

  return (
    <div style={{padding:'36px 40px',minHeight:'100vh',background:'#0A0F0C',color:'#EDF7F1',fontFamily:'DM Sans,sans-serif'}}>
      <style>{`@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@400;500&display=swap');`}</style>

      <div style={{marginBottom:28}}>
        <h2 style={{fontFamily:'Syne,sans-serif',fontSize:24,fontWeight:800,letterSpacing:-0.5,color:'#EDF7F1',marginBottom:4}}>Transactions</h2>
        <p style={{fontSize:13,color:'rgba(237,247,241,0.3)'}}>
          {transactions.length} total · all providers
        </p>
      </div>

      {isLoading ? (
        <p style={{color:'rgba(237,247,241,0.3)',fontSize:14}}>Loading...</p>
      ) : (
        <div style={{background:'rgba(237,247,241,0.02)',border:'1px solid rgba(237,247,241,0.07)',borderRadius:16,overflow:'hidden'}}>
          <table style={{width:'100%',borderCollapse:'collapse',fontSize:13}}>
            <thead>
              <tr style={{borderBottom:'1px solid rgba(237,247,241,0.06)'}}>
                {['Reference','Provider','Method','Amount','Status','Date'].map(h=>(
                  <th key={h} style={{textAlign:'left',padding:'14px 16px',fontSize:11,fontWeight:500,color:'rgba(237,247,241,0.3)',letterSpacing:'0.08em',textTransform:'uppercase'}}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {transactions.map((t:any,i:number) => (
                <tr key={t.id} style={{borderBottom: i<transactions.length-1 ? '1px solid rgba(237,247,241,0.04)' : 'none'}}>
                  <td style={{padding:'14px 16px'}}>
                    <div style={{fontWeight:500,color:'#EDF7F1'}}>{t.reference}</div>
                    <div style={{fontSize:11,color:'rgba(237,247,241,0.25)',marginTop:2,fontFamily:'monospace'}}>{t.internal_ref?.slice(0,12)}...</div>
                  </td>
                  <td style={{padding:'14px 16px'}}>
                    <div style={{display:'flex',alignItems:'center',gap:7}}>
                      <div style={{width:7,height:7,borderRadius:'50%',background:providerColor[t.provider]||'#888',flexShrink:0}}/>
                      <span style={{color:'rgba(237,247,241,0.6)',textTransform:'capitalize'}}>{t.provider}</span>
                    </div>
                  </td>
                  <td style={{padding:'14px 16px',color:'rgba(237,247,241,0.4)',textTransform:'capitalize'}}>{t.method?.replace('_',' ')}</td>
                  <td style={{padding:'14px 16px',fontWeight:500,color:'#EDF7F1'}}>{t.currency} {Number(t.amount).toLocaleString()}</td>
                  <td style={{padding:'14px 16px'}}>
                    <span style={{
                      display:'inline-flex',alignItems:'center',gap:4,
                      padding:'3px 10px',borderRadius:100,fontSize:11,fontWeight:500,
                      background:statusStyle[t.status]?.bg||'rgba(237,247,241,0.07)',
                      color:statusStyle[t.status]?.color||'rgba(237,247,241,0.4)',
                    }}>
                      <span style={{width:5,height:5,borderRadius:'50%',background:'currentColor',display:'inline-block'}}/>
                      {t.status}
                    </span>
                  </td>
                  <td style={{padding:'14px 16px',color:'rgba(237,247,241,0.3)'}}>{new Date(t.created_at).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {transactions.length===0 && (
            <p style={{textAlign:'center',padding:'48px',color:'rgba(237,247,241,0.2)',fontSize:14}}>No transactions yet</p>
          )}
        </div>
      )}
    </div>
  )
}