import React, { useEffect, useState } from 'react';
import api from '../services/api';

const Inventory = () => {
  const [items, setItems] = useState([]);

  useEffect(() => {
    const fetchInventory = async () => {
      try {
        const response = await api.get('/api/inventory');
        setItems(response.data);
      } catch (error) {
        console.error('Failed to fetch inventory:', error);
      }
    };

    fetchInventory();
  }, []);

  return (
    <div>
      <h2>Inventory</h2>
      {items.length === 0 ? (
        <p>No inventory items found.</p>
      ) : (
        <ul style={{ listStyle: 'none', padding: 0 }}>
          {items.map(item => (
            <li key={item._id} style={{ border: '1px solid #ddd', padding: '1rem', margin: '0.5rem 0', borderRadius: '4px' }}>
              <strong>{item.name}</strong> - {item.quantity} units - ${item.price}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default Inventory;