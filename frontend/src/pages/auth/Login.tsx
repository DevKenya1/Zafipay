import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../lib/auth'

const providers = [
  { name: 'M-Pesa', color: '#00A651', logo: '/logos/ma_symbol_opt_45_1x.png' },
  { name: 'Airtel', color: '#FF0000', logo: '/logos/airtel.png' },
  { name: 'PayPal', color: '#009CDE', logo: '/logos/paypal.png' },
  { name: 'Visa', color: '#1A1F71', logo: '/logos/visa.png' },
  { name: 'Safaricom', color: '#00A651', logo: '/logos/SAF-MAIN-LOGO.png' },
]

export default function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    const t = setTimeout(() => setMounted(true), 80)
    return () => clearTimeout(t)
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(email, password)
      navigate('/')
    } catch {
      setError('Invalid credentials. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@300;400;500&display=swap');
        html,body,#root{height:100%;margin:0;padding:0;}
        *,*::before,*::after{box-sizing:border-box;}

        .lr{
          height:100vh;width:100vw;
          display:grid;
          grid-template-columns:1fr 440px;
          background:#060A08;
          font-family:'DM Sans',sans-serif;
          position:relative;overflow:hidden;
        }

        .gbg{
          position:absolute;inset:0;pointer-events:none;
          background-image:linear-gradient(rgba(16,185,90,0.035) 1px,transparent 1px),linear-gradient(90deg,rgba(16,185,90,0.035) 1px,transparent 1px);
          background-size:56px 56px;
        }
        .o1{position:absolute;pointer-events:none;border-radius:50%;width:600px;height:600px;top:-200px;left:-100px;background:radial-gradient(circle,rgba(16,185,90,0.09) 0%,transparent 65%);}
        .o2{position:absolute;pointer-events:none;border-radius:50%;width:350px;height:350px;bottom:-80px;left:35%;background:radial-gradient(circle,rgba(16,185,90,0.05) 0%,transparent 65%);}

        .lp{
          display:flex;flex-direction:column;justify-content:space-between;
          padding:44px 52px 36px;position:relative;z-index:1;overflow:hidden;
        }

        .logo{display:flex;align-items:center;gap:10px;font-family:'Syne',sans-serif;font-size:22px;font-weight:800;color:#10B95A;letter-spacing:-0.3px;}
        .logo-box{width:34px;height:34px;background:#10B95A;border-radius:9px;display:flex;align-items:center;justify-content:center;flex-shrink:0;}

        .lp-body{flex:1;display:flex;flex-direction:column;justify-content:center;padding:40px 0 24px;}

        .eyebrow{font-size:11px;font-weight:500;letter-spacing:0.18em;text-transform:uppercase;color:#10B95A;margin-bottom:20px;display:flex;align-items:center;gap:10px;opacity:0;transform:translateY(12px);transition:opacity 0.7s ease,transform 0.7s ease;}
        .eyebrow.in{opacity:1;transform:translateY(0);}
        .eyebrow::before{content:'';display:block;width:24px;height:1px;background:#10B95A;}

        .h1{font-family:'Syne',sans-serif;font-size:clamp(36px,4vw,58px);font-weight:800;color:#EDF7F1;line-height:1.03;letter-spacing:-2px;margin-bottom:20px;opacity:0;transform:translateY(20px);transition:opacity 0.8s ease 0.1s,transform 0.8s ease 0.1s;}
        .h1.in{opacity:1;transform:translateY(0);}
        .h1 em{color:#10B95A;font-style:normal;}

        .sub{font-size:15px;color:rgba(237,247,241,0.38);line-height:1.65;max-width:380px;font-weight:300;opacity:0;transform:translateY(16px);transition:opacity 0.8s ease 0.2s,transform 0.8s ease 0.2s;}
        .sub.in{opacity:1;transform:translateY(0);}

        .stats{display:flex;opacity:0;transform:translateY(14px);transition:opacity 0.8s ease 0.3s,transform 0.8s ease 0.3s;}
        .stats.in{opacity:1;transform:translateY(0);}
        .stat{padding:16px 28px 16px 0;margin-right:28px;border-right:1px solid rgba(16,185,90,0.15);}
        .stat:last-child{border-right:none;margin-right:0;}
        .sv{font-family:'Syne',sans-serif;font-size:28px;font-weight:700;color:#EDF7F1;letter-spacing:-1px;}
        .sl{font-size:11px;color:rgba(237,247,241,0.3);margin-top:4px;}

        .to{overflow:hidden;margin:18px 0 14px;opacity:0;transition:opacity 0.8s ease 0.45s;position:relative;}
        .to.in{opacity:1;}
        .to::before,.to::after{content:'';position:absolute;top:0;bottom:0;width:50px;z-index:2;pointer-events:none;}
        .to::before{left:0;background:linear-gradient(90deg,#060A08,transparent);}
        .to::after{right:0;background:linear-gradient(-90deg,#060A08,transparent);}

        .tt{display:flex;gap:10px;align-items:center;animation:ticker 22s linear infinite;width:max-content;}
        @keyframes ticker{to{transform:translateX(-50%);}}

        .tp{display:flex;align-items:center;gap:8px;padding:7px 14px;border-radius:100px;border:1px solid rgba(255,255,255,0.07);background:rgba(255,255,255,0.03);white-space:nowrap;flex-shrink:0;}
        .tp img{width:20px;height:20px;object-fit:contain;}
        .tp span{font-size:12px;font-weight:500;color:rgba(237,247,241,0.45);}
        .tp-dot{width:7px;height:7px;border-radius:50%;flex-shrink:0;}

        .sys{display:flex;align-items:center;gap:8px;font-size:12px;color:rgba(237,247,241,0.22);}
        .sdot{width:6px;height:6px;border-radius:50%;background:#10B95A;animation:pulse 2.5s ease-in-out infinite;}
        @keyframes pulse{0%,100%{opacity:1}50%{opacity:0.35}}

        /* RIGHT — fixed 440px, vertically centered, padding inside */
        .rp{
          display:flex;align-items:center;justify-content:center;
          padding:32px 36px;
          position:relative;z-index:1;
        }

        .fc{
          width:100%;
          background:rgba(237,247,241,0.025);
          border:1px solid rgba(237,247,241,0.07);
          border-radius:24px;padding:38px 32px;
          backdrop-filter:blur(20px);
          opacity:0;transform:translateY(16px);
          transition:opacity 0.7s ease 0.2s,transform 0.7s ease 0.2s;
        }
        .fc.in{opacity:1;transform:translateY(0);}

        .fc-badge{display:inline-flex;align-items:center;gap:6px;background:rgba(16,185,90,0.08);border:1px solid rgba(16,185,90,0.15);border-radius:100px;padding:4px 12px;font-size:11px;font-weight:500;color:#10B95A;letter-spacing:0.08em;text-transform:uppercase;margin-bottom:16px;}
        .fc-title{font-family:'Syne',sans-serif;font-size:24px;font-weight:800;color:#EDF7F1;letter-spacing:-0.8px;margin-bottom:4px;}
        .fc-sub{font-size:13px;color:rgba(237,247,241,0.3);margin-bottom:26px;font-weight:300;}

        .fld{margin-bottom:14px;}
        .fld label{display:block;font-size:11px;font-weight:500;letter-spacing:0.1em;text-transform:uppercase;color:rgba(237,247,241,0.3);margin-bottom:7px;}
        .fld input{width:100%;background:rgba(237,247,241,0.04);border:1px solid rgba(237,247,241,0.08);border-radius:11px;padding:13px 14px;font-size:14px;font-family:'DM Sans',sans-serif;color:#EDF7F1;outline:none;transition:border-color 0.2s,background 0.2s,box-shadow 0.2s;}
        .fld input::placeholder{color:rgba(237,247,241,0.14);}
        .fld input:focus{border-color:rgba(16,185,90,0.4);background:rgba(16,185,90,0.035);box-shadow:0 0 0 3px rgba(16,185,90,0.07);}

        .err{display:flex;align-items:center;gap:8px;font-size:13px;color:#F87171;background:rgba(248,113,113,0.07);border:1px solid rgba(248,113,113,0.13);border-radius:9px;padding:10px 13px;margin-bottom:14px;}

        .sbtn{width:100%;background:#10B95A;color:#060A08;border:none;border-radius:11px;padding:13px;font-size:15px;font-weight:600;font-family:'DM Sans',sans-serif;cursor:pointer;letter-spacing:0.01em;margin-top:6px;display:flex;align-items:center;justify-content:center;gap:8px;box-shadow:0 4px 20px rgba(16,185,90,0.22);transition:background 0.15s,transform 0.1s,box-shadow 0.15s;}
        .sbtn:hover:not(:disabled){background:#0EA050;transform:translateY(-1px);box-shadow:0 6px 28px rgba(16,185,90,0.32);}
        .sbtn:disabled{opacity:0.45;cursor:not-allowed;box-shadow:none;}

        .spin{width:14px;height:14px;border:2px solid rgba(6,10,8,0.2);border-top-color:#060A08;border-radius:50%;animation:spin 0.65s linear infinite;}
        @keyframes spin{to{transform:rotate(360deg);}}

        .fc-foot{margin-top:20px;padding-top:16px;border-top:1px solid rgba(237,247,241,0.06);text-align:center;font-size:11px;color:rgba(237,247,241,0.18);line-height:1.5;}
      `}</style>

      <div className="lr">
        <div className="gbg"/><div className="o1"/><div className="o2"/>

        <div className="lp">
          <div className="logo">
            <div className="logo-box">
              <svg width="18" height="18" viewBox="0 0 18 18" fill="#060A08"><path d="M9 1.5L16 5.25V12.75L9 16.5L2 12.75V5.25L9 1.5Z"/></svg>
            </div>
            Zafipay
          </div>

          <div className="lp-body">
            <div className={`eyebrow${mounted?' in':''}`}>Payment infrastructure</div>
            <h1 className={`h1${mounted?' in':''}`}>Move money<br/>at <em>internet</em><br/>speed.</h1>
            <p className={`sub${mounted?' in':''}`}>One unified API for M-Pesa, Airtel Money, Stripe, Flutterwave and PayPal. Built for Kenya, ready for the world.</p>
          </div>

          <div className={`stats${mounted?' in':''}`}>
            <div className="stat"><div className="sv">5+</div><div className="sl">Payment providers</div></div>
            <div className="stat"><div className="sv">&lt;2s</div><div className="sl">STK push latency</div></div>
            <div className="stat"><div className="sv">99.9%</div><div className="sl">Uptime SLA</div></div>
          </div>

          <div className={`to${mounted?' in':''}`}>
            <div className="tt">
              {[...providers,...providers].map((p,i)=>(
                <div key={i} className="tp">
                  <div className="tp-dot" style={{background:p.color}}/>
                  <img src={p.logo} alt={p.name} onError={e=>{(e.target as HTMLImageElement).style.display='none'}}/>
                  <span>{p.name}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="sys"><div className="sdot"/>All systems operational · sandbox active</div>
        </div>

        <div className="rp">
          <div className={`fc${mounted?' in':''}`}>
            <div className="fc-badge"><div style={{width:6,height:6,borderRadius:'50%',background:'#10B95A'}}/>Merchant portal</div>
            <div className="fc-title">Welcome back</div>
            <div className="fc-sub">Sign in to your dashboard</div>

            <form onSubmit={handleSubmit}>
              <div className="fld">
                <label>Email address</label>
                <input type="email" placeholder="you@business.com" value={email} onChange={e=>setEmail(e.target.value)} required autoComplete="email"/>
              </div>
              <div className="fld">
                <label>Password</label>
                <input type="password" placeholder="••••••••••••" value={password} onChange={e=>setPassword(e.target.value)} required autoComplete="current-password"/>
              </div>
              {error&&<div className="err"><svg width="14" height="14" viewBox="0 0 14 14" fill="none"><circle cx="7" cy="7" r="6.5" stroke="#F87171"/><path d="M7 4v3.5" stroke="#F87171" strokeWidth="1.5" strokeLinecap="round"/><circle cx="7" cy="10.5" r="0.75" fill="#F87171"/></svg>{error}</div>}
              <button type="submit" className="sbtn" disabled={loading}>
                {loading?<><div className="spin"/>Authenticating...</>:'Sign in to dashboard →'}
              </button>
            </form>
            <div className="fc-foot">256-bit encrypted · SOC2 compliant · GDPR ready</div>
          </div>
        </div>
      </div>
    </>
  )
}