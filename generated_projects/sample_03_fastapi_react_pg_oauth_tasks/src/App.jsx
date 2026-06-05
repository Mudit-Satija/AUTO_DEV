import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';
import Dashboard from './pages/Dashboard';
import Login from './pages/Login';
import Teams from './pages/Teams';

function App() {
  return (
    <Router>
      <div className="app">
        <nav>
          <h1>Project Dashboard</h1>
          <div>
            <a href="/">Dashboard</a>
            <a href="/teams">Teams</a>
            <a href="/login">Login</a>
          </div>
        </nav>
        <main>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/teams" element={<Teams />} />
            <Route path="/login" element={<Login />} />
          </Routes>
        </main>
        <footer className="footer">
          &copy; {new Date().getFullYear()} Project Dashboard
        </footer>
      </div>
    </Router>
  );
}

export default App;