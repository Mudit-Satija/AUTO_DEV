import api from '../services/api'
import { useState, useEffect } from 'react'

export default function Dashboard() {
  const [metrics, setMetrics] = useState({})
  const [recentTransactions, setRecentTransactions] = useState([])
  const [upcomingExpenses, setUpcomingExpenses] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true)
        const res = await api.get('/api/dashboard')
        setMetrics(res.data.metrics)
        setRecentTransactions(res.data.recentTransactions)
        setUpcomingExpenses(res.data.upcomingExpenses)
        setError('')
      } catch (err) {
        setError(err.response?.data?.message || 'Failed to load dashboard data')
      } finally {
        setLoading(false)
      }
    }

    fetchDashboardData()
  }, [])

  if (loading) return <div className="app-wrapper">Loading...</div>
  if (error) return <div className="app-wrapper"><div className="empty-state"><p>{error}</p><button className="btn btn-primary" onClick={() => window.location.reload()}>Retry</button></div></div>

  return (
    <div className="app-wrapper">
      <div className="page-header">
        <h1>Dashboard</h1>
      </div>
      <div className="stats-grid">
        <div className="stat-card">
          <h3>Total Expenses</h3>
          <p className="stat-value">${metrics.totalExpenses?.toFixed(2) || '0.00'}</p>
        </div>
        <div className="stat-card">
          <h3>Remaining Budget</h3>
          <p className="stat-value">${metrics.remainingBudget?.toFixed(2) || '0.00'}</p>
        </div>
        <div className="stat-card">
          <h3>Transactions This Month</h3>
          <p className="stat-value">{metrics.transactionCount || 0}</p>
        </div>
        <div className="stat-card">
          <h3>Overdue Bills</h3>
          <p className="stat-value">{metrics.overdueCount || 0}</p>
        </div>
      </div>
      <div className="section">
        <h2>Recent Activity</h2>
        <div className="activity-feed">
          {recentTransactions.length > 0 ? (
            recentTransactions.map(transaction => (
              <div key={transaction._id} className="activity-item">
                <div className="activity-title">{transaction.description}</div>
                <div className="activity-meta">
                  <span className={transaction.type === 'expense' ? 'badge badge-danger' : 'badge badge-success'}>
                    {transaction.type === 'expense' ? 'Expense' : 'Income'}
                  </span>
                  <span>${transaction.amount}</span>
                  <span>{new Date(transaction.date).toLocaleDateString()}</span>
                </div>
              </div>
            ))
          ) : (
            <div className="empty-state">
              <p>No recent activity yet.</p>
            </div>
          )}
        </div>
      </div>
      <div className="section">
        <h2>Upcoming</h2>
        <div className="upcoming-list">
          {upcomingExpenses.length > 0 ? (
            upcomingExpenses.map(expense => (
              <div key={expense._id} className="upcoming-item">
                <div className="upcoming-title">{expense.description}</div>
                <div className="upcoming-meta">
                  <span>${expense.amount}</span>
                  <span>Due: {new Date(expense.dueDate).toLocaleDateString()}</span>
                </div>
              </div>
            ))
          ) : (
            <div className="empty-state">
              <p>No upcoming expenses.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}