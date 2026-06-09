import { BrowserRouter } from 'react-router-dom';
import './App.css';

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-900 text-gray-100">
        <main className="container mx-auto px-4 py-8">
          <div className="max-w-6xl mx-auto">
            <div className="mb-8">
              <h1 className="text-3xl font-bold text-white">TaskFlow</h1>
              <p className="text-gray-300">Manage your tasks efficiently</p>
            </div>
          </div>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;