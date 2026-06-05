import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import Tasks from './pages/Tasks';
import Notes from './pages/Notes';
import './App.css';

function App() {
  return (
    <Router>
      <div className="app">
        <nav className="navbar">
          <a href="/">Dashboard</a>
          <a href="/tasks">Tasks</a>
          <a href="/notes">Notes</a>
        </nav>
        <main className="content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/tasks" element={<Tasks />} />
            <Route path="/notes" element={<Notes />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;