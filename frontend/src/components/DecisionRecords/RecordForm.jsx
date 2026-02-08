import { useState } from 'react';

const STATUSES = [
  { value: 'proposed', label: 'Proposed' },
  { value: 'accepted', label: 'Accepted' },
  { value: 'implemented', label: 'Implemented' },
  { value: 'implemented_inferred', label: 'Implemented (Inferred)' },
  { value: 'rejected', label: 'Rejected' },
  { value: 'deprecated', label: 'Deprecated' },
];

function RecordForm({ initialData, onSubmit, onCancel }) {
  const [formData, setFormData] = useState({
    decision_description: initialData?.decision_description || '',
    status: initialData?.status || 'proposed',
    context: initialData?.context || '',
    constraints: initialData?.constraints || '',
    rationale: initialData?.rationale || '',
    assumptions: initialData?.assumptions || '',
    consequences: initialData?.consequences || '',
    tradeoffs: initialData?.tradeoffs || '',
    evidence: initialData?.evidence || '',
    options_considered: initialData?.options_considered || '',
    version: initialData?.version || 1,
  });

  const isInferred = formData.status === 'implemented_inferred';

  const handleChange = (field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {/* Status */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Status *
          </label>
          <select
            value={formData.status}
            onChange={(e) => handleChange('status', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            disabled={!!initialData}
          >
            {STATUSES.map((s) => (
              <option key={s.value} value={s.value}>{s.label}</option>
            ))}
          </select>
          {!!initialData && (
            <p className="text-xs text-gray-500 mt-1">Use status dropdown on card to change status</p>
          )}
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Version
          </label>
          <input
            type="number"
            value={formData.version}
            onChange={(e) => handleChange('version', parseInt(e.target.value) || 1)}
            min="1"
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
          />
        </div>
      </div>

      {/* Decision Description - Always Required */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Decision Description *
        </label>
        <textarea
          value={formData.decision_description}
          onChange={(e) => handleChange('decision_description', e.target.value)}
          rows={4}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
          placeholder="Describe the decision being made..."
          required
        />
      </div>

      {isInferred && (
        <div className="bg-emerald-50 p-3 rounded-lg border border-emerald-200 text-sm text-emerald-800">
          For inferred decisions, only the description is required. Other fields are optional.
        </div>
      )}

      {/* Context */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Context {!isInferred && <span className="text-gray-400">(recommended)</span>}
        </label>
        <textarea
          value={formData.context}
          onChange={(e) => handleChange('context', e.target.value)}
          rows={2}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
          placeholder="Why now? What prompted this decision?"
        />
      </div>

      {/* Constraints */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Constraints
        </label>
        <textarea
          value={formData.constraints}
          onChange={(e) => handleChange('constraints', e.target.value)}
          rows={2}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
          placeholder="What requirements must be met?"
        />
      </div>

      {/* Rationale */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Rationale
        </label>
        <textarea
          value={formData.rationale}
          onChange={(e) => handleChange('rationale', e.target.value)}
          rows={2}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
          placeholder="Why was this choice made?"
        />
      </div>

      {/* Assumptions - Highlighted */}
      <div className="bg-amber-50 p-4 rounded-lg border border-amber-200">
        <label className="block text-sm font-medium text-amber-800 mb-1">
          Assumptions (Critical for Validation)
        </label>
        <textarea
          value={formData.assumptions}
          onChange={(e) => handleChange('assumptions', e.target.value)}
          rows={3}
          className="w-full px-3 py-2 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-amber-500 bg-white"
          placeholder="What are we assuming to be true? When these change, revisit this decision."
        />
        <p className="text-xs text-amber-700 mt-1">
          When new information invalidates these assumptions, this decision should be reconsidered.
        </p>
      </div>

      {/* Consequences */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Consequences
        </label>
        <textarea
          value={formData.consequences}
          onChange={(e) => handleChange('consequences', e.target.value)}
          rows={2}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
          placeholder="What are the positive and negative impacts?"
        />
      </div>

      {/* Tradeoffs */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Tradeoffs
        </label>
        <textarea
          value={formData.tradeoffs}
          onChange={(e) => handleChange('tradeoffs', e.target.value)}
          rows={2}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
          placeholder="What are we giving up with this choice?"
        />
      </div>

      {/* Evidence */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Evidence
        </label>
        <textarea
          value={formData.evidence}
          onChange={(e) => handleChange('evidence', e.target.value)}
          rows={2}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
          placeholder="Links, resources, benchmarks that support this decision..."
        />
      </div>

      {/* Options Considered */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Options Considered
        </label>
        <textarea
          value={formData.options_considered}
          onChange={(e) => handleChange('options_considered', e.target.value)}
          rows={3}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
          placeholder="What other options were considered and why were they not chosen?"
        />
      </div>

      {/* Actions */}
      <div className="flex justify-end space-x-3 pt-4 border-t">
        <button
          type="button"
          onClick={onCancel}
          className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
        >
          Cancel
        </button>
        <button
          type="submit"
          className="px-4 py-2 text-white bg-indigo-600 rounded-lg hover:bg-indigo-700"
        >
          {initialData ? 'Update Record' : 'Create Record'}
        </button>
      </div>
    </form>
  );
}

export default RecordForm;
