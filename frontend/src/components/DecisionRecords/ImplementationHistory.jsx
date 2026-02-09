import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { decisionsApi } from '../../services/api';
import StatusBadge from './StatusBadge';

function ImplementationHistory({ decisionId }) {
  const [history, setHistory] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expandedRecord, setExpandedRecord] = useState(null);

  useEffect(() => {
    loadHistory();
  }, [decisionId]);

  const loadHistory = async () => {
    try {
      setLoading(true);
      const response = await decisionsApi.getImplementationHistory(decisionId);
      setHistory(response.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load implementation history');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return 'N/A';
    return new Date(dateStr).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const calculateDuration = (implementedAt, deprecatedAt) => {
    if (!implementedAt || !deprecatedAt) return null;
    const start = new Date(implementedAt);
    const end = new Date(deprecatedAt);
    const diff = end - start;
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    const months = Math.floor(days / 30);
    const years = Math.floor(months / 12);

    if (years > 0) return `${years}y ${months % 12}m`;
    if (months > 0) return `${months}m ${days % 30}d`;
    return `${days}d`;
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-48">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-8 text-red-600">
        <p>{error}</p>
        <button onClick={loadHistory} className="mt-2 text-indigo-600 hover:text-indigo-800">
          Try again
        </button>
      </div>
    );
  }

  const { current_implementation, past_implementations, total_implementations } = history || {};

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <h3 className="text-lg font-semibold text-gray-900">Implementation History</h3>
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
            {total_implementations || 0} implementation{total_implementations !== 1 ? 's' : ''}
          </span>
        </div>
      </div>

      {/* Current Implementation */}
      {current_implementation ? (
        <div className="relative">
          {/* Current Label */}
          <div className="absolute -top-3 left-4 z-10">
            <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-green-600 text-white shadow-lg">
              <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              CURRENT
            </span>
          </div>

          <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl p-6 border-2 border-green-300 shadow-lg">
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center space-x-3">
                <StatusBadge status={current_implementation.status} />
                <span className="text-sm text-gray-500">v{current_implementation.version}</span>
              </div>
              <Link 
                to={`/records/${current_implementation.id}`}
                className="text-indigo-600 hover:text-indigo-800 text-sm flex items-center space-x-1"
              >
                <span>View Details</span>
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
              </Link>
            </div>

            <div className="mb-4">
              <h4 className="font-semibold text-gray-900 mb-2">Decision</h4>
              <p className="text-gray-700 whitespace-pre-wrap">{current_implementation.decision_description}</p>
            </div>

            {current_implementation.implemented_at && (
              <div className="flex items-center text-sm text-green-700 mt-4 pt-4 border-t border-green-200">
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                <span>Implemented on {formatDate(current_implementation.implemented_at)}</span>
              </div>
            )}
          </div>
        </div>
      ) : (
        <div className="bg-gray-50 rounded-xl p-8 border-2 border-dashed border-gray-300 text-center">
          <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
              d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <h3 className="mt-2 text-sm font-medium text-gray-900">No Current Implementation</h3>
          <p className="mt-1 text-sm text-gray-500">
            No decision record is currently implemented for this decision.
          </p>
        </div>
      )}

      {/* Past Implementations Timeline */}
      {past_implementations && past_implementations.length > 0 && (
        <div>
          <h4 className="text-md font-semibold text-gray-700 mb-4 flex items-center">
            <svg className="w-5 h-5 mr-2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Previous Implementations
          </h4>

          <div className="relative">
            {/* Vertical timeline line */}
            <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-gray-200"></div>

            <div className="space-y-6">
              {past_implementations.map((impl, index) => {
                const duration = calculateDuration(impl.implemented_at, impl.deprecated_at);
                const isExpanded = expandedRecord === impl.id;

                return (
                  <div key={impl.id} className="relative pl-14">
                    {/* Timeline marker */}
                    <div className="absolute left-4 -translate-x-1/2 flex items-center justify-center w-5 h-5 rounded-full bg-gray-400 ring-4 ring-gray-100">
                      <span className="text-xs font-bold text-white">{past_implementations.length - index}</span>
                    </div>

                    {/* Card */}
                    <div 
                      className={`bg-white rounded-lg border border-gray-200 shadow-sm hover:shadow-md transition-shadow cursor-pointer ${isExpanded ? 'ring-2 ring-indigo-200' : ''}`}
                      onClick={() => setExpandedRecord(isExpanded ? null : impl.id)}
                    >
                      <div className="p-4">
                        {/* Header Row */}
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center space-x-2">
                            <StatusBadge status="deprecated" size="sm" />
                            <span className="text-xs text-gray-500">v{impl.version}</span>
                            {duration && (
                              <span className="inline-flex items-center px-2 py-0.5 rounded text-xs bg-blue-100 text-blue-700">
                                Active for {duration}
                              </span>
                            )}
                          </div>
                          <Link 
                            to={`/records/${impl.id}`}
                            onClick={(e) => e.stopPropagation()}
                            className="text-xs text-indigo-600 hover:text-indigo-800"
                          >
                            View →
                          </Link>
                        </div>

                        {/* Description Preview */}
                        <p className="text-sm text-gray-700 line-clamp-2">
                          {impl.decision_description}
                        </p>

                        {/* Dates Row */}
                        <div className="mt-3 flex items-center space-x-4 text-xs text-gray-500">
                          <div className="flex items-center">
                            <svg className="w-3.5 h-3.5 mr-1 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                            </svg>
                            {formatDate(impl.implemented_at)}
                          </div>
                          <svg className="w-4 h-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
                          </svg>
                          <div className="flex items-center">
                            <svg className="w-3.5 h-3.5 mr-1 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
                            </svg>
                            {formatDate(impl.deprecated_at)}
                          </div>
                        </div>

                        {/* Expanded content */}
                        {isExpanded && (
                          <div className="mt-4 pt-4 border-t border-gray-100 space-y-3">
                            {impl.deprecation_reason && (
                              <div>
                                <h5 className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-1">
                                  Deprecation Reason
                                </h5>
                                <p className="text-sm text-gray-700 italic">"{impl.deprecation_reason}"</p>
                              </div>
                            )}

                            {impl.rationale && (
                              <div>
                                <h5 className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-1">
                                  Original Rationale
                                </h5>
                                <p className="text-sm text-gray-600">{impl.rationale}</p>
                              </div>
                            )}

                            {impl.code_reference && (
                              <div className="bg-slate-50 p-3 rounded-lg border border-slate-200">
                                <h5 className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-1">
                                  Code Reference
                                </h5>
                                <pre className="text-sm text-gray-700 font-mono whitespace-pre-wrap overflow-x-auto">{impl.code_reference}</pre>
                              </div>
                            )}

                            {/* Superseded by relationship */}
                            {impl.outgoing_relationships?.some(r => r.relationship_type === 'superseded_by') && (
                              <div className="flex items-center text-sm text-indigo-600">
                                <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                                    d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                                </svg>
                                <span>Superseded by newer implementation</span>
                              </div>
                            )}
                          </div>
                        )}

                        {/* Expand indicator */}
                        <div className="mt-2 flex justify-center">
                          <svg 
                            className={`w-4 h-4 text-gray-400 transition-transform ${isExpanded ? 'rotate-180' : ''}`} 
                            fill="none" 
                            stroke="currentColor" 
                            viewBox="0 0 24 24"
                          >
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                          </svg>
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* Empty state for past implementations */}
      {(!past_implementations || past_implementations.length === 0) && current_implementation && (
        <div className="text-center py-6 text-gray-500">
          <p className="text-sm">This is the first implementation - no previous versions.</p>
        </div>
      )}
    </div>
  );
}

export default ImplementationHistory;
