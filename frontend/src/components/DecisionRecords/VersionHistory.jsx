import { useState, useEffect } from 'react';
import { recordsApi } from '../../services/api';

function VersionHistory({ recordId, currentVersion, onViewVersion, onRevert }) {
  const [versions, setVersions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedVersion, setSelectedVersion] = useState(null);
  const [viewingSnapshot, setViewingSnapshot] = useState(null);

  useEffect(() => {
    loadVersions();
  }, [recordId]);

  const loadVersions = async () => {
    try {
      const response = await recordsApi.getVersions(recordId);
      setVersions(response.data);
    } catch (error) {
      console.error('Failed to load versions:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleViewVersion = async (version) => {
    try {
      const response = await recordsApi.getAtVersion(recordId, version);
      setViewingSnapshot(response.data);
      setSelectedVersion(version);
    } catch (error) {
      console.error('Failed to load version:', error);
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
      <h3 className="text-lg font-semibold text-gray-900">Version History</h3>

      {versions.length === 0 ? (
        <p className="text-gray-500 text-sm">No version history available.</p>
      ) : (
        <div className="space-y-2">
          {versions.map((v) => (
            <div
              key={v.id}
              className={`p-3 rounded-lg border ${
                v.version === currentVersion
                  ? 'border-indigo-300 bg-indigo-50'
                  : 'border-gray-200 bg-white hover:bg-gray-50'
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <span className={`inline-flex items-center justify-center w-8 h-8 rounded-full text-sm font-medium ${
                    v.version === currentVersion
                      ? 'bg-indigo-600 text-white'
                      : 'bg-gray-200 text-gray-700'
                  }`}>
                    v{v.version}
                  </span>
                  <div>
                    <p className="text-sm text-gray-600">
                      {new Date(v.created_at).toLocaleString()}
                    </p>
                    {v.version === currentVersion && (
                      <span className="text-xs text-indigo-600 font-medium">Current Version</span>
                    )}
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => handleViewVersion(v.version)}
                    className="text-sm text-indigo-600 hover:text-indigo-800"
                  >
                    View
                  </button>
                  {v.version !== currentVersion && (
                    <button
                      onClick={() => onRevert(v.version)}
                      className="text-sm text-amber-600 hover:text-amber-800"
                    >
                      Revert
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Version Snapshot Modal */}
      {viewingSnapshot && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[80vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-bold">Version {selectedVersion} Snapshot</h3>
              <button
                onClick={() => {
                  setViewingSnapshot(null);
                  setSelectedVersion(null);
                }}
                className="text-gray-400 hover:text-gray-600"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div className="space-y-4">
              <SnapshotField label="Decision Description" value={viewingSnapshot.decision_description} />
              <SnapshotField label="Context" value={viewingSnapshot.context} />
              <SnapshotField label="Constraints" value={viewingSnapshot.constraints} />
              <SnapshotField label="Rationale" value={viewingSnapshot.rationale} />
              <SnapshotField label="Assumptions" value={viewingSnapshot.assumptions} highlight />
              <SnapshotField label="Consequences" value={viewingSnapshot.consequences} />
              <SnapshotField label="Tradeoffs" value={viewingSnapshot.tradeoffs} />
              <SnapshotField label="Evidence" value={viewingSnapshot.evidence} />
              <SnapshotField label="Options Considered" value={viewingSnapshot.options_considered} />
            </div>

            <div className="mt-6 flex justify-end space-x-3">
              {selectedVersion !== currentVersion && (
                <button
                  onClick={() => {
                    onRevert(selectedVersion);
                    setViewingSnapshot(null);
                    setSelectedVersion(null);
                  }}
                  className="px-4 py-2 bg-amber-600 text-white rounded-lg hover:bg-amber-700"
                >
                  Revert to This Version
                </button>
              )}
              <button
                onClick={() => {
                  setViewingSnapshot(null);
                  setSelectedVersion(null);
                }}
                className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function SnapshotField({ label, value, highlight = false }) {
  if (!value) return null;

  return (
    <div className={highlight ? 'bg-amber-50 p-3 rounded-lg border border-amber-200' : ''}>
      <h4 className={`text-sm font-medium ${highlight ? 'text-amber-800' : 'text-gray-700'} mb-1`}>
        {label}
      </h4>
      <p className={`text-sm ${highlight ? 'text-amber-900' : 'text-gray-600'} whitespace-pre-wrap`}>
        {value}
      </p>
    </div>
  );
}

export default VersionHistory;
