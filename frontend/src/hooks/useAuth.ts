import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { authApi } from '../services/api'
import type { User } from '../types'

export function useAuth() {
  const queryClient = useQueryClient()
  const token = localStorage.getItem('access_token')

  const { data: user, isLoading, error } = useQuery({
    queryKey: ['auth', 'me'],
    queryFn: () => authApi.getMe(),
    enabled: !!token,
    retry: false,
  })

  const loginMutation = useMutation({
    mutationFn: authApi.login,
    onSuccess: (data) => {
      localStorage.setItem('access_token', data.access_token)
      queryClient.setQueryData(['auth', 'me'], data.user)
    },
  })

  const logoutMutation = useMutation({
    mutationFn: authApi.logout,
    onSuccess: () => {
      localStorage.removeItem('access_token')
      queryClient.clear()
    },
  })

  const login = (staffId: string, password: string) => {
    return loginMutation.mutateAsync({ staff_id: staffId, password })
  }

  const logout = () => {
    return logoutMutation.mutateAsync()
  }

  const isAuthenticated = !!token && !!user
  const currentUser = user as User | undefined

  return {
    user: currentUser,
    isAuthenticated,
    isLoading,
    error,
    login,
    logout,
    loginError: loginMutation.error,
  }
}
