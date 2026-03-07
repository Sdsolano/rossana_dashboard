import { createContext, useContext, useState, useCallback, type ReactNode } from "react"

const TOKEN_KEY = "therapist_token"

type AuthContextType = {
  token: string | null
  login: (t: string) => void
  logout: () => void
  isAuthenticated: boolean
}

const AuthContext = createContext<AuthContextType | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setTokenState] = useState<string | null>(() => localStorage.getItem(TOKEN_KEY))

  const login = useCallback((t: string) => {
    localStorage.setItem(TOKEN_KEY, t)
    setTokenState(t)
  }, [])

  const logout = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY)
    setTokenState(null)
  }, [])

  return (
    <AuthContext.Provider
      value={{
        token,
        login,
        logout,
        isAuthenticated: !!token,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error("useAuth must be used within AuthProvider")
  return ctx
}

export function getAuthHeader(): { Authorization: string } | object {
  const t = localStorage.getItem(TOKEN_KEY)
  return t ? { Authorization: `Token ${t}` } : {}
}
