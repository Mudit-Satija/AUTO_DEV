import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Feed from './pages/Feed';
import Login from './pages/Login';
import Profile from './pages/Profile';
import './App.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Feed />} />
        <Route path="/login" element={<Login />} />
        <Route path="/profile" element={<Profile />} />
      </Routes>
    </Router>
  );
}

export default App;