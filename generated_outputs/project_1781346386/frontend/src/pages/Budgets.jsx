import api from '../services/api'
import { useState, useEffect } from 'react'

export default function Budgets() {
  const [budgets, setBudgets] = useState([])
  const [categories, setCategories] = useState([])
  const [newBudget, setNewBudget] = useState({ category: '', amount: '', month: '' })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  useEffect(() => {
    const fetchBudgetsAndCategories = async () => {
      try {
        setLoading(true)
        const [budgetsRes, categoriesRes] = await Promise.all([
          api.get('/api/budgets'),
          api.get('/api/categories')
        ])
        setBudgets(budgetsRes.data)
        setCategories(categoriesRes.data)
        setError('')
      } catch (err) {
        setError(err.response?.data?.message || 'Failed to load budgets and categories')
      } finally {
        setLoading(false)
      }
    }

    fetchBudgetsAndCategories()
  }, [])

  const handleCreateBudget = async (e) => {
    e.preventDefault()
    if (!newBudget.category || !newBudget.amount || !newBudget.month) return

    try {
      await api.post('/api/budgets', newBudget)
      setSuccess('Budget created successfully!')
      setNewBudget({ category: '', amount: '', month: '' })
      const res = await api.get('/api/budgets')
      setBudgets(res.data)
      setTimeout(() => setSuccess(''), 3000)
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to create budget')
    }
  }

  const handleDeleteBudget = async (id) => {
    if (!window.confirm('Are you sure you want to delete this budget?')) return

    try {
      await api.delete(`/api/budgets/${id}`)
      setBudgets(budgets.filter(b => b._id !== id))
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to delete budget')
    }
  }

  if (loading) return <div className="app-wrapper">Loading...</div>
  if (error) return <div className="app-wrapper"><div className="empty-state"><p>{error}</p><button className="btn btn-primary" onClick={() => window.location.reload()}>Retry</button></div></div>

  return (
    <div className="app-wrapper">
      <div className="page-header">
        <h1>Budgets</h1>
      </div>
      <div className="form-card">
        <form onSubmit={handleCreateBudget}>
          <div className="form-group">
            <label className="form-label">Category</label>
            <select 
              className="form-select" 
              value={newBudget.category} 
              onChange={(e) => setNewBudget({...newBudget, category: e.target.value})}
              required
            >
              <option value="">Select a category</option>
              {categories.map(cat => (
                <option key={cat._id} value={cat._id}>{cat.name}</option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">Amount ($)</label>
            <input 
              type="number" 
              className="form-input" 
              value={newBudget.amount} 
              onChange={(e) => setNewBudget({...newBudget, amount: e.target.value})} 
              placeholder="0.00" 
              step="0.01" 
              min="0" 
              required 
            />
          </div>
          <div className="form-group">
            <label className="form-label">Month</label>
            <input 
              type="month" 
              className="form-input" 
              value={newBudget.month} 
              onChange={(e) => setNewBudget({...newBudget, month: e.target.value})} 
              required 
            />
          </div>
          <div className="form-actions">
            <button type="submit" className="btn btn-primary">Create Budget</button>
            {success && <p className="badge badge-success">{success}</p>}
          </div>
        </form>
      </div>
      <div className="stats-grid">
        <div className="stat-card">
          <h3>Total Budgets</h3>
          <p className="stat-value">{budgets.length}</p>
        </div>
        <div className="stat-card">
          <h3>Total Allocated</h3>
          <p className="stat-value">${budgets.reduce((sum, b) => sum + parseFloat(b.amount), 0).toFixed(2)}</p>
        </div>
        <div className="stat-card">
          <h3>Active Months</h3>
          <p className="stat-value">{new Set(budgets.map(b => b.month)).size}</p>
        </div>
      </div>
      <div className="section">
        <h2>Current Budgets</h2>
        <div className="items-grid">
          {budgets.length > 0 ? (
            budgets.map(budget => (
              <div key={budget._id} className="item-card">
                <div className="item-title">{categories.find(c => c._id === budget.category)?.name || 'Unknown'}</div>
                <div className="item-details">
                  <p>Amount: ${budget.amount}</p>
                  <p>Month: {new Date(budget.month).toLocaleDateString('en-US', { year: 'numeric', month: 'long' })}</p>
                </div>
                <div className="item-actions">
                  <button className="btn btn-danger btn-sm" onClick={() => handleDeleteBudget(budget._id)}>Delete</button>
                </div>
              </div>
            ))
          ) : (
            <div className="empty-state">
              <p>No budgets set yet. Create your first budget above.</p>
              <button className="btn btn-primary">Create Budget</button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}