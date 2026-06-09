import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';

interface Course {
  id: string;
  name: string;
  code: string;
  description: string;
  syllabus: string;
}

interface Assignment {
  id: string;
  title: string;
  description: string;
  dueDate: string;
  status: 'pending' | 'completed';
  courseId: string;
}

export default function CourseDetails() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [course, setCourse] = useState<Course | null>(null);
  const [assignments, setAssignments] = useState<Assignment[]>(() => {
    const saved = localStorage.getItem('assignments');
    return saved ? JSON.parse(saved) : [];
  });

  useEffect(() => {
    const savedCourses = localStorage.getItem('courses');
    if (savedCourses) {
      const courses: Course[] = JSON.parse(savedCourses);
      setCourse(courses.find(c => c.id === id) || null);
    }
  }, [id]);

  useEffect(() => {
    localStorage.setItem('assignments', JSON.stringify(assignments));
  }, [assignments]);

  const courseAssignments = assignments.filter(a => a.courseId === id);

  if (!course) {
    return (
      <div className="p-6 text-center">
        <h1 className="text-2xl font-bold text-gray-800 mb-4">Course Not Found</h1>
        <button
          onClick={() => navigate('/courses')}
          className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md transition-colors"
        >
          Back to Courses
        </button>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-800">{course.name}</h1>
        <button
          onClick={() => navigate('/courses')}
          className="bg-gray-300 hover:bg-gray-400 text-gray-800 px-4 py-2 rounded-md transition-colors"
        >
          Back to Courses
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">Course Details</h2>
          <p className="text-gray-600 mb-2"><strong>Code:</strong> {course.code}</p>
          <p className="text-gray-600 mb-4">{course.description}</p>

          <h3 className="text-xl font-semibold text-gray-800 mb-3">Syllabus</h3>
          <div className="bg-gray-50 p-4 rounded-md text-gray-700 whitespace-pre-line">
            {course.syllabus || 'No syllabus provided.'}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-semibold text-gray-800">Assignments</h2>
            <Link
              to="/assignments"
              className="text-indigo-600 hover:text-indigo-800 text-sm font-medium"
            >
              View All Assignments
            </Link>
          </div>

          {courseAssignments.length === 0 ? (
            <div className="text-center py-8 bg-gray-50 rounded-md">
              <p className="text-gray-500 mb-4">No assignments for this course.</p>
              <Link
                to="/assignments"
                className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md transition-colors"
              >
                Create Assignment
              </Link>
            </div>
          ) : (
            <div className="space-y-4">
              {courseAssignments.map(assignment => (
                <div
                  key={assignment.id}
                  className="p-4 border border-gray-200 rounded-md hover:shadow-md transition-shadow"
                >
                  <h3 className="font-medium text-gray-800">{assignment.title}</h3>
                  {assignment.description && (
                    <p className="text-gray-600 mt-1 text-sm">{assignment.description}</p>
                  )}
                  <p className="text-sm text-gray-500 mt-1">
                    Due: {new Date(assignment.dueDate).toLocaleDateString()}
                  </p>
                  <span
                    className={`inline-block px-2 py-1 text-xs rounded-full mt-2 ${
                      assignment.status === 'completed'
                        ? 'bg-green-100 text-green-800'
                        : 'bg-yellow-100 text-yellow-800'
                    }`}
                  >
                    {assignment.status === 'completed' ? 'Completed' : 'Pending'}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}