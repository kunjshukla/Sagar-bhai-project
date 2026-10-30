import { CheckCircle2, MessageCircle, RefreshCw, Smartphone } from 'lucide-react'
import { useEffect, useState } from 'react'
import api from '../api'
import { PageTitle } from './Dashboard'

export default function WhatsApp() {
  const [state, setState] = useState(null); const [stamp, setStamp] = useState(Date.now())
  const [qrUrl, setQrUrl] = useState('')
  function load() { api.get('/api/whatsapp/status').then(({ data }) => setState(data)) }
  useEffect(() => { load(); const id = setInterval(load, 3000); return () => clearInterval(id) }, [])
  useEffect(() => {
    if (!state?.has_qr) { setQrUrl(''); return undefined }
    let active = true
    let objectUrl = ''
    api.get('/api/whatsapp/qr', { responseType: 'blob' }).then(({ data }) => {
      objectUrl = URL.createObjectURL(data)
      if (active) setQrUrl(objectUrl)
    })
    return () => {
      active = false
      if (objectUrl) URL.revokeObjectURL(objectUrl)
    }
  }, [state?.has_qr, stamp])
  return <>
    <PageTitle kicker="NEONIZE SESSION" title="WhatsApp pairing" subtitle="Link Mechman’s WhatsApp number now; the transport can be replaced with WABA later." action={<button className="secondary-button" onClick={() => { setStamp(Date.now()); load() }}><RefreshCw size={16} />Refresh</button>} />
    <section className="pair-panel">
      <div className="pair-copy">{state?.status === 'connected' ? <><div className="pair-icon connected"><CheckCircle2 /></div><span className="eyebrow">CONNECTED</span><h2>WhatsApp is linked.</h2><p>The bot is ready to receive messages. The encrypted Neonize session is persisted locally.</p></> : state?.status === 'disconnected' ? <><div className="pair-icon"><MessageCircle /></div><span className="eyebrow">SESSION OFFLINE</span><h2>WhatsApp is not running.</h2><p>Enable WhatsApp auto-start and restart the service to link a number.</p></> : <><div className="pair-icon"><MessageCircle /></div><span className="eyebrow">{state?.status === 'awaiting_scan' ? 'READY TO SCAN' : 'STARTING SESSION'}</span><h2>Link a WhatsApp number.</h2><ol><li>Open WhatsApp on your phone.</li><li>Go to Settings → Linked Devices.</li><li>Tap Link a Device and scan the QR.</li></ol></>}</div>
      <div className="qr-frame">{qrUrl ? <img src={qrUrl} alt="WhatsApp pairing QR code" /> : state?.status === 'connected' ? <Smartphone size={84} /> : <div className="qr-placeholder"><RefreshCw className="spin" />Waiting for QR…</div>}</div>
    </section>
    <div className="notice"><strong>Production path</strong><p>Neonize is isolated behind the transport adapter. When WABA credentials are ready, replace the adapter without changing booking, CRM, or dashboard data.</p></div>
  </>
}
