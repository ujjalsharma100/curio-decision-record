import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { decisionsApi, recordsApi, projectsApi } from '../services/api';
import StatusBadge from '../components/DecisionRecords/StatusBadge';
import RecordCard from '../components/DecisionRecords/RecordCard';
import RecordForm from '../components/DecisionRecords/RecordForm';
import StatusChangeModal from '../components/DecisionRecords/StatusChangeModal';
import ConfirmationModal from '../components/Common/ConfirmationModal';
import ErrorModal from '../components/Common/ErrorModal';
import DecisionTimeline from '../components/DecisionRecords/DecisionTimeline';
import ImplementationHistory from '../components/DecisionRecords/ImplementationHistory';
import DecisionRelationshipManager from '../components/Decisions/DecisionRelationshipManager';

function DecisionDetailPage() {
  const { decisionId } = useParams();
  const [decision, setDecision] = useState(null);
  const [project, setProject] = useState(null);
  const [allProjectRecords, setAllProjectRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingRecord, setEditingRecord] = useState(null);
  const [activeTab, setActiveTab] = useState('implemented');
  const [activeView, setActiveView] = useState('records'); // 'current-implementation', 'records', 'timeline', 'implementation-history', 'decision-relationships'
  const [statusChangeModal, setStatusChangeModal] = useState({ isOpen: false, recordId: null, currentStatus: null, newStatus: null });
  const [deleteConfirmModal, setDeleteConfirmModal] = useState({ isOpen: false, recordId: null });
  const [errorModal, setErrorModal] = useState({ isOpen: false, message: '' });

  useEffect(() => {
    loadDecision();
  }, [decisionId]);

  const loadDecision = async () => {
    try {
      const response = await decisionsApi.get(decisionId);
      setDecision(response.data);
      // Load project for breadcrumb
      const projectResponse = await projectsApi.get(response.data.project_id);
      setProject(projectResponse.data);
      // Load all project records for cross-decision relationship targets
      const recordsResponse = await projectsApi.getRecords(response.data.project_id);
      setAllProjectRecords(recordsResponse.data || []);
      
      // Set default active view and tab
      if (response.data.records && response.data.records.length > 0) {
        const statusOrder = ['implemented', 'implemented_inferred', 'accepted', 'proposed', 'deprecated', 'rejected'];
        const statusCounts = response.data.records.reduce((acc, r) => {
          acc[r.status] = (acc[r.status] || 0) + 1;
          return acc;
        }, {});
        
        // Check for implemented first - set to current-implementation view
        const implementedCount = (statusCounts.implemented || 0) + (statusCounts.implemented_inferred || 0);
        if (implementedCount > 0) {
          setActiveView('current-implementation');
          setActiveTab('implemented');
        } else {
          setActiveView('records');
          // Find first status with records
          for (const status of statusOrder.slice(2)) {
            if (statusCounts[status] > 0) {
              setActiveTab(status);
              break;
            }
          }
        }
      } else {
        setActiveView('records');
      }
    } catch (error) {
      console.error('Failed to load decision:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateRecord = async (data) => {
    try {
      await recordsApi.create(decisionId, data);
      setShowForm(false);
      loadDecision();
    } catch (error) {
      console.error('Failed to create record:', error);
    }
  };

  const handleUpdateRecord = async (data) => {
    try {
      await recordsApi.update(editingRecord.id, data);
      setEditingRecord(null);
      loadDecision();
    } catch (error) {
      console.error('Failed to update record:', error);
    }
  };

  const handleDeleteRecord = (id) => {
    setDeleteConfirmModal({ isOpen: true, recordId: id });
  };

  const handleDeleteConfirm = async () => {
    try {
      await recordsApi.delete(deleteConfirmModal.recordId);
      setDeleteConfirmModal({ isOpen: false, recordId: null });
      loadDecision();
    } catch (error) {
      console.error('Failed to delete record:', error);
      setErrorModal({ isOpen: true, message: error.response?.data?.error || 'Failed to delete record' });
      setDeleteConfirmModal({ isOpen: false, recordId: null });
    }
  };

  const handleStatusChangeRequest = (recordId, currentStatus, newStatus) => {
    setStatusChangeModal({
      isOpen: true,
      recordId,
      currentStatus,
      newStatus
    });
  };

  const handleStatusChangeConfirm = async (newStatus, reason) => {
    try {
      await recordsApi.changeStatus(statusChangeModal.recordId, newStatus, reason);
      setStatusChangeModal({ isOpen: false, recordId: null, currentStatus: null, newStatus: null });
      loadDecision();
    } catch (error) {
      console.error('Failed to change status:', error);
      setErrorModal({ isOpen: true, message: error.response?.data?.error || 'Failed to change status' });
      setStatusChangeModal({ isOpen: false, recordId: null, currentStatus: null, newStatus: null });
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (!decision) {
    return <div className="text-center text-gray-500">Decision not found</div>;
  }

  // Define status order: Implemented (primary), Accepted, Proposed, Deprecated, Rejected
  const statusOrder = ['implemented', 'implemented_inferred', 'accepted', 'proposed', 'deprecated', 'rejected'];
  
  // Group records by status
  const recordsByStatus = decision.records?.reduce((acc, r) => {
    const status = r.status;
    if (!acc[status]) {
      acc[status] = [];
    }
    acc[status].push(r);
    return acc;
  }, {}) || {};

  // Calculate status counts
  const statusCounts = decision.records?.reduce((acc, r) => {
    acc[r.status] = (acc[r.status] || 0) + 1;
    return acc;
  }, {}) || {};

  // Get records for active tab
  // For "implemented" tab, show both "implemented" and "implemented_inferred"
  const getActiveTabRecords = () => {
    if (activeTab === 'implemented') {
      return [
        ...(recordsByStatus.implemented || []),
        ...(recordsByStatus.implemented_inferred || [])
      ];
    }
    return recordsByStatus[activeTab] || [];
  };

  const activeTabRecords = getActiveTabRecords();

  // Get count for implemented tab (combines both implemented statuses)
  const getTabCount = (status) => {
    if (status === 'implemented') {
      return (statusCounts.implemented || 0) + (statusCounts.implemented_inferred || 0);
    }
    return statusCounts[status] || 0;
  };

  return (
    <div>
      {/* Breadcrumb */}
      <nav className="mb-4 text-sm">
        <Link to="/" className="text-indigo-600 hover:text-indigo-800">Projects</Link>
        <span className="mx-2 text-gray-400">/</span>
        {project && (
          <>
            <Link to={`/projects/${project.id}`} className="text-indigo-600 hover:text-indigo-800">
              {project.name}
            </Link>
            <span className="mx-2 text-gray-400">/</span>
          </>
        )}
        <span className="text-gray-600">{decision.title}</span>
      </nav>

      {/* Decision Header */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h1 className="text-3xl font-bold text-gray-900">{decision.title}</h1>
        <div className="mt-4 flex flex-wrap gap-2">
          {/* Show implemented badge (no count) */}
          {(statusCounts.implemented || statusCounts.implemented_inferred) && (
              <StatusBadge status="implemented" />
          )}
          {/* Show accepted badge (no count) */}
          {statusCounts.accepted && (
            <StatusBadge status="accepted" />
          )}
          {/* Show other statuses in order (with counts) */}
          {statusOrder.slice(3).map((status) => {
            if (statusCounts[status]) {
              return (
                <span key={status} className="inline-flex items-center space-x-1">
                  <StatusBadge status={status} />
                  <span className="text-sm text-gray-500">({statusCounts[status]})</span>
                </span>
              );
            }
            return null;
          })}
        </div>
      </div>

      {/* View Toggle */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <div className="flex space-x-1 bg-gray-100 rounded-lg p-1">
          {(() => {
            const hasCurrentImplementation = decision.records?.some(
              r => r.status === 'implemented' || r.status === 'implemented_inferred'
            );
            
            return (
              <>
                {hasCurrentImplementation && (
                  <button
                    onClick={() => setActiveView('current-implementation')}
                    className={`flex-1 flex items-center justify-center space-x-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                      activeView === 'current-implementation'
                        ? 'bg-white text-indigo-700 shadow-sm'
                        : 'text-gray-600 hover:text-gray-900'
                    }`}
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                        d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span>Current Implementation</span>
                  </button>
                )}
                <button
                  onClick={() => setActiveView('records')}
                  className={`flex-1 flex items-center justify-center space-x-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                    activeView === 'records'
                      ? 'bg-white text-indigo-700 shadow-sm'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                      d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <span>Records</span>
                </button>
                <button
                  onClick={() => setActiveView('decision-relationships')}
                  className={`flex-1 flex items-center justify-center space-x-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                    activeView === 'decision-relationships'
                      ? 'bg-white text-indigo-700 shadow-sm'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                      d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                  </svg>
                  <span>Decision Links</span>
                </button>
                <button
                  onClick={() => setActiveView('implementation-history')}
                  className={`flex-1 flex items-center justify-center space-x-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                    activeView === 'implementation-history'
                      ? 'bg-white text-indigo-700 shadow-sm'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                      d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span>Implementation History</span>
                </button>
                <button
                  onClick={() => setActiveView('timeline')}
                  className={`flex-1 flex items-center justify-center space-x-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                    activeView === 'timeline'
                      ? 'bg-white text-indigo-700 shadow-sm'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                      d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span>Activity Timeline</span>
                </button>
              </>
            );
          })()}
        </div>
      </div>

      {/* Records Section - Only show when Records view is active */}
      {activeView === 'records' && (
        <>
      <div className="mb-4">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold text-gray-900">Decision Records</h2>
          <button
            onClick={() => setShowForm(true)}
            className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 flex items-center space-x-2"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            <span>New Record</span>
          </button>
        </div>

        {/* Status Tabs */}
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8" aria-label="Tabs">
            {statusOrder.map((status) => {
              // Skip implemented_inferred as it's shown in implemented tab
              if (status === 'implemented_inferred') return null;
              
              const count = getTabCount(status);
              const isActive = activeTab === status;
                  // Don't show count for implemented or accepted (always 1)
                  const showCount = status !== 'implemented' && status !== 'accepted';
              
              return (
                <button
                  key={status}
                  onClick={() => setActiveTab(status)}
                  className={`
                    ${isActive
                      ? 'border-indigo-500 text-indigo-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }
                    whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2
                  `}
                >
                  <StatusBadge status={status} size="sm" />
                      {showCount && <span>({count})</span>}
                </button>
              );
            })}
          </nav>
        </div>
      </div>

      {/* Form Modal */}
      {(showForm || editingRecord) && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg p-6 w-full max-w-3xl max-h-[90vh] overflow-y-auto">
            <h2 className="text-xl font-bold mb-4">
              {editingRecord ? 'Edit Decision Record' : 'New Decision Record'}
            </h2>
            <RecordForm
              initialData={editingRecord}
              onSubmit={editingRecord ? handleUpdateRecord : handleCreateRecord}
              onCancel={() => {
                setShowForm(false);
                setEditingRecord(null);
              }}
            />
          </div>
        </div>
      )}

      {/* Records List */}
      {activeTabRecords.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg border-2 border-dashed border-gray-300">
          <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <h3 className="mt-2 text-sm font-medium text-gray-900">No records found</h3>
          <p className="mt-1 text-sm text-gray-500">
            {activeTab === 'implemented' 
              ? 'No implemented records yet.' 
              : `No records with ${activeTab} status.`}
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {activeTabRecords.map((record) => (
            <RecordCard
              key={record.id}
              record={record}
              allRecords={allProjectRecords}
              currentDecisionTitle={decision.title}
              onEdit={() => setEditingRecord(record)}
              onDelete={() => handleDeleteRecord(record.id)}
              onStatusChange={(newStatus) => handleStatusChangeRequest(record.id, record.status, newStatus)}
              onRefresh={loadDecision}
            />
          ))}
            </div>
          )}
        </>
      )}

      {/* Current Implementation View */}
      {activeView === 'current-implementation' && (() => {
        const currentImplemented = decision.records?.find(
          r => r.status === 'implemented' || r.status === 'implemented_inferred'
        );
        
        if (!currentImplemented) {
          return (
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="text-center py-12">
                <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <h3 className="mt-2 text-sm font-medium text-gray-900">No Current Implementation</h3>
                <p className="mt-1 text-sm text-gray-500">
                  No decision record is currently implemented for this decision.
                </p>
              </div>
            </div>
          );
        }
        
        return (
          <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl p-6 border-2 border-green-300 shadow-lg">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-3">
                <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-green-600 text-white shadow-md">
                  <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  CURRENT IMPLEMENTATION
                </span>
                <StatusBadge status={currentImplemented.status} />
                <span className="text-sm text-gray-600">v{currentImplemented.version}</span>
              </div>
              <Link 
                to={`/records/${currentImplemented.id}`}
                className="text-indigo-600 hover:text-indigo-800 text-sm flex items-center space-x-1 font-medium"
              >
                <span>View Full Details</span>
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
              </Link>
            </div>

            {/* Decision Description */}
            <div className="mb-4">
              <h2 className="text-lg font-semibold text-gray-900 mb-2">Decision</h2>
              <p className="text-gray-700 whitespace-pre-wrap">{currentImplemented.decision_description}</p>
            </div>

            {/* Context */}
            {currentImplemented.context && (
              <div className="mb-4">
                <h3 className="text-md font-semibold text-gray-800 mb-2">Context</h3>
                <p className="text-gray-700 whitespace-pre-wrap">{currentImplemented.context}</p>
              </div>
            )}

            {/* Constraints */}
            {currentImplemented.constraints && (
              <div className="mb-4">
                <h3 className="text-md font-semibold text-gray-800 mb-2">Constraints</h3>
                <p className="text-gray-700 whitespace-pre-wrap">{currentImplemented.constraints}</p>
              </div>
            )}

            {/* Assumptions - Highlighted */}
            {currentImplemented.assumptions && (
              <div className="bg-amber-50 rounded-lg p-4 mb-4 border border-amber-200">
                <h3 className="text-md font-semibold text-amber-800 mb-2 flex items-center space-x-2">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                      d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                  <span>Assumptions</span>
                </h3>
                <p className="text-amber-900 whitespace-pre-wrap">{currentImplemented.assumptions}</p>
                <p className="text-sm text-amber-700 mt-2 italic">
                  When these assumptions are invalidated, this decision should be revisited.
                </p>
              </div>
            )}

            {/* Rationale */}
            {currentImplemented.rationale && (
              <div className="mb-4">
                <h3 className="text-md font-semibold text-gray-800 mb-2">Rationale</h3>
                <p className="text-gray-700 whitespace-pre-wrap">{currentImplemented.rationale}</p>
              </div>
            )}

            {/* Consequences */}
            {currentImplemented.consequences && (
              <div className="mb-4">
                <h3 className="text-md font-semibold text-gray-800 mb-2">Consequences</h3>
                <p className="text-gray-700 whitespace-pre-wrap">{currentImplemented.consequences}</p>
              </div>
            )}

            {/* Tradeoffs */}
            {currentImplemented.tradeoffs && (
              <div className="mb-4">
                <h3 className="text-md font-semibold text-gray-800 mb-2">Tradeoffs</h3>
                <p className="text-gray-700 whitespace-pre-wrap">{currentImplemented.tradeoffs}</p>
              </div>
            )}

            {/* Evidence */}
            {currentImplemented.evidence && (
              <div className="mb-4">
                <h3 className="text-md font-semibold text-gray-800 mb-2">Evidence</h3>
                <p className="text-gray-700 whitespace-pre-wrap">{currentImplemented.evidence}</p>
              </div>
            )}

            {/* Options Considered */}
            {currentImplemented.options_considered && (
              <div className="mb-4">
                <h3 className="text-md font-semibold text-gray-800 mb-2">Options Considered</h3>
                <p className="text-gray-700 whitespace-pre-wrap">{currentImplemented.options_considered}</p>
              </div>
            )}

            {/* Metadata */}
            <div className="mt-4 pt-4 border-t border-green-200 flex items-center justify-between text-sm text-gray-600">
              <div className="flex items-center space-x-4">
                <span>Created: {new Date(currentImplemented.created_at).toLocaleString()}</span>
                <span>Updated: {new Date(currentImplemented.updated_at).toLocaleString()}</span>
              </div>
            </div>
          </div>
        );
      })()}

      {/* Decision Relationships View */}
      {activeView === 'decision-relationships' && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Decision-Level Relationships</h2>
          <p className="text-sm text-gray-500 mb-4">
            Link this decision to others in the project (e.g., supersedes, depends_on). These capture conceptual relationships between decisions.
          </p>
          <DecisionRelationshipManager
            decision={decision}
            allDecisions={project?.decisions || []}
            onUpdate={loadDecision}
          />
        </div>
      )}

      {/* Implementation History View */}
      {activeView === 'implementation-history' && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <ImplementationHistory decisionId={decisionId} />
        </div>
      )}

      {/* Timeline View */}
      {activeView === 'timeline' && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <DecisionTimeline decisionId={decisionId} />
        </div>
      )}

      {/* Status Change Modal */}
      <StatusChangeModal
        isOpen={statusChangeModal.isOpen}
        onClose={() => setStatusChangeModal({ isOpen: false, recordId: null, currentStatus: null, newStatus: null })}
        currentStatus={statusChangeModal.currentStatus}
        newStatus={statusChangeModal.newStatus}
        onConfirm={handleStatusChangeConfirm}
      />

      {/* Delete Confirmation Modal */}
      <ConfirmationModal
        isOpen={deleteConfirmModal.isOpen}
        onClose={() => setDeleteConfirmModal({ isOpen: false, recordId: null })}
        onConfirm={handleDeleteConfirm}
        title="Delete Record"
        message="Are you sure you want to delete this record? This action cannot be undone."
        confirmText="Delete"
        cancelText="Cancel"
        variant="danger"
      />

      {/* Error Modal */}
      <ErrorModal
        isOpen={errorModal.isOpen}
        onClose={() => setErrorModal({ isOpen: false, message: '' })}
        message={errorModal.message}
      />
    </div>
  );
}

export default DecisionDetailPage;
