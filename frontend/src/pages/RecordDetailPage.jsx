import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { recordsApi, decisionsApi, projectsApi } from '../services/api';
import StatusBadge from '../components/DecisionRecords/StatusBadge';
import VersionHistory from '../components/DecisionRecords/VersionHistory';
import Changelog from '../components/DecisionRecords/Changelog';
import VersionDiff from '../components/DecisionRecords/VersionDiff';
import RevertModal from '../components/DecisionRecords/RevertModal';

function RecordDetailPage() {
  const { recordId } = useParams();
  const [record, setRecord] = useState(null);
  const [decision, setDecision] = useState(null);
  const [project, setProject] = useState(null);
  const [history, setHistory] = useState([]);
  const [versions, setVersions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('details');
  const [revertModal, setRevertModal] = useState({ isOpen: false, targetVersion: null });

  useEffect(() => {
    loadRecord();
  }, [recordId]);

  const loadRecord = async () => {
    try {
      const recordResponse = await recordsApi.get(recordId);
      setRecord(recordResponse.data);

      const historyResponse = await recordsApi.getHistory(recordId);
      setHistory(historyResponse.data);

      const versionsResponse = await recordsApi.getVersions(recordId);
      setVersions(versionsResponse.data);

      const decisionResponse = await decisionsApi.get(recordResponse.data.decision_id);
      setDecision(decisionResponse.data);

      const projectResponse = await projectsApi.get(decisionResponse.data.project_id);
      setProject(projectResponse.data);
    } catch (error) {
      console.error('Failed to load record:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRevert = async (version, reason) => {
    try {
      await recordsApi.revertToVersion(recordId, version, reason);
      loadRecord();
    } catch (error) {
      console.error('Failed to revert:', error);
      throw error;
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (!record) {
    return <div className="text-center text-gray-500">Record not found</div>;
  }

  const tabs = [
    { id: 'details', label: 'Details' },
    { id: 'versions', label: 'Versions', count: versions.length },
    { id: 'changelog', label: 'Changelog' },
    { id: 'compare', label: 'Compare' },
  ];

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
        {decision && (
          <>
            <Link to={`/decisions/${decision.id}`} className="text-indigo-600 hover:text-indigo-800">
              {decision.title}
            </Link>
            <span className="mx-2 text-gray-400">/</span>
          </>
        )}
        <span className="text-gray-600">Record v{record.version}</span>
      </nav>

      {/* Record Header */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center space-x-4 mb-2">
              <StatusBadge status={record.status} />
              <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-gray-100 text-gray-800">
                Version {record.version}
              </span>
            </div>
            <h1 className="text-2xl font-bold text-gray-900">{decision?.title}</h1>
          </div>
          <Link
            to={`/decisions/${decision?.id}`}
            className="text-indigo-600 hover:text-indigo-800 text-sm flex items-center space-x-1"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            <span>Back to Decision</span>
          </Link>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`
                ${activeTab === tab.id
                  ? 'border-indigo-500 text-indigo-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }
                whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2
              `}
            >
              <span>{tab.label}</span>
              {tab.count !== undefined && (
                <span className={`inline-flex items-center justify-center px-2 py-0.5 rounded-full text-xs ${
                  activeTab === tab.id ? 'bg-indigo-100 text-indigo-600' : 'bg-gray-100 text-gray-600'
                }`}>
                  {tab.count}
                </span>
              )}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === 'details' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Decision Description */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-3">Decision</h2>
              <p className="text-gray-700 whitespace-pre-wrap">{record.decision_description}</p>
            </div>

            {/* Decision Details */}
            {record.decision_details && (
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-3" title="Detailed explanation of the decision.">Decision Details</h2>
                <p className="text-gray-700 whitespace-pre-wrap">{record.decision_details}</p>
              </div>
            )}

            {/* Context */}
            {record.context && (
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-3" title="Why this decision is being made now. The background situation, pressure, or trigger that necessitates it.">Context</h2>
                <p className="text-gray-700 whitespace-pre-wrap">{record.context}</p>
              </div>
            )}

            {/* Constraints */}
            {record.constraints && (
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-3" title="Hard requirements or limitations that must be satisfied. Explains why certain obvious options weren't viable.">Constraints</h2>
                <p className="text-gray-700 whitespace-pre-wrap">{record.constraints}</p>
              </div>
            )}

            {/* Assumptions - Highlighted */}
            {record.assumptions && (
              <div className="bg-amber-50 rounded-lg shadow-md p-6 border border-amber-200">
                <h2 className="text-lg font-semibold text-amber-800 mb-3 flex items-center space-x-2" title="Things that must remain true for this decision to stay valid. When assumptions break or expire, the decision should be re-evaluated.">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                      d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                  <span>Assumptions</span>
                </h2>
                <p className="text-amber-900 whitespace-pre-wrap">{record.assumptions}</p>
                <p className="text-sm text-amber-700 mt-4 italic">
                  When these assumptions are invalidated, this decision should be revisited.
                </p>
              </div>
            )}

            {/* Rationale */}
            {record.rationale && (
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-3" title="Why this specific option was chosen over alternatives. The reasoning and justification.">Rationale</h2>
                <p className="text-gray-700 whitespace-pre-wrap">{record.rationale}</p>
              </div>
            )}

            {/* Consequences */}
            {record.consequences && (
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-3" title="Downstream impact, both positive and negative. What it will cause, enable, or require going forward.">Consequences</h2>
                <p className="text-gray-700 whitespace-pre-wrap">{record.consequences}</p>
              </div>
            )}

            {/* Tradeoffs */}
            {record.tradeoffs && (
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-3" title="What is explicitly being given up. Makes costs intentional so future teams know pain points are by design.">Tradeoffs</h2>
                <p className="text-gray-700 whitespace-pre-wrap">{record.tradeoffs}</p>
              </div>
            )}

            {/* Evidence */}
            {record.evidence && (
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-3" title="Links to resources (papers, blogs, benchmarks, experiments) that support and defend the decision.">Evidence</h2>
                <p className="text-gray-700 whitespace-pre-wrap">{record.evidence}</p>
              </div>
            )}

            {/* Options Considered */}
            {record.options_considered && (
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-3" title="Alternatives that were evaluated and why they were rejected. Prevents re-proposing already-rejected ideas.">Options Considered</h2>
                <p className="text-gray-700 whitespace-pre-wrap">{record.options_considered}</p>
              </div>
            )}

            {/* Code Reference */}
            {record.code_reference && (
              <div className="bg-slate-50 rounded-lg shadow-md p-6 border border-slate-200">
                <h2 className="text-lg font-semibold text-gray-900 mb-3" title="References to implemented code: file paths, line ranges, and code snippets that highlight where the decision is implemented.">Code Reference</h2>
                <pre className="text-gray-700 whitespace-pre-wrap font-mono text-sm overflow-x-auto">{record.code_reference}</pre>
              </div>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Status History */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Status History</h2>
              <div className="space-y-3">
                {history.map((entry, index) => {
                  const isAutomatic = entry.metadata?.change_type === 'automatic';
                  const triggeringRecordId = entry.metadata?.triggering_decision_record_id;
                  
                  return (
                    <div key={entry.id} className="relative pl-6">
                      {index < history.length - 1 && (
                        <div className="absolute left-2 top-6 bottom-0 w-0.5 bg-gray-200"></div>
                      )}
                      <div className={`absolute left-0 top-1.5 w-4 h-4 rounded-full border-2 border-white ${
                        isAutomatic ? 'bg-amber-500' : 'bg-indigo-500'
                      }`}></div>
                      <div>
                        <div className="flex items-center space-x-2">
                          {entry.from_status ? (
                            <>
                              <StatusBadge status={entry.from_status} size="sm" />
                              <span className="text-gray-400">→</span>
                            </>
                          ) : null}
                          <StatusBadge status={entry.to_status} size="sm" />
                          {isAutomatic && (
                            <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-amber-100 text-amber-800">
                              Automatic
                            </span>
                          )}
                        </div>
                        <p className="text-xs text-gray-500 mt-1">
                          {new Date(entry.changed_at).toLocaleString()}
                        </p>
                        {entry.reason && (
                          <p className="text-sm text-gray-600 mt-1">{entry.reason}</p>
                        )}
                        {isAutomatic && triggeringRecordId && (
                          <div className="mt-2 text-xs">
                            <span className="text-gray-500">Triggered by: </span>
                            <Link 
                              to={`/records/${triggeringRecordId}`}
                              className="text-indigo-600 hover:text-indigo-800 hover:underline font-mono"
                            >
                              {triggeringRecordId.substring(0, 8)}...
                            </Link>
                            <span className="text-gray-400 ml-1">
                              <svg className="w-3 h-3 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                              </svg>
                            </span>
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Relationships */}
            {(record.outgoing_relationships?.length > 0 || record.incoming_relationships?.length > 0) && (
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Relationships</h2>
                {record.outgoing_relationships?.length > 0 && (
                  <div className="mb-4">
                    <h3 className="text-sm font-medium text-gray-700 mb-2">Outgoing</h3>
                    <ul className="space-y-2">
                      {record.outgoing_relationships.map((rel) => (
                        <li key={rel.id} className="text-sm">
                          <span className="font-medium text-indigo-600">{rel.relationship_type}</span>
                          <span className="text-gray-500"> → </span>
                          <Link to={`/records/${rel.target_record_id}`} className="text-indigo-600 hover:underline">
                            View Record
                          </Link>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                {record.incoming_relationships?.length > 0 && (
                  <div>
                    <h3 className="text-sm font-medium text-gray-700 mb-2">Incoming</h3>
                    <ul className="space-y-2">
                      {record.incoming_relationships.map((rel) => (
                        <li key={rel.id} className="text-sm">
                          <Link to={`/records/${rel.source_record_id}`} className="text-indigo-600 hover:underline">
                            View Record
                          </Link>
                          <span className="text-gray-500"> → </span>
                          <span className="font-medium text-indigo-600">{rel.relationship_type}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}

            {/* Metadata */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Metadata</h2>
              <dl className="space-y-2 text-sm">
                <div>
                  <dt className="text-gray-500">Created</dt>
                  <dd className="text-gray-900">{new Date(record.created_at).toLocaleString()}</dd>
                </div>
                <div>
                  <dt className="text-gray-500">Last Updated</dt>
                  <dd className="text-gray-900">{new Date(record.updated_at).toLocaleString()}</dd>
                </div>
                <div>
                  <dt className="text-gray-500">Record ID</dt>
                  <dd className="text-gray-900 font-mono text-xs">{record.id}</dd>
                </div>
              </dl>
            </div>

            {/* VCS Info */}
            {record.metadata?.vcs && (
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center space-x-2">
                  <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                      d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                  </svg>
                  <span>Version Control</span>
                </h2>
                <dl className="space-y-2 text-sm">
                  <div>
                    <dt className="text-gray-500">VCS Type</dt>
                    <dd className="text-gray-900 capitalize">{record.metadata.vcs.type}</dd>
                  </div>
                  <div>
                    <dt className="text-gray-500">Revision</dt>
                    <dd className="text-gray-900 font-mono text-xs break-all">{record.metadata.vcs.revision}</dd>
                  </div>
                </dl>
              </div>
            )}
          </div>
        </div>
      )}

      {activeTab === 'versions' && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <VersionHistory
            recordId={recordId}
            currentVersion={record.version}
            onRevert={(version) => setRevertModal({ isOpen: true, targetVersion: version })}
          />
        </div>
      )}

      {activeTab === 'changelog' && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <Changelog recordId={recordId} />
        </div>
      )}

      {activeTab === 'compare' && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <VersionDiff recordId={recordId} versions={versions} currentVersion={record?.version} />
        </div>
      )}

      {/* Revert Modal */}
      <RevertModal
        isOpen={revertModal.isOpen}
        onClose={() => setRevertModal({ isOpen: false, targetVersion: null })}
        onConfirm={handleRevert}
        targetVersion={revertModal.targetVersion}
        currentVersion={record.version}
      />
    </div>
  );
}

export default RecordDetailPage;
