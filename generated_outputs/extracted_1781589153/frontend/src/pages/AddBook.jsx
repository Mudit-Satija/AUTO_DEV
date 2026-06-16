import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';

function AddBook({ books, setBooks }) {
  const navigate = useNavigate();
  const [title, setTitle] = useState('');
  const [author, setAuthor] = useState('');
  const [pages, setPages] = useState('');
  const [genre, setGenre] = useState('');
  const [readingStatus, setReadingStatus] = useState('');
  const [dateAdded, setDateAdded] = useState('');
  const [totalPages, setTotalPages] = useState('');

  const handleAdd = (e) => {
    e.preventDefault();
    if (!title.trim()) return;
    const updated = [
      ...books,
      {
        id: crypto.randomUUID(),
        title: title.trim(),
        author: author.trim(),
        pages: pages.trim(),
        genre: genre.trim(),
        readingStatus: readingStatus.trim(),
        dateAdded: dateAdded.trim(),
        totalPages: totalPages.trim(),
      },
    ];
    setBooks(updated);
    localStorage.setItem('books', JSON.stringify(updated));
    setTitle('');
    setAuthor('');
    setPages('');
    setGenre('');
    setReadingStatus('');
    setDateAdded('');
    setTotalPages('');
    navigate('/books');
  };

  const handleDelete = (id) => {
    const updated = books.filter((book) => book.id !== id);
    setBooks(updated);
    localStorage.setItem('books', JSON.stringify(updated));
  };

  return (
    <div className="app-wrapper">
      <div className="page-header">
        <h1>Add Book</h1>
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
            <label className="form-label">Pages</label>
            <input className="form-input" value={pages} onChange={(e) => setPages(e.target.value)} />
          </div>
          <div className="form-group">
            <label className="form-label">Genre</label>
            <input className="form-input" value={genre} onChange={(e) => setGenre(e.target.value)} />
          </div>
          <div className="form-group">
            <label className="form-label">Reading Status</label>
            <input className="form-input" value={readingStatus} onChange={(e) => setReadingStatus(e.target.value)} />
          </div>
          <div className="form-group">
            <label className="form-label">Date Added</label>
            <input className="form-input" value={dateAdded} onChange={(e) => setDateAdded(e.target.value)} />
          </div>
          <div className="form-group">
            <label className="form-label">Total Pages</label>
            <input className="form-input" value={totalPages} onChange={(e) => setTotalPages(e.target.value)} />
          </div>
          <div className="form-actions">
            <button type="submit" className="btn btn-primary">Add</button>
          </div>
        </form>
      </div>

      <div className="section">
        <h2>All Books</h2>
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
                <p className="item-details">Author: {book.author}</p>
                <p className="item-details">Pages: {book.pages}</p>
                <p className="item-details">Genre: {book.genre}</p>
                <p className="item-details">Reading Status: {book.readingStatus}</p>
                <p className="item-details">Date Added: {book.dateAdded}</p>
                <p className="item-details">Total Pages: {book.totalPages}</p>
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

export default AddBook;