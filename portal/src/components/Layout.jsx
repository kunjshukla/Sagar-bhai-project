import { useState } from 'react'
import { Menu, X } from 'lucide-react'
import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar'

export default function Layout() {
  const [open, setOpen] = useState(false)
  return (
    <div className="app-shell">
      <aside className={`sidebar-wrap ${open ? 'open' : ''}`}><Sidebar onNavigate={() => setOpen(false)} /></aside>
      {open && <button className="scrim" aria-label="Close menu" onClick={() => setOpen(false)} />}
      <section className="app-main">
        <header className="mobile-header">
          <div className="brand-mark small">MS</div><strong>Mechman CRM</strong>
          <button className="icon-button" onClick={() => setOpen((v) => !v)}>{open ? <X /> : <Menu />}</button>
        </header>
        <main className="page"><Outlet /></main>
      </section>
    </div>
  )
}
