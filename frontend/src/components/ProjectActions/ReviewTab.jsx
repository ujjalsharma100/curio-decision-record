import { Link } from 'react-router-dom';
import StatusBadge from '../DecisionRecords/StatusBadge';

function ReviewTab({ reviewItems, onStatusChange, loading }) {
  if (loading) {
    return (
      <div className="flex justify-center items-center h-32">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (!reviewItems || reviewItems.length === 0) {
    return (
      <div className="text-center py-12 bg-white rounded-lg border-2 border-dashed border-gray-300">
        <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
            d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <h3 className="mt-2 text-sm font-medium text-gray-900">All caught up</h3>
        <p className="mt-1 text-sm text-gray-500">No proposed decisions waiting for review.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {reviewItems.map((item) => (
        <div key={item.decision.id} className="bg-white rounded-lg shadow-md overflow-hidden">
          {/* Decision Header */}
          <div className="px-6 py-4 bg-yellow-50 border-b border-yellow-200">
            <div className="flex items-center justify-between">
              <Link to={`/decisions/${item.decision.id}`} className="flex items-center space-x-3 group">
                <div className="flex-shrink-0 w-8 h-8 bg-yellow-200 rounded-full flex items-center justify-center">
                  <svg className="w-4 h-4 text-yellow-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                      d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                      d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                </div>
                <h3 className="text-lg font-semibold text-gray-900 group-hover:text-indigo-600 transition-colors">
                  {item.decision.title}
                </h3>
              </Link>
              <span className="text-sm text-yellow-700 bg-yellow-100 px-3 py-1 rounded-full font-medium">
                {item.records.length} proposed record{item.records.length !== 1 ? 's' : ''}
              </span>
            </div>
          </div>

          {/* Proposed Records */}
          <div className="divide-y divide-gray-100">
            {item.records.map((record) => (
              <div key={record.id} className="px-6 py-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0 mr-4">
                    <div className="flex items-center space-x-2 mb-2">
                      <StatusBadge status="proposed" size="sm" />
                      <span className="text-xs text-gray-400">v{record.version}</span>
                    </div>
                    <p className="text-sm text-gray-800 font-medium mb-1">{record.decision_description}</p>
                    {record.context && (
                      <p className="text-xs text-gray-500 line-clamp-2">{record.context}</p>
                    )}
                    {record.rationale && (
                      <p className="text-xs text-gray-500 mt-1 line-clamp-2">
                        <span className="font-medium text-gray-600">Rationale:</span> {record.rationale}
                      </p>
                    )}
                  </div>

                  {/* Action Buttons */}
                  <div className="flex items-center space-x-2 flex-shrink-0">
                    <Link
                      to={`/records/${record.id}`}
                      className="text-xs text-gray-500 hover:text-indigo-600 underline mr-2"
                    >
                      View Details
                    </Link>
                    <button
                      onClick={() => onStatusChange(record.id, 'proposed', 'accepted')}
                      className="inline-flex items-center px-3 py-1.5 text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 transition-colors shadow-sm"
                    >
                      <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      Accept
                    </button>
                    <button
                      onClick={() => onStatusChange(record.id, 'proposed', 'rejected')}
                      className="inline-flex items-center px-3 py-1.5 text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700 transition-colors shadow-sm"
                    >
                      <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                      Reject
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

export default ReviewTab;
