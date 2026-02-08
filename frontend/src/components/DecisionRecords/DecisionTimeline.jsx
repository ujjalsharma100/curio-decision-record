import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { decisionsApi } from '../../services/api';
import StatusBadge from './StatusBadge';

const eventTypeConfig = {
  record_created: {
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
          d="M12 9v3m0 0v3m0-3h3m-3 0H9m12 0a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
    color: 'bg-indigo-500',
    ringColor: 'ring-indigo-100',
    label: 'Record Created',
    bgColor: 'bg-indigo-50',
  },
  status_change: {
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
          d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4" />
      </svg>
    ),
    color: 'bg-amber-500',
    ringColor: 'ring-amber-100',
    label: 'Status Changed',
    bgColor: 'bg-amber-50',
  },
  content_change: {
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
          d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
      </svg>
    ),
    color: 'bg-cyan-500',
    ringColor: 'ring-cyan-100',
    label: 'Content Updated',
    bgColor: 'bg-cyan-50',
  },
};

function DecisionTimeline({ decisionId }) {
  const [timeline, setTimeline] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expandedEvents, setExpandedEvents] = useState({});

  useEffect(() => {
    loadTimeline();
  }, [decisionId]);

  const loadTimeline = async () => {
    try {
      setLoading(true);
      const response = await decisionsApi.getTimeline(decisionId);
      setTimeline(response.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load timeline');
    } finally {
      setLoading(false);
    }
  };

  const toggleExpand = (eventId) => {
    setExpandedEvents(prev => ({
      ...prev,
      [eventId]: !prev[eventId]
    }));
  };

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    return {
      date: date.toLocaleDateString('en-US', { 
        weekday: 'short',
        year: 'numeric', 
        month: 'short', 
        day: 'numeric' 
      }),
      time: date.toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit',
        second: '2-digit'
      }),
      relative: getRelativeTime(date)
    };
  };

  const getRelativeTime = (date) => {
    const now = new Date();
    const diff = now - date;
    const seconds = Math.floor(diff / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);

    if (days > 30) return null;
    if (days > 0) return `${days}d ago`;
    if (hours > 0) return `${hours}h ago`;
    if (minutes > 0) return `${minutes}m ago`;
    return 'Just now';
  };

  const renderEventContent = (event, isExpanded) => {
    const config = eventTypeConfig[event.event_type] || eventTypeConfig.record_created;

    switch (event.event_type) {
      case 'record_created':
        return (
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-medium text-gray-900">New record proposed</span>
              <StatusBadge status={event.details?.initial_status} size="sm" />
            </div>
            {isExpanded && event.decision_description && (
              <p className="mt-2 text-sm text-gray-600 bg-gray-50 p-3 rounded-lg">
                {event.decision_description}
              </p>
            )}
          </div>
        );

      case 'status_change':
        return (
          <div>
            <div className="flex items-center flex-wrap gap-2">
              <span className="font-medium text-gray-900">Status changed</span>
              <div className="flex items-center space-x-2">
                <StatusBadge status={event.details?.from_status} size="sm" />
                <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
                </svg>
                <StatusBadge status={event.details?.to_status} size="sm" />
              </div>
              {event.details?.is_automatic && (
                <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-amber-100 text-amber-800">
                  Automatic
                </span>
              )}
            </div>
            {event.details?.reason && (
              <p className="mt-2 text-sm text-gray-600 italic">
                "{event.details.reason}"
              </p>
            )}
          </div>
        );

      case 'content_change':
        return (
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-medium text-gray-900">
                Version {event.details?.from_version} → {event.details?.to_version}
              </span>
              {event.details?.summary && (
                <span className="text-sm text-gray-500">{event.details.summary}</span>
              )}
            </div>
            {isExpanded && event.details?.changes && (
              <div className="mt-2 space-y-1">
                {Object.keys(event.details.changes).map((field) => (
                  <span 
                    key={field}
                    className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-700 mr-1"
                  >
                    {field.replace(/_/g, ' ')}
                  </span>
                ))}
              </div>
            )}
          </div>
        );

      default:
        return <span className="text-gray-600">Unknown event</span>;
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-48">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-8 text-red-600">
        <p>{error}</p>
        <button onClick={loadTimeline} className="mt-2 text-indigo-600 hover:text-indigo-800">
          Try again
        </button>
      </div>
    );
  }

  if (!timeline || timeline.events.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
            d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <p className="mt-2">No events yet</p>
      </div>
    );
  }

  // Group events by date
  const groupedByDate = timeline.grouped_by_date || {};
  const sortedDates = Object.keys(groupedByDate).sort((a, b) => new Date(b) - new Date(a));

  return (
    <div className="space-y-8">
      {/* Header Stats */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-4">
          <h3 className="text-lg font-semibold text-gray-900">Activity Timeline</h3>
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
            {timeline.total_events} events
          </span>
        </div>
      </div>

      {/* Timeline by Date */}
      {sortedDates.map((dateKey) => {
        const dateEvents = groupedByDate[dateKey];
        const formattedDate = new Date(dateKey).toLocaleDateString('en-US', {
          weekday: 'long',
          year: 'numeric',
          month: 'long',
          day: 'numeric'
        });

        return (
          <div key={dateKey} className="relative">
            {/* Date Header */}
            <div className="sticky top-0 z-10 bg-white pb-4">
              <div className="flex items-center">
                <div className="flex-shrink-0 w-3 h-3 rounded-full bg-gray-300"></div>
                <div className="ml-4 text-sm font-semibold text-gray-500 uppercase tracking-wider">
                  {formattedDate}
                </div>
                <div className="flex-1 ml-4 border-t border-gray-200"></div>
              </div>
            </div>

            {/* Events for this date */}
            <div className="ml-1.5 border-l-2 border-gray-200 pl-8 space-y-6">
              {dateEvents.map((event, idx) => {
                const config = eventTypeConfig[event.event_type] || eventTypeConfig.record_created;
                const ts = formatTimestamp(event.timestamp);
                const eventKey = `${dateKey}-${idx}-${event.record_id}`;
                const isExpanded = expandedEvents[eventKey];

                return (
                  <div key={eventKey} className="relative">
                    {/* Timeline dot */}
                    <div className={`absolute -left-[2.5rem] flex items-center justify-center w-8 h-8 rounded-full ${config.color} text-white ring-4 ${config.ringColor}`}>
                      {config.icon}
                    </div>

                    {/* Event Card */}
                    <div 
                      className={`${config.bgColor} rounded-lg p-4 cursor-pointer hover:shadow-md transition-shadow`}
                      onClick={() => toggleExpand(eventKey)}
                    >
                      {/* Time and concurrent indicator */}
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center space-x-2">
                          <span className="text-xs font-mono text-gray-500">{ts.time}</span>
                          {ts.relative && (
                            <span className="text-xs text-gray-400">({ts.relative})</span>
                          )}
                          {event.has_concurrent_events && (
                            <span className="inline-flex items-center px-1.5 py-0.5 rounded text-xs bg-purple-100 text-purple-700">
                              +{event.concurrent_count - 1} concurrent
                            </span>
                          )}
                        </div>
                        <Link 
                          to={`/records/${event.record_id}`}
                          onClick={(e) => e.stopPropagation()}
                          className="text-xs text-indigo-600 hover:text-indigo-800 hover:underline font-mono"
                        >
                          v{event.record_version}
                        </Link>
                      </div>

                      {/* Event Content */}
                      {renderEventContent(event, isExpanded)}

                      {/* Expand indicator */}
                      <div className="mt-2 flex items-center text-xs text-gray-400">
                        <svg 
                          className={`w-4 h-4 transition-transform ${isExpanded ? 'rotate-180' : ''}`} 
                          fill="none" 
                          stroke="currentColor" 
                          viewBox="0 0 24 24"
                        >
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                        </svg>
                        <span className="ml-1">{isExpanded ? 'Less' : 'More'}</span>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        );
      })}
    </div>
  );
}

export default DecisionTimeline;
