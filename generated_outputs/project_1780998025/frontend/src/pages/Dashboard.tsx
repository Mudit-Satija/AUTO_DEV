import { useState, useEffect } from 'react';

interface Task {
  id: string;
  title: string;
  description: string;
  priority: 'low' | 'medium' | 'high';
  completed: boolean;
  createdAt: string;
}

export default function Dashboard() {
  const [tasks, setTasks] = useState<Task[]>([]);
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

  const totalTasks = tasks.length;
  const completedTasks = tasks.filter(t => t.completed).length;
  const completionRate = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;
  const highPriority = tasks.filter(t => t.priority === 'high').length;
  const mediumPriority = tasks.filter(t => t.priority === 'medium').length;
  const lowPriority = tasks.filter(t => t.priority === 'low').length;

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-700 rounded w-1/4"></div>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {[1,2,3,4].map(i => (
              <div key={i} className="h-32 bg-gray-700 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-gray-800 p-6 rounded-lg shadow-md">
          <h2 className="text-lg font-medium text-gray-400">Total Tasks</h2>
          <p className="text-3xl font-bold">{totalTasks}</p>
        </div>
        <div className="bg-gray-800 p-6 rounded-lg shadow-md">
          <h2 className="text-lg font-medium text-gray-400">Completed</h2>
          <p className="text-3xl font-bold">{completedTasks}</p>
        </div>
        <div className="bg-gray-800 p-6 rounded-lg shadow-md">
          <h2 className="text-lg font-medium text-gray-400">Completion Rate</h2>
          <p className="text-3xl font-bold">{completionRate}%</p>
        </div>
        <div className="bg-gray-800 p-6 rounded-lg shadow-md">
          <h2 className="text-lg font-medium text-gray-400">High Priority</h2>
          <p className="text-3xl font-bold">{highPriority}</p>
        </div>
      </div>

      <div className="bg-gray-800 p-6 rounded-lg shadow-md mb-8">
        <h2 className="text-2xl font-bold mb-4">Priority Overview</h2>
        <div className="flex flex-col space-y-3">
          <div className="flex justify-between">
            <span className="text-gray-300">High Priority</span>
            <span className="font-medium">{highPriority}</span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-2.5">
            <div 
              className="bg-red-500 h-2.5 rounded-full" 
              style={{ width: `${highPriority > 0 ? (highPriority / totalTasks) * 100 : 0}%` }}
            ></div>
          </div>
          
          <div className="flex justify-between">
            <span className="text-gray-300">Medium Priority</span>
            <span className="font-medium">{mediumPriority}</span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-2.5">
            <div 
              className="bg-yellow-500 h-2.5 rounded-full" 
              style={{ width: `${mediumPriority > 0 ? (mediumPriority / totalTasks) * 100 : 0}%` }}
            ></div>
          </div>
          
          <div className="flex justify-between">
            <span className="text-gray-300">Low Priority</span>
            <span className="font-medium">{lowPriority}</span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-2.5">
            <div 
              className="bg-green-500 h-2.5 rounded-full" 
              style={{ width: `${lowPriority > 0 ? (lowPriority / totalTasks) * 100 : 0}%` }}
            ></div>
          </div>
        </div>
      </div>

      <div className="bg-gray-800 p-6 rounded-lg shadow-md">
        <h2 className="text-2xl font-bold mb-4">Recent Tasks</h2>
        <div className="space-y-3">
          {tasks.slice(0, 5).map(task => (
            <div 
              key={task.id} 
              className={`flex justify-between items-center p-3 rounded ${task.completed ? 'bg-gray-700' : 'bg-gray-800'}`}
            >
              <div>
                <h3 className="font-medium">{task.title}</h3>
                <p className="text-sm text-gray-400">{task.description}</p>
              </div>
              <div className="flex items-center space-x-4">
                <span className={`text-xs px-2 py-1 rounded ${
                  task.priority === 'high' ? 'bg-red-600' : 
                  task.priority === 'medium' ? 'bg-yellow-600' : 'bg-green-600'
                }`}>
                  {task.priority}
                </span>
                <span className={`text-xs px-2 py-1 rounded ${
                  task.completed ? 'bg-green-600' : 'bg-gray-600'
                }`}>
                  {task.completed ? 'Completed' : 'Pending'}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}