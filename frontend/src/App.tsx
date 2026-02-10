import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './hooks/useAuth'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import FindingsListPage from './pages/FindingsListPage'
import FindingDetailPage from './pages/FindingDetailPage'
import ReportsPage from './pages/ReportsPage'
import NotificationSettingsPage from './pages/NotificationSettingsPage'
import UsersManagementPage from './pages/UsersManagementPage'
import AreasManagementPage from './pages/AreasManagementPage'
import Layout from './components/Layout'

function App() {
  const { isAuthenticated, isLoading } = useAuth()

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <Routes>
      <Route
        path="/login"
        element={!isAuthenticated ? <LoginPage /> : <Navigate to="/" replace />}
      />
      <Route
        path="/"
        element={
          isAuthenticated ? (
            <Layout />
          ) : (
            <Navigate to="/login" replace />
          )
        }
      >
        <Route index element={<DashboardPage />} />
        <Route path="findings" element={<FindingsListPage />} />
        <Route path="findings/:id" element={<FindingDetailPage />} />
        <Route path="reports" element={<ReportsPage />} />
        <Route path="settings" element={<NotificationSettingsPage />} />
        <Route path="admin/users" element={<UsersManagementPage />} />
        <Route path="admin/areas" element={<AreasManagementPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default App
