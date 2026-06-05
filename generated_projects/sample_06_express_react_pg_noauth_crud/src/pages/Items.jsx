import React, { useState, useEffect } from 'react';
import api from '../services/api';

function Items() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchItems = async () => {
      try {
        const response = await api.get('/items');
        setItems(response.data);
      } catch (err) {
        setError(err.response?.data?.message || 'Failed to fetch items');
      } finally {
        setLoading(false);
      }
    };

    fetchItems();
  }, []);

  if (loading) return <p>Loading items...</p>;
  if (error) return <p style={{ color: 'red' }}>{error}</p>;

  return (
    <div>
      <h1>Items</h1>
      <ul>
        {items.map(item => (
          <li key={item.id}>{item.name} - {item.description}</li>
        ))}
      </ul>
    </div>
  );
}

export default Items;