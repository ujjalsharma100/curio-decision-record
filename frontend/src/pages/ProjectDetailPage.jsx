import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { projectsApi, decisionsApi } from '../services/api';
import DecisionCard from '../components/Decisions/DecisionCard';
import DecisionForm from '../components/Decisions/DecisionForm';
import ConfirmationModal from '../components/Common/ConfirmationModal';
import ErrorModal from '../components/Common/ErrorModal';

function ProjectDetailPage() {
  const { projectId } = useParams();
  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingDecision, setEditingDecision] = useState(null);
  const [deleteConfirmModal, setDeleteConfirmModal] = useState({ isOpen: false, decisionId: null });
  const [errorModal, setErrorModal] = useState({ isOpen: false, message: '' });

  useEffect(() => {
    loadProject();
  }, [projectId]);

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

  const handleCreateDecision = async (data) => {
    try {
      await decisionsApi.create(projectId, data);
      setShowForm(false);
      loadProject();
    } catch (error) {
      console.error('Failed to create decision:', error);
    }
  };

  const handleUpdateDecision = async (data) => {
    try {
      await decisionsApi.update(editingDecision.id, data);
      setEditingDecision(null);
      loadProject();
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
    } catch (error) {
      console.error('Failed to delete decision:', error);
      setErrorModal({ isOpen: true, message: error.response?.data?.error || 'Failed to delete decision' });
      setDeleteConfirmModal({ isOpen: false, decisionId: null });
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

      {/* Decisions Section */}
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

      {/* Decisions List */}
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
