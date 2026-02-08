import { Link } from 'react-router-dom';

function ProjectCard({ project, onEdit, onDelete }) {
  return (
    <div className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow">
      <div className="p-6">
        <div className="flex justify-between items-start">
          <Link to={`/projects/${project.id}`} className="flex-1">
            <h3 className="text-lg font-semibold text-gray-900 hover:text-indigo-600">
              {project.name}
            </h3>
          </Link>
          <div className="flex space-x-2">
            <button
              onClick={onEdit}
              className="text-gray-400 hover:text-indigo-600"
              title="Edit"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
            </button>
            <button
              onClick={onDelete}
              className="text-gray-400 hover:text-red-600"
              title="Delete"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          </div>
        </div>

        {project.description && (
          <p className="mt-2 text-gray-600 text-sm line-clamp-2">
            {project.description}
          </p>
        )}

        <div className="mt-4 flex items-center justify-between text-sm">
          <span className="text-gray-500">
            {project.decision_count} decision{project.decision_count !== 1 ? 's' : ''}
          </span>
          <span className="text-gray-400">
            {new Date(project.created_at).toLocaleDateString()}
          </span>
        </div>
      </div>
    </div>
  );
}

export default ProjectCard;
