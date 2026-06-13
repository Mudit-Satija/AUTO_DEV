import api from '../services/api'
import { useState, useEffect } from 'react'

const Orders = () => {
  const [orders, setOrders] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const fetchOrders = async () => {
      try {
        const res = await api.get('/orders')
        setOrders(res.data)
        setLoading(false)
      } catch (err) {
        setError(err.response?.data?.message || err.message)
        setLoading(false)
      }
    }

    fetchOrders()
  }, [])

  if (loading) return <div className="app-wrapper">Loading...</div>
  if (error) return <div className="app-wrapper">Error: {error}</div>

  return (
    <div className="app-wrapper">
      <div className="page-header">
        <h1>Orders</h1>
      </div>
      <div className="form-card">
        <div className="form-group">
          <label className="form-label">Add New Order</label>
          <p className="form-textarea">Order creation form would be implemented here.</p>
        </div>
        <div className="form-actions">
          <button className="btn btn-primary">Create Order</button>
        </div>
      </div>
      <div className="stats-grid">
        <div className="stat-card">
          <h3>Total Orders</h3>
          <p className="stat-value">{orders.length}</p>
        </div>
        <div className="stat-card">
          <h3>Total Revenue</h3>
          <p className="stat-value">${orders.reduce((sum, order) => sum + order.totalAmount, 0).toFixed(2)}</p>
        </div>
      </div>
      <div className="section">
        <h2>Order List</h2>
        <div className="items-grid">
          {orders.length > 0 ? (
            orders.map(order => (
              <div key={order._id} className="item-card">
                <div className="item-header">
                  <h3 className="item-title">Order #{order.orderNumber}</h3>
                </div>
                <div className="item-details">
                  <p><strong>Customer:</strong> {order.customerName}</p>
                  <p><strong>Date:</strong> {new Date(order.createdAt).toLocaleDateString()}</p>
                  <p><strong>Total:</strong> ${order.totalAmount.toFixed(2)}</p>
                  <p><strong>Status:</strong> <span className={`badge ${order.status === 'completed' ? 'badge-success' : order.status === 'pending' ? 'badge-warning' : 'badge-danger'}`}>{order.status}</span></p>
                </div>
                <div className="item-actions">
                  <button className="btn btn-secondary">View</button>
                  <button className="btn btn-danger">Delete</button>
                </div>
              </div>
            ))
          ) : (
            <div className="empty-state">
              <p>No orders found. Create your first order.</p>
              <button className="btn btn-primary">Create Order</button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Orders