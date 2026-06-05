import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import Orders from './pages/Orders';
import Products from './pages/Products';
import './App.css';

function App() {
  return (
    <Router>
      <div className="app">
        <nav className="navbar">
          <a href="/">Dashboard</a>
          <a href="/orders">Orders</a>
          <a href="/products">Products</a>
        </nav>
        <main className="content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/orders" element={<Orders />} />
            <Route path="/products" element={<Products />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;