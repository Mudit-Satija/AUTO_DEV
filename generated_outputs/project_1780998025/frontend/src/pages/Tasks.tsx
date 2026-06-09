import { useState, useEffect } from 'react';

interface Task {
  id: string;
  title: string;
  description: string;
  priority: 'low' | 'medium' | 'high';
  completed: boolean;
  createdAt: string;
}

export default function Tasks() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState<'low' | 'medium' | 'high'>('medium');
  const [editingId, setEditingId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulate fetching tasks
    const mockTasks: Task[] = [
      { id: '1', title: 'Complete dashboard', description: 'Finish the task dashboard UI', priority: 'high', completed: true, createdAt: '2024-01-15T10:00:00Z' },
      { id: '2', title: 'Review API endpoints', description: 'Ensure all endpoints return correct data', priority: 'medium', completed: false, createdAt: '2024-01-16T14:30:00Z' },
      { id: '3', title: 'Write unit tests', description: 'Cover all components with tests', priority: 'high', completed: false, createdAt: '2024-01-17T09:15:00Z' },
      { id: '4', title: 'Deploy to staging', description: 'Push changes to staging environment', priority: 'low', completed: true, createdAt: '2024-01-18T11:20:00Z' },
    ];
    setTasks(mockTasks);
    setLoading(false);
  }, []);

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
    
    setTasks([newTask, ...tasks]);
    setTitle('');
    setDescription('');
    setPriority('medium');
  };

  const updateTask = () => {
    if (!editingId || !title.trim()) return;
    
    setTasks(tasks.map(task => 
      task.id === editingId 
        ? { ...task, title: title.trim(), description: description.trim(), priority } 
        : task
    ));
    
    setEditingId(null);
    setTitle('');
    setDescription('');
    setPriority('medium');
  };

  const deleteTask = (id: string) => {
    setTasks(tasks.filter(task => task.id !== id));
  };

  const toggleComplete = (id: string) => {
    setTasks(tasks.map(task => 
      task.id === id ? { ...task, completed: !task.completed } : task
    ));
  };

  const startEditing = (task: Task) => {
    setEditingId(task.id);
    setTitle(task.title);
    setDescription(task.description);
    setPriority(task.priority);
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-700 rounded w-1/4"></div>
          <div className="h-12 bg-gray-700 rounded"></div>
          <div className="space-y-3">
            {[1,2,3].map(i => (
              <div key={i} className="h-20 bg-gray-700 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">Tasks</h1>
      
      <div className="bg-gray-800 p-6 rounded-lg shadow-md mb-8">
        <h2 className="text-xl font-semibold mb-4">{editingId ? 'Edit Task' : 'Add New Task'}</h2>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">Title</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Task title"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">Description</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows={3}
              placeholder="Task description"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">Priority</label>
            <select
              value={priority}
              onChange={(e) => setPriority(e.target.value as 'low' | 'medium' | 'high')}
              className="px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </select>
          </div>
          
          <div className="flex space-x-4">
            <button
              onClick={editingId ? updateTask : addTask}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {editingId ? 'Update Task' : 'Add Task'}
            </button>
            
            {editingId && (
              <button
                onClick={() => {
                  setEditingId(null);
                  setTitle('');
                  setDescription('');
                  setPriority('medium');
                }}
                className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500"
              >
                Cancel
              </button>
            )}
          </div>
        </div>
      </div>
      
      <div className="space-y-4">
        {tasks.length === 0 ? (
          <div className="bg-gray-800 p-8 rounded-lg shadow-md text-center">
            <p className="text-gray-400">No tasks yet. Add one above!</p>
          </div>
        ) : (
          tasks.map(task => (
            <div 
              key={task.id} 
              className={`flex items-center justify-between p-4 bg-gray-800 rounded-lg shadow-md ${
                task.completed ? 'opacity-70' : ''
              }`}
            >
              <div className="flex items-center flex-1">
                <input
                  type="checkbox"
                  checked={task.completed}
                  onChange={() => toggleComplete(task.id)}
                  className="h-5 w-5 text-blue-600 rounded focus:ring-blue-500"
                />
                <div className="ml-4">
                  <h3 className={`font-medium ${task.completed ? 'line-through text-gray-500' : 'text-white'}`}>
                    {task.title}
                  </h3>
                  <p className={`text-sm ${task.completed ? 'text-gray-500' : 'text-gray-300'}`}>
                    {task.description}
                  </p>
                  <div className="flex items-center space-x-2 mt-1">
                    <span className={`text-xs px-2 py-1 rounded ${
                      task.priority === 'high' ? 'bg-red-600' : 
                      task.priority === 'medium' ? 'bg-yellow-600' : 'bg-green-600'
                    }`}>
                      {task.priority}
                    </span>
                    <span className="text-xs text-gray-400">
                      {new Date(task.createdAt).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              </div>
              
              <div className="flex space-x-2 ml-4">
                <button
                  onClick={() => startEditing(task)}
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
}