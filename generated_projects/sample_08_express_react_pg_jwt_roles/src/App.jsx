import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import Admin from './pages/Admin';
import Login from './pages/Login';
import './App.css';

function App() {
  return (
    <Router>
      <div className="app">
        <nav className="navbar">
          <h1>Project Management</h1>
          <div>
            <a href="/">Dashboard</a>
            <a href="/admin">Admin</a>
            <a href="/login">Login</a>
          </div>
        </nav>
        <main className="container">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/admin" element={<Admin />} />
            <Route path="/login" element={<Login />} />
          </Routes>
        </main>
        <footer className="footer">
          <p>&copy; 2024 Project Management App</p>
        </footer>
      </div>
    </Router>
  );
}

export default App;