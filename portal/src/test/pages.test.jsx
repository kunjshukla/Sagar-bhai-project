import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, beforeEach, describe, expect, test, vi } from 'vitest'

import BookingForm from '../pages/BookingForm'
import Layout from '../components/Layout'
import Sidebar from '../components/Sidebar'
import CRM from '../pages/CRM'
import Dashboard from '../pages/Dashboard'
import Login from '../pages/Login'
import Meetings from '../pages/Meetings'
import Settings from '../pages/Settings'
import WhatsApp from '../pages/WhatsApp'

const api = vi.hoisted(() => ({
  get: vi.fn(),
  post: vi.fn(),
  patch: vi.fn(),
  put: vi.fn(),
}))
const publicApi = vi.hoisted(() => ({ get: vi.fn(), post: vi.fn() }))
const auth = vi.hoisted(() => ({
  login: vi.fn(),
  logout: vi.fn(),
  user: { full_name: 'Mechman Admin', role: 'admin' },
}))

vi.mock('../api', () => ({ default: api, publicApi, API_BASE_URL: '' }))
vi.mock('../contexts/AuthContext', () => ({ useAuth: () => auth }))

const renderRoute = (component, route = '/') => render(
  <MemoryRouter initialEntries={[route]}>{component}</MemoryRouter>,
)

beforeEach(() => {
  api.get.mockReset()
  api.post.mockReset()
  api.patch.mockReset()
  api.put.mockReset()
  publicApi.get.mockReset()
  publicApi.post.mockReset()
  auth.login.mockReset()
  auth.logout.mockReset()
})

afterEach(cleanup)

describe('dashboard controls', () => {
  test('login submits credentials and reports an invalid login', async () => {
    const user = userEvent.setup()
    auth.login.mockRejectedValueOnce({ response: { data: { detail: 'Invalid username or password' } } })
    renderRoute(<Login />, '/login')

    await user.type(screen.getByLabelText('Username'), 'admin')
    await user.type(screen.getByLabelText('Password'), 'wrong-password')
    await user.click(screen.getByRole('button', { name: /sign in/i }))

    expect(auth.login).toHaveBeenCalledWith('admin', 'wrong-password')
    expect(await screen.findByText('Invalid username or password')).toBeVisible()
  })

  test('booking form loads slots, selects a time, and submits', async () => {
    const user = userEvent.setup()
    publicApi.get.mockImplementation((url) => {
      if (url === '/api/public/config') return Promise.resolve({ data: { business_hours: 'Monday-Saturday' } })
      return Promise.resolve({ data: [{ start_time: '09:00', label: '9:00 AM' }] })
    })
    publicApi.post.mockResolvedValue({
      data: { meeting_id: 7, start_at: '2027-01-04T09:00:00+05:30' },
    })
    renderRoute(<BookingForm />, '/book?name=Asha&phone=9876543210')

    await user.type(screen.getByLabelText('Email address *'), 'asha@example.com')
    fireEvent.change(screen.getByLabelText('Meeting date *'), { target: { value: '2026-11-02' } })
    await user.click(await screen.findByRole('button', { name: /9:00 AM/i }))
    await user.click(screen.getByRole('button', { name: 'Book meeting' }))

    expect(publicApi.post).toHaveBeenCalledWith('/api/public/meetings', expect.objectContaining({
      name: 'Asha', phone: '9876543210', email: 'asha@example.com', start_time: '09:00',
    }))
    expect(await screen.findByText('Your meeting is requested.')).toBeVisible()
  })

  test('meetings search, filters, opens a record, and updates fields', async () => {
    const user = userEvent.setup()
    const meeting = {
      id: 1, name: 'Asha Shah', phone: '919876543210', company: 'Acme',
      interest: 'Fusion 360', purpose: 'CAM workflow', start_at: '2027-01-04T09:00:00+05:30',
      meeting_mode: 'Video', lead_stage: 'new', status: 'requested', history: [],
    }
    api.get.mockImplementation((url) => Promise.resolve({ data: url === '/api/meetings/1' ? meeting : [meeting] }))
    api.patch.mockImplementation((_url, change) => Promise.resolve({ data: { ...meeting, ...change, history: [] } }))
    renderRoute(<Meetings />)

    expect(await screen.findByText('Asha Shah')).toBeVisible()
    await user.type(screen.getByPlaceholderText(/Search name/), 'Asha')
    await user.selectOptions(screen.getByRole('combobox', { name: 'Filter by status' }), 'requested')
    await user.click(screen.getByText('Asha Shah'))
    expect(await screen.findByText('REQUEST #1')).toBeVisible()

    await user.selectOptions(screen.getByRole('combobox', { name: 'Status' }), 'confirmed')
    expect(api.patch).toHaveBeenCalledWith('/api/meetings/1', { status: 'confirmed' })

    const assigned = screen.getByLabelText('Assigned to')
    await user.type(assigned, 'Kiran')
    fireEvent.blur(assigned)
    expect(api.patch).toHaveBeenCalledWith('/api/meetings/1', { assigned_to: 'Kiran' })
    await user.click(screen.getByRole('button', { name: 'Close meeting details' }))
    expect(screen.queryByText('REQUEST #1')).not.toBeInTheDocument()
  })

  test('CRM search opens and closes a contact drawer', async () => {
    const user = userEvent.setup()
    const row = { id: 2, name: 'Dev Mehta', phone: '919999999999', email: 'dev@example.com', company: 'Delta', lead_stage: 'qualified', meeting_count: 1 }
    api.get.mockImplementation((url) => Promise.resolve({ data: url === '/api/crm/contacts/2' ? { ...row, meetings: [] } : [row] }))
    renderRoute(<CRM />)

    await user.type(screen.getByPlaceholderText(/Search contact/), 'Dev')
    expect(await screen.findByText('Dev Mehta')).toBeVisible()
    await user.click(screen.getByText('Dev Mehta'))
    expect(await screen.findByText('CRM CONTACT #2')).toBeVisible()
    await user.click(screen.getByRole('button', { name: 'Close contact details' }))
    expect(screen.queryByText('CRM CONTACT #2')).not.toBeInTheDocument()
  })

  test('notification settings toggle and save', async () => {
    const user = userEvent.setup()
    const settings = {
      reminder_enabled: true,
      reminder_minutes_before: 60,
      followup_enabled: true,
      followup_days: [1, 3],
      reminder_template: 'Reminder message long enough for validation',
      followup_template: 'Follow-up message long enough for validation',
    }
    api.get.mockImplementation((url) => Promise.resolve({ data: url.endsWith('/deliveries') ? [] : settings }))
    api.put.mockResolvedValue({ data: { ...settings, reminder_enabled: false } })
    renderRoute(<Settings />)

    const reminderToggle = await screen.findByRole('checkbox', { name: /Enable reminders/i })
    await user.click(reminderToggle)
    await user.click(screen.getByRole('button', { name: /Save settings/i }))

    expect(api.put).toHaveBeenCalledWith('/api/settings/notifications', expect.objectContaining({
      reminder_enabled: false, reminder_minutes_before: 60, followup_days: [1, 3],
    }))
    expect(await screen.findByText('Notification settings saved.')).toBeVisible()
  })

  test('WhatsApp status and refresh call the API', async () => {
    const user = userEvent.setup()
    api.get.mockResolvedValue({ data: { status: 'connected', has_qr: false } })
    renderRoute(<WhatsApp />)

    expect(await screen.findByText('WhatsApp is linked.')).toBeVisible()
    await user.click(screen.getByRole('button', { name: /Refresh/i }))
    expect(api.get).toHaveBeenCalledTimes(2)
  })

  test('WhatsApp QR is loaded through the authenticated API client', async () => {
    api.get.mockImplementation((url) => Promise.resolve({
      data: url === '/api/whatsapp/qr'
        ? new Blob(['qr'], { type: 'image/png' })
        : { status: 'awaiting_scan', has_qr: true },
    }))
    renderRoute(<WhatsApp />)

    const image = await screen.findByRole('img', { name: 'WhatsApp pairing QR code' })
    expect(image).toHaveAttribute('src', 'blob:mock-qr')
    expect(api.get).toHaveBeenCalledWith('/api/whatsapp/qr', { responseType: 'blob' })
  })

  test('analytics renders all summary cards and recent meetings', async () => {
    api.get.mockResolvedValue({ data: {
      total_contacts: 5, total_meetings: 5, upcoming_meetings: 4, today_meetings: 1,
      by_status: [{ status: 'requested', count: 5 }], monthly_trend: [{ month: '2027-01', count: 5 }],
      recent_meetings: [{ id: 1, name: 'Asha Shah', phone: '919876543210', status: 'requested' }],
    } })
    renderRoute(<Dashboard />)

    expect(await screen.findByText('Asha Shah')).toBeVisible()
    expect(screen.getByText('CRM contacts')).toBeVisible()
    expect(screen.getByText('Meeting requests')).toBeVisible()
  })

  test('sidebar navigation, sign out, and mobile menu controls respond', async () => {
    const user = userEvent.setup()
    const onNavigate = vi.fn()
    const { unmount } = renderRoute(<Sidebar onNavigate={onNavigate} />)

    await user.click(screen.getByRole('link', { name: /Meetings/i }))
    expect(onNavigate).toHaveBeenCalled()
    await user.click(screen.getByRole('button', { name: /Sign out/i }))
    expect(auth.logout).toHaveBeenCalled()
    unmount()

    renderRoute(<Layout />)
    await user.click(screen.getByRole('button', { name: 'Open menu' }))
    expect(screen.getByRole('button', { name: 'Close menu' })).toBeVisible()
    await user.click(screen.getByRole('button', { name: 'Close menu' }))
    expect(screen.getByRole('button', { name: 'Open menu' })).toBeVisible()
  })
})
