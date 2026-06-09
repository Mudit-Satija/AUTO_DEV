import React, { useState, useEffect } from 'react';

interface Course {
  id: string;
  name: string;
  code: string;
  instructor: string;
  color: string;
}

interface Assignment {
  id: string;
  title: string;
  course: string;
  dueDate: string;
  status: 'pending' | 'completed';
  priority: 'low' | 'medium' | 'high';
}

interface Event {
  id: string;
  title: string;
  date: string;
  type: 'exam' | 'deadline' | 'meeting' | 'other';
}

const Dashboard: React.FC = () => {
  const [courses, setCourses] = useState<Course[]>([]);
  const [assignments, setAssignments] = useState<Assignment[]>([]);
  const [events, setEvents] = useState<Event[]>([]);

  useEffect(() => {
    const storedCourses = localStorage.getItem('courses');
    const storedAssignments = localStorage.getItem('assignments');
    const storedEvents = localStorage.getItem('events');

    if (storedCourses) setCourses(JSON.parse(storedCourses));
    if (storedAssignments) setAssignments(JSON.parse(storedAssignments));
    if (storedEvents) setEvents(JSON.parse(storedEvents));
  }, []);

  const upcomingAssignments = assignments
    .filter(a => a.status === 'pending')
    .sort((a, b) => new Date(a.dueDate).getTime() - new Date(b.dueDate).getTime())
    .slice(0, 3);

  const upcomingEvents = events
    .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
    .slice(0, 3);

  const totalCourses = courses.length;
  const totalAssignments = assignments.length;
  const completedAssignments = assignments.filter(a => a.status === 'completed').length;
  const pendingAssignments = assignments.filter(a => a.status === 'pending').length;
  const highPriorityAssignments = assignments.filter(a => a.priority === 'high').length;

  const getCourseName = (courseId: string) => {
    const course = courses.find(c => c.id === courseId);
    return course ? course.name : 'Unknown Course';
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold text-gray-800 mb-6">Dashboard</h1>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-blue-500">
          <h3 className="text-gray-500 text-sm font-medium">Total Courses</h3>
          <p className="text-3xl font-bold text-gray-800">{totalCourses}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-green-500">
          <h3 className="text-gray-500 text-sm font-medium">Total Assignments</h3>
          <p className="text-3xl font-bold text-gray-800">{totalAssignments}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-yellow-500">
          <h3 className="text-gray-500 text-sm font-medium">Pending</h3>
          <p className="text-3xl font-bold text-gray-800">{pendingAssignments}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-red-500">
          <h3 className="text-gray-500 text-sm font-medium">High Priority</h3>
          <p className="text-3xl font-bold text-gray-800">{highPriorityAssignments}</p>
        </div>
      </div>

      {/* Upcoming Deadlines */}
      <div className="mb-8">
        <h2 className="text-2xl font-semibold text-gray-800 mb-4">Upcoming Deadlines</h2>
        {upcomingAssignments.length === 0 ? (
          <div className="bg-gray-50 p-8 rounded-lg text-center">
            <p className="text-gray-500 mb-4">No upcoming assignments.</p>
            <a href="/assignments" className="text-blue-600 hover:text-blue-800 font-medium">
              View All Assignments
            </a>
          </div>
        ) : (
          <div className="space-y-4">
            {upcomingAssignments.map(assignment => (
              <div
                key={assignment.id}
                className="flex items-center justify-between p-4 bg-white rounded-lg shadow-md"
              >
                <div className="flex items-center">
                  <div
                    className={`w-3 h-3 rounded-full mr-3 ${
                      assignment.priority === 'high' ? 'bg-red-500' :
                      assignment.priority === 'medium' ? 'bg-yellow-500' : 'bg-green-500'
                    }`}
                  ></div>
                  <div>
                    <h3 className="font-medium text-gray-800">{assignment.title}</h3>
                    <p className="text-sm text-gray-500">Due: {formatDate(assignment.dueDate)} in {getCourseName(assignment.course)}</p>
                  </div>
                </div>
                <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                  assignment.priority === 'high' ? 'bg-red-100 text-red-800' :
                  assignment.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' : 'bg-green-100 text-green-800'
                }`}>
                  {assignment.priority}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Upcoming Events */}
      <div className="mb-8">
        <h2 className="text-2xl font-semibold text-gray-800 mb-4">Upcoming Events</h2>
        {upcomingEvents.length === 0 ? (
          <div className="bg-gray-50 p-8 rounded-lg text-center">
            <p className="text-gray-500 mb-4">No upcoming events.</p>
            <a href="/calendar" className="text-blue-600 hover:text-blue-800 font-medium">
              View Calendar
            </a>
          </div>
        ) : (
          <div className="space-y-4">
            {upcomingEvents.map(event => (
              <div
                key={event.id}
                className="flex items-center justify-between p-4 bg-white rounded-lg shadow-md"
              >
                <div>
                  <h3 className="font-medium text-gray-800">{event.title}</h3>
                  <p className="text-sm text-gray-500">
                    {event.type === 'exam' && 'Exam'}{' '}
                    {event.type === 'deadline' && 'Deadline'}{' '}
                    {event.type === 'meeting' && 'Meeting'}{' '}
                    {event.type === 'other' && 'Other'}{' '}
                    on {formatDate(event.date)}
                  </p>
                </div>
                <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                  event.type === 'exam' ? 'bg-red-100 text-red-800' :
                  event.type === 'deadline' ? 'bg-blue-100 text-blue-800' :
                  event.type === 'meeting' ? 'bg-purple-100 text-purple-800' : 'bg-gray-100 text-gray-800'
                }`}>
                  {event.type}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Recent Courses */}
      <div>
        <h2 className="text-2xl font-semibold text-gray-800 mb-4">Your Courses</h2>
        {courses.length === 0 ? (
          <div className="bg-gray-50 p-8 rounded-lg text-center">
            <p className="text-gray-500 mb-4">No courses yet.</p>
            <a href="/courses" className="text-blue-600 hover:text-blue-800 font-medium">
              Add Your First Course
            </a>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {courses.map(course => (
              <div
                key={course.id}
                className="border border-gray-200 rounded-lg p-5 shadow-md hover:shadow-lg transition"
                style={{ borderLeft: `4px solid ${course.color}` }}
              >
                <h3 className="text-xl font-semibold text-gray-800 mb-2">{course.name}</h3>
                <p className="text-gray-600 mb-1"><strong>Code:</strong> {course.code}</p>
                <p className="text-gray-600 mb-3"><strong>Instructor:</strong> {course.instructor}</p>
                <div className="flex space-x-2">
                  <span className="px-3 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                    {assignments.filter(a => a.course === course.id).length} assignments
                  </span>
                  <span className="px-3 py-1 bg-gray-100 text-gray-800 text-xs rounded-full">
                    {events.filter(e => e.date && e.date.includes(course.id)).length} events
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;