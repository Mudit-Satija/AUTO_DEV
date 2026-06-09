import React, { useState, useEffect } from 'react';

interface Task {
  id: string;
  title: string;
  description: string;
  priority: 'high' | 'medium' | 'low';
  completed: boolean;
  createdAt: string;
}

const Tasks: React.FC = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState<'high' | 'medium' | 'low'>('medium');
  const [editingId, setEditingId] = useState<string | null>(null);

  useEffect(() => {
    const storedTasks = localStorage.getItem('tasks');
    if (storedTasks) {
      setTasks(JSON.parse(storedTasks));
    }
  }, []);

  useEffect(() => {
    localStorage.setItem('tasks', JSON.stringify(tasks));
  }, [tasks]);

  const addTask = (e: React.FormEvent) => {
    e.preventDefault();
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

  const updateTask = (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim() || !editingId) return;

    setTasks(
      tasks.map((task) =>
        task.id === editingId
          ? {
              ...task,
              title: title.trim(),
              description: description.trim(),
              priority,
            }
          : task
      )
    );

    setTitle('');
    setDescription('');
    setPriority('medium');
    setEditingId(null);
  };

  const deleteTask = (id: string) => {
    setTasks(tasks.filter((task) => task.id !== id));
  };

  const toggleComplete = (id: string) => {
    setTasks(
      tasks.map((task) =>
        task.id === id ? { ...task, completed: !task.completed } : task
      )
    );
  };

  const editTask = (task: Task) => {
    setTitle(task.title);
    setDescription(task.description);
    setPriority(task.priority);
    setEditingId(task.id);
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
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-8">Tasks</h1>

      <form onSubmit={editingId ? updateTask : addTask} className="mb-8 bg-gray-800 p-6 rounded-lg shadow-lg">
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-300 mb-1">Title</label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Enter task title"
            required
          />
        </div>
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-300 mb-1">Description</label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Enter task description"
            rows={3}
          />
        </div>
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-300 mb-1">Priority</label>
          <select
            value={priority}
            onChange={(e) => setPriority(e.target.value as 'high' | 'medium' | 'low')}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
        </div>
        <button
          type="submit"
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          {editingId ? 'Update Task' : 'Add Task'}
        </button>
        {editingId && (
          <button
            type="button"
            onClick={() => {
              setTitle('');
              setDescription('');
              setPriority('medium');
              setEditingId(null);
            }}
            className="ml-2 px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500"
          >
            Cancel
          </button>
        )}
      </form>

      <div className="space-y-4">
        {tasks.length === 0 ? (
          <p className="text-gray-400">No tasks yet. Add one above!</p>
        ) : (
          tasks.map((task) => (
            <div
              key={task.id}
              className={`flex items-center p-4 bg-gray-800 rounded-lg shadow-md ${
                task.completed ? 'opacity-70' : ''
              }`}
            >
              <input
                type="checkbox"
                checked={task.completed}
                onChange={() => toggleComplete(task.id)}
                className="h-5 w-5 text-blue-600 rounded focus:ring-blue-500"
              />
              <div className="ml-4 flex-1">
                <h3 className={`font-medium ${task.completed ? 'line-through text-gray-500' : 'text-white'}`}>
                  {task.title}
                </h3>
                {task.description && (
                  <p className="text-gray-400 text-sm mt-1">{task.description}</p>
                )}
                <div className="flex items-center mt-2">
                  <span
                    className={`inline-block w-3 h-3 rounded-full mr-2 ${getPriorityColor(task.priority)}`}
                  ></span>
                  <span className="text-xs text-gray-400 capitalize">{task.priority}</span>
                  <span className="text-xs text-gray-500 ml-4">
                    {new Date(task.createdAt).toLocaleDateString()}
                  </span>
                </div>
              </div>
              <div className="flex space-x-2">
                <button
                  onClick={() => editTask(task)}
                  className="px-3 py-1 bg-yellow-600 text-white text-sm rounded hover:bg-yellow-700 focus:outline-none focus:ring-2 focus:ring-yellow-500"
                >
                  Edit
                </button>
                <button
                  onClick={() => deleteTask(task.id)}
                  className="px-3 py-1 bg-red-600 text-white text-sm rounded hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500"
                >
                  Delete
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default Tasks;