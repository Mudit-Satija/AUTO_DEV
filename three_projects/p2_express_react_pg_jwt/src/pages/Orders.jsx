import api from '../services/api';
import { useEffect, useState } from 'react';

export default function Orders() {
  const [orders, setOrders] = useState([]);

  useEffect(() => {
    const fetchOrders = async () => {
      try {
        const response = await api.get('/api/orders');
        setOrders(response.data);
      } catch (error) {
        console.error('Failed to fetch orders:', error);
      }
    };

    fetchOrders();
  }, []);

  return (
    <div>
      <h1>Orders</h1>
      {orders.length > 0 ? (
        <ul>
          {orders.map(order => (
            <li key={order.id}>
              Order #{order.id} - {order.status} - ${order.total}
            </li>
          ))}
        </ul>
      ) : (
        <p>No orders found.</p>
      )}
    </div>
  );
}