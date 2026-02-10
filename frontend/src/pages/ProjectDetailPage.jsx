import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { projectsApi, decisionsApi, recordsApi } from '../services/api';
import DecisionCard from '../components/Decisions/DecisionCard';
import DecisionForm from '../components/Decisions/DecisionForm';
import ConfirmationModal from '../components/Common/ConfirmationModal';
import ErrorModal from '../components/Common/ErrorModal';
import StatusChangeModal from '../components/DecisionRecords/StatusChangeModal';
import ReviewTab from '../components/ProjectActions/ReviewTab';
import PendingImplementationTab from '../components/ProjectActions/PendingImplementationTab';

function ProjectDetailPage() {
  const { projectId } = useParams();
  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingDecision, setEditingDecision] = useState(null);
  const [deleteConfirmModal, setDeleteConfirmModal] = useState({ isOpen: false, decisionId: null });
  const [errorModal, setErrorModal] = useState({ isOpen: false, message: '' });

  // Tabs state
  const [activeTab, setActiveTab] = useState('all');
  const [actionItems, setActionItems] = useState({ review: [], pending_implementation: [] });
  const [actionItemsLoading, setActionItemsLoading] = useState(false);

  // Status change modal
  const [statusChangeModal, setStatusChangeModal] = useState({
    isOpen: false, recordId: null, currentStatus: null, newStatus: null
  });

  useEffect(() => {
    loadProject();
  }, [projectId]);

  useEffect(() => {
    if (activeTab === 'review' || activeTab === 'pending') {
      loadActionItems();
    }
  }, [activeTab, projectId]);

  const loadProject = async () => {
    try {
      const response = await projectsApi.get(projectId);
      setProject(response.data);
    } catch (error) {
      console.error('Failed to load project:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadActionItems = async () => {
    setActionItemsLoading(true);
    try {
      const response = await projectsApi.getActionItems(projectId);
      setActionItems(response.data);
    } catch (error) {
      console.error('Failed to load action items:', error);
    } finally {
      setActionItemsLoading(false);
    }
  };

  const handleCreateDecision = async (data) => {
    try {
      await decisionsApi.create(projectId, data);
      setShowForm(false);
      loadProject();
      loadActionItems();
    } catch (error) {
      console.error('Failed to create decision:', error);
    }
  };

  const handleUpdateDecision = async (data) => {
    try {
      await decisionsApi.update(editingDecision.id, data);
      setEditingDecision(null);
      loadProject();
      loadActionItems();
    } catch (error) {
      console.error('Failed to update decision:', error);
    }
  };

  const handleDeleteDecision = (id) => {
    setDeleteConfirmModal({ isOpen: true, decisionId: id });
  };

  const handleDeleteConfirm = async () => {
    try {
      await decisionsApi.delete(deleteConfirmModal.decisionId);
      setDeleteConfirmModal({ isOpen: false, decisionId: null });
      loadProject();
      loadActionItems();
    } catch (error) {
      console.error('Failed to delete decision:', error);
      setErrorModal({ isOpen: true, message: error.response?.data?.error || 'Failed to delete decision' });
      setDeleteConfirmModal({ isOpen: false, decisionId: null });
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
      loadProject();
      loadActionItems();
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

  if (!project) {
    return <div className="text-center text-gray-500">Project not found</div>;
  }

  // Compute tab counts from project data for the badge
  const reviewCount = project.decisions?.reduce((sum, d) => {
    return sum + (d.status_counts?.proposed || 0);
  }, 0) || 0;

  const pendingCount = project.decisions?.reduce((sum, d) => {
    return sum + (d.status_counts?.accepted || 0);
  }, 0) || 0;

  const tabs = [
    {
      id: 'all',
      label: 'All Decisions',
      count: project.decisions?.length || 0,
      icon: (
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
            d="M4 6h16M4 10h16M4 14h16M4 18h16" />
        </svg>
      ),
    },
    {
      id: 'review',
      label: 'Review',
      count: reviewCount,
      icon: (
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
            d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
            d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
        </svg>
      ),
      accentColor: 'yellow',
    },
    {
      id: 'pending',
      label: 'Pending Implementation',
      count: pendingCount,
      icon: (
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
            d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
        </svg>
      ),
      accentColor: 'blue',
    },
  ];

  const getTabClasses = (tab, isActive) => {
    if (isActive) {
      return 'border-indigo-500 text-indigo-700 bg-white shadow-sm';
    }
    return 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 hover:bg-gray-50';
  };

  const getBadgeClasses = (tab, isActive) => {
    if (tab.id === 'review' && tab.count > 0) {
      return isActive
        ? 'bg-yellow-100 text-yellow-800'
        : 'bg-yellow-50 text-yellow-600';
    }
    if (tab.id === 'pending' && tab.count > 0) {
      return isActive
        ? 'bg-blue-100 text-blue-800'
        : 'bg-blue-50 text-blue-600';
    }
    return isActive
      ? 'bg-indigo-100 text-indigo-700'
      : 'bg-gray-100 text-gray-600';
  };

  return (
    <div>
      {/* Breadcrumb */}
      <nav className="mb-4 text-sm">
        <Link to="/" className="text-indigo-600 hover:text-indigo-800">Projects</Link>
        <span className="mx-2 text-gray-400">/</span>
        <span className="text-gray-600">{project.name}</span>
      </nav>

      {/* Project Header */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h1 className="text-3xl font-bold text-gray-900">{project.name}</h1>
        {project.description && (
          <p className="mt-2 text-gray-600">{project.description}</p>
        )}
      </div>

      {/* Tabs */}
      <div className="mb-6">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-1" aria-label="Project tabs">
            {tabs.map((tab) => {
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`
                    ${getTabClasses(tab, isActive)}
                    group inline-flex items-center px-4 py-3 border-b-2 font-medium text-sm rounded-t-lg transition-all
                  `}
                >
                  <span className={`mr-2 ${isActive ? 'text-indigo-600' : 'text-gray-400 group-hover:text-gray-500'}`}>
                    {tab.icon}
                  </span>
                  <span>{tab.label}</span>
                  {tab.count > 0 && (
                    <span className={`ml-2 inline-flex items-center justify-center px-2 py-0.5 rounded-full text-xs font-semibold ${getBadgeClasses(tab, isActive)}`}>
                      {tab.count}
                    </span>
                  )}
                </button>
              );
            })}
          </nav>
        </div>
      </div>

      {/* Tab Content: All Decisions */}
      {activeTab === 'all' && (
        <>
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold text-gray-900">Decisions</h2>
            <button
              onClick={() => setShowForm(true)}
              className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 flex items-center space-x-2"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              <span>New Decision</span>
            </button>
          </div>

          {project.decisions?.length === 0 ? (
            <div className="text-center py-12 bg-white rounded-lg border-2 border-dashed border-gray-300">
              <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <h3 className="mt-2 text-sm font-medium text-gray-900">No decisions yet</h3>
              <p className="mt-1 text-sm text-gray-500">Start by creating a new decision.</p>
            </div>
          ) : (
            <div className="space-y-4">
              {project.decisions?.map((decision) => (
                <DecisionCard
                  key={decision.id}
                  decision={decision}
                  onEdit={() => setEditingDecision(decision)}
                  onDelete={() => handleDeleteDecision(decision.id)}
                />
              ))}
            </div>
          )}
        </>
      )}

      {/* Tab Content: Review */}
      {activeTab === 'review' && (
        <div>
          <div className="mb-4">
            <h2 className="text-xl font-semibold text-gray-900">Decisions to Review</h2>
            <p className="text-sm text-gray-500 mt-1">
              Proposed decisions waiting for your review. Accept or reject each proposal.
            </p>
          </div>
          <ReviewTab
            reviewItems={actionItems.review}
            onStatusChange={handleStatusChangeRequest}
            loading={actionItemsLoading}
          />
        </div>
      )}

      {/* Tab Content: Pending Implementation */}
      {activeTab === 'pending' && (
        <div>
          <div className="mb-4">
            <h2 className="text-xl font-semibold text-gray-900">Pending Implementation</h2>
            <p className="text-sm text-gray-500 mt-1">
              Accepted decisions waiting to be implemented in code. These will clear once implemented.
            </p>
          </div>
          <PendingImplementationTab
            pendingItems={actionItems.pending_implementation}
            onStatusChange={handleStatusChangeRequest}
            loading={actionItemsLoading}
          />
        </div>
      )}

      {/* Form Modal */}
      {(showForm || editingDecision) && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h2 className="text-xl font-bold mb-4">
              {editingDecision ? 'Edit Decision' : 'New Decision'}
            </h2>
            <DecisionForm
              initialData={editingDecision}
              onSubmit={editingDecision ? handleUpdateDecision : handleCreateDecision}
              onCancel={() => {
                setShowForm(false);
                setEditingDecision(null);
              }}
            />
          </div>
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
        onClose={() => setDeleteConfirmModal({ isOpen: false, decisionId: null })}
        onConfirm={handleDeleteConfirm}
        title="Delete Decision"
        message="Are you sure you want to delete this decision? This will also delete all associated records. This action cannot be undone."
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

export default ProjectDetailPage;
