import { useAuth } from '../../lib/auth'

export default function Settings() {
  const { merchant, toggleMode } = useAuth()

  const row = (label:string, value:string) => (
    <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',padding:'14px 0',borderBottom:'1px solid rgba(237,247,241,0.05)'}}>
      <span style={{fontSize:13,color:'rgba(237,247,241,0.35)'}}>{label}</span>
      <span style={{fontSize:13,fontWeight:500,color:'#EDF7F1'}}>{value}</span>
    </div>
  )

  return (
    <div style={{padding:'36px 40px',minHeight:'100vh',background:'#0A0F0C',color:'#EDF7F1',fontFamily:'DM Sans,sans-serif'}}>
      <style>{`@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@400;500&display=swap');`}</style>

      <h2 style={{fontFamily:'Syne,sans-serif',fontSize:24,fontWeight:800,letterSpacing:-0.5,marginBottom:28}}>Settings</h2>

      <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:20,maxWidth:800}}>
        <div style={{background:'rgba(237,247,241,0.02)',border:'1px solid rgba(237,247,241,0.07)',borderRadius:16,padding:'24px'}}>
          <p style={{fontSize:11,fontWeight:500,letterSpacing:'0.1em',textTransform:'uppercase',color:'rgba(237,247,241,0.3)',marginBottom:4}}>Business details</p>
          {row('Business name', merchant?.business_name||'-')}
          {row('Email', merchant?.email||'-')}
          {row('Phone', merchant?.phone||'-')}
          {row('Country', merchant?.country||'-')}
          {row('Account status', merchant?.is_active ? 'Active' : 'Inactive')}
        </div>

        <div style={{background:'rgba(237,247,241,0.02)',border:'1px solid rgba(237,247,241,0.07)',borderRadius:16,padding:'24px'}}>
          <p style={{fontSize:11,fontWeight:500,letterSpacing:'0.1em',textTransform:'uppercase',color:'rgba(237,247,241,0.3)',marginBottom:16}}>Payment mode</p>
          <div style={{
            background: merchant?.mode==='test' ? 'rgba(245,166,35,0.05)' : 'rgba(16,185,90,0.05)',
            border: `1px solid ${merchant?.mode==='test' ? 'rgba(245,166,35,0.15)' : 'rgba(16,185,90,0.15)'}`,
            borderRadius:12, padding:'16px', marginBottom:16,
          }}>
            <div style={{display:'flex',alignItems:'center',gap:8,marginBottom:6}}>
              <div style={{width:8,height:8,borderRadius:'50%',background:merchant?.mode==='test'?'#F5A623':'#10B95A'}}/>
              <span style={{fontSize:14,fontWeight:600,color:merchant?.mode==='test'?'#F5A623':'#10B95A',textTransform:'capitalize'}}>{merchant?.mode} mode active</span>
            </div>
            <p style={{fontSize:12,color:'rgba(237,247,241,0.3)',lineHeight:1.5}}>
              {merchant?.mode==='test'
                ? 'Using sandbox credentials. No real money moves.'
                : 'Live mode. Real payments are processed.'}
            </p>
          </div>
          <button onClick={toggleMode} style={{
            width:'100%', padding:'12px', borderRadius:10, border:'none', cursor:'pointer',
            fontFamily:'DM Sans,sans-serif', fontSize:13, fontWeight:600,
            background: merchant?.mode==='test' ? '#10B95A' : 'rgba(245,166,35,0.15)',
            color: merchant?.mode==='test' ? '#060A08' : '#F5A623',
            transition:'opacity 0.15s',
          }}>
            Switch to {merchant?.mode==='test'?'live':'test'} mode
          </button>
        </div>
      </div>
    </div>
  )
}