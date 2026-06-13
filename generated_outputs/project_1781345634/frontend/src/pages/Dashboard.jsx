import api from '../services/api'
import React, { useState, useEffect } from 'react'

const Dashboard = () => {
  const [stats, setStats] = useState({ products: 0, orders: 0, revenue: 0, customers: 0 })
  const [recentActivity, setRecentActivity] = useState([])
  const [upcoming, setUpcoming] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [productsRes, ordersRes] = await Promise.all([
          api.get('/products'),
          api.get('/orders')
        ])

        const products = productsRes.data
        const orders = ordersRes.data

        const totalRevenue = orders.reduce((sum, order) => sum + order.totalAmount, 0)
        const uniqueCustomers = new Set(orders.map(order => order.customerId)).size

        setStats({
          products: products.length,
          orders: orders.length,
          revenue: totalRevenue.toFixed(2),
          customers: uniqueCustomers
        })

        const sortedOrders = [...orders].sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))
        setRecentActivity(sortedOrders.slice(0, 5))

        const upcomingOrders = orders.filter(order => new Date(order.expectedDelivery) > new Date()).sort((a, b) => new Date(a.expectedDelivery) - new Date(b.expectedDelivery))
        setUpcoming(upcomingOrders.slice(0, 5))

        setLoading(false)
      } catch (err) {
        setError(err.response?.data?.message || err.message)
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  if (loading) return <div>Loading...</div>
  if (error) return <div className="app-wrapper"><div className="page-header"><h1>Dashboard</h1></div><div className="empty-state"><p>{error}</p><button className="btn btn-primary" onClick={() => window.location.reload()}>Retry</button></div></div>

  return (
    <div className="app-wrapper">
      <div className="page-header">
        <h1>Dashboard</h1>
      </div>
      <div className="stats-grid">
        <div className="stat-card">
          <h3>Products</h3>
          <p className="stat-value">{stats.products}</p>
        </div>
        <div className="stat-card">
          <h3>Orders</h3>
          <p className="stat-value">{stats.orders}</p>
        </div>
        <div className="stat-card">
          <h3>Revenue</h3>
          <p className="stat-value">${stats.revenue}</p>
        </div>
        <div className="stat-card">
          <h3>Customers</h3>
          <p className="stat-value">{stats.customers}</p>
        </div>
      </div>
      <div className="section">
        <h2>Recent Activity</h2>
        <div className="activity-feed">
          {recentActivity.length > 0 ? (
            recentActivity.map((activity, index) => (
              <div key={index} className="activity-item">
                <div className="activity-title">Order #{activity._id}</div>
                <div className="activity-meta">{new Date(activity.createdAt).toLocaleDateString()} - ${activity.totalAmount}</div>
              </div>
            ))
          ) : (
            <div className="empty-state">
              <p>No recent activity</p>
            </div>
          )}
        </div>
      </div>
      <div className="section">
        <h2>Upcoming</h2>
        <div className="upcoming-list">
          {upcoming.length > 0 ? (
            upcoming.map((item, index) => (
              <div key={index} className="upcoming-item">
                <div className="upcoming-title">Order #{item._id}</div>
                <div className="upcoming-meta">Expected delivery: {new Date(item.expectedDelivery).toLocaleDateString()}</div>
              </div>
            ))
          ) : (
            <div className="empty-state">
              <p>No upcoming orders</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Dashboard