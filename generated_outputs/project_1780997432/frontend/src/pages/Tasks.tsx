import React, { useState } from 'react';

interface Task {
  id: string;
  title: string;
  description: string;
  priority: 'high' | 'medium' | 'low';
  completed: boolean;
  createdAt: string;
}

const Tasks: React.FC = () => {
  const [tasks, setTasks] = useState<Task[]>([
    {
      id: '1',
      title: 'Complete project proposal',
      description: 'Draft and submit the Q3 project proposal',
      priority: 'high',
      completed: false,
      createdAt: '2024-01-15',
    },
    {
      id: '2',
      title: 'Review design mockups',
      description: 'Provide feedback on the new UI designs',
      priority: 'medium',
      completed: true,
      createdAt: '2024-01-14',
    },
  ]);

  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState<'high' | 'medium' | 'low'>('medium');
  const [editingId, setEditingId] = useState<string | null>(null);

  const addTask = () => {
    if (!title.trim()) return;
    
    const newTask: Task = {
      id: Date.now().toString(),
      title: title.trim(),
      description: description.trim(),
      priority,
      completed: false,
      createdAt: new Date().toISOString().split('T')[0],
    };
    
    setTasks([...tasks, newTask]);
    setTitle('');
    setDescription('');
    setPriority('medium');
  };

  const updateTask = (id: string) => {
    const task = tasks.find(t => t.id === id);
    if (!task || !title.trim()) return;
    
    setTasks(tasks.map(t => 
      t.id === id 
        ? { ...t, title: title.trim(), description: description.trim(), priority } 
        : t
    ));
    
    setTitle('');
    setDescription('');
    setPriority('medium');
    setEditingId(null);
  };

  const deleteTask = (id: string) => {
    setTasks(tasks.filter(t => t.id !== id));
  };

  const toggleComplete = (id: string) => {
    setTasks(tasks.map(t => 
      t.id === id ? { ...t, completed: !t.completed } : t
    ));
  };

  const startEdit = (task: Task) => {
    setTitle(task.title);
    setDescription(task.description);
    setPriority(task.priority);
    setEditingId(task.id);
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'text-red-400 bg-red-900/30 border-red-500';
      case 'medium': return 'text-yellow-400 bg-yellow-900/30 border-yellow-500';
      case 'low': return 'text-green-400 bg-green-900/30 border-green-500';
      default: return 'text-gray-400 bg-gray-800/50 border-gray-600';
    }
  };

  return (
    <div className="space-y-8">
      <h2 className="text-2xl font-bold text-white">Tasks</h2>

      <div className="bg-gray-800 p-6 rounded-lg shadow-md">
        <h3 className="text-lg font-semibold text-white mb-4">
          {editingId ? 'Edit Task' : 'Add New Task'}
        </h3>
        
        <div className="space-y-4">
          <div>
            <label className="block text-gray-300 mb-1">Title</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter task title"
            />
          </div>
          
          <div>
            <label className="block text-gray-300 mb-1">Description</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows={3}
              placeholder="Enter task description"
            />
          </div>
          
          <div>
            <label className="block text-gray-300 mb-1">Priority</label>
            <select
              value={priority}
              onChange={(e) => setPriority(e.target.value as 'high' | 'medium' | 'low')}
              className="px-4 py-2 bg-gray-700 border border-gray-600 rounded text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </select>
          </div>
          
          <div className="flex gap-3">
            <button
              onClick={editingId ? () => updateTask(editingId) : addTask}
              className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
            >
              {editingId ? 'Update' : 'Add Task'}
            </button>
            
            {editingId && (
              <button
                onClick={() => {
                  setTitle('');
                  setDescription('');
                  setPriority('medium');
                  setEditingId(null);
                }}
                className="px-6 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 transition-colors"
              >
                Cancel
              </button>
            )}
          </div>
        </div>
      </div>

      <div className="bg-gray-800 p-6 rounded-lg shadow-md">
        <h3 className="text-lg font-semibold text-white mb-4">Task List</h3>
        
        {tasks.length === 0 ? (
          <p className="text-gray-400">No tasks yet. Add one above!</p>
        ) : (
          <ul className="space-y-4">
            {tasks.map(task => (
              <li 
                key={task.id} 
                className={`p-4 rounded-lg border transition-all ${
                  task.completed 
                    ? 'bg-gray-700/50 border-gray-600 opacity-70' 
                    : 'bg-gray-700 border-gray-600 hover:border-gray-500'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <input
                        type="checkbox"
                        checked={task.completed}
                        onChange={() => toggleComplete(task.id)}
                        className="h-5 w-5 text-blue-500 rounded focus:ring-blue-500"
                      />
                      <h4 className={`text-lg font-medium ${
                        task.completed ? 'line-through text-gray-500' : 'text-white'
                      }`}>
                        {task.title}
                      </h4>
                    </div>
                    
                    {task.description && (
                      <p className="text-gray-300 mb-3">{task.description}</p>
                    )}
                    
                    <div className="flex items-center gap-4 text-sm">
                      <span className={`px-2 py-1 rounded-full text-xs border ${getPriorityColor(task.priority)}`}>
                        {task.priority.charAt(0).toUpperCase() + task.priority.slice(1)}
                      </span>
                      <span className="text-gray-400">{task.createdAt}</span>
                    </div>
                  </div>
                  
                  <div className="flex gap-2 ml-4">
                    <button
                      onClick={() => startEdit(task)}
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