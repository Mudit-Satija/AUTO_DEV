import api from '../services/api.js';
import { useEffect, useState } from 'react';

export default function Dashboard() {
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
      <p>Welcome to the dashboard.</p>
      <h2>Posts</h2>
      <ul>
        {data.map(post => (
          <li key={post._id}>{post.title}</li>
        ))}
      </ul>
    </div>
  );
}