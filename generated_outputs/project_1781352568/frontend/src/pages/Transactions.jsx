import api from '../services/api'
import { useState, useEffect } from 'react'

export default function Transactions() {
  const [transactions, setTransactions] = useState([])
  const [categories, setCategories] = useState([])
  const [newTransaction, setNewTransaction] = useState({
    description: '',
    amount: '',
    type: 'expense',
    category: '',
    date: new Date().toISOString().split('T')[0]
  })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  useEffect(() => {
    const fetchTransactionsAndCategories = async () => {
      try {
        setLoading(true)
        const [transactionsRes, categoriesRes] = await Promise.all([
          api.get('/api/transactions'),
          api.get('/api/categories')
        ])
        setTransactions(transactionsRes.data)
        setCategories(categoriesRes.data)
        setError('')
      } catch (err) {
        setError(err.response?.data?.message || 'Failed to load transactions and categories')
      } finally {
        setLoading(false)
      }
    }

    fetchTransactionsAndCategories()
  }, [])

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setNewTransaction(prev => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      await api.post('/api/transactions', newTransaction)
      setSuccess('Transaction added successfully!')
      setNewTransaction({
        description: '',
        amount: '',
        type: 'expense',
        category: '',
        date: new Date().toISOString().split('T')[0]
      })
      const res = await api.get('/api/transactions')
      setTransactions(res.data)
      setTimeout(() => setSuccess(''), 3000)
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to add transaction')
    }
  }

  if (loading) return <div className="app-wrapper">Loading...</div>
  if (error) return <div className="app-wrapper"><div className="empty-state"><p>{error}</p><button className="btn btn-primary" onClick={() => window.location.reload()}>Retry</button></div></div>

  return (
    <div className="app-wrapper">
      <div className="page-header">
        <h1>Transactions</h1>
      </div>
      <div className="form-card">
        <form onSubmit={handleSubmit}>
          <div className="form-row">
            <div className="form-group">
              <label className="form-label">Description</label>
              <input 
                type="text" 
                className="form-input" 
                name="description" 
                value={newTransaction.description} 
                onChange={handleInputChange} 
                required 
              />
            </div>
            <div className="form-group">
              <label className="form-label">Amount ($)</label>
              <input 
                type="number" 
                className="form-input" 
                name="amount" 
                value={newTransaction.amount} 
                onChange={handleInputChange} 
                required 
                step="0.01" 
                min="0"
              />
            </div>
            <div className="form-group">
              <label className="form-label">Type</label>
              <select className="form-select" name="type" value={newTransaction.type} onChange={handleInputChange} required>
                <option value="income">Income</option>
                <option value="expense">Expense</option>
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Category</label>
              <select className="form-select" name="category" value={newTransaction.category} onChange={handleInputChange} required>
                <option value="">Select a category</option>
                {categories.map(cat => (
                  <option key={cat._id} value={cat._id}>{cat.name}</option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Date</label>
              <input 
                type="date" 
                className="form-input" 
                name="date" 
                value={newTransaction.date} 
                onChange={handleInputChange} 
                required 
              />
            </div>
          </div>
          <div className="form-actions">
            <button type="submit" className="btn btn-primary">Add Transaction</button>
          </div>
        </form>
      </div>
      {success && <div className="badge badge-success">{success}</div>}
      <div className="stats-grid">
        <div className="stat-card">
          <h3>Total Income</h3>
          <p className="stat-value">${transactions.filter(t => t.type === 'income').reduce((sum, t) => sum + t.amount, 0).toFixed(2)}</p>
        </div>
        <div className="stat-card">
          <h3>Total Expenses</h3>
          <p className="stat-value">${transactions.filter(t => t.type === 'expense').reduce((sum, t) => sum + t.amount, 0).toFixed(2)}</p>
        </div>
        <div className="stat-card">
          <h3>Net Balance</h3>
          <p className="stat-value">${(transactions.filter(t => t.type === 'income').reduce((sum, t) => sum + t.amount, 0) - 
            transactions.filter(t => t.type === 'expense').reduce((sum, t) => sum + t.amount, 0)).toFixed(2)}</p>
        </div>
        <div className="stat-card">
          <h3>Total Transactions</h3>
          <p className="stat-value">{transactions.length}</p>
        </div>
      </div>
      <div className="section">
        <h2>All Transactions</h2>
        <div className="items-grid">
          {transactions.length > 0 ? (
            transactions.map(transaction => (
              <div key={transaction._id} className="item-card">
                <div className="item-title">{transaction.description}</div>
                <div className="item-details">
                  <span className={transaction.type === 'income' ? 'badge badge-success' : 'badge badge-danger'}>
                    {transaction.type === 'income' ? '+' : '-'}${transaction.amount.toFixed(2)}
                  </span>
                  <span>{new Date(transaction.date).toLocaleDateString()}</span>
                  <span className="badge badge-info">{transaction.category?.name || 'Uncategorized'}</span>
                </div>
                <div className="item-actions">
                  <span className="badge badge-primary">{transaction.type}</span>
                </div>
              </div>
            ))
          ) : (
            <div className="empty-state">
              <p>No transactions yet. Add your first transaction above.</p>
              <button className="btn btn-primary" onClick={() => document.querySelector('form').reset()}>Add Transaction</button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}