import './App.css';
import Dashboard from './pages/Dashboard';
import Tasks from './pages/Tasks';
import { BrowserRouter, Routes, Route } from 'react-router-dom';

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-900 text-gray-100">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/tasks" element={<Tasks />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;