import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Projects
export const projectsApi = {
  list: () => api.get('/projects'),
  get: (id) => api.get(`/projects/${id}`),
  getRecords: (projectId) => api.get(`/projects/${projectId}/records`),
  getActionItems: (projectId) => api.get(`/projects/${projectId}/action-items`),
  create: (data) => api.post('/projects', data),
  update: (id, data) => api.put(`/projects/${id}`, data),
  delete: (id) => api.delete(`/projects/${id}`),
};

// Decisions
export const decisionsApi = {
  list: (projectId) => api.get(`/projects/${projectId}/decisions`),
  get: (id) => api.get(`/decisions/${id}`),
  create: (projectId, data) => api.post(`/projects/${projectId}/decisions`, data),
  update: (id, data) => api.put(`/decisions/${id}`, data),
  delete: (id) => api.delete(`/decisions/${id}`),
  getTimeline: (id) => api.get(`/decisions/${id}/timeline`),
  getImplementationHistory: (id) => api.get(`/decisions/${id}/implementation-history`),
};

// Decision Records
export const recordsApi = {
  list: (decisionId) => api.get(`/decisions/${decisionId}/records`),
  get: (id) => api.get(`/records/${id}`),
  create: (decisionId, data) => api.post(`/decisions/${decisionId}/records`, data),
  update: (id, data) => api.put(`/records/${id}`, data),
  delete: (id) => api.delete(`/records/${id}`),
  changeStatus: (id, status, reason = null, autoHandle = true) =>
    api.patch(`/records/${id}/status`, { status, reason, auto_handle_conflicts: autoHandle }),
  getHistory: (id) => api.get(`/records/${id}/history`),

  // Version Control
  getVersions: (id) => api.get(`/records/${id}/versions`),
  getAtVersion: (id, version) => api.get(`/records/${id}/versions/${version}`),
  getChangelog: (id) => api.get(`/records/${id}/changelog`),
  getDiff: (id, fromVersion, toVersion) =>
    api.get(`/records/${id}/diff`, { params: { from_version: fromVersion, to_version: toVersion } }),
  revertToVersion: (id, version, reason = null) =>
    api.post(`/records/${id}/revert`, { version, reason }),
};

// Relationships (record-level)
export const relationshipsApi = {
  list: (recordId) => api.get(`/records/${recordId}/relationships`),
  create: (recordId, targetRecordId, relationshipType, description = null) =>
    api.post(`/records/${recordId}/relationships`, {
      target_record_id: targetRecordId,
      relationship_type: relationshipType,
      description,
    }),
  delete: (id) => api.delete(`/relationships/${id}`),
};

// Decision-level relationships
export const decisionRelationshipsApi = {
  list: (decisionId) => api.get(`/decisions/${decisionId}/decision-relationships`),
  create: (decisionId, targetDecisionId, relationshipType, description = null) =>
    api.post(`/decisions/${decisionId}/decision-relationships`, {
      target_decision_id: targetDecisionId,
      relationship_type: relationshipType,
      description,
    }),
  delete: (id) => api.delete(`/decision-relationships/${id}`),
};

export default api;
