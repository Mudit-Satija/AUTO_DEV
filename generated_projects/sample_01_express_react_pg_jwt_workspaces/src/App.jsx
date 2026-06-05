import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Login from './pages/Login.jsx';
import Dashboard from './pages/Dashboard.jsx';
import Settings from './pages/Settings.jsx';

function App() {
  return (
    <Router>
      <div className="app">
        <nav>
          <h1>Project Management</h1>
          <div>
            <a href="/">Dashboard</a>
            <a href="/settings">Settings</a>
          </div>
        </nav>
        <div className="container">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/login" element={<Login />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;