import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import About from './pages/About';
import Items from './pages/Items';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <nav className="navbar">
          <a href="/">Home</a>
          <a href="/about">About</a>
          <a href="/items">Items</a>
        </nav>
        <main className="container">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/about" element={<About />} />
            <Route path="/items" element={<Items />} />
          </Routes>
        </main>
        <footer className="footer">
          &copy; {new Date().getFullYear()} React App
        </footer>
      </div>
    </Router>
  );
}

export default App;