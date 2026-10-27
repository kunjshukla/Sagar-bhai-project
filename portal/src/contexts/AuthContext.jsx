import { createContext, useContext, useEffect, useState } from 'react'
import api, { clearToken, getToken, setToken } from '../api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!getToken()) { setLoading(false); return }
    api.get('/api/auth/me').then(({ data }) => setUser(data)).catch(() => clearToken()).finally(() => setLoading(false))
  }, [])

  async function login(username, password) {
    const { data } = await api.post('/api/auth/login', { username, password })
    setToken(data.access_token)
    setUser(data.user)
  }

  function logout() {
    clearToken(); setUser(null); window.location.href = '/login'
  }

  return <AuthContext.Provider value={{ user, loading, login, logout }}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const value = useContext(AuthContext)
  if (!value) throw new Error('useAuth must be used inside AuthProvider')
  return value
}
