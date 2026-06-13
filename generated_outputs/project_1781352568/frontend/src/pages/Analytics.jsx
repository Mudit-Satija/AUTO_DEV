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
          <p className="stat-value">${metrics.totalExpenses?.toFixed(2) || '0.00'}</p>
        </div>
        <div className="stat-card">
          <h3>Total Income</h3>
          <p className="stat-value">${metrics.totalIncome?.toFixed(2) || '0.00'}</p>
        </div>
        <div className="stat-card">
          <h3>Net Balance</h3>
          <p className="stat-value">${metrics.netBalance?.toFixed(2) || '0.00'}</p>
        </div>
        <div className="stat-card">
          <h3>Transactions</h3>
          <p className="stat-value">{metrics.totalTransactions || 0}</p>
        </div>
      </div>
      <div className="section">
        <h2>Breakdown</h2>
        <div className="chart-container">
          {breakdown.map((item, index) => (
            <div key={index} className="breakdown-section">
              <div className="item-title">{item.category}</div>
              <div className="item-details">
                <div style={{ width: '100%', backgroundColor: '#f0f0f0', borderRadius: '4px', height: '20px', overflow: 'hidden' }}>
                  <div 
                    style={{ 
                      width: `${(item.amount / metrics.totalExpenses) * 100}%`, 
                      height: '100%', 
                      backgroundColor: index % 2 === 0 ? '#3b82f6' : '#10b981',
                      transition: 'width 0.5s ease'
                    }}
                  />
                </div>
                <span className="stat-value">${item.amount.toFixed(2)}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}