import React, { useState } from 'react';
import { Link } from 'react-router-dom';

function Books({ books, setBooks }) {
  const [title, setTitle] = useState('');
  const [author, setAuthor] = useState('');
  const [genre, setGenre] = useState('');

  const handleAdd = (e) => {
    e.preventDefault();
    if (!title.trim() || !author.trim() || !genre.trim()) return;
    const updated = [
      ...books,
      {
        id: crypto.randomUUID(),
        title: title.trim(),
        author: author.trim(),
        genre: genre.trim(),
      },
    ];
    setBooks(updated);
    localStorage.setItem('books', JSON.stringify(updated));
    setTitle('');
    setAuthor('');
    setGenre('');
  };

  const handleDelete = (id) => {
    const updated = books.filter((book) => book.id !== id);
    setBooks(updated);
    localStorage.setItem('books', JSON.stringify(updated));
  };

  return (
    <div className="app-wrapper">
      <div className="page-header">
        <h1>Books</h1>
      </div>

      <div className="form-card">
        <h2>Add Book</h2>
        <form onSubmit={handleAdd}>
          <div className="form-group">
            <label className="form-label">Title</label>
            <input className="form-input" value={title} onChange={(e) => setTitle(e.target.value)} />
          </div>
          <div className="form-group">
            <label className="form-label">Author</label>
            <input className="form-input" value={author} onChange={(e) => setAuthor(e.target.value)} />
          </div>
          <div className="form-group">
            <label className="form-label">Genre</label>
            <input className="form-input" value={genre} onChange={(e) => setGenre(e.target.value)} />
          </div>
          <div className="form-actions">
            <button type="submit" className="btn btn-primary">
              Add
            </button>
          </div>
        </form>
      </div>

      <div className="section">
        <h2>All Books</h2>
        <div className="items-grid">
          {books.length === 0 ? (
            <div className="empty-state">
              <p>No books yet.</p>
              <Link to="/books" className="btn btn-primary">
                Add your first book
              </Link>
            </div>
          ) : (
            books.map((book) => (
              <div key={book.id} className="item-card">
                <h3 className="item-title">{book.title}</h3>
                <p className="item-details">
                  {book.author} ({book.genre})
                </p>
                <div className="item-actions">
                  <button className="btn btn-danger btn-sm" onClick={() => handleDelete(book.id)}>
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

export default Books;