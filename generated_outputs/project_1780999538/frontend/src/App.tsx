import './App.css';
import Dashboard from './pages/Dashboard';
import Tasks from './pages/Tasks';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-900 text-white">
        <nav className="bg-gray-800 shadow-lg">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex">
                <Link
                  to="/"
                  className="flex items-center px-3 py-2 rounded-md text-sm font-medium text-gray-300 hover:text-white hover:bg-gray-700 mr-2"
                >
                  Dashboard
                </Link>
                <Link
                  to="/tasks"
                  className="flex items-center px-3 py-2 rounded-md text-sm font-medium text-gray-300 hover:text-white hover:bg-gray-700"
                >
                  Tasks
                </Link>
              </div>
            </div>
          </div>
        </nav>

        <main className="p-6">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/tasks" element={<Tasks />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;