import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import './App.css';
import Books from './pages/Books';
import AddBook from './pages/AddBook';
import ReadingList from './pages/ReadingList';
import Dashboard from './pages/Dashboard';

function App() {
  const [books, setBooks] = useState([]);
  const [readingEntries, setReadingEntries] = useState([]);

  useEffect(() => {
    const seedBooks = [
      { id: crypto.randomUUID(), title: 'Book 1', author: 'Author 1', genre: 'Fiction', pages: '300', totalPages: '300', readingStatus: 'Completed', dateAdded: '2024-01-15' },
      { id: crypto.randomUUID(), title: 'Book 2', author: 'Author 2', genre: 'Non-Fiction', pages: '250', totalPages: '250', readingStatus: 'Reading', dateAdded: '2024-01-20' },
    ];

    const seedReadingEntries = [
      { id: crypto.randomUUID(), bookId: seedBooks[0].id, status: 'Completed', dateAdded: '2024-01-15' },
      { id: crypto.randomUUID(), bookId: seedBooks[1].id, status: 'Reading', dateAdded: '2024-01-20' },
    ];

    const storedBooks = localStorage.getItem('books');
    setBooks(storedBooks ? JSON.parse(storedBooks) : seedBooks);
    if (!storedBooks) localStorage.setItem('books', JSON.stringify(seedBooks));

    const storedReadingEntries = localStorage.getItem('readingEntries');
    setReadingEntries(storedReadingEntries ? JSON.parse(storedReadingEntries) : seedReadingEntries);
    if (!storedReadingEntries) localStorage.setItem('readingEntries', JSON.stringify(seedReadingEntries));
  }, []);

  useEffect(() => {
    localStorage.setItem('books', JSON.stringify(books));
  }, [books]);

  useEffect(() => {
    localStorage.setItem('readingEntries', JSON.stringify(readingEntries));
  }, [readingEntries]);

  return (
    <BrowserRouter>
      <div className="app-wrapper">
        <nav className="navbar">
          <Link to="/" className="navbar-brand">BookShelf</Link>
          <div className="nav-links">
            <Link to="/books" className="nav-link">Books</Link>
            <Link to="/add-book" className="nav-link">Add Book</Link>
            <Link to="/reading-list" className="nav-link">Reading List</Link>
            <Link to="/dashboard" className="nav-link">Dashboard</Link>
          </div>
        </nav>
        <Routes>
          <Route path="/" element={<Books books={books} setBooks={setBooks} />} />
          <Route path="/books" element={<Books books={books} setBooks={setBooks} />} />
          <Route path="/add-book" element={<AddBook books={books} setBooks={setBooks} />} />
          <Route path="/reading-list" element={<ReadingList readingEntries={readingEntries} setReadingEntries={setReadingEntries} books={books} />} />
          <Route path="/dashboard" element={<Dashboard books={books} setBooks={setBooks} readingEntries={readingEntries} setReadingEntries={setReadingEntries} />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;