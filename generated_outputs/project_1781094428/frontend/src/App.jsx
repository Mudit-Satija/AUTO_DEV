import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import './App.css';
import Products from './pages/Products';
import Orders from './pages/Orders';
import Dashboard from './pages/Dashboard';

function App() {
  return (
    <Router>
      <div className="app-wrapper">
        <nav className="navbar">
          <div className="navbar-brand">ShopManager</div>
          <div className="nav-links">
            <Link to="/" className="nav-link active">Dashboard</Link>
            <Link to="/products" className="nav-link">Products</Link>
            <Link to="/orders" className="nav-link">Orders</Link>
          </div>
        </nav>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/products" element={<Products />} />
          <Route path="/orders" element={<Orders />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;