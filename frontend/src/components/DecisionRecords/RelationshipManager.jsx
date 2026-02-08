import { useState, useMemo } from 'react';
import { relationshipsApi } from '../../services/api';
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

function RelationshipManager({ record, allRecords, currentDecisionTitle, onUpdate }) {
  const [targetRecordId, setTargetRecordId] = useState('');
  const [relationshipType, setRelationshipType] = useState('related_to');
  const [targetDecisionTitle, setTargetDecisionTitle] = useState(currentDecisionTitle || '');
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [deleteConfirmModal, setDeleteConfirmModal] = useState({ isOpen: false, relationshipId: null });
  const [errorModal, setErrorModal] = useState({ isOpen: false, message: '' });

  // Unique decisions from all records (sorted; current decision first)
  const decisionTitles = useMemo(() => {
    const titles = [...new Set(allRecords?.map((r) => r.decision_title).filter(Boolean) || [])];
    if (currentDecisionTitle && !titles.includes(currentDecisionTitle)) {
      titles.unshift(currentDecisionTitle);
    }
    titles.sort((a, b) => {
      if (a === currentDecisionTitle) return -1;
      if (b === currentDecisionTitle) return 1;
      return a.localeCompare(b);
    });
    return titles;
  }, [allRecords, currentDecisionTitle]);

  // Ensure target decision is set when we have decisions but it's empty
  const effectiveTargetDecision = targetDecisionTitle || decisionTitles[0] || '';

  // Target records filtered by selected decision, excluding current record
  const availableTargets = useMemo(() => {
    return (allRecords?.filter(
      (r) => r.id !== record.id && r.decision_title === effectiveTargetDecision
    ) || []);
  }, [allRecords, record.id, effectiveTargetDecision]);

  const handleTargetDecisionChange = (newDecisionTitle) => {
    setTargetDecisionTitle(newDecisionTitle);
    setTargetRecordId('');
  };

  const handleAdd = async () => {
    if (!targetRecordId) return;

    setLoading(true);
    try {
      await relationshipsApi.create(
        record.id,
        targetRecordId,
        relationshipType,
        description || null
      );
      setTargetRecordId('');
      setDescription('');
      onUpdate();
    } catch (error) {
      console.error('Failed to add relationship:', error);
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
      await relationshipsApi.delete(deleteConfirmModal.relationshipId);
      setDeleteConfirmModal({ isOpen: false, relationshipId: null });
      onUpdate();
    } catch (error) {
      console.error('Failed to delete relationship:', error);
      setErrorModal({ isOpen: true, message: error.response?.data?.error || 'Failed to delete relationship' });
      setDeleteConfirmModal({ isOpen: false, relationshipId: null });
    }
  };

  return (
    <div className="space-y-4">
      {/* Add New Relationship */}
      <div className="space-y-3 p-4 bg-gray-50 rounded-lg">
        <h4 className="font-medium text-gray-700">Add Relationship</h4>

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
            value={effectiveTargetDecision}
            onChange={(e) => handleTargetDecisionChange(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
          >
            {decisionTitles.map((title) => (
              <option key={title} value={title}>
                {title}{title === currentDecisionTitle ? ' (current)' : ''}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm text-gray-600 mb-1">Target Record</label>
          <select
            value={targetRecordId}
            onChange={(e) => setTargetRecordId(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
          >
            <option value="">Select a record...</option>
            {availableTargets.map((r) => (
              <option key={r.id} value={r.id}>
                [{r.status}] {r.decision_description?.slice(0, 60) || ''}{r.decision_description?.length > 60 ? '...' : ''}
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
          disabled={!targetRecordId || loading}
          className="w-full px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'Adding...' : 'Add Relationship'}
        </button>
      </div>

      {/* Existing Relationships */}
      <div>
        <h4 className="font-medium text-gray-700 mb-2">Outgoing Relationships</h4>
        {record.outgoing_relationships?.length === 0 ? (
          <p className="text-sm text-gray-500 italic">No outgoing relationships</p>
        ) : (
          <ul className="space-y-2">
            {record.outgoing_relationships?.map((rel) => {
              const target = allRecords?.find((r) => r.id === rel.target_record_id);
              return (
                <li key={rel.id} className="flex items-center justify-between bg-white p-2 rounded border">
                  <div className="text-sm">
                    <span className="font-medium text-indigo-600">{rel.relationship_type}</span>
                    <span className="text-gray-500"> → </span>
                    <span className="text-gray-700">
                      {target ? (
                        <>
                          {target.decision_title && <span className="text-gray-500">[{target.decision_title}] </span>}
                          {target.decision_description?.slice(0, 30) || ''}{target.decision_description?.length > 30 ? '...' : ''}
                        </>
                      ) : (
                        rel.target_record_id.slice(0, 8) + '...'
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
        <h4 className="font-medium text-gray-700 mb-2">Incoming Relationships</h4>
        {record.incoming_relationships?.length === 0 ? (
          <p className="text-sm text-gray-500 italic">No incoming relationships</p>
        ) : (
          <ul className="space-y-2">
            {record.incoming_relationships?.map((rel) => {
              const source = allRecords?.find((r) => r.id === rel.source_record_id);
              return (
                <li key={rel.id} className="bg-white p-2 rounded border text-sm">
                  <span className="text-gray-700">
                    {source ? (
                      <>
                        {source.decision_title && <span className="text-gray-500">[{source.decision_title}] </span>}
                        {source.decision_description?.slice(0, 30) || ''}{source.decision_description?.length > 30 ? '...' : ''}
                      </>
                    ) : (
                      rel.source_record_id.slice(0, 8) + '...'
                    )}
                  </span>
                  <span className="text-gray-500"> → </span>
                  <span className="font-medium text-indigo-600">{rel.relationship_type}</span>
                  {rel.description && (
                    <span className="text-gray-400 text-xs ml-2">({rel.description})</span>
                  )}
                </li>
              );
            })}
          </ul>
        )}
      </div>

      {/* Delete Confirmation Modal */}
      <ConfirmationModal
        isOpen={deleteConfirmModal.isOpen}
        onClose={() => setDeleteConfirmModal({ isOpen: false, relationshipId: null })}
        onConfirm={handleDeleteConfirm}
        title="Remove Relationship"
        message="Are you sure you want to remove this relationship?"
        confirmText="Remove"
        cancelText="Cancel"
        variant="warning"
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

export default RelationshipManager;
