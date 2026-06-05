import { useEffect, useState } from 'react';
import api from '../services/api';

const Tasks = () => {
  const [tasks, setTasks] = useState([]);

  useEffect(() => {
    const fetchTasks = async () => {
      try {
        const response = await api.get('/api/tasks');
        setTasks(response.data);
      } catch (error) {
        console.error('Failed to fetch tasks:', error);
      }
    };

    fetchTasks();
  }, []);

  return (
    <div>
      <h2>Tasks</h2>
      {tasks.length === 0 ? (
        <p>No tasks found.</p>
      ) : (
        <ul style={{ listStyle: 'none', padding: 0 }}>
          {tasks.map(task => (
            <li
              key={task._id}
              style={{
                border: '1px solid #ddd',
                padding: '1rem',
                margin: '0.5rem 0',
                borderRadius: '8px',
                backgroundColor: task.completed ? '#e8f5e9' : '#fff'
              }}
            >
              <strong>{task.title}</strong>
              <p>{task.description}</p>
              <small>
                Status: {task.completed ? 'Completed' : 'Pending'} | Created: {new Date(task.createdAt).toLocaleDateString()}
              </small>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default Tasks;