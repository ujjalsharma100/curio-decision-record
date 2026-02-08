const statusStyles = {
  proposed: 'bg-yellow-100 text-yellow-800 border-yellow-300',
  accepted: 'bg-blue-100 text-blue-800 border-blue-300',
  implemented: 'bg-green-100 text-green-800 border-green-300',
  implemented_inferred: 'bg-emerald-100 text-emerald-800 border-emerald-300',
  rejected: 'bg-red-100 text-red-800 border-red-300',
  deprecated: 'bg-gray-100 text-gray-800 border-gray-300',
};

const statusLabels = {
  proposed: 'Proposed',
  accepted: 'Accepted',
  implemented: 'Implemented',
  implemented_inferred: 'Implemented (Inferred)',
  rejected: 'Rejected',
  deprecated: 'Deprecated',
};

function StatusBadge({ status, size = 'md' }) {
  const sizeClasses = size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-3 py-1 text-sm';

  return (
    <span
      className={`inline-flex items-center rounded-full border font-medium ${statusStyles[status] || statusStyles.proposed} ${sizeClasses}`}
    >
      {statusLabels[status] || status}
    </span>
  );
}

export default StatusBadge;
