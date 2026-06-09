import { useState, useEffect } from 'react';

const Tasks = () => {
  const [tasks, setTasks] = useState([]);
  const [newTaskTitle, setNewTaskTitle] = useState('');
  const [newTaskPriority, setNewTaskPriority] = useState('medium');
  const [editingTask, setEditingTask] = useState(null);

  useEffect(() => {
    // In a real app, this would fetch from API
    // For now, mock data
    setTasks([
      { id: 1, title: 'Complete project', priority: 'high', completed: false },
      { id: 2, title: 'Review code', priority: 'medium', completed: true },
      { id: 3, title: 'Update documentation', priority: 'low', completed: true },
    ]);
  }, []);

  const addTask = () => {
    if (!newTaskTitle.trim()) return;
    const task = {
      id: Date.now(),
      title: newTaskTitle,
      priority: newTaskPriority,
      completed: false,
    };
    setTasks([...tasks, task]);
    setNewTaskTitle('');
  };

  const updateTask = (id, updates) => {
    setTasks(tasks.map(task => task.id === id ? { ...task, ...updates } : task));
    setEditingTask(null);
  };

  const deleteTask = (id) => {
    setTasks(tasks.filter(task => task.id !== id));
  };

  const toggleComplete = (id) => {
    setTasks(tasks.map(task =>
      task.id === id ? { ...task, completed: !task.completed } : task
    ));
  };

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-8">Tasks</h1>

      <div className="bg-gray-800 rounded-lg p-6 shadow-lg mb-8">
        <h2 className="text-2xl font-bold mb-6">Add New Task</h2>
        <div className="flex flex-col sm:flex-row gap-4">
          <input
            type="text"
            value={newTaskTitle}
            onChange={(e) => setNewTaskTitle(e.target.value)}
            placeholder="Task title"
            className="flex-1 px-4 py-2 bg-gray-700 border border-gray-600 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <select
            value={newTaskPriority}
            onChange={(e) => setNewTaskPriority(e.target.value)}
            className="px-4 py-2 bg-gray-700 border border-gray-600 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
          <button
            onClick={addTask}
            className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
          >
            Add
          </button>
        </div>
      </div>

      <div className="bg-gray-800 rounded-lg p-6 shadow-lg">
        <h2 className="text-2xl font-bold mb-6">Task List</h2>
        <ul className="space-y-3">
          {tasks.map(task => (
            <li key={task.id} className="flex items-center justify-between p-4 bg-gray-700 rounded hover:bg-gray-650 transition-colors">
              <div className="flex items-center flex-1">
                <input
                  type="checkbox"
                  checked={task.completed}
                  onChange={() => toggleComplete(task.id)}
                  className="h-5 w-5 text-blue-600 rounded focus:ring-blue-500"
                />
                <span
                  className={`ml-3 flex-1 ${
                    task.completed ? 'line-through text-gray-500' : ''
                  }`}
                >
                  {task.title}
                </span>
                <span className={`px-2 py-1 text-xs rounded-full ml-3 ${
                  task.priority === 'high' ? 'bg-red-600' :
                  task.priority === 'medium' ? 'bg-yellow-600' :
                  'bg-green-600'
                }`}>
                  {task.priority}
                </span>
              </div>
              <div className="flex space-x-2 ml-4">
                <button
                  onClick={() => setEditingTask(task)}
                  className="px-3 py-1 bg-yellow-600 text-white text-sm rounded hover:bg-yellow-700 transition-colors"
                >
                  Edit
                </button>
                <button
                  onClick={() => deleteTask(task.id)}
                  className="px-3 py-1 bg-red-600 text-white text-sm rounded hover:bg-red-700 transition-colors"
                >
                  Delete
                </button>
              </div>
            </li>
          ))}
        </ul>
      </div>

      {editingTask && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-gray-800 rounded-lg p-6 w-full max-w-md">
            <h3 className="text-2xl font-bold mb-4">Edit Task</h3>
            <input
              type="text"
              value={editingTask.title}
              onChange={(e) => setEditingTask({ ...editingTask, title: e.target.value })}
              className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded mb-4 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <select
              value={editingTask.priority}
              onChange={(e) => setEditingTask({ ...editingTask, priority: e.target.value })}
              className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded mb-4 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </select>
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setEditingTask(null)}
                className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={() => updateTask(editingTask.id, editingTask)}
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
              >
                Save
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Tasks;