import { useState } from 'react';
import { Link } from 'react-router-dom';
import StatusBadge from './StatusBadge';
import RelationshipManager from './RelationshipManager';

const VALID_TRANSITIONS = {
  proposed: ['accepted', 'rejected'],
  accepted: ['implemented', 'rejected', 'deprecated'],
  implemented: ['deprecated'],
  implemented_inferred: ['deprecated'],
  rejected: [],
  deprecated: [],
};

function RecordCard({ record, allRecords, currentDecisionTitle, onEdit, onDelete, onStatusChange, onRefresh }) {
  const [expanded, setExpanded] = useState(false);
  const [showRelationships, setShowRelationships] = useState(false);

  const validTransitions = VALID_TRANSITIONS[record.status] || [];

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b bg-gray-50">
        <div className="flex justify-between items-start">
          <div className="flex items-center space-x-3">
            <StatusBadge status={record.status} />
            <span className="text-sm text-gray-500">v{record.version}</span>
          </div>
          <div className="flex items-center space-x-2">
            {/* Status Change Dropdown */}
            {validTransitions.length > 0 && (
              <select
                onChange={(e) => {
                  if (e.target.value) {
                    onStatusChange(e.target.value);
                    e.target.value = '';
                  }
                }}
                className="text-sm border border-gray-300 rounded px-2 py-1"
                defaultValue=""
              >
                <option value="" disabled>Change status...</option>
                {validTransitions.map((status) => (
                  <option key={status} value={status}>
                    {status.charAt(0).toUpperCase() + status.slice(1).replace('_', ' ')}
                  </option>
                ))}
              </select>
            )}
            <button
              onClick={() => setShowRelationships(!showRelationships)}
              className="text-gray-400 hover:text-indigo-600"
              title="Relationships"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
              </svg>
            </button>
            <button onClick={onEdit} className="text-gray-400 hover:text-indigo-600" title="Edit">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
            </button>
            <button onClick={onDelete} className="text-gray-400 hover:text-red-600" title="Delete">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
            <Link to={`/records/${record.id}`} className="text-gray-400 hover:text-indigo-600" title="View Details">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
              </svg>
            </Link>
          </div>
        </div>
      </div>

      {/* Decision Description */}
      <div className="p-4">
        <h3 className="font-medium text-gray-900 mb-2">Decision</h3>
        <p className="text-gray-700 whitespace-pre-wrap">{record.decision_description}</p>
      </div>

      {/* Expand/Collapse Button */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full px-4 py-2 text-sm text-indigo-600 hover:bg-indigo-50 flex items-center justify-center space-x-1"
      >
        <span>{expanded ? 'Show less' : 'Show more details'}</span>
        <svg
          className={`w-4 h-4 transform transition-transform ${expanded ? 'rotate-180' : ''}`}
          fill="none" stroke="currentColor" viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {/* Expanded Details */}
      {expanded && (
        <div className="px-4 pb-4 space-y-4 border-t">
          {record.decision_details && (
            <div className="pt-4">
              <h4 className="font-medium text-gray-700 text-sm" title="Detailed explanation of the decision.">Decision Details</h4>
              <p className="text-gray-600 text-sm mt-1 whitespace-pre-wrap">{record.decision_details}</p>
            </div>
          )}

          {record.context && (
            <div className="pt-4">
              <h4 className="font-medium text-gray-700 text-sm" title="Why this decision is being made now. The background situation, pressure, or trigger that necessitates it.">Context</h4>
              <p className="text-gray-600 text-sm mt-1 whitespace-pre-wrap">{record.context}</p>
            </div>
          )}

          {record.constraints && (
            <div>
              <h4 className="font-medium text-gray-700 text-sm" title="Hard requirements or limitations that must be satisfied. Explains why certain obvious options weren't viable.">Constraints</h4>
              <p className="text-gray-600 text-sm mt-1 whitespace-pre-wrap">{record.constraints}</p>
            </div>
          )}

          {record.rationale && (
            <div>
              <h4 className="font-medium text-gray-700 text-sm" title="Why this specific option was chosen over alternatives. The reasoning and justification.">Rationale</h4>
              <p className="text-gray-600 text-sm mt-1 whitespace-pre-wrap">{record.rationale}</p>
            </div>
          )}

          {record.assumptions && (
            <div className="bg-amber-50 p-3 rounded-lg border border-amber-200">
              <h4 className="font-medium text-amber-800 text-sm flex items-center space-x-1" title="Things that must remain true for this decision to stay valid. When assumptions break or expire, the decision should be re-evaluated.">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                    d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                <span>Assumptions (Critical for Validation)</span>
              </h4>
              <p className="text-amber-900 text-sm mt-1 whitespace-pre-wrap">{record.assumptions}</p>
            </div>
          )}

          {record.consequences && (
            <div>
              <h4 className="font-medium text-gray-700 text-sm" title="Downstream impact, both positive and negative. What it will cause, enable, or require going forward.">Consequences</h4>
              <p className="text-gray-600 text-sm mt-1 whitespace-pre-wrap">{record.consequences}</p>
            </div>
          )}

          {record.tradeoffs && (
            <div>
              <h4 className="font-medium text-gray-700 text-sm" title="What is explicitly being given up. Makes costs intentional so future teams know pain points are by design.">Tradeoffs</h4>
              <p className="text-gray-600 text-sm mt-1 whitespace-pre-wrap">{record.tradeoffs}</p>
            </div>
          )}

          {record.evidence && (
            <div>
              <h4 className="font-medium text-gray-700 text-sm" title="Links to resources (papers, blogs, benchmarks, experiments) that support and defend the decision.">Evidence</h4>
              <p className="text-gray-600 text-sm mt-1 whitespace-pre-wrap">{record.evidence}</p>
            </div>
          )}

          {record.options_considered && (
            <div>
              <h4 className="font-medium text-gray-700 text-sm" title="Alternatives that were evaluated and why they were rejected. Prevents re-proposing already-rejected ideas.">Options Considered</h4>
              <p className="text-gray-600 text-sm mt-1 whitespace-pre-wrap">{record.options_considered}</p>
            </div>
          )}

          {record.code_reference && (
            <div className="bg-slate-50 p-3 rounded-lg border border-slate-200">
              <h4 className="font-medium text-slate-700 text-sm" title="References to implemented code: file paths, line ranges, and code snippets.">Code Reference</h4>
              <pre className="text-slate-700 text-sm mt-1 whitespace-pre-wrap font-mono overflow-x-auto">{record.code_reference}</pre>
            </div>
          )}

          {/* VCS Info */}
          {record.metadata?.vcs && (
            <div className="bg-gray-50 p-3 rounded-lg border border-gray-200">
              <h4 className="font-medium text-gray-700 text-sm flex items-center space-x-1">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                    d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                </svg>
                <span>Version Control</span>
              </h4>
              <div className="text-sm mt-1 space-y-1">
                <div className="flex items-center space-x-2">
                  <span className="text-gray-500">Type:</span>
                  <span className="text-gray-700 capitalize">{record.metadata.vcs.type}</span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-gray-500">Revision:</span>
                  <span className="text-gray-700 font-mono text-xs">{record.metadata.vcs.revision?.substring(0, 12)}...</span>
                </div>
              </div>
            </div>
          )}

          {/* Relationships Summary */}
          {(record.outgoing_relationships?.length > 0 || record.incoming_relationships?.length > 0) && (
            <div className="border-t pt-4">
              <h4 className="font-medium text-gray-700 text-sm mb-2">Relationships</h4>
              <div className="space-y-1">
                {record.outgoing_relationships?.map((rel) => (
                  <div key={rel.id} className="text-sm text-gray-600">
                    <span className="font-medium">{rel.relationship_type}</span> → Record {rel.target_record_id.slice(0, 8)}...
                  </div>
                ))}
                {record.incoming_relationships?.map((rel) => (
                  <div key={rel.id} className="text-sm text-gray-600">
                    Record {rel.source_record_id.slice(0, 8)}... → <span className="font-medium">{rel.relationship_type}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="text-xs text-gray-400 pt-2 border-t">
            Created: {new Date(record.created_at).toLocaleString()} |
            Updated: {new Date(record.updated_at).toLocaleString()}
          </div>
        </div>
      )}

      {/* Relationship Manager Modal */}
      {showRelationships && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg p-6 w-full max-w-lg">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-bold">Manage Relationships</h3>
              <button
                onClick={() => setShowRelationships(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <RelationshipManager
              record={record}
              allRecords={allRecords}
              currentDecisionTitle={currentDecisionTitle}
              onUpdate={() => {
                onRefresh();
              }}
            />
          </div>
        </div>
      )}
    </div>
  );
}

export default RecordCard;
