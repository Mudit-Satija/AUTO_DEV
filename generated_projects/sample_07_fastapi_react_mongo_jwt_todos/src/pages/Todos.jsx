import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

export default function Todos() {
  const [todos, setTodos] = useState([]);
  const [newTodo, setNewTodo] = useState('');
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/');
      return;
    }

    const fetchTodos = async () => {
      try {
        const response = await api.get('/todos');
        setTodos(response.data);
      } catch (err) {
        console.error('Failed to fetch todos:', err);
        localStorage.removeItem('token');
        navigate('/');
      } finally {
        setLoading(false);
      }
    };

    fetchTodos();
  }, [navigate]);

  const handleAddTodo = async () => {
    if (!newTodo.trim()) return;
    try {
      const response = await api.post('/todos', { text: newTodo });
      setTodos([...todos, response.data]);
      setNewTodo('');
    } catch (err) {
      console.error('Failed to add todo:', err);
    }
  };

  const handleToggleTodo = async (id) => {
    try {
      const todo = todos.find(t => t._id === id);
      const response = await api.patch(`/todos/${id}`, { completed: !todo.completed });
      setTodos(todos.map(t => t._id === id ? response.data : t));
    } catch (err) {
      console.error('Failed to update todo:', err);
    }
  };

  const handleDeleteTodo = async (id) => {
    try {
      await api.delete(`/todos/${id}`);
      setTodos(todos.filter(t => t._id !== id));
    } catch (err) {
      console.error('Failed to delete todo:', err);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/');
  };

  if (loading) {
    return <div style={{ textAlign: 'center', padding: '50px' }}>Loading...</div>;
  }

  return (
    <div style={{ padding: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h2>My Todos</h2>
        <button onClick={handleLogout} className="danger">Logout</button>
      </div>
      <div style={{ display: 'flex', marginBottom: '20px' }}>
        <input
          type="text"
          placeholder="Add a new todo..."
          value={newTodo}
          onChange={(e) => setNewTodo(e.target.value)}
          style={{ flex: 1, padding: '10px', marginRight: '10px' }}
        />
        <button onClick={handleAddTodo} className="primary">Add</button>
      </div>
      <div>
        {todos.length === 0 ? (
          <p style={{ textAlign: 'center', color: '#7f8c8d' }}>No todos yet. Add one above!</p>
        ) : (
          todos.map((todo) => (
            <div
              key={todo._id}
              className={`list-item ${todo.completed ? 'completed' : ''}`}
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                padding: '15px',
                margin: '10px 0',
                backgroundColor: '#f9f9f9',
                borderRadius: '4px',
                borderLeft: `4px solid ${todo.completed ? '#95a5a6' : '#3498db'}`
              }}
            >
              <span style={{ flex: 1, cursor: 'pointer' }} onClick={() => handleToggleTodo(todo._id)}>
                {todo.text}
              </span>
              <button onClick={() => handleDeleteTodo(todo._id)} className="danger" style={{ marginLeft: '10px' }}>
                Delete
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );
}