import { useEffect, useState } from 'react';

const Tasks = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState<'low' | 'medium' | 'high'>('medium');
  const [editingId, setEditingId] = useState<string | null>(null);

  interface Task {
    id: string;
    title: string;
    description?: string;
    priority: 'low' | 'medium' | 'high';
    completed: boolean;
    createdAt: string;
  }

  useEffect(() => {
    const storedTasks = localStorage.getItem('tasks');
    if (storedTasks) {
      setTasks(JSON.parse(storedTasks));
    }
  }, []);

  const saveTask = () => {
    if (!title.trim()) return;

    const newTask: Task = {
      id: editingId || Date.now().toString(),
      title: title.trim(),
      description: description.trim() || undefined,
      priority,
      completed: false,
      createdAt: new Date().toISOString(),
    };

    if (editingId) {
      setTasks(tasks.map(task => (task.id === editingId ? newTask : task)));
      setEditingId(null);
    } else {
      setTasks([...tasks, newTask]);
    }

    setTitle('');
    setDescription('');
    setPriority('medium');
    localStorage.setItem('tasks', JSON.stringify([...tasks, newTask]));
  };

  const deleteTask = (id: string) => {
    setTasks(tasks.filter(task => task.id !== id));
    localStorage.setItem('tasks', JSON.stringify(tasks.filter(task => task.id !== id)));
  };

  const toggleComplete = (id: string) => {
    setTasks(tasks.map(task =>
      task.id === id ? { ...task, completed: !task.completed } : task
    ));
    localStorage.setItem('tasks', JSON.stringify(tasks.map(task =>
      task.id === id ? { ...task, completed: !task.completed } : task
    )));
  };

  const startEdit = (task: Task) => {
    setEditingId(task.id);
    setTitle(task.title);
    setDescription(task.description || '');
    setPriority(task.priority);
  };

  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold text-white">Manage Tasks</h1>

      <div className="bg-gray-800 rounded-lg p-6 shadow-lg border border-gray-700">
        <h2 className="text-xl font-semibold text-white mb-4">
          {editingId ? 'Edit Task' : 'Add New Task'}
        </h2>
        <div className="space-y-4">
          <input
            type="text"
            placeholder="Task title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <textarea
            placeholder="Description (optional)"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
            rows={3}
          />
          <div className="flex items-center space-x-4">
            <label className="text-gray-300">Priority:</label>
            <select
              value={priority}
              onChange={(e) => setPriority(e.target.value as 'low' | 'medium' | 'high')}
              className="px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </select>
          </div>
          <div className="flex space-x-3">
            <button
              onClick={saveTask}
              className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-6 rounded-lg transition-colors"
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
                className="bg-gray-600 hover:bg-gray-700 text-white font-medium py-2 px-6 rounded-lg transition-colors"
              >
                Cancel
              </button>
            )}
          </div>
        </div>
      </div>

      <div className="bg-gray-800 rounded-lg p-6 shadow-lg border border-gray-700">
        <h2 className="text-xl font-semibold text-white mb-4">Task List</h2>
        {tasks.length === 0 ? (
          <div className="text-center py-12 text-gray-400">
            <p>No tasks yet. Add one above!</p>
          </div>
        ) : (
          <ul className="space-y-3">
            {tasks.map(task => (
              <li
                key={task.id}
                className={`flex items-center justify-between p-4 bg-gray-700 rounded-lg border border-gray-600 ${
                  task.completed ? 'opacity-70' : ''
                }`}
              >
                <div className="flex items-center space-x-4 flex-grow">
                  <input
                    type="checkbox"
                    checked={task.completed}
                    onChange={() => toggleComplete(task.id)}
                    className="w-5 h-5 text-blue-600 rounded focus:ring-blue-500"
                  />
                  <div className="flex-1">
                    <h3 className={`font-medium ${task.completed ? 'line-through text-gray-500' : 'text-white'}`}>
                      {task.title}
                    </h3>
                    {task.description && (
                      <p className="text-gray-400 text-sm mt-1">{task.description}</p>
                    )}
                    <span className={`inline-block px-2 py-1 text-xs rounded-full mt-2 ${
                      task.priority === 'high' ? 'bg-red-500 text-white' :
                      task.priority === 'medium' ? 'bg-yellow-500 text-white' :
                      'bg-green-500 text-white'
                    }`}>
                      {task.priority.charAt(0).toUpperCase() + task.priority.slice(1)}
                    </span>
                  </div>
                </div>
                <div className="flex space-x-2">
                  <button
                    onClick={() => startEdit(task)}
                    className="text-blue-400 hover:text-blue-300 font-medium transition-colors"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => deleteTask(task.id)}
                    className="text-red-400 hover:text-red-300 font-medium transition-colors"
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