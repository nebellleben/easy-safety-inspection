import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { findingsApi } from '../services/api'

function FindingDetailPage() {
  const { id } = useParams<{ id: string }>()

  const { data: finding, isLoading } = useQuery({
    queryKey: ['findings', id],
    queryFn: () => findingsApi.get(id!),
    enabled: !!id,
  })

  if (isLoading) {
    return <div className="text-center py-12">Loading...</div>
  }

  if (!finding) {
    return <div className="text-center py-12">Finding not found</div>
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
      <div className="mb-6">
        <a href="/findings" className="text-blue-600 hover:text-blue-800">
          ← Back to Findings
        </a>
      </div>

      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-start">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{finding.report_id}</h1>
            <p className="mt-1 text-sm text-gray-500">
              Reported on {new Date(finding.reported_at).toLocaleString()}
            </p>
          </div>
          <div className="flex space-x-2">
            <span className={`px-3 py-1 text-sm font-medium rounded-full ${severityColors[finding.severity]}`}>
              {finding.severity}
            </span>
            <span className={`px-3 py-1 text-sm font-medium rounded-full ${statusColors[finding.status]}`}>
              {finding.status.replace('_', ' ')}
            </span>
          </div>
        </div>

        <div className="px-6 py-6">
          <div className="grid grid-cols-2 gap-6 mb-6">
            <div>
              <h3 className="text-sm font-medium text-gray-500">Reporter</h3>
              <p className="mt-1 text-gray-900">{finding.reporter?.full_name || 'Unknown'}</p>
              <p className="text-sm text-gray-500">{finding.reporter?.staff_id}</p>
            </div>
            <div>
              <h3 className="text-sm font-medium text-gray-500">Area</h3>
              <p className="mt-1 text-gray-900">{finding.area?.full_path || finding.area?.name || 'Unknown'}</p>
            </div>
            {finding.location && (
              <div>
                <h3 className="text-sm font-medium text-gray-500">Location</h3>
                <p className="mt-1 text-gray-900">{finding.location}</p>
              </div>
            )}
            <div>
              <h3 className="text-sm font-medium text-gray-500">Assigned To</h3>
              <p className="mt-1 text-gray-900">
                {finding.assignee ? finding.assignee.full_name : 'Unassigned'}
              </p>
            </div>
          </div>

          <div className="mb-6">
            <h3 className="text-sm font-medium text-gray-500 mb-2">Description</h3>
            <p className="text-gray-900">{finding.description}</p>
          </div>

          {finding.photos && finding.photos.length > 0 && (
            <div className="mb-6">
              <h3 className="text-sm font-medium text-gray-500 mb-2">Photos</h3>
              <div className="grid grid-cols-4 gap-4">
                {finding.photos.map((photo) => (
                  <div key={photo.id} className="aspect-square bg-gray-100 rounded-lg">
                    {/* Photo would be displayed here */}
                    <div className="w-full h-full flex items-center justify-center text-gray-400">
                      📷
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {finding.status_history && finding.status_history.length > 0 && (
            <div>
              <h3 className="text-sm font-medium text-gray-500 mb-4">Status History</h3>
              <div className="space-y-4">
                {finding.status_history.map((history) => (
                  <div key={history.id} className="flex items-start">
                    <div className="flex-shrink-0 h-2 w-2 mt-2 rounded-full bg-blue-600"></div>
                    <div className="ml-4">
                      <p className="text-sm text-gray-900">
                        {history.old_status ? `Changed from ${history.old_status}` : 'Created'} to {history.new_status}
                      </p>
                      <p className="text-xs text-gray-500">
                        {new Date(history.updated_at).toLocaleString()}
                      </p>
                      {history.notes && (
                        <p className="mt-1 text-sm text-gray-600">{history.notes}</p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default FindingDetailPage
