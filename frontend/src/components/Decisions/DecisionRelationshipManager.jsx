import { useState } from 'react';
import { Link } from 'react-router-dom';
import { decisionRelationshipsApi } from '../../services/api';
import ConfirmationModal from '../Common/ConfirmationModal';
import ErrorModal from '../Common/ErrorModal';

const RELATIONSHIP_TYPES = [
  { value: 'superseded_by', label: 'Superseded By' },
  { value: 'supersedes', label: 'Supersedes' },
  { value: 'related_to', label: 'Related To' },
  { value: 'depends_on', label: 'Depends On' },
  { value: 'merged_from', label: 'Merged From' },
  { value: 'derived_from', label: 'Derived From' },
  { value: 'conflicts_with', label: 'Conflicts With' },
];

function DecisionRelationshipManager({ decision, allDecisions, onUpdate }) {
  const [targetDecisionId, setTargetDecisionId] = useState('');
  const [relationshipType, setRelationshipType] = useState('related_to');
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [deleteConfirmModal, setDeleteConfirmModal] = useState({ isOpen: false, relationshipId: null });
  const [errorModal, setErrorModal] = useState({ isOpen: false, message: '' });

  const availableTargets = allDecisions?.filter((d) => d.id !== decision.id) || [];

  const handleAdd = async () => {
    if (!targetDecisionId) return;

    setLoading(true);
    try {
      await decisionRelationshipsApi.create(
        decision.id,
        targetDecisionId,
        relationshipType,
        description || null
      );
      setTargetDecisionId('');
      setDescription('');
      onUpdate();
    } catch (error) {
      console.error('Failed to add decision relationship:', error);
      setErrorModal({ isOpen: true, message: error.response?.data?.error || 'Failed to add relationship' });
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = (relationshipId) => {
    setDeleteConfirmModal({ isOpen: true, relationshipId });
  };

  const handleDeleteConfirm = async () => {
    try {
      await decisionRelationshipsApi.delete(deleteConfirmModal.relationshipId);
      setDeleteConfirmModal({ isOpen: false, relationshipId: null });
      onUpdate();
    } catch (error) {
      console.error('Failed to delete decision relationship:', error);
      setErrorModal({ isOpen: true, message: error.response?.data?.error || 'Failed to delete relationship' });
      setDeleteConfirmModal({ isOpen: false, relationshipId: null });
    }
  };

  const getDecisionById = (id) => allDecisions?.find((d) => d.id === id);

  return (
    <div className="space-y-4">
      {/* Add New Relationship */}
      <div className="space-y-3 p-4 bg-gray-50 rounded-lg">
        <h4 className="font-medium text-gray-700">Add Decision Relationship</h4>

        <div>
          <label className="block text-sm text-gray-600 mb-1">Relationship Type</label>
          <select
            value={relationshipType}
            onChange={(e) => setRelationshipType(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
          >
            {RELATIONSHIP_TYPES.map((t) => (
              <option key={t.value} value={t.value}>{t.label}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm text-gray-600 mb-1">Target Decision</label>
          <select
            value={targetDecisionId}
            onChange={(e) => setTargetDecisionId(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
          >
            <option value="">Select a decision...</option>
            {availableTargets.map((d) => (
              <option key={d.id} value={d.id}>
                {d.title}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm text-gray-600 mb-1">Description (optional)</label>
          <input
            type="text"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Additional context..."
            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
          />
        </div>

        <button
          onClick={handleAdd}
          disabled={!targetDecisionId || loading}
          className="w-full px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'Adding...' : 'Add Relationship'}
        </button>
      </div>

      {/* Existing Relationships */}
      <div>
        <h4 className="font-medium text-gray-700 mb-2">Outgoing</h4>
        {decision.outgoing_decision_relationships?.length === 0 ? (
          <p className="text-sm text-gray-500 italic">No outgoing decision relationships</p>
        ) : (
          <ul className="space-y-2">
            {decision.outgoing_decision_relationships?.map((rel) => {
              const target = getDecisionById(rel.target_decision_id);
              return (
                <li key={rel.id} className="flex items-center justify-between bg-white p-2 rounded border">
                  <div className="text-sm">
                    <span className="font-medium text-indigo-600">{rel.relationship_type}</span>
                    <span className="text-gray-500"> → </span>
                    <span className="text-gray-700">
                      {target ? (
                        <Link to={`/decisions/${target.id}`} className="text-indigo-600 hover:underline">
                          {target.title}
                        </Link>
                      ) : (
                        rel.target_decision_id.slice(0, 8) + '...'
                      )}
                    </span>
                    {rel.description && (
                      <span className="text-gray-400 text-xs ml-2">({rel.description})</span>
                    )}
                  </div>
                  <button
                    onClick={() => handleDelete(rel.id)}
                    className="text-red-500 hover:text-red-700"
                    title="Delete relationship"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </li>
              );
            })}
          </ul>
        )}
      </div>

      <div>
        <h4 className="font-medium text-gray-700 mb-2">Incoming</h4>
        {decision.incoming_decision_relationships?.length === 0 ? (
          <p className="text-sm text-gray-500 italic">No incoming decision relationships</p>
        ) : (
          <ul className="space-y-2">
            {decision.incoming_decision_relationships?.map((rel) => {
              const source = getDecisionById(rel.source_decision_id);
              return (
                <li key={rel.id} className="flex items-center justify-between bg-white p-2 rounded border">
                  <div className="text-sm">
                    <span className="text-gray-700">
                      {source ? (
                        <Link to={`/decisions/${source.id}`} className="text-indigo-600 hover:underline">
                          {source.title}
                        </Link>
                      ) : (
                        rel.source_decision_id.slice(0, 8) + '...'
                      )}
                    </span>
                    <span className="text-gray-500"> → </span>
                    <span className="font-medium text-indigo-600">{rel.relationship_type}</span>
                    {rel.description && (
                      <span className="text-gray-400 text-xs ml-2">({rel.description})</span>
                    )}
                  </div>
                </li>
              );
            })}
          </ul>
        )}
      </div>

      <ConfirmationModal
        isOpen={deleteConfirmModal.isOpen}
        onClose={() => setDeleteConfirmModal({ isOpen: false, relationshipId: null })}
        onConfirm={handleDeleteConfirm}
        title="Remove Decision Relationship"
        message="Are you sure you want to remove this decision relationship?"
        confirmText="Remove"
        cancelText="Cancel"
        variant="warning"
      />

      <ErrorModal
        isOpen={errorModal.isOpen}
        onClose={() => setErrorModal({ isOpen: false, message: '' })}
        message={errorModal.message}
      />
    </div>
  );
}

export default DecisionRelationshipManager;
