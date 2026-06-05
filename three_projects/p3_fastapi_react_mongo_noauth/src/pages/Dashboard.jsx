import React, { useEffect, useState } from 'react';
import api from '../services/api';

const Dashboard = () => {
  const [stats, setStats] = useState({ tasks: 0, notes: 0 });

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const [tasksRes, notesRes] = await Promise.all([
          api.get('/tasks'),
          api.get('/notes')
        ]);
        setStats({
          tasks: tasksRes.data.length,
          notes: notesRes.data.length
        });
      } catch (error) {
        console.error('Failed to fetch stats:', error);
      }
    };

    fetchStats();
  }, []);

  return (
    <div>
      <h1>Dashboard</h1>
      <div style={{ display: 'flex', gap: '2rem', marginTop: '2rem' }}>
        <div style={{ padding: '1rem', border: '1px solid #ddd', borderRadius: '8px', textAlign: 'center' }}>
          <h2>{stats.tasks}</h2>
          <p>Tasks</p>
        </div>
        <div style={{ padding: '1rem', border: '1px solid #ddd', borderRadius: '8px', textAlign: 'center' }}>
          <h2>{stats.notes}</h2>
          <p>Notes</p>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;