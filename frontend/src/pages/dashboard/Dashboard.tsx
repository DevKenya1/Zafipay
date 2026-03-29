import { useQuery } from '@tanstack/react-query'
import { transactionsApi } from '../../lib/api'
import { useAuth } from '../../lib/auth'
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'

const COLORS = ['#10B95A','#635BFF','#F5A623','#009CDE','#FF0000']

export default function Dashboard() {
  const { merchant } = useAuth()

  const { data } = useQuery({
    queryKey: ['transactions'],
    queryFn: () => transactionsApi.list({ page_size: 100 }),
  })

  const transactions = data?.data?.results || []
  const completed = transactions.filter((t:any) => t.status === 'completed')
  const failed = transactions.filter((t:any) => t.status === 'failed')
  const volume = completed.reduce((s:number,t:any) => s + parseFloat(t.amount), 0)

  const byProvider = ['mpesa','stripe','flutterwave','paypal','airtel']
    .map((p,i) => ({ name:p, value:transactions.filter((t:any)=>t.provider===p).length, color:COLORS[i] }))
    .filter(p=>p.value>0)

  const last7 = Array.from({length:7},(_,i)=>{
    const d = new Date(); d.setDate(d.getDate()-6+i)
    const label = d.toLocaleDateString('en',{weekday:'short'})
    const day = d.toDateString()
    return {
      label,
      completed: completed.filter((t:any)=>new Date(t.created_at).toDateString()===day).length,
      failed: failed.filter((t:any)=>new Date(t.created_at).toDateString()===day).length,
    }
  })

  return (
    <div style={{padding:'36px 40px',minHeight:'100vh',background:'#0A0F0C',color:'#EDF7F1',fontFamily:'DM Sans,sans-serif'}}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@300;400;500&display=swap');
        .db-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:28px;}
        .db-grid2{display:grid;grid-template-columns:1.4fr 1fr;gap:20px;margin-bottom:20px;}
        .sc{background:rgba(237,247,241,0.03);border:1px solid rgba(237,247,241,0.07);border-radius:16px;padding:22px;}
        .sc-label{font-size:12px;color:rgba(237,247,241,0.35);margin-bottom:8px;}
        .sc-val{font-family:'Syne',sans-serif;font-size:28px;font-weight:700;letter-spacing:-1px;color:#EDF7F1;}
        .sc-sub{font-size:12px;color:rgba(237,247,241,0.25);margin-top:4px;}
        .panel{background:rgba(237,247,241,0.03);border:1px solid rgba(237,247,241,0.07);border-radius:16px;padding:24px;}
        .panel-title{font-size:11px;font-weight:500;color:rgba(237,247,241,0.3);margin-bottom:20px;letter-spacing:0.08em;text-transform:uppercase;}
        .tx-row{display:flex;align-items:center;justify-content:space-between;padding:10px 0;border-bottom:1px solid rgba(237,247,241,0.04);}
        .tx-row:last-child{border-bottom:none;}
        .tag{display:inline-flex;align-items:center;gap:4px;padding:3px 9px;border-radius:100px;font-size:11px;font-weight:500;}
        .tag-completed{background:rgba(16,185,90,0.1);color:#10B95A;}
        .tag-failed{background:rgba(248,113,113,0.1);color:#F87171;}
        .tag-processing{background:rgba(99,91,255,0.1);color:#635BFF;}
        .tag-pending{background:rgba(237,247,241,0.07);color:rgba(237,247,241,0.4);}
      `}</style>

      <div style={{marginBottom:28,display:'flex',alignItems:'center',justifyContent:'space-between'}}>
        <div>
          <h2 style={{fontFamily:'Syne,sans-serif',fontSize:24,fontWeight:800,letterSpacing:-0.5,color:'#EDF7F1',marginBottom:4}}>Dashboard</h2>
          <p style={{fontSize:13,color:'rgba(237,247,241,0.3)'}}>
            {merchant?.business_name}
            <span style={{marginLeft:10,padding:'2px 10px',borderRadius:100,fontSize:11,fontWeight:500,background:merchant?.mode==='test'?'rgba(245,166,35,0.1)':'rgba(16,185,90,0.1)',color:merchant?.mode==='test'?'#F5A623':'#10B95A'}}>
              {merchant?.mode} mode
            </span>
          </p>
        </div>
        <div style={{display:'flex',alignItems:'center',gap:6,fontSize:12,color:'rgba(237,247,241,0.25)'}}>
          <div style={{width:6,height:6,borderRadius:'50%',background:'#10B95A'}}/>Live data
        </div>
      </div>

      <div className="db-grid">
        <div className="sc"><div className="sc-label">Total transactions</div><div className="sc-val">{transactions.length}</div><div className="sc-sub">All time</div></div>
        <div className="sc"><div className="sc-label">Completed</div><div className="sc-val" style={{color:'#10B95A'}}>{completed.length}</div><div className="sc-sub">Successful</div></div>
        <div className="sc"><div className="sc-label">Failed</div><div className="sc-val" style={{color:'#F87171'}}>{failed.length}</div><div className="sc-sub">Unsuccessful</div></div>
        <div className="sc"><div className="sc-label">Volume (KES)</div><div className="sc-val">{Number(volume).toLocaleString()}</div><div className="sc-sub">Completed only</div></div>
      </div>

      <div className="db-grid2">
        <div className="panel">
          <div className="panel-title">Transaction activity — last 7 days</div>
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={last7} margin={{top:0,right:0,left:-28,bottom:0}}>
              <defs>
                <linearGradient id="gc" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#10B95A" stopOpacity={0.2}/><stop offset="100%" stopColor="#10B95A" stopOpacity={0}/>
                </linearGradient>
                <linearGradient id="gf" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#F87171" stopOpacity={0.15}/><stop offset="100%" stopColor="#F87171" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <XAxis dataKey="label" tick={{fill:'rgba(237,247,241,0.3)',fontSize:11}} axisLine={false} tickLine={false}/>
              <YAxis tick={{fill:'rgba(237,247,241,0.3)',fontSize:11}} axisLine={false} tickLine={false}/>
              <Tooltip contentStyle={{background:'#1A2018',border:'1px solid rgba(237,247,241,0.08)',borderRadius:8,fontSize:12,color:'#EDF7F1'}}/>
              <Area type="monotone" dataKey="completed" stroke="#10B95A" strokeWidth={2} fill="url(#gc)" name="Completed"/>
              <Area type="monotone" dataKey="failed" stroke="#F87171" strokeWidth={2} fill="url(#gf)" name="Failed"/>
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div className="panel">
          <div className="panel-title">By provider</div>
          {byProvider.length > 0 ? (
            <>
              <ResponsiveContainer width="100%" height={130}>
                <PieChart>
                  <Pie data={byProvider} cx="50%" cy="50%" innerRadius={35} outerRadius={55} dataKey="value" strokeWidth={0}>
                    {byProvider.map((p,i)=><Cell key={i} fill={p.color}/>)}
                  </Pie>
                  <Tooltip contentStyle={{background:'#1A2018',border:'1px solid rgba(237,247,241,0.08)',borderRadius:8,fontSize:12,color:'#EDF7F1'}}/>
                </PieChart>
              </ResponsiveContainer>
              <div style={{display:'flex',flexDirection:'column',gap:6,marginTop:8}}>
                {byProvider.map(p=>(
                  <div key={p.name} style={{display:'flex',alignItems:'center',justifyContent:'space-between',fontSize:12}}>
                    <div style={{display:'flex',alignItems:'center',gap:6}}>
                      <div style={{width:7,height:7,borderRadius:'50%',background:p.color}}/>
                      <span style={{color:'rgba(237,247,241,0.5)',textTransform:'capitalize'}}>{p.name}</span>
                    </div>
                    <span style={{color:'#EDF7F1',fontWeight:500}}>{p.value}</span>
                  </div>
                ))}
              </div>
            </>
          ) : <p style={{fontSize:13,color:'rgba(237,247,241,0.25)',marginTop:20}}>No data yet</p>}
        </div>
      </div>

      <div className="panel">
        <div className="panel-title">Recent transactions</div>
        {transactions.slice(0,8).map((t:any)=>(
          <div key={t.id} className="tx-row">
            <div>
              <div style={{fontSize:13,fontWeight:500,color:'#EDF7F1'}}>{t.reference}</div>
              <div style={{fontSize:11,color:'rgba(237,247,241,0.3)',marginTop:2}}>{t.provider} · {t.method?.replace('_',' ')} · {new Date(t.created_at).toLocaleDateString()}</div>
            </div>
            <div style={{textAlign:'right'}}>
              <div style={{fontSize:13,fontWeight:500,color:'#EDF7F1'}}>{t.currency} {Number(t.amount).toLocaleString()}</div>
              <span className={`tag tag-${t.status}`} style={{marginTop:4,display:'inline-flex'}}>{t.status}</span>
            </div>
          </div>
        ))}
        {transactions.length===0&&<p style={{fontSize:13,color:'rgba(237,247,241,0.25)',textAlign:'center',padding:'24px 0'}}>No transactions yet</p>}
      </div>
    </div>
  )
}