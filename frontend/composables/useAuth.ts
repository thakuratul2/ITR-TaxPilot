export interface UserProfile {
  id: string
  email: string
  full_name?: string
  name?: string
  is_active?: boolean
  created_at?: string
}

export const useAuth = () => {
  const currentUser = useState<UserProfile | null>('auth_user', () => null)
  const authToken = useState<string | null>('auth_token', () => null)
  const isAuthModalOpen = useState<boolean>('auth_modal_open', () => false)
  const isSignupMode = useState<boolean>('auth_signup_mode', () => false)
  const hasPendingResults = useState<boolean>('auth_pending_results', () => false)
  const authError = useState<string | null>('auth_error', () => null)
  const isSubmitting = useState<boolean>('auth_submitting', () => false)

  // Initialize from localStorage on client
  const initAuth = async () => {
    if (import.meta.client) {
      const storedToken = localStorage.getItem('taxpilot_token')
      const storedUser = localStorage.getItem('taxpilot_user')
      if (storedToken) {
        authToken.value = storedToken
        if (storedUser) {
          try {
            currentUser.value = JSON.parse(storedUser)
          } catch {
            // Ignore
          }
        }
        await verifySession()
      }
    }
  }

  const verifySession = async () => {
    if (!authToken.value) return
    try {
      const res = await fetch('/api/v1/auth/me', {
        headers: { Authorization: `Bearer ${authToken.value}` },
      })
      if (res.ok) {
        const user = await res.json()
        currentUser.value = user
        if (import.meta.client) {
          localStorage.setItem('taxpilot_user', JSON.stringify(user))
        }
      } else {
        logout()
      }
    } catch {
      // Offline fallback
    }
  }

  const register = async (email: string, password: string, fullName?: string) => {
    isSubmitting.value = true
    authError.value = null
    try {
      const res = await fetch('/api/v1/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password, full_name: fullName }),
      })
      const data = await res.json()
      if (res.ok && data.access_token) {
        authToken.value = data.access_token
        currentUser.value = data.user
        if (import.meta.client) {
          localStorage.setItem('taxpilot_token', data.access_token)
          localStorage.setItem('taxpilot_user', JSON.stringify(data.user))
        }
        isAuthModalOpen.value = false
        return true
      } else {
        authError.value = data.detail || 'Registration failed.'
        return false
      }
    } catch {
      // Demo fallback
      const mockUser = { id: 'usr_demo', email, full_name: fullName || 'Taxpayer' }
      currentUser.value = mockUser
      authToken.value = 'demo-jwt-token'
      if (import.meta.client) {
        localStorage.setItem('taxpilot_token', 'demo-jwt-token')
        localStorage.setItem('taxpilot_user', JSON.stringify(mockUser))
      }
      isAuthModalOpen.value = false
      return true
    } finally {
      isSubmitting.value = false
    }
  }

  const login = async (email: string, password: string) => {
    isSubmitting.value = true
    authError.value = null
    try {
      const res = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      })
      const data = await res.json()
      if (res.ok && data.access_token) {
        authToken.value = data.access_token
        currentUser.value = data.user
        if (import.meta.client) {
          localStorage.setItem('taxpilot_token', data.access_token)
          localStorage.setItem('taxpilot_user', JSON.stringify(data.user))
        }
        isAuthModalOpen.value = false
        return true
      } else {
        authError.value = data.detail || 'Invalid email or password.'
        return false
      }
    } catch {
      const mockUser = { id: 'usr_demo', email, full_name: email.split('@')[0] }
      currentUser.value = mockUser
      authToken.value = 'demo-jwt-token'
      if (import.meta.client) {
        localStorage.setItem('taxpilot_token', 'demo-jwt-token')
        localStorage.setItem('taxpilot_user', JSON.stringify(mockUser))
      }
      isAuthModalOpen.value = false
      return true
    } finally {
      isSubmitting.value = false
    }
  }

  const logout = async () => {
    try {
      await fetch('/api/v1/auth/logout', { method: 'POST' })
    } catch {
      // Ignore
    }
    currentUser.value = null
    authToken.value = null
    if (import.meta.client) {
      localStorage.removeItem('taxpilot_token')
      localStorage.removeItem('taxpilot_user')
    }
  }

  const openAuthModal = (isSignup = false, pending = false) => {
    isSignupMode.value = isSignup
    hasPendingResults.value = pending
    authError.value = null
    isAuthModalOpen.value = true
  }

  const closeAuthModal = () => {
    isAuthModalOpen.value = false
  }

  return {
    currentUser,
    authToken,
    isAuthModalOpen,
    isSignupMode,
    hasPendingResults,
    authError,
    isSubmitting,
    initAuth,
    login,
    register,
    logout,
    openAuthModal,
    closeAuthModal,
  }
}
