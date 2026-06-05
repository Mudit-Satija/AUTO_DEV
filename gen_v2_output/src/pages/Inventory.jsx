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
      {items.length > 0 ? (
        <ul>
          {items.map(item => (
            <li key={item._id}>
              {item.name} - {item.quantity} units
            </li>
          ))}
        </ul>
      ) : (
        <p>No inventory items found.</p>
      )}
    </div>
  );
};

export default Inventory;