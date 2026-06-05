import React, { useState, useEffect } from 'react';
import api from '../services/api';

const Dashboard = () => {
  const [data, setData] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await api.get('/api/posts');
        setData(response.data);
      } catch (error) {
        console.error('Error fetching posts:', error);
      }
    };

    fetchData();
  }, []);

  return (
    <div>
      <h1>Dashboard</h1>
      <p>Total Posts: {data.length}</p>
      <ul>
        {data.map(post => (
          <li key={post._id}>{post.title}</li>
        ))}
      </ul>
    </div>
  );
};

export default Dashboard;