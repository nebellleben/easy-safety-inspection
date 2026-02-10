import { useQuery, useMutation } from '@tanstack/react-query'
import { notificationsApi } from '../services/api'

function NotificationSettingsPage() {
  const { data: settings, isLoading } = useQuery({
    queryKey: ['notifications', 'settings'],
    queryFn: () => notificationsApi.getSettings(),
  })

  const updateMutation = useMutation({
    mutationFn: notificationsApi.updateSettings,
  })

  if (isLoading) {
    return <div className="text-center py-12">Loading...</div>
  }

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Notification Settings</h1>
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-medium text-gray-900">Configure your notification preferences</h2>
        </div>
        <div className="px-6 py-6 space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-medium text-gray-900">New Finding Alerts</h3>
              <p className="text-sm text-gray-500">Get notified when new findings are reported in your area</p>
            </div>
            <input
              type="checkbox"
              checked={settings?.new_finding ?? false}
              onChange={(e) => updateMutation.mutate({ ...settings!, new_finding: e.target.checked })}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
          </div>
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-medium text-gray-900">Status Change Alerts</h3>
              <p className="text-sm text-gray-500">Get notified when findings change status</p>
            </div>
            <input
              type="checkbox"
              checked={settings?.status_change ?? false}
              onChange={(e) => updateMutation.mutate({ ...settings!, status_change: e.target.checked })}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
          </div>
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-medium text-gray-900">Daily Summary</h3>
              <p className="text-sm text-gray-500">Receive a daily summary of open findings</p>
            </div>
            <input
              type="checkbox"
              checked={settings?.daily_summary ?? false}
              onChange={(e) => updateMutation.mutate({ ...settings!, daily_summary: e.target.checked })}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
          </div>
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-medium text-gray-900">Weekly Summary</h3>
              <p className="text-sm text-gray-500">Receive a weekly summary report</p>
            </div>
            <input
              type="checkbox"
              checked={settings?.weekly_summary ?? false}
              onChange={(e) => updateMutation.mutate({ ...settings!, weekly_summary: e.target.checked })}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
          </div>
        </div>
      </div>
    </div>
  )
}

export default NotificationSettingsPage
