import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';

function ReadingList({ readingEntries, setReadingEntries }) {
  const navigate = useNavigate();
  const [bookId, setBookId] = useState('');
  const [status, setStatus] = useState('');
  const [dateAdded, setDateAdded] = useState('');

  const handleAdd = (e) => {
    e.preventDefault();
    if (!bookId.trim() || !status.trim() || !dateAdded.trim()) return;
    const newReadingEntry = {
      id: crypto.randomUUID(),
      bookId,
      status,
      dateAdded,
    };
    const updated = [...readingEntries, newReadingEntry];
    setReadingEntries(updated);
    localStorage.setItem('readingEntries', JSON.stringify(updated));
    setBookId('');
    setStatus('');
    setDateAdded('');
    navigate('/reading-list');
  };

  const handleDelete = (id) => {
    const updated = readingEntries.filter((entry) => entry.id !== id);
    setReadingEntries(updated);
    localStorage.setItem('readingEntries', JSON.stringify(updated));
  };

  useEffect(() => {
    const storedReadingEntries = localStorage.getItem('readingEntries');
    if (storedReadingEntries) {
      setReadingEntries(JSON.parse(storedReadingEntries));
    }
  }, []);

  useEffect(() => {
    localStorage.setItem('readingEntries', JSON.stringify(readingEntries));
  }, [readingEntries]);

  return (
    <div className="app-wrapper">
      <div className="page-header">
        <h1>Reading List</h1>
      </div>

      <div className="form-card">
        <h2>Add Reading Entry</h2>
        <form onSubmit={handleAdd}>
          <div className="form-group">
            <label className="form-label">Book ID</label>
            <input className="form-input" value={bookId} onChange={(e) => setBookId(e.target.value)} />
          </div>
          <div className="form-group">
            <label className="form-label">Status</label>
            <input className="form-input" value={status} onChange={(e) => setStatus(e.target.value)} />
          </div>
          <div className="form-group">
            <label className="form-label">Date Added</label>
            <input className="form-input" value={dateAdded} onChange={(e) => setDateAdded(e.target.value)} />
          </div>
          <div className="form-actions">
            <button type="submit" className="btn btn-primary">
              Add
            </button>
          </div>
        </form>
      </div>

      <div className="section">
        <h2>All Reading Entries</h2>
        <div className="items-grid">
          {readingEntries.length === 0 ? (
            <div className="empty-state">
              <p>No reading entries yet.</p>
              <Link to="/reading-list" className="btn btn-primary">
                Add your first entry
              </Link>
            </div>
          ) : (
            readingEntries.map((entry) => (
              <div key={entry.id} className="item-card">
                <h3 className="item-title">Book ID: {entry.bookId}</h3>
                <p className="item-details">Status: {entry.status}</p>
                <p className="item-details">Date Added: {entry.dateAdded}</p>
                <div className="item-actions">
                  <button className="btn btn-danger btn-sm" onClick={() => handleDelete(entry.id)}>
                    Delete
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

export default ReadingList;