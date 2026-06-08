import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import Calculator from './pages/Calculator.jsx';

const App = () => {
  return (
    <BrowserRouter>
      <nav style={{ padding: '10px', backgroundColor: '#f0f0f0' }}>
        <Link to="/">Calculator</Link>
      </nav>
      <Routes>
        <Route path="/" element={<Calculator />} />
      </Routes>
    </BrowserRouter>
  );
};

export default App;
