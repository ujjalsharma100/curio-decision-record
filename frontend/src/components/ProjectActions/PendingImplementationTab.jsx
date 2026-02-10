import { Link } from 'react-router-dom';
import StatusBadge from '../DecisionRecords/StatusBadge';

function PendingImplementationTab({ pendingItems, onStatusChange, loading }) {
  if (loading) {
    return (
      <div className="flex justify-center items-center h-32">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (!pendingItems || pendingItems.length === 0) {
    return (
      <div className="text-center py-12 bg-white rounded-lg border-2 border-dashed border-gray-300">
        <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
            d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
        </svg>
        <h3 className="mt-2 text-sm font-medium text-gray-900">Nothing pending</h3>
        <p className="mt-1 text-sm text-gray-500">No accepted decisions waiting for implementation.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {pendingItems.map((item) => (
        <div key={item.decision.id} className="bg-white rounded-lg shadow-md overflow-hidden">
          {/* Decision Header */}
          <div className="px-6 py-4 bg-blue-50 border-b border-blue-200">
            <div className="flex items-center justify-between">
              <Link to={`/decisions/${item.decision.id}`} className="flex items-center space-x-3 group">
                <div className="flex-shrink-0 w-8 h-8 bg-blue-200 rounded-full flex items-center justify-center">
                  <svg className="w-4 h-4 text-blue-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                      d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                  </svg>
                </div>
                <h3 className="text-lg font-semibold text-gray-900 group-hover:text-indigo-600 transition-colors">
                  {item.decision.title}
                </h3>
              </Link>
              <StatusBadge status="accepted" size="sm" />
            </div>
          </div>

          {/* Accepted Record Details */}
          <div className="px-6 py-4">
            <div className="flex items-start justify-between">
              <div className="flex-1 min-w-0 mr-4">
                <div className="flex items-center space-x-2 mb-2">
                  <span className="text-xs text-gray-400">v{item.record.version}</span>
                  <span className="text-xs text-gray-400">
                    Accepted {new Date(item.record.updated_at).toLocaleDateString()}
                  </span>
                </div>
                <p className="text-sm text-gray-800 font-medium mb-1">{item.record.decision_description}</p>
                {item.record.decision_details && (
                  <p className="text-xs text-gray-500 line-clamp-2 mb-1">{item.record.decision_details}</p>
                )}
                {item.record.rationale && (
                  <p className="text-xs text-gray-500 line-clamp-2">
                    <span className="font-medium text-gray-600">Rationale:</span> {item.record.rationale}
                  </p>
                )}
                {item.record.consequences && (
                  <p className="text-xs text-gray-500 mt-1 line-clamp-2">
                    <span className="font-medium text-gray-600">Consequences:</span> {item.record.consequences}
                  </p>
                )}
              </div>

              {/* Action Buttons */}
              <div className="flex items-center space-x-2 flex-shrink-0">
                <Link
                  to={`/records/${item.record.id}`}
                  className="text-xs text-gray-500 hover:text-indigo-600 underline mr-2"
                >
                  View Details
                </Link>
                <button
                  onClick={() => onStatusChange(item.record.id, 'accepted', 'deprecated')}
                  className="inline-flex items-center px-3 py-1.5 text-sm font-medium rounded-md text-gray-700 bg-gray-100 hover:bg-gray-200 border border-gray-300 transition-colors"
                >
                  <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                      d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
                  </svg>
                  Deprecate
                </button>
              </div>
            </div>
          </div>

          {/* Implementation hint */}
          <div className="px-6 py-3 bg-gray-50 border-t border-gray-100">
            <p className="text-xs text-gray-500 flex items-center space-x-1">
              <svg className="w-3.5 h-3.5 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>This decision will move to <strong>Implemented</strong> once the code changes are applied and confirmed.</span>
            </p>
          </div>
        </div>
      ))}
    </div>
  );
}

export default PendingImplementationTab;
