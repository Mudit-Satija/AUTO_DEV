import React, { useEffect, useState } from 'react';
import api from '../services/api';

const Tasks = () => {
  const [tasks, setTasks] = useState([]);

  useEffect(() => {
    const fetchTasks = async () => {
      try {
        const response = await api.get('/tasks');
        setTasks(response.data);
      } catch (error) {
        console.error('Failed to fetch tasks:', error);
      }
    };

    fetchTasks();
  }, []);

  return (
    <div>
      <h1>Tasks</h1>
      {tasks.length === 0 ? (
        <p>No tasks available.</p>
      ) : (
        <ul style={{ listStyle: 'none', padding: 0 }}>
          {tasks.map(task => (
            <li key={task._id} style={{ margin: '1rem 0', padding: '1rem', border: '1px solid #ddd', borderRadius: '8px' }}>
              <h3>{task.title}</h3>
              <p>{task.description}</p>
              <small>Completed: {task.completed ? 'Yes' : 'No'}</small>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default Tasks;