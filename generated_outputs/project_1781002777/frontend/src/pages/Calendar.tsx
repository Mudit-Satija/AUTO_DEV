import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

interface Event {
  id: string;
  title: string;
  description: string;
  date: string;
  courseId: string;
}

export default function Calendar() {
  const [events, setEvents] = useState<Event[]>(() => {
    const saved = localStorage.getItem('events');
    return saved ? JSON.parse(saved) : [];
  });

  const [newEvent, setNewEvent] = useState<Omit<Event, 'id'>>({
    title: '',
    description: '',
    date: '',
    courseId: '',
  });

  useEffect(() => {
    localStorage.setItem('events', JSON.stringify(events));
  }, [events]);

  const handleCreateEvent = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newEvent.title || !newEvent.date) return;

    const event: Event = {
      ...newEvent,
      id: Date.now().toString(),
    };

    setEvents(prev => [...prev, event]);
    setNewEvent({
      title: '',
      description: '',
      date: '',
      courseId: '',
    });
  };

  const getEventsByDate = () => {
    const eventsByDate: Record<string, Event[]> = {};
    events.forEach(event => {
      if (!eventsByDate[event.date]) {
        eventsByDate[event.date] = [];
      }
      eventsByDate[event.date].push(event);
    });
    return eventsByDate;
  };

  const eventsByDate = getEventsByDate();
  const sortedDates = Object.keys(eventsByDate).sort();

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-800">Calendar</h1>
        <button
          onClick={() => document.getElementById('new-event-form')?.classList.remove('hidden')}
          className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md transition-colors"
        >
          Add Event
        </button>
      </div>

      <div
        id="new-event-form"
        className="hidden p-6 bg-white rounded-lg shadow mb-8"
      >
        <h2 className="text-xl font-semibold mb-4">Add New Event</h2>
        <form onSubmit={handleCreateEvent} className="space-y-4">
          <div>
            <label className="block text-gray-700 mb-1">Title</label>
            <input
              type="text"
              value={newEvent.title}
              onChange={e => setNewEvent({ ...newEvent, title: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
              required
            />
          </div>
          <div>
            <label className="block text-gray-700 mb-1">Date</label>
            <input
              type="date"
              value={newEvent.date}
              onChange={e => setNewEvent({ ...newEvent, date: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
              required
            />
          </div>
          <div>
            <label className="block text-gray-700 mb-1">Description</label>
            <textarea
              value={newEvent.description}
              onChange={e => setNewEvent({ ...newEvent, description: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
              rows={3}
            />
          </div>
          <div>
            <label className="block text-gray-700 mb-1">Course</label>
            <input
              type="text"
              value={newEvent.courseId}
              onChange={e => setNewEvent({ ...newEvent, courseId: e.target.value })}
              placeholder="Course ID (optional)"
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            />
          </div>
          <div className="flex space-x-4">
            <button
              type="submit"
              className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md transition-colors"
            >
              Add Event
            </button>
            <button
              type="button"
              onClick={() => document.getElementById('new-event-form')?.classList.add('hidden')}
              className="bg-gray-300 hover:bg-gray-400 text-gray-800 px-4 py-2 rounded-md transition-colors"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>

      {sortedDates.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg shadow">
          <p className="text-gray-500 mb-4">No events scheduled.</p>
          <button
            onClick={() => document.getElementById('new-event-form')?.classList.remove('hidden')}
            className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-2 rounded-md transition-colors"
          >
            Create Your First Event
          </button>
        </div>
      ) : (
        <div className="space-y-8">
          {sortedDates.map(date => (
            <div key={date} className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold text-gray-800 mb-4">
                {new Date(date).toLocaleDateString('en-US', {
                  weekday: 'long',
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric',
                })}
              </h2>
              <div className="space-y-3">
                {eventsByDate[date].map(event => (
                  <div
                    key={event.id}
                    className="p-4 border border-gray-200 rounded-md hover:shadow-md transition-shadow"
                  >
                    <h3 className="font-medium text-gray-800">{event.title}</h3>
                    {event.description && (
                      <p className="text-gray-600 mt-1">{event.description}</p>
                    )}
                    {event.courseId && (
                      <p className="text-sm text-gray-500 mt-1">
                        Course: {event.courseId}
                      </p>
                    )}
                    <Link
                      to={`/courses/${event.courseId}`}
                      className="text-indigo-600 hover:text-indigo-800 text-sm mt-2 inline-block"
                    >
                      View Course
                    </Link>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}