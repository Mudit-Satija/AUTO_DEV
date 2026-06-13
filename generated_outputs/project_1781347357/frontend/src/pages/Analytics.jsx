import api from '../services/api'
import { useState, useEffect } from 'react'

export default function Analytics() {
  const [metrics, setMetrics] = useState({})
  const [breakdown, setBreakdown] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        setLoading(true)
        const res = await api.get('/api/analytics')
        setMetrics(res.data.metrics)
        setBreakdown(res.data.breakdown)
        setError('')
      } catch (err) {
        setError(err.response?.data?.message || 'Failed to load analytics data')
      } finally {
        setLoading(false)
      }
    }

    fetchAnalytics()
  }, [])

  if (loading) return <div className="app-wrapper">Loading...</div>
  if (error) return <div className="app-wrapper"><div className="empty-state"><p>{error}</p><button className="btn btn-primary" onClick={() => window.location.reload()}>Retry</button></div></div>

  return (
    <div className="app-wrapper">
      <div className="page-header">
        <h1>Analytics</h1>
      </div>
      <div className="stats-grid">
        <div className="stat-card">
          <h3>Total Expenses</h3>
          <p className="stat-value">${metrics.totalExpenses?.toFixed(2) || 0}</p>
        </div>
        <div className="stat-card">
          <h3>Total Income</h3>
          <p className="stat-value">${metrics.totalIncome?.toFixed(2) || 0}</p>
        </div>
        <div className="stat-card">
          <h3>Net Balance</h3>
          <p className="stat-value">${metrics.netBalance?.toFixed(2) || 0}</p>
        </div>
        <div className="stat-card">
          <h3>Spending Rate</h3>
          <p className="stat-value">{metrics.spendingRate?.toFixed(1) || 0}%</p>
        </div>
      </div>
      <div className="section">
        <h2>Breakdown</h2>
        <div className="chart-container">
          {breakdown.map((item) => (
            <div key={item.category} className="card">
              <div className="card-header">
                <h3>{item.category}</h3>
                <span className="stat-value">${item.amount.toFixed(2)}</span>
              </div>
              <div className="card-content">
                <div className="progress-bar" style={{ width: `${(item.amount / metrics.totalExpenses) * 100}%` }}></div>
              </div>
              <div className="card-footer">
                <span className="badge badge-info">{item.percentage.toFixed(1)}%</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}