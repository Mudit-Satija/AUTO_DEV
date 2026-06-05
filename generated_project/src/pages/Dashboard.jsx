import { useEffect, useState } from 'react';
import api from '../services/api';

const Dashboard = () => {
  const [stats, setStats] = useState({ total: 0, completed: 0, pending: 0 });

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await api.get('/api/tasks/stats');
        setStats(response.data);
      } catch (error) {
        console.error('Failed to fetch stats:', error);
      }
    };

    fetchStats();
  }, []);

  return (
    <div>
      <h2>Dashboard</h2>
      <div style={{ display: 'flex', gap: '2rem', margin: '2rem 0' }}>
        <div style={{ border: '1px solid #ccc', padding: '1rem', borderRadius: '8px', width: '150px', textAlign: 'center' }}>
          <h3>Total Tasks</h3>
          <p style={{ fontSize: '2rem', fontWeight: 'bold' }}>{stats.total}</p>
        </div>
        <div style={{ border: '1px solid #ccc', padding: '1rem', borderRadius: '8px', width: '150px', textAlign: 'center' }}>
          <h3>Completed</h3>
          <p style={{ fontSize: '2rem', fontWeight: 'bold', color: 'green' }}>{stats.completed}</p>
        </div>
        <div style={{ border: '1px solid #ccc', padding: '1rem', borderRadius: '8px', width: '150px', textAlign: 'center' }}>
          <h3>Pending</h3>
          <p style={{ fontSize: '2rem', fontWeight: 'bold', color: 'orange' }}>{stats.pending}</p>
        </div>
      </div>
      <p>Welcome to your dashboard. View your task statistics here.</p>
    </div>
  );
};

export default Dashboard;