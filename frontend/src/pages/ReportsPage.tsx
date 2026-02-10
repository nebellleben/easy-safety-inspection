function ReportsPage() {
  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Reports</h1>
      <div className="bg-white rounded-lg shadow p-6">
        <p className="text-gray-500">Generate summary reports for your areas.</p>
        <div className="mt-4">
          <label className="block text-sm font-medium text-gray-700">Date Range</label>
          <div className="mt-2 flex space-x-4">
            <input
              type="date"
              className="border border-gray-300 rounded-md px-3 py-2"
            />
            <input
              type="date"
              className="border border-gray-300 rounded-md px-3 py-2"
            />
            <button className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700">
              Generate Report
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ReportsPage
