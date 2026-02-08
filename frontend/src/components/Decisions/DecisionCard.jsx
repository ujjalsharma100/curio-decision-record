import { Link } from 'react-router-dom';
import StatusBadge from '../DecisionRecords/StatusBadge';

function DecisionCard({ decision, onEdit, onDelete }) {
  const statusCounts = decision.status_counts || {};
  const totalRecords = decision.record_count || 0;

  return (
    <div className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow p-6">
      <div className="flex justify-between items-start">
        <Link to={`/decisions/${decision.id}`} className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900 hover:text-indigo-600">
            {decision.title}
          </h3>
        </Link>
        <div className="flex space-x-2">
          <button
            onClick={onEdit}
            className="text-gray-400 hover:text-indigo-600"
            title="Edit"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
          </button>
          <button
            onClick={onDelete}
            className="text-gray-400 hover:text-red-600"
            title="Delete"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        </div>
      </div>

      <div className="mt-4">
        <div className="mb-2">
          <h4 className="text-sm font-medium text-gray-700 mb-2">Records</h4>
          {totalRecords === 0 ? (
            <span className="text-sm text-gray-500">No records yet</span>
          ) : (
            <div className="flex flex-wrap gap-2">
              {Object.entries(statusCounts).map(([status, count]) => (
                <span key={status} className="inline-flex items-center space-x-1">
                  <StatusBadge status={status} size="sm" />
                  <span className="text-xs text-gray-500">({count})</span>
                </span>
              ))}
            </div>
          )}
        </div>
        <div className="flex items-center justify-between text-sm text-gray-400">
          <span>{totalRecords} record{totalRecords !== 1 ? 's' : ''} total</span>
          <span>{new Date(decision.created_at).toLocaleDateString()}</span>
        </div>
      </div>
    </div>
  );
}

export default DecisionCard;
