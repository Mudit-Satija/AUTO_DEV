import React, { useEffect, useState } from 'react';
import api from '../services/api';

const Dashboard = () => {
  const [stats, setStats] = useState({ posts: 0, inventory: 0, roles: 0 });

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const [postsRes, inventoryRes, rolesRes] = await Promise.all([
          api.get('/api/posts/count'),
          api.get('/api/inventory/count'),
          api.get('/api/roles/count')
        ]);
        setStats({
          posts: postsRes.data.count,
          inventory: inventoryRes.data.count,
          roles: rolesRes.data.count
        });
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
        <div style={{ border: '1px solid #ccc', padding: '1rem', borderRadius: '8px', textAlign: 'center', flex: 1 }}>
          <h3>Posts</h3>
          <p style={{ fontSize: '2rem', fontWeight: 'bold' }}>{stats.posts}</p>
        </div>
        <div style={{ border: '1px solid #ccc', padding: '1rem', borderRadius: '8px', textAlign: 'center', flex: 1 }}>
          <h3>Inventory Items</h3>
          <p style={{ fontSize: '2rem', fontWeight: 'bold' }}>{stats.inventory}</p>
        </div>
        <div style={{ border: '1px solid #ccc', padding: '1rem', borderRadius: '8px', textAlign: 'center', flex: 1 }}>
          <h3>Roles</h3>
          <p style={{ fontSize: '2rem', fontWeight: 'bold' }}>{stats.roles}</p>
        </div>
      </div>
      <p>Welcome to the dashboard. View and manage your posts, inventory, and roles.</p>
    </div>
  );
};

export default Dashboard;