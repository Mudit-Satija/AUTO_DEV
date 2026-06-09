import React, { useState, useEffect } from 'react';

interface Task {
  id: string;
  title: string;
  description: string;
  priority: 'low' | 'medium' | 'high';
  completed: boolean;
  createdAt: string;
}

const Tasks: React.FC = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState<'low' | 'medium' | 'high'>('medium');
  const [editingId, setEditingId] = useState<string | null>(null);

  // Load tasks from localStorage on component mount
  useEffect(() => {
    const savedTasks = localStorage.getItem('tasks');
    if (savedTasks) {
      setTasks(JSON.parse(savedTasks));
    }
  }, []);

  // Save tasks to localStorage whenever tasks change
  useEffect(() => {
    localStorage.setItem('tasks', JSON.stringify(tasks));
  }, [tasks]);

  const addTask = () => {
    if (!title.trim()) return;

    const newTask: Task = {
      id: Date.now().toString(),
      title: title.trim(),
      description: description.trim(),
      priority,
      completed: false,
      createdAt: new Date().toISOString(),
    };

    setTasks([...tasks, newTask]);
    setTitle('');
    setDescription('');
    setPriority('medium');
  };

  const updateTask = (id: string) => {
    const task = tasks.find(t => t.id === id);
    if (!task || !title.trim()) return;

    setTasks(
      tasks.map(t =>
        t.id === id
          ? {
              ...t,
              title: title.trim(),
              description: description.trim(),
              priority,
            }
          : t
      )
    );
    setTitle('');
    setDescription('');
    setPriority('medium');
    setEditingId(null);
  };

  const deleteTask = (id: string) => {
    setTasks(tasks.filter(task => task.id !== id));
  };

  const toggleComplete = (id: string) => {
    setTasks(
      tasks.map(task =>
        task.id === id ? { ...task, completed: !task.completed } : task
      )
    );
  };

  const startEditing = (task: Task) => {
    setEditingId(task.id);
    setTitle(task.title);
    setDescription(task.description);
    setPriority(task.priority);
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'bg-red-500';
      case 'medium':
        return 'bg-yellow-500';
      case 'low':
        return 'bg-green-500';
      default:
        return 'bg-gray-500';
    }
  };

  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold">Tasks</h1>

      <div className="bg-gray-800 rounded-lg p-6 shadow-md">
        <h2 className="text-xl font-semibold mb-4">{editingId ? 'Edit Task' : 'Add New Task'}</h2>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">Title</label>
            <input
              type="text"
              value={title}
              onChange={e => setTitle(e.target.value)}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Task title"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">Description</label>
            <textarea
              value={description}
              onChange={e => setDescription(e.target.value)}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows={3}
              placeholder="Task description"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">Priority</label>
            <select
              value={priority}
              onChange={e => setPriority(e.target.value as 'low' | 'medium' | 'high')}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </select>
          </div>
          <div className="flex space-x-4">
            <button
              onClick={editingId ? () => updateTask(editingId) : addTask}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {editingId ? 'Update' : 'Add'}
            </button>
            {editingId && (
              <button
                onClick={() => {
                  setEditingId(null);
                  setTitle('');
                  setDescription('');
                  setPriority('medium');
                }}
                className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500"
              >
                Cancel
              </button>
            )}
          </div>
        </div>
      </div>

      <div className="bg-gray-800 rounded-lg p-6 shadow-md">
        <h2 className="text-xl font-semibold mb-4">Task List</h2>
        {tasks.length === 0 ? (
          <p className="text-gray-400">No tasks yet. Add one above!</p>
        ) : (
          <ul className="space-y-4">
            {tasks.map(task => (
              <li
                key={task.id}
                className="bg-gray-700 rounded-md p-4 flex flex-col md:flex-row md:items-center justify-between gap-4"
              >
                <div className="flex-1">
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      checked={task.completed}
                      onChange={() => toggleComplete(task.id)}
                      className="h-5 w-5 text-blue-600 rounded focus:ring-blue-500"
                    />
                    <h3
                      className={`ml-3 text-lg font-medium ${
                        task.completed ? 'line-through text-gray-500' : 'text-white'
                      }`}
                    >
                      {task.title}
                    </h3>
                  </div>
                  <p className={`mt-1 text-gray-400 ${task.completed ? 'text-gray-600' : ''}`}>
                    {task.description}
                  </p>
                  <div className="flex items-center mt-2">
                    <span
                      className={`inline-block px-2 py-1 text-xs rounded-full text-white ${getPriorityColor(task.priority)}`}
                    >
                      {task.priority.charAt(0).toUpperCase() + task.priority.slice(1)}
                    </span>
                    <span className="ml-3 text-gray-500 text-sm">
                      {new Date(task.createdAt).toLocaleDateString()}
                    </span>
                  </div>
                </div>
                <div className="flex space-x-2">
                  <button
                    onClick={() => startEditing(task)}
                    className="px-3 py-1 bg-yellow-600 text-white rounded-md hover:bg-yellow-700 focus:outline-none focus:ring-2 focus:ring-yellow-500 text-sm"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => deleteTask(task.id)}
                    className="px-3 py-1 bg-red-600 text-white rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 text-sm"
                  >
                    Delete
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

export default Tasks;