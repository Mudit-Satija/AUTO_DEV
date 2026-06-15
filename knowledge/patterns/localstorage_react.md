# Frontend-Only React + localStorage — Complete Working Example

Copy this pattern EXACTLY for every frontend-only (no backend API) project.

---

## App.jsx — ONLY for the root component file

```jsx
import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import './App.css';
import Items from './pages/Items';

function App() {
  const [items, setItems] = useState([]);

  useEffect(() => {
    const stored = localStorage.getItem('items');
    if (stored) {
      setItems(JSON.parse(stored));
    } else {
      const seed = [
        { id: crypto.randomUUID(), title: 'Recipe 1', description: 'A delicious starter' },
        { id: crypto.randomUUID(), title: 'Recipe 2', description: 'A hearty main course' },
      ];
      localStorage.setItem('items', JSON.stringify(seed));
      setItems(seed);
    }
  }, []);

  useEffect(() => {
    localStorage.setItem('items', JSON.stringify(items));
  }, [items]);

  return (
    <BrowserRouter>
      <div className="app-wrapper">
        <nav className="navbar">
          <Link to="/" className="navbar-brand">My App</Link>
          <div className="nav-links">
            <Link to="/items" className="nav-link">Items</Link>
          </div>
        </nav>
        <Routes>
          <Route path="/" element={<Items items={items} setItems={setItems} />} />
          <Route path="/items" element={<Items items={items} setItems={setItems} />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
```

---

## Pages — for EVERY file in src/pages/

**CRITICAL RULES for page files:**
- Pages do NOT import BrowserRouter, Routes, or Route — those are App.jsx-only
- Pages receive data as props from App.jsx: `({ items, setItems }) =>`
- If your JSX uses `<Link>`, `<NavLink>`, or `<Navigate>`, you MUST import it from 'react-router-dom'
- Pages use `crypto.randomUUID()` for every new entity object (every created item MUST have an id field)
- Pages must update BOTH state AND localStorage on every change

```jsx
import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

function Items({ items, setItems }) {
  const navigate = useNavigate();
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');

  const handleAdd = (e) => {
    e.preventDefault();
    if (!title.trim()) return;
    const updated = [
      ...items,
      { id: crypto.randomUUID(), title: title.trim(), description: description.trim() },
    ];
    setItems(updated);
    localStorage.setItem('items', JSON.stringify(updated));
    setTitle('');
    setDescription('');
    navigate('/items');
  };

  const handleDelete = (id) => {
    const updated = items.filter((item) => item.id !== id);
    setItems(updated);
    localStorage.setItem('items', JSON.stringify(updated));
  };

  return (
    <div className="app-wrapper">
      <div className="page-header">
        <h1>Items</h1>
      </div>

      <div className="form-card">
        <h2>Add Item</h2>
        <form onSubmit={handleAdd}>
          <div className="form-group">
            <label className="form-label">Title</label>
            <input className="form-input" value={title} onChange={(e) => setTitle(e.target.value)} />
          </div>
          <div className="form-group">
            <label className="form-label">Description</label>
            <input className="form-input" value={description} onChange={(e) => setDescription(e.target.value)} />
          </div>
          <div className="form-actions">
            <button type="submit" className="btn btn-primary">Add</button>
          </div>
        </form>
      </div>

      <div className="section">
        <h2>All Items</h2>
        <div className="items-grid">
          {items.length === 0 ? (
            <div className="empty-state">
              <p>No items yet.</p>
              <Link to="/items" className="btn btn-primary">Add your first item</Link>
            </div>
          ) : (
            items.map((item) => (
              <div key={item.id} className="item-card">
                <h3 className="item-title">{item.title}</h3>
                <p className="item-details">{item.description}</p>
                <div className="item-actions">
                  <button className="btn btn-danger btn-sm" onClick={() => handleDelete(item.id)}>
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

export default Items;
```

---

## main.jsx (already exists — for reference only, never generate)

```jsx
import { createRoot } from 'react-dom/client';
import App from './App';
import './App.css';

createRoot(document.getElementById('root')).render(<App />);
```

---

## Key rules this example demonstrates:

1. **main.jsx handles mounting** — App.jsx does NOT import ReactDOM, does NOT call render/createRoot. It just exports `App`.
2. **Complete import statements** — `BrowserRouter, Routes, Route, Link, useNavigate` all imported correctly.
3. **Props from App** — Page components receive `items` + `setItems` as props. They never fetch data themselves.
4. **useEffect for persistence** — App loads from localStorage on mount, persists on every change.
5. **crypto.randomUUID()** — generates unique IDs (built-in browser API, no dependency needed).
6. **State + localStorage in sync** — Every mutation updates both React state and localStorage.
7. **Seed data on first visit** — App writes sample data if localStorage is empty.
8. **Form with controlled inputs** — value={state} + onChange handlers.
9. **Pages do NOT import BrowserRouter/Routes/Route** — those are App.jsx-only.
10. **Pages use `Link` for navigation**, `useNavigate` for programmatic navigation.
