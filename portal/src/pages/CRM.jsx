import { Search, X } from 'lucide-react'
import { useEffect, useState } from 'react'
import api from '../api'
import { PageTitle } from './Dashboard'

const when = (value) => value ? new Date(value).toLocaleString('en-IN', { dateStyle: 'medium', timeStyle: 'short' }) : '—'

export default function CRM() {
  const [rows, setRows] = useState([]); const [q, setQ] = useState(''); const [selected, setSelected] = useState(null)
  useEffect(() => { api.get('/api/crm/contacts', { params: { q } }).then(({ data }) => setRows(data)) }, [q])
  async function open(id) { const { data } = await api.get(`/api/crm/contacts/${id}`); setSelected(data) }
  return <>
    <PageTitle kicker="RELATIONSHIP PIPELINE" title="CRM contacts" subtitle="One contact record with the full meeting history and next action." />
    <label className="search wide-search"><Search size={17} /><input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search contact, phone, or company…" aria-label="Search CRM contacts" /></label>
    <section className="panel no-pad"><div className="table-wrap"><table><thead><tr><th>Contact</th><th>Company</th><th>Lead stage</th><th>Meetings</th><th>Next meeting</th><th>Last activity</th></tr></thead><tbody>{rows.map((item) => <tr key={item.id} className="clickable" onClick={() => open(item.id)}><td><strong>{item.name}</strong><small>{item.phone}{item.email ? ` · ${item.email}` : ''}</small></td><td>{item.company || '—'}<small>{item.designation || item.city || ''}</small></td><td><span className="stage">{item.lead_stage}</span></td><td>{item.meeting_count}</td><td>{when(item.next_meeting)}</td><td>{when(item.last_activity)}</td></tr>)}</tbody></table>{!rows.length && <div className="empty">No contacts yet. New bookings create CRM contacts automatically.</div>}</div></section>
    {selected && <div className="drawer-backdrop" onClick={() => setSelected(null)}><aside className="drawer" onClick={(e) => e.stopPropagation()}><button className="drawer-close" aria-label="Close contact details" onClick={() => setSelected(null)}><X /></button><span className="eyebrow">CRM CONTACT #{selected.id}</span><h2>{selected.name}</h2><p className="muted">{selected.phone} · {selected.email || 'No email'}</p><div className="contact-card"><div><span>Company</span><strong>{selected.company || '—'}</strong></div><div><span>Designation</span><strong>{selected.designation || '—'}</strong></div><div><span>City</span><strong>{selected.city || '—'}</strong></div><div><span>Stage</span><strong>{selected.lead_stage}</strong></div></div><h3 className="history-title">Meeting history</h3><div className="meeting-list">{selected.meetings.map((meeting) => <article key={meeting.id}><div><strong>{meeting.interest || 'General enquiry'}</strong><span>{when(meeting.start_at)}</span></div><p>{meeting.purpose}</p><small>{meeting.status} · {meeting.source}</small></article>)}</div></aside></div>}
  </>
}
