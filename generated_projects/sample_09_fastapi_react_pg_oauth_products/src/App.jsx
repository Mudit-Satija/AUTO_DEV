import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Products from './pages/Products';
import Cart from './pages/Cart';
import Login from './pages/Login';
import './App.css';

function App() {
  return (
    <Router>
      <div>
        <nav>
          <h1>Product Marketplace</h1>
          <div>
            <a href="/">Products</a>
            <a href="/cart">Cart</a>
            <a href="/login">Login</a>
          </div>
        </nav>
        <div className="container">
          <Routes>
            <Route path="/" element={<Products />} />
            <Route path="/cart" element={<Cart />} />
            <Route path="/login" element={<Login />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;