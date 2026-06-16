import React, { useState } from 'react';
import { Link } from 'react-router-dom';

function Dashboard({ books, setBooks, readingEntries, setReadingEntries }) {
  const [title, setTitle] = useState('');
  const [author, setAuthor] = useState('');
  const [status, setStatus] = useState('');
  const [dateAdded, setDateAdded] = useState('');

  const handleAddBook = (e) => {
    e.preventDefault();
    if (!title.trim() || !author.trim()) return;
    const updated = [
      ...books,
      { id: crypto.randomUUID(), title: title.trim(), author: author.trim(), genre: '', pages: '', totalPages: '', readingStatus: '', dateAdded: '' },
    ];
    setBooks(updated);
    localStorage.setItem('books', JSON.stringify(updated));
    setTitle('');
    setAuthor('');
  };

  const handleAddReadingEntry = (e) => {
    e.preventDefault();
    if (!status.trim() || !dateAdded.trim()) return;
    const updated = [
      ...readingEntries,
      { id: crypto.randomUUID(), bookId: '', status: status.trim(), dateAdded: dateAdded.trim() },
    ];
    setReadingEntries(updated);
    localStorage.setItem('readingEntries', JSON.stringify(updated));
    setStatus('');
    setDateAdded('');
  };

  return (
    <div className="app-wrapper">
      <div className="page-header">
        <h1>Dashboard</h1>
      </div>

      <div className="form-card">
        <h2>Add Book</h2>
        <form onSubmit={handleAddBook}>
          <div className="form-group">
            <label className="form-label">Title</label>
            <input className="form-input" value={title} onChange={(e) => setTitle(e.target.value)} />
          </div>
          <div className="form-group">
            <label className="form-label">Author</label>
            <input className="form-input" value={author} onChange={(e) => setAuthor(e.target.value)} />
          </div>
          <div className="form-actions">
            <button type="submit" className="btn btn-primary">Add</button>
          </div>
        </form>
      </div>

      <div className="form-card">
        <h2>Add Reading Entry</h2>
        <form onSubmit={handleAddReadingEntry}>
          <div className="form-group">
            <label className="form-label">Status</label>
            <input className="form-input" value={status} onChange={(e) => setStatus(e.target.value)} />
          </div>
          <div className="form-group">
            <label className="form-label">Date Added</label>
            <input className="form-input" value={dateAdded} onChange={(e) => setDateAdded(e.target.value)} />
          </div>
          <div className="form-actions">
            <button type="submit" className="btn btn-primary">Add</button>
          </div>
        </form>
      </div>

      <div className="section">
        <h2>Books</h2>
        <div className="items-grid">
          {books.length === 0 ? (
            <div className="empty-state">
              <p>No books yet.</p>
              <Link to="/books" className="btn btn-primary">Add your first book</Link>
            </div>
          ) : (
            books.map((book) => (
              <div key={book.id} className="item-card">
                <h3 className="item-title">{book.title}</h3>
                <p className="item-details">{book.author}</p>
                <div className="item-actions">
                  <button className="btn btn-danger btn-sm" onClick={() => { const updated = books.filter(b => b.id !== book.id); setBooks(updated); localStorage.setItem('books', JSON.stringify(updated)); }}>Delete</button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      <div className="section">
        <h2>Reading Entries</h2>
        <div className="items-grid">
          {readingEntries.length === 0 ? (
            <div className="empty-state">
              <p>No reading entries yet.</p>
              <Link to="/reading-list" className="btn btn-primary">Add your first reading entry</Link>
            </div>
          ) : (
            readingEntries.map((entry) => (
              <div key={entry.id} className="item-card">
                <h3 className="item-title">Status: {entry.status}</h3>
                <p className="item-details">Date: {entry.dateAdded}</p>
                <div className="item-actions">
                  <button className="btn btn-danger btn-sm" onClick={() => { const updated = readingEntries.filter(e => e.id !== entry.id); setReadingEntries(updated); localStorage.setItem('readingEntries', JSON.stringify(updated)); }}>Delete</button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

export default Dashboard;