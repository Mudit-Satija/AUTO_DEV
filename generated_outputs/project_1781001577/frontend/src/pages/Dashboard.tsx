import { useEffect, useState } from 'react';

const Dashboard = () => {
  const [tasks, setTasks] = useState<Task[]>([]);

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

  const totalTasks = tasks.length;
  const completedTasks = tasks.filter(task => task.completed).length;
  const pendingTasks = totalTasks - completedTasks;
  const highPriorityTasks = tasks.filter(task => task.priority === 'high').length;
  const mediumPriorityTasks = tasks.filter(task => task.priority === 'medium').length;
  const lowPriorityTasks = tasks.filter(task => task.priority === 'low').length;
  const completionRate = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;

  if (totalTasks === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-center p-8">
        <div className="mb-6 text-gray-400">
          <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
          </svg>
        </div>
        <h2 className="text-2xl font-bold text-gray-200 mb-2">No tasks yet</h2>
        <p className="text-gray-400 mb-6">Get started by adding your first task.</p>
        <a href="/tasks" className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-6 rounded-lg transition-colors">
          Add Tasks
        </a>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold text-white">Dashboard</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-gray-800 rounded-lg p-6 shadow-lg border border-gray-700">
          <h2 className="text-gray-400 text-sm font-medium">Total Tasks</h2>
          <p className="text-3xl font-bold text-white mt-2">{totalTasks}</p>
        </div>

        <div className="bg-gray-800 rounded-lg p-6 shadow-lg border border-gray-700">
          <h2 className="text-gray-400 text-sm font-medium">Completed</h2>
          <p className="text-3xl font-bold text-green-400 mt-2">{completedTasks}</p>
        </div>

        <div className="bg-gray-800 rounded-lg p-6 shadow-lg border border-gray-700">
          <h2 className="text-gray-400 text-sm font-medium">Pending</h2>
          <p className="text-3xl font-bold text-red-400 mt-2">{pendingTasks}</p>
        </div>

        <div className="bg-gray-800 rounded-lg p-6 shadow-lg border border-gray-700">
          <h2 className="text-gray-400 text-sm font-medium">Completion Rate</h2>
          <p className="text-3xl font-bold text-blue-400 mt-2">{completionRate}%</p>
        </div>
      </div>

      <div className="bg-gray-800 rounded-lg p-6 shadow-lg border border-gray-700">
        <h2 className="text-2xl font-bold text-white mb-6">Priority Overview</h2>
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <span className="text-gray-300">High Priority</span>
            <div className="flex items-center space-x-2">
              <span className="text-white font-medium">{highPriorityTasks}</span>
              <div className="w-32 bg-gray-700 rounded-full h-2">
                <div 
                  className="bg-red-500 h-2 rounded-full transition-all duration-500" 
                  style={{ width: `${totalTasks > 0 ? (highPriorityTasks / totalTasks) * 100 : 0}%` }}
                ></div>
              </div>
            </div>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-gray-300">Medium Priority</span>
            <div className="flex items-center space-x-2">
              <span className="text-white font-medium">{mediumPriorityTasks}</span>
              <div className="w-32 bg-gray-700 rounded-full h-2">
                <div 
                  className="bg-yellow-500 h-2 rounded-full transition-all duration-500" 
                  style={{ width: `${totalTasks > 0 ? (mediumPriorityTasks / totalTasks) * 100 : 0}%` }}
                ></div>
              </div>
            </div>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-gray-300">Low Priority</span>
            <div className="flex items-center space-x-2">
              <span className="text-white font-medium">{lowPriorityTasks}</span>
              <div className="w-32 bg-gray-700 rounded-full h-2">
                <div 
                  className="bg-green-500 h-2 rounded-full transition-all duration-500" 
                  style={{ width: `${totalTasks > 0 ? (lowPriorityTasks / totalTasks) * 100 : 0}%` }}
                ></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;