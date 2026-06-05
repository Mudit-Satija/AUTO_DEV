import React, { useState, useEffect } from 'react';
import api from '../services/api';

const Teams = () => {
  const [teams, setTeams] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchTeams = async () => {
      try {
        const response = await api.get('/teams');
        setTeams(response.data);
      } catch (err) {
        setError('Failed to load teams');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchTeams();
  }, []);

  if (loading) return <p>Loading teams...</p>;
  if (error) return <p style={{ color: 'red' }}>{error}</p>;

  return (
    <div>
      <h2>Teams</h2>
      {teams.length === 0 ? (
        <p>No teams found.</p>
      ) : (
        <ul>
          {teams.map((team) => (
            <li key={team.id} style={{ margin: '1rem 0', padding: '1rem', border: '1px solid #ddd', borderRadius: '4px' }}>
              <strong>{team.name}</strong>
              <p>{team.description}</p>
              <small>Members: {team.member_count}</small>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default Teams;