import React, { useEffect, useState } from 'react';
import api from '../services/api';

const Notes = () => {
  const [notes, setNotes] = useState([]);

  useEffect(() => {
    const fetchNotes = async () => {
      try {
        const response = await api.get('/notes');
        setNotes(response.data);
      } catch (error) {
        console.error('Failed to fetch notes:', error);
      }
    };

    fetchNotes();
  }, []);

  return (
    <div>
      <h1>Notes</h1>
      {notes.length === 0 ? (
        <p>No notes available.</p>
      ) : (
        <ul style={{ listStyle: 'none', padding: 0 }}>
          {notes.map(note => (
            <li key={note._id} style={{ margin: '1rem 0', padding: '1rem', border: '1px solid #ddd', borderRadius: '8px' }}>
              <h3>{note.title}</h3>
              <p>{note.content}</p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default Notes;