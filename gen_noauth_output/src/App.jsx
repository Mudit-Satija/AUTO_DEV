import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import Posts from './pages/Posts';
import './App.css';

function App() {
  return (
    <Router>
      <nav>
        <a href="/">Dashboard</a>
        <a href="/posts">Posts</a>
      </nav>
      <div className="content">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/posts" element={<Posts />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;