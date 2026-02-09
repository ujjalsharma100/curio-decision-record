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
    decision_details: initialData?.decision_details || '',
    status: initialData?.status || 'proposed',
    context: initialData?.context || '',
    constraints: initialData?.constraints || '',
    rationale: initialData?.rationale || '',
    assumptions: initialData?.assumptions || '',
    consequences: initialData?.consequences || '',
    tradeoffs: initialData?.tradeoffs || '',
    evidence: initialData?.evidence || '',
    options_considered: initialData?.options_considered || '',
    code_reference: initialData?.code_reference || '',
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

      {/* Decision Details */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1" title="Detailed explanation of the decision. Elaborates on the decision description with implementation specifics, examples, or additional context.">
          Decision Details
        </label>
        <textarea
          value={formData.decision_details}
          onChange={(e) => handleChange('decision_details', e.target.value)}
          rows={4}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
          placeholder="Explain the details of the decision. Implementation specifics, examples, or additional context..."
        />
      </div>

      {isInferred && (
        <div className="bg-emerald-50 p-3 rounded-lg border border-emerald-200 text-sm text-emerald-800">
          For inferred decisions, only the description is required. Other fields are optional.
        </div>
      )}

      {/* Context */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1" title="Why this decision is being made now. The background situation, pressure, or trigger that necessitates it.">
          Context {!isInferred && <span className="text-gray-400">(recommended)</span>}
        </label>
        <textarea
          value={formData.context}
          onChange={(e) => handleChange('context', e.target.value)}
          rows={2}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
          placeholder="Why now? Background situation or trigger that necessitates this decision."
        />
      </div>

      {/* Constraints */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1" title="Hard requirements or limitations that must be satisfied. Explains why certain obvious options weren't viable.">
          Constraints
        </label>
        <textarea
          value={formData.constraints}
          onChange={(e) => handleChange('constraints', e.target.value)}
          rows={2}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
          placeholder="Hard requirements that must be satisfied (e.g., Python ecosystem, latency limits, compatibility)."
        />
      </div>

      {/* Rationale */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1" title="Why this specific option was chosen over alternatives. The reasoning and justification behind the decision.">
          Rationale
        </label>
        <textarea
          value={formData.rationale}
          onChange={(e) => handleChange('rationale', e.target.value)}
          rows={2}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
          placeholder="Why this option was chosen over alternatives. The reasoning and justification."
        />
      </div>

      {/* Assumptions - Highlighted */}
      <div className="bg-amber-50 p-4 rounded-lg border border-amber-200">
        <label className="block text-sm font-medium text-amber-800 mb-1" title="Things that must remain true for this decision to stay valid. When assumptions break or expire, the decision should be re-evaluated.">
          Assumptions (Critical for Validation)
        </label>
        <textarea
          value={formData.assumptions}
          onChange={(e) => handleChange('assumptions', e.target.value)}
          rows={3}
          className="w-full px-3 py-2 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-amber-500 bg-white"
          placeholder="What must remain true for this decision to stay valid? Re-evaluate when these change."
        />
        <p className="text-xs text-amber-700 mt-1">
          When new information invalidates these assumptions, this decision should be reconsidered.
        </p>
      </div>

      {/* Consequences */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1" title="Downstream impact of this decision, both positive and negative. What it will cause, enable, or require going forward.">
          Consequences
        </label>
        <textarea
          value={formData.consequences}
          onChange={(e) => handleChange('consequences', e.target.value)}
          rows={2}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
          placeholder="Downstream impact — positive and negative. What this will cause or enable."
        />
      </div>

      {/* Tradeoffs */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1" title="What is explicitly being given up by choosing this option. Makes costs intentional so future teams know pain points are by design.">
          Tradeoffs
        </label>
        <textarea
          value={formData.tradeoffs}
          onChange={(e) => handleChange('tradeoffs', e.target.value)}
          rows={2}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
          placeholder="What is explicitly being given up. Costs that are intentional."
        />
      </div>

      {/* Evidence */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1" title="Links to resources (papers, blogs, benchmarks, experiments) that support and defend the decision. Builds credibility and auditability.">
          Evidence
        </label>
        <textarea
          value={formData.evidence}
          onChange={(e) => handleChange('evidence', e.target.value)}
          rows={2}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
          placeholder="Links to papers, blogs, benchmarks, resources that support this decision."
        />
      </div>

      {/* Options Considered */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1" title="Alternatives that were evaluated and why they were rejected. Prevents future teams from re-proposing already-rejected ideas.">
          Options Considered
        </label>
        <textarea
          value={formData.options_considered}
          onChange={(e) => handleChange('options_considered', e.target.value)}
          rows={3}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
          placeholder="Alternatives evaluated and why they were rejected."
        />
      </div>

      {/* Code Reference */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1" title="References to implemented code: file paths, line ranges (e.g. src/utils.py:42-58), and code snippets that highlight where the decision is implemented.">
          Code Reference
        </label>
        <textarea
          value={formData.code_reference}
          onChange={(e) => handleChange('code_reference', e.target.value)}
          rows={5}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 font-mono text-sm"
          placeholder={'e.g. src/auth/service.py:42-58\n\ndef authenticate(user):\n    # Token validation logic...'}
        />
        <p className="text-xs text-gray-500 mt-1">
          File paths, line ranges (e.g. src/utils.py:42-58), and code snippets that show where this decision is implemented.
        </p>
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
