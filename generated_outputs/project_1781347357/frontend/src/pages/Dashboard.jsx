import api from '../services/api'
import { useState, useEffect } from 'react'

export default function Dashboard() {
  const [stats, setStats] = useState({})
  const [recentTransactions, setRecentTransactions] = useState([])
  const [upcomingBills, setUpcomingBills] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true)
        const res = await api.get('/api/dashboard')
        setStats(res.data.stats)
        setRecentTransactions(res.data.recentTransactions)
        setUpcomingBills(res.data.upcomingBills)
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
          <h3>Total Balance</h3>
          <p className="stat-value">${stats.totalBalance?.toFixed(2) || 0}</p>
        </div>
        <div className="stat-card">
          <h3>This Month's Expenses</h3>
          <p className="stat-value">${stats.monthlyExpenses?.toFixed(2) || 0}</p>
        </div>
        <div className="stat-card">
          <h3>This Month's Income</h3>
          <p className="stat-value">${stats.monthlyIncome?.toFixed(2) || 0}</p>
        </div>
        <div className="stat-card">
          <h3>Unbudgeted</h3>
          <p className="stat-value">${stats.unbudgeted?.toFixed(2) || 0}</p>
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
                  <span className={`badge ${transaction.type === 'expense' ? 'badge-danger' : 'badge-success'}`}>
                    {transaction.type === 'expense' ? 'Expense' : 'Income'}
                  </span>
                  <span>${transaction.amount.toFixed(2)}</span>
                  <span>{new Date(transaction.date).toLocaleDateString()}</span>
                </div>
              </div>
            ))
          ) : (
            <div className="empty-state">
              <p>No recent transactions.</p>
            </div>
          )}
        </div>
      </div>
      <div className="section">
        <h2>Upcoming</h2>
        <div className="upcoming-list">
          {upcomingBills.length > 0 ? (
            upcomingBills.map(bill => (
              <div key={bill._id} className="upcoming-item">
                <div className="upcoming-title">{bill.description}</div>
                <div className="upcoming-meta">
                  <span>${bill.amount.toFixed(2)}</span>
                  <span>{new Date(bill.dueDate).toLocaleDateString()}</span>
                </div>
              </div>
            ))
          ) : (
            <div className="empty-state">
              <p>No upcoming bills or payments.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}