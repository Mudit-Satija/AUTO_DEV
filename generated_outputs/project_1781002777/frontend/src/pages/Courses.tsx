import React, { useState, useEffect } from 'react';

interface Course {
  id: string;
  name: string;
  code: string;
  instructor: string;
  color: string;
}

const Courses: React.FC = () => {
  const [courses, setCourses] = useState<Course[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [editingCourse, setEditingCourse] = useState<Course | null>(null);
  const [form, setForm] = useState({
    name: '',
    code: '',
    instructor: '',
    color: '#3b82f6',
  });

  useEffect(() => {
    const storedCourses = localStorage.getItem('courses');
    if (storedCourses) {
      setCourses(JSON.parse(storedCourses));
    }
  }, []);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setForm({ ...form, [name]: value });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (editingCourse) {
      setCourses(courses.map(course => 
        course.id === editingCourse.id 
          ? { ...form, id: course.id } 
          : course
      ));
      setEditingCourse(null);
    } else {
      const newCourse: Course = {
        ...form,
        id: Date.now().toString(),
      };
      setCourses([...courses, newCourse]);
    }
    localStorage.setItem('courses', JSON.stringify(courses));
    setForm({ name: '', code: '', instructor: '', color: '#3b82f6' });
    setShowForm(false);
  };

  const handleEdit = (course: Course) => {
    setEditingCourse(course);
    setForm({
      name: course.name,
      code: course.code,
      instructor: course.instructor,
      color: course.color,
    });
    setShowForm(true);
  };

  const handleDelete = (id: string) => {
    setCourses(courses.filter(course => course.id !== id));
    localStorage.setItem('courses', JSON.stringify(courses.filter(course => course.id !== id)));
  };

  const colors = [
    '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#f97316',
  ];

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-800">Courses</h1>
        <button
          onClick={() => {
            setShowForm(true);
            setEditingCourse(null);
            setForm({ name: '', code: '', instructor: '', color: '#3b82f6' });
          }}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition"
        >
          Add Course
        </button>
      </div>

      {showForm && (
        <div className="mb-6 p-6 bg-white rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-4">{editingCourse ? 'Edit Course' : 'Add New Course'}</h2>
          <form onSubmit={handleSubmit}>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Course Name</label>
                <input
                  type="text"
                  name="name"
                  value={form.name}
                  onChange={handleInputChange}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Course Code</label>
                <input
                  type="text"
                  name="code"
                  value={form.code}
                  onChange={handleInputChange}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Instructor</label>
                <input
                  type="text"
                  name="instructor"
                  value={form.instructor}
                  onChange={handleInputChange}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Color</label>
                <div className="flex items-center space-x-2">
                  <input
                    type="color"
                    name="color"
                    value={form.color}
                    onChange={handleInputChange}
                    className="w-10 h-10 rounded border-0 cursor-pointer"
                  />
                  <input
                    type="text"
                    name="color"
                    value={form.color}
                    onChange={handleInputChange}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>
            </div>
            <div className="flex space-x-4">
              <button
                type="submit"
                className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition"
              >
                {editingCourse ? 'Update' : 'Add'}
              </button>
              <button
                type="button"
                onClick={() => {
                  setShowForm(false);
                  setEditingCourse(null);
                  setForm({ name: '', code: '', instructor: '', color: '#3b82f6' });
                }}
                className="bg-gray-300 text-gray-800 px-6 py-2 rounded-lg hover:bg-gray-400 transition"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {courses.length === 0 ? (
          <div className="col-span-full text-center py-12 bg-gray-50 rounded-lg">
            <p className="text-gray-500 mb-4">No courses yet.</p>
            <button
              onClick={() => setShowForm(true)}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition"
            >
              Add Your First Course
            </button>
          </div>
        ) : (
          courses.map(course => (
            <div
              key={course.id}
              className="border border-gray-200 rounded-lg p-5 shadow-md hover:shadow-lg transition"
              style={{ borderLeft: `4px solid ${course.color}` }}
            >
              <div className="flex justify-between items-start mb-3">
                <h3 className="text-xl font-semibold text-gray-800">{course.name}</h3>
                <div className="flex space-x-2">
                  <button
                    onClick={() => handleEdit(course)}
                    className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => handleDelete(course.id)}
                    className="text-red-600 hover:text-red-800 text-sm font-medium"
                  >
                    Delete
                  </button>
                </div>
              </div>
              <p className="text-gray-600 mb-1"><strong>Code:</strong> {course.code}</p>
              <p className="text-gray-600 mb-1"><strong>Instructor:</strong> {course.instructor}</p>
              <div className="mt-4 flex flex-wrap gap-1">
                {colors.map(color => (
                  <div
                    key={color}
                    className={`w-5 h-5 rounded-full border-2 cursor-pointer ${
                      color === course.color ? 'border-gray-800 scale-110' : 'border-gray-200'
                    }`}
                    style={{ backgroundColor: color }}
                    onClick={() => {
                      const updatedCourses = courses.map(c =>
                        c.id === course.id ? { ...c, color } : c
                      );
                      setCourses(updatedCourses);
                      localStorage.setItem('courses', JSON.stringify(updatedCourses));
                    }}
                  />
                ))}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default Courses;