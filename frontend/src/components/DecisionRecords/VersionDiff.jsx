import { useState } from 'react';
import { recordsApi } from '../../services/api';

function VersionDiff({ recordId, versions, currentVersion }) {
  const [fromVersion, setFromVersion] = useState('');
  const [toVersion, setToVersion] = useState('');
  const [diff, setDiff] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleCompare = async () => {
    if (!fromVersion || !toVersion) return;

    setLoading(true);
    setError(null);
    setDiff(null);

    try {
      // Handle "current" as a string, otherwise parse as integer
      const from = fromVersion === 'current' ? 'current' : parseInt(fromVersion);
      const to = toVersion === 'current' ? 'current' : parseInt(toVersion);
      const response = await recordsApi.getDiff(recordId, from, to);
      setDiff(response.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load diff');
    } finally {
      setLoading(false);
    }
  };

  const availableVersions = versions.map((v) => v.version).sort((a, b) => b - a);

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-gray-900">Compare Versions</h3>

      {/* Version Selectors */}
      <div className="flex items-center space-x-4">
        <div className="flex-1">
          <label className="block text-sm font-medium text-gray-700 mb-1">From Version</label>
          <select
            value={fromVersion}
            onChange={(e) => setFromVersion(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
          >
            <option value="">Select version...</option>
            <option value="current">Current (v{currentVersion || '?'})</option>
            {availableVersions.map((v) => (
              <option key={v} value={v}>
                Version {v}
              </option>
            ))}
          </select>
        </div>

        <div className="pt-6">
          <svg className="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
          </svg>
        </div>

        <div className="flex-1">
          <label className="block text-sm font-medium text-gray-700 mb-1">To Version</label>
          <select
            value={toVersion}
            onChange={(e) => setToVersion(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
          >
            <option value="">Select version...</option>
            <option value="current">Current (v{currentVersion || '?'})</option>
            {availableVersions.map((v) => (
              <option key={v} value={v}>
                Version {v}
              </option>
            ))}
          </select>
        </div>

        <div className="pt-6">
          <button
            onClick={handleCompare}
            disabled={!fromVersion || !toVersion || loading}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Comparing...' : 'Compare'}
          </button>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
          {error}
        </div>
      )}

      {/* Diff Results */}
      {diff && (
        <div className="border border-gray-200 rounded-lg overflow-hidden">
          <div className="px-4 py-3 bg-gray-50 border-b border-gray-200">
            <p className="text-sm font-medium text-gray-700">
              Changes from <span className="text-indigo-600">
                {diff.from_version === 'current' ? `Current (v${diff.from_version_number || '?'})` : `v${diff.from_version}`}
              </span> to{' '}
              <span className="text-indigo-600">
                {diff.to_version === 'current' ? `Current (v${diff.to_version_number || '?'})` : `v${diff.to_version}`}
              </span>
            </p>
          </div>

          <div className="p-4">
            {Object.keys(diff.changes).length === 0 ? (
              <p className="text-gray-500 text-sm text-center py-4">No changes between these versions</p>
            ) : (
              <div className="space-y-4">
                {Object.entries(diff.changes).map(([field, change]) => (
                  <DiffField key={field} field={field} change={change} />
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

function DiffField({ field, change }) {
  const fieldLabel = field
    .split('_')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');

  return (
    <div className="space-y-2">
      <h4 className="text-sm font-medium text-gray-900">{fieldLabel}</h4>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
        {/* Old Value */}
        <div className="relative">
          <div className="absolute top-0 left-0 px-2 py-0.5 bg-red-100 text-red-700 text-xs font-medium rounded-br">
            Old
          </div>
          <div className="bg-red-50 border border-red-200 rounded-lg p-3 pt-6 min-h-[80px]">
            <p className="text-sm text-red-900 whitespace-pre-wrap">
              {change.old || <span className="text-red-400 italic">empty</span>}
            </p>
          </div>
        </div>
        {/* New Value */}
        <div className="relative">
          <div className="absolute top-0 left-0 px-2 py-0.5 bg-green-100 text-green-700 text-xs font-medium rounded-br">
            New
          </div>
          <div className="bg-green-50 border border-green-200 rounded-lg p-3 pt-6 min-h-[80px]">
            <p className="text-sm text-green-900 whitespace-pre-wrap">
              {change.new || <span className="text-green-400 italic">empty</span>}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default VersionDiff;
