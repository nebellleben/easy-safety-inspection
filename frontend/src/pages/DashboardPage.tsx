import { useQuery } from '@tanstack/react-query'
import { findingsApi } from '../services/api'

function DashboardPage() {
  const { data: findingsData } = useQuery({
    queryKey: ['findings', 'dashboard'],
    queryFn: () => findingsApi.list({ page_size: 10 }),
  })

  const findings = findingsData?.items || []

  // Calculate statistics
  const stats = {
    total: findings.length,
    open: findings.filter((f) => f.status === 'open').length,
    inProgress: findings.filter((f) => f.status === 'in_progress').length,
    critical: findings.filter((f) => f.severity === 'critical').length,
  }

  const severityColors = {
    low: 'severity-low',
    medium: 'severity-medium',
    high: 'severity-high',
    critical: 'severity-critical',
  }

  const statusColors = {
    open: 'status-open',
    in_progress: 'status-in_progress',
    resolved: 'status-resolved',
    closed: 'status-closed',
  }

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Dashboard</h1>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-sm font-medium text-gray-500">Total Findings</div>
          <div className="mt-2 text-3xl font-bold text-gray-900">{stats.total}</div>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-sm font-medium text-gray-500">Open</div>
          <div className="mt-2 text-3xl font-bold text-blue-600">{stats.open}</div>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-sm font-medium text-gray-500">In Progress</div>
          <div className="mt-2 text-3xl font-bold text-purple-600">{stats.inProgress}</div>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-sm font-medium text-gray-500">Critical</div>
          <div className="mt-2 text-3xl font-bold text-red-600">{stats.critical}</div>
        </div>
      </div>

      {/* Recent Findings */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-medium text-gray-900">Recent Findings</h2>
        </div>
        <div className="divide-y divide-gray-200">
          {findings.length === 0 ? (
            <div className="px-6 py-12 text-center text-gray-500">
              No findings yet. Use the Telegram bot to report issues.
            </div>
          ) : (
            findings.map((finding) => (
              <div key={finding.id} className="px-6 py-4 hover:bg-gray-50">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      <span className="font-medium text-gray-900">{finding.report_id}</span>
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${severityColors[finding.severity]}`}>
                        {finding.severity}
                      </span>
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${statusColors[finding.status]}`}>
                        {finding.status.replace('_', ' ')}
                      </span>
                    </div>
                    <p className="mt-1 text-sm text-gray-600 line-clamp-1">
                      {finding.description}
                    </p>
                    <p className="mt-1 text-xs text-gray-400">
                      {finding.area?.name || 'Unknown area'} • {new Date(finding.reported_at).toLocaleDateString()}
                    </p>
                  </div>
                  <button
                    onClick={() => (window.location.href = `/findings/${finding.id}`)}
                    className="ml-4 text-sm text-blue-600 hover:text-blue-800"
                  >
                    View
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  )
}

export default DashboardPage
