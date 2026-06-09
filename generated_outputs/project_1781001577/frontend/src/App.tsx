import './App.css';
import Dashboard from './pages/Dashboard';
import Tasks from './pages/Tasks';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';

function App() {
  return (
    <Router>
      <div className="flex flex-col h-screen">
        <header className="bg-gray-800 shadow-md">
          <nav className="container mx-auto px-4 py-3 flex space-x-6">
            <Link to="/" className="text-blue-400 hover:text-blue-300 font-medium transition-colors">
              Dashboard
            </Link>
            <Link to="/tasks" className="text-gray-300 hover:text-white font-medium transition-colors">
              Tasks
            </Link>
          </nav>
        </header>
        <main className="flex-grow container mx-auto px-4 py-6 overflow-auto">
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