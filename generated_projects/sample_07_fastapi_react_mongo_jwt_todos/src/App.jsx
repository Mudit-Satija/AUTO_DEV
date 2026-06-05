import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Login from './pages/Login';
import Todos from './pages/Todos';
import './App.css';

function App() {
  return (
    <Router>
      <div className="app">
        <header className="header">
          <h1>Todo App</h1>
          <nav className="nav-links">
            <a href="/">Login</a>
            <a href="/todos">Todos</a>
          </nav>
        </header>
        <main className="container">
          <Routes>
            <Route path="/" element={<Login />} />
            <Route path="/todos" element={<Todos />} />
          </Routes>
        </main>
        <footer className="footer">
          &copy; {new Date().getFullYear()} Todo App - Powered by FastAPI & React
        </footer>
      </div>
    </Router>
  );
}

export default App;