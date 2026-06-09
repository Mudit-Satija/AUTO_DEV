import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

interface Assignment {
  id: string;
  title: string;
  description: string;
  dueDate: string;
  status: 'pending' | 'completed';
  courseId: string;
}

export default function Assignments() {
  const [assignments, setAssignments] = useState<Assignment[]>(() => {
    const saved = localStorage.getItem('assignments');
    return saved ? JSON.parse(saved) : [];
  });
  const [filter, setFilter] = useState<'all' | 'pending' | 'completed'>('all');

  useEffect(() => {
    localStorage.setItem('assignments', JSON.stringify(assignments));
  }, [assignments]);

  const handleToggleStatus = (id: string) => {
    setAssignments(prev =>
      prev.map(assignment =>
        assignment.id === id
          ? { ...assignment, status: assignment.status === 'pending' ? 'completed' : 'pending' }
          : assignment
      )
    );
  };

  const handleCreateAssignment = () => {
    const newAssignment: Assignment = {
      id: Date.now().toString(),
      title: 'New Assignment',
      description: '',
      dueDate: new Date().toISOString().split('T')[0],
      status: 'pending',
      courseId: '',
    };
    setAssignments(prev => [...prev, newAssignment]);
  };

  const filteredAssignments = assignments.filter(assignment => {
    if (filter === 'pending') return assignment.status === 'pending';
    if (filter === 'completed') return assignment.status === 'completed';
    return true;
  });

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-800">Assignments</h1>
        <button
          onClick={handleCreateAssignment}
          className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md transition-colors"
        >
          Add Assignment
        </button>
      </div>

      <div className="flex space-x-4 mb-6">
        <button
          onClick={() => setFilter('all')}
          className={`px-4 py-2 rounded-md transition-colors ${
            filter === 'all' ? 'bg-indigo-600 text-white' : 'bg-gray-200 text-gray-700'
          }`}
        >
          All
        </button>
        <button
          onClick={() => setFilter('pending')}
          className={`px-4 py-2 rounded-md transition-colors ${
            filter === 'pending' ? 'bg-indigo-600 text-white' : 'bg-gray-200 text-gray-700'
          }`}
        >
          Pending
        </button>
        <button
          onClick={() => setFilter('completed')}
          className={`px-4 py-2 rounded-md transition-colors ${
            filter === 'completed' ? 'bg-indigo-600 text-white' : 'bg-gray-200 text-gray-700'
          }`}
        >
          Completed
        </button>
      </div>

      {filteredAssignments.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg shadow">
          <p className="text-gray-500 mb-4">No assignments found.</p>
          <button
            onClick={handleCreateAssignment}
            className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-2 rounded-md transition-colors"
          >
            Create Your First Assignment
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredAssignments.map(assignment => (
            <div
              key={assignment.id}
              className="p-4 bg-white rounded-lg shadow border-l-4 border-indigo-500"
            >
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <h2 className="text-xl font-semibold text-gray-800">{assignment.title}</h2>
                  <p className="text-gray-600 mt-1">{assignment.description || 'No description'}</p>
                  <p className="text-sm text-gray-500 mt-2">
                    Due: {new Date(assignment.dueDate).toLocaleDateString()}
                  </p>
                  <p className="text-sm text-gray-500 mt-1">
                    Course: {assignment.courseId || 'Unassigned'}
                  </p>
                </div>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => handleToggleStatus(assignment.id)}
                    className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                      assignment.status === 'completed'
                        ? 'bg-green-100 text-green-800'
                        : 'bg-yellow-100 text-yellow-800'
                    }`}
                  >
                    {assignment.status === 'completed' ? 'Completed' : 'Pending'}
                  </button>
                  <Link
                    to={`/courses/${assignment.courseId}`}
                    className="text-indigo-600 hover:text-indigo-800 text-sm"
                  >
                    View Course
                  </Link>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}