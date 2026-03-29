import { createContext, useContext, useState, useEffect } from 'react'
import type { ReactNode } from 'react'
import { authApi } from './api'

interface Merchant {
  id: string
  business_name: string
  email: string
  phone: string
  country: string
  mode: string
  is_active: boolean
}

interface AuthContextType {
  merchant: Merchant | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (username: string, password: string) => Promise<void>
  logout: () => void
  toggleMode: () => Promise<void>
  refreshProfile: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [merchant, setMerchant] = useState<Merchant | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  const refreshProfile = async () => {
    try {
      const res = await authApi.getProfile()
      setMerchant(res.data)
    } catch {
      setMerchant(null)
    }
  }

  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (token) {
      refreshProfile().finally(() => setIsLoading(false))
    } else {
      setIsLoading(false)
    }
  }, [])

  const login = async (username: string, password: string) => {
    const res = await authApi.login(username, password)
    localStorage.setItem('access_token', res.data.access)
    localStorage.setItem('refresh_token', res.data.refresh)
    await refreshProfile()
  }

  const logout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    setMerchant(null)
  }

  const toggleMode = async () => {
    await authApi.toggleMode()
    await refreshProfile()
  }

  return (
    <AuthContext.Provider value={{ merchant, isAuthenticated: !!merchant, isLoading, login, logout, toggleMode, refreshProfile }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider')
  return ctx
}