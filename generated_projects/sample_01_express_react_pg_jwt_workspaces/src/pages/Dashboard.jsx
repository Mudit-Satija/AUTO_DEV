import React, { useEffect, useState } from 'react';
import api from '../services/api';

const Dashboard = () => {
  const [workspaces, setWorkspaces] = useState([]);
  const [projects, setProjects] = useState([]);
  const [tasks, setTasks] = useState([]);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const [workspacesRes, projectsRes, tasksRes] = await Promise.all([
          api.get('/api/workspaces'),
          api.get('/api/projects'),
          api.get('/api/tasks')
        ]);
        setWorkspaces(workspacesRes.data);
        setProjects(projectsRes.data);
        setTasks(tasksRes.data);
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error);
      }
    };

    fetchDashboardData();
  }, []);

  return (
    <div>
      <h2>Dashboard</h2>
      <p>Workspaces: {workspaces.length}</p>
      <p>Projects: {projects.length}</p>
      <p>Tasks: {tasks.length}</p>
    </div>
  );
};

export default Dashboard;