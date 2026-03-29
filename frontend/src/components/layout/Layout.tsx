import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../../lib/auth'
import { LayoutDashboard, ArrowLeftRight, Webhook, Key, RotateCcw, Settings, LogOut, RefreshCw } from 'lucide-react'

const nav = [
  { path:'/', label:'Dashboard', icon:LayoutDashboard },
  { path:'/transactions', label:'Transactions', icon:ArrowLeftRight },
  { path:'/webhooks', label:'Webhooks', icon:Webhook },
  { path:'/api-keys', label:'API Keys', icon:Key },
  { path:'/refunds', label:'Refunds', icon:RotateCcw },
  { path:'/settings', label:'Settings', icon:Settings },
]

export default function Layout({ children }: { children: React.ReactNode }) {
  const { merchant, logout, toggleMode } = useAuth()
  const location = useLocation()
  const navigate = useNavigate()

  return (
    <div style={{display:'flex',height:'100vh',background:'#0A0F0C',fontFamily:'DM Sans,sans-serif',overflow:'hidden'}}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@400;500&display=swap');
        .nav-link{display:flex;align-items:center;gap:10px;padding:9px 12px;border-radius:10px;font-size:13.5px;font-weight:400;color:rgba(237,247,241,0.4);text-decoration:none;transition:background 0.15s,color 0.15s;}
        .nav-link:hover{background:rgba(237,247,241,0.04);color:rgba(237,247,241,0.7);}
        .nav-link.active{background:rgba(16,185,90,0.1);color:#10B95A;font-weight:500;}
        .mode-btn{width:100%;display:flex;align-items:center;gap:8px;padding:9px 12px;border-radius:10px;font-size:13px;font-weight:500;border:none;cursor:pointer;transition:background 0.15s;font-family:'DM Sans',sans-serif;}
        .logout-btn{width:100%;display:flex;align-items:center;gap:8px;padding:9px 12px;border-radius:10px;font-size:13px;color:rgba(237,247,241,0.3);background:transparent;border:none;cursor:pointer;transition:background 0.15s,color 0.15s;font-family:'DM Sans',sans-serif;}
        .logout-btn:hover{background:rgba(248,113,113,0.07);color:#F87171;}
      `}</style>

      <aside style={{width:220,background:'#080D0A',borderRight:'1px solid rgba(237,247,241,0.06)',display:'flex',flexDirection:'column',flexShrink:0}}>
        <div style={{padding:'24px 20px 20px',borderBottom:'1px solid rgba(237,247,241,0.05)'}}>
          <div style={{display:'flex',alignItems:'center',gap:9,marginBottom:4}}>
            <div style={{width:28,height:28,background:'#10B95A',borderRadius:7,display:'flex',alignItems:'center',justifyContent:'center',flexShrink:0}}>
              <svg width="14" height="14" viewBox="0 0 18 18" fill="#080D0A"><path d="M9 1.5L16 5.25V12.75L9 16.5L2 12.75V5.25L9 1.5Z"/></svg>
            </div>
            <span style={{fontFamily:'Syne,sans-serif',fontSize:18,fontWeight:800,color:'#10B95A',letterSpacing:-0.3}}>Zafipay</span>
          </div>
          <p style={{fontSize:11,color:'rgba(237,247,241,0.25)',marginLeft:37,marginTop:2,overflow:'hidden',textOverflow:'ellipsis',whiteSpace:'nowrap'}}>{merchant?.business_name}</p>
        </div>

        <nav style={{flex:1,padding:'16px 10px',display:'flex',flexDirection:'column',gap:2}}>
          <p style={{fontSize:10,fontWeight:500,letterSpacing:'0.12em',textTransform:'uppercase',color:'rgba(237,247,241,0.2)',padding:'0 10px',marginBottom:6,marginTop:4}}>Menu</p>
          {nav.map(({path,label,icon:Icon})=>(
            <Link key={path} to={path} className={`nav-link${location.pathname===path?' active':''}`}>
              <Icon size={15}/>{label}
            </Link>
          ))}
        </nav>

        <div style={{padding:'12px 10px 20px',borderTop:'1px solid rgba(237,247,241,0.05)',display:'flex',flexDirection:'column',gap:4}}>
          <button onClick={toggleMode} className="mode-btn" style={{background:merchant?.mode==='test'?'rgba(245,166,35,0.08)':'rgba(16,185,90,0.08)',color:merchant?.mode==='test'?'#F5A623':'#10B95A'}}>
            <RefreshCw size={13}/>{merchant?.mode==='test'?'Test mode':'Live mode'}
          </button>
          <button className="logout-btn" onClick={()=>{logout();navigate('/login')}}>
            <LogOut size={13}/>Log out
          </button>
        </div>
      </aside>

      <main style={{flex:1,overflowY:'auto',background:'#0A0F0C'}}>{children}</main>
    </div>
  )
}