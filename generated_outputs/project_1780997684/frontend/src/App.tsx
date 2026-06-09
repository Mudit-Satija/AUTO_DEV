import './App.css';
import Dashboard from './pages/Dashboard';
import Tasks from './pages/Tasks';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

function App() {
  return (
    <Router>
      <div className="bg-gray-900 text-white min-h-screen">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/tasks" element={<Tasks />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;