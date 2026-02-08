import { useState, useEffect } from 'react';
import { recordsApi } from '../../services/api';

function Changelog({ recordId }) {
  const [changelog, setChangelog] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expandedEntry, setExpandedEntry] = useState(null);

  useEffect(() => {
    loadChangelog();
  }, [recordId]);

  const loadChangelog = async () => {
    try {
      const response = await recordsApi.getChangelog(recordId);
      setChangelog(response.data);
    } catch (error) {
      console.error('Failed to load changelog:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center py-4">
        <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-gray-900">Changelog</h3>

      {changelog.length === 0 ? (
        <p className="text-gray-500 text-sm">No changes recorded yet.</p>
      ) : (
        <div className="space-y-3">
          {changelog.map((entry) => (
            <div
              key={entry.id}
              className="border border-gray-200 rounded-lg overflow-hidden"
            >
              {/* Header */}
              <button
                onClick={() => setExpandedEntry(expandedEntry === entry.id ? null : entry.id)}
                className="w-full px-4 py-3 bg-gray-50 hover:bg-gray-100 flex items-center justify-between text-left"
              >
                <div className="flex items-center space-x-3">
                  <div className="flex items-center space-x-1 text-sm">
                    <span className="font-medium text-gray-700">v{entry.from_version}</span>
                    <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                    </svg>
                    <span className="font-medium text-indigo-600">v{entry.to_version}</span>
                  </div>
                  <span className="text-sm text-gray-500">
                    {new Date(entry.changed_at).toLocaleString()}
                  </span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-xs text-gray-500">
                    {Object.keys(entry.changes || {}).length} field(s) changed
                  </span>
                  <svg
                    className={`w-5 h-5 text-gray-400 transform transition-transform ${
                      expandedEntry === entry.id ? 'rotate-180' : ''
                    }`}
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </div>
              </button>

              {/* Summary */}
              {entry.summary && (
                <div className="px-4 py-2 border-t border-gray-100 bg-white">
                  <p className="text-sm text-gray-600">{entry.summary}</p>
                </div>
              )}

              {/* Expanded Changes */}
              {expandedEntry === entry.id && entry.changes && (
                <div className="px-4 py-3 border-t border-gray-200 bg-white space-y-3">
                  {Object.entries(entry.changes).map(([field, change]) => (
                    <ChangeItem key={field} field={field} change={change} />
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function ChangeItem({ field, change }) {
  const fieldLabel = field
    .split('_')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');

  return (
    <div className="space-y-2">
      <h4 className="text-sm font-medium text-gray-700">{fieldLabel}</h4>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
        {/* Old Value */}
        <div className="bg-red-50 border border-red-200 rounded p-2">
          <span className="text-xs font-medium text-red-700 block mb-1">Before</span>
          <p className="text-sm text-red-900 whitespace-pre-wrap">
            {change.old || <span className="text-red-400 italic">empty</span>}
          </p>
        </div>
        {/* New Value */}
        <div className="bg-green-50 border border-green-200 rounded p-2">
          <span className="text-xs font-medium text-green-700 block mb-1">After</span>
          <p className="text-sm text-green-900 whitespace-pre-wrap">
            {change.new || <span className="text-green-400 italic">empty</span>}
          </p>
        </div>
      </div>
    </div>
  );
}

export default Changelog;
