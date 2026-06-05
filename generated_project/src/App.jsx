import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './pages/Dashboard.jsx';
import Tasks from './pages/Tasks.jsx';
import './App.css';

function App() {
  return (
    <Router>
      <div className="app">
        <nav className="navbar">
          <h1>Task Management</h1>
          <div>
            <a href="/">Dashboard</a>
            <a href="/tasks">Tasks</a>
          </div>
        </nav>
        <main className="content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/tasks" element={<Tasks />} />
          </Routes>
        </main>
        <footer className="footer">
          <p>&copy; 2024 Task Management App</p>
        </footer>
      </div>
    </Router>
  );
}

export default App;