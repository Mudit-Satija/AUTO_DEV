import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';
import Dashboard from './pages/Dashboard';
import Transactions from './pages/Transactions';
import Budgets from './pages/Budgets';
import Reports from './pages/Reports';
import Analytics from './pages/Analytics';

function App() {
  return (
    <Router>
      <div>
        <nav>
          <ul>
            <li><a href="/">Dashboard</a></li>
            <li><a href="/transactions">Transactions</a></li>
            <li><a href="/budgets">Budgets</a></li>
            <li><a href="/reports">Reports</a></li>
            <li><a href="/analytics">Analytics</a></li>
          </ul>
        </nav>
        <main>
          <div className="container">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/transactions" element={<Transactions />} />
              <Route path="/budgets" element={<Budgets />} />
              <Route path="/reports" element={<Reports />} />
              <Route path="/analytics" element={<Analytics />} />
            </Routes>
          </div>
        </main>
      </div>
    </Router>
  );
}

export default App;