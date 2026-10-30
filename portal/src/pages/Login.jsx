import { AlertCircle, ArrowRight, ShieldCheck } from 'lucide-react'
import { useState } from 'react'
import { Navigate, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

export default function Login() {
  const { login, user, loading } = useAuth()
  const navigate = useNavigate()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  async function submit(event) {
    event.preventDefault(); setBusy(true); setError('')
    try { await login(username, password); navigate('/', { replace: true }) }
    catch (requestError) { setError(requestError.response?.data?.detail || 'Unable to sign in') }
    finally { setBusy(false) }
  }

  if (loading) return <div className="screen-center">Loading dashboard…</div>
  if (user) return <Navigate to="/" replace />

  return (
    <div className="login-shell">
      <section className="login-story">
        <div className="brand light"><div className="brand-mark">MS</div><div><strong>Mechman Solutions</strong><span>Operations Console</span></div></div>
        <div>
          <span className="eyebrow">AUTODESK CAM · VADODARA</span>
          <h1>Every enquiry.<br />One clear next step.</h1>
          <p>Track meeting requests, qualification history, scheduled demos, and WhatsApp conversations from one focused workspace.</p>
        </div>
        <small>Program faster. Cut smarter.</small>
      </section>
      <section className="login-form-wrap">
        <form className="login-form" onSubmit={submit}>
          <div className="login-icon"><ShieldCheck /></div>
          <h2>Welcome back</h2><p>Sign in to Mechman’s meeting CRM.</p>
          {error && <div className="alert error"><AlertCircle size={16} />{error}</div>}
          <label>Username<input value={username} onChange={(e) => setUsername(e.target.value)} autoComplete="username" required /></label>
          <label>Password<input type="password" value={password} onChange={(e) => setPassword(e.target.value)} autoComplete="current-password" required /></label>
          <button className="primary-button" disabled={busy}>{busy ? 'Signing in…' : 'Sign in'}<ArrowRight size={18} /></button>
        </form>
      </section>
    </div>
  )
}
