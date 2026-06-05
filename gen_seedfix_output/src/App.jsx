import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Dashboard from './pages/Dashboard.jsx';
import Posts from './pages/Posts.jsx';
import './App.css';

function App() {
  return (
    <BrowserRouter>
      <nav>
        <a href="/">Dashboard</a>
        <a href="/posts">Posts</a>
      </nav>
      <div className="container">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/posts" element={<Posts />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;