import React, { useState, useEffect } from 'react';
import api from '../services/api';

function Orders() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchOrders = async () => {
      try {
        setLoading(true);
        const response = await api.get('/orders');
        setOrders(response.data);
      } catch (err) {
        setError(err.response?.data?.message || err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchOrders();
  }, []);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div className="app-wrapper">
      <div className="page-header">
        <h1>Orders</h1>
        <p>Manage and view all customer orders</p>
      </div>

      <div className="form-card">
        <div className="form-group">
          <label className="form-label">Add New Order</label>
          <p className="form-input" style={{ color: 'var(--secondary-color)' }}>
            Order creation is handled via backend API only. Use the API endpoint /orders to create new orders.
          </p>
        </div>
        <div className="form-actions">
          <button className="btn btn-primary" disabled>
            Create Order
          </button>
        </div>
      </div>

      <div className="section">
        <h2>All Orders</h2>
        {orders.length > 0 ? (
          <div className="table-wrapper">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Order #</th>
                  <th>Customer</th>
                  <th>Date</th>
                  <th>Total</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {orders.map(order => (
                  <tr key={order._id} className="leaderboard-row">
                    <td>{order.orderNumber}</td>
                    <td>{order.customerName}</td>
                    <td>{new Date(order.createdAt).toLocaleDateString()}</td>
                    <td>${order.totalAmount.toFixed(2)}</td>
                    <td>
                      <span className={`badge ${order.status === 'completed' ? 'badge-success' : order.status === 'pending' ? 'badge-warning' : 'badge-danger'}`}>
                        {order.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="empty-state">
            <p>No orders found. Create your first order via the API.</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default Orders;