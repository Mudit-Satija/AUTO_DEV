import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import Posts from './pages/Posts';
import Inventory from './pages/Inventory';
import './App.css';

function App() {
  return (
    <Router>
      <div className="app">
        <nav className="navbar">
          <h1>Project Dashboard</h1>
          <div>
            <a href="/">Dashboard</a>
            <a href="/posts">Posts</a>
            <a href="/inventory">Inventory</a>
          </div>
        </nav>
        <main className="content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/posts" element={<Posts />} />
            <Route path="/inventory" element={<Inventory />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;