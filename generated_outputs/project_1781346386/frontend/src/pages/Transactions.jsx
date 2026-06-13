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

  const handleCreateTransaction = async (e) => {
    e.preventDefault()
    if (!newTransaction.description || !newTransaction.amount || !newTransaction.category) return

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
      setError(err.response?.data?.message || 'Failed to create transaction')
    }
  }

  const handleDeleteTransaction = async (id) => {
    if (!window.confirm('Are you sure you want to delete this transaction?')) return

    try {
      await api.delete(`/api/transactions/${id}`)
      setTransactions(transactions.filter(t => t._id !== id))
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to delete transaction')
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
        <form onSubmit={handleCreateTransaction}>
          <div className="form-group">
            <label className="form-label">Description</label>
            <input 
              type="text" 
              className="form-input" 
              value={newTransaction.description} 
              onChange={(e) => setNewTransaction({...newTransaction, description: e.target.value})} 
              placeholder="e.g. Grocery shopping" 
              required 
            />
          </div>
          <div className="form-group">
            <label className="form-label">Amount ($)</label>
            <input 
              type="number" 
              className="form-input" 
              value={newTransaction.amount} 
              onChange={(e) => setNewTransaction({...newTransaction, amount: e.target.value})} 
              placeholder="0.00" 
              step="0.01" 
              min="0" 
              required 
            />
          </div>
          <div className="form-group">
            <label className="form-label">Type</label>
            <select 
              className="form-select" 
              value={newTransaction.type} 
              onChange={(e) => setNewTransaction({...newTransaction, type: e.target.value})}
              required
            >
              <option value="expense">Expense</option>
              <option value="income">Income</option>
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">Category</label>
            <select 
              className="form-select" 
              value={newTransaction.category} 
              onChange={(e) => setNewTransaction({...newTransaction, category: e.target.value})}
              required
            >
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
              value={newTransaction.date} 
              onChange={(e) => setNewTransaction({...newTransaction, date: e.target.value})} 
              required 
            />
          </div>
          <div className="form-actions">
            <button type="submit" className="btn btn-primary">Add Transaction</button>
            {success && <p className="badge badge-success">{success}</p>}
          </div>
        </form>
      </div>
      <div className="stats-grid">
        <div className="stat-card">
          <h3>Total Transactions</h3>
          <p className="stat-value">{transactions.length}</p>
        </div>
        <div className="stat-card">
          <h3>Total Income</h3>
          <p className="stat-value">${transactions.filter(t => t.type === 'income').reduce((sum, t) => sum + parseFloat(t.amount), 0).toFixed(2)}</p>
        </div>
        <div className="stat-card">
          <h3>Total Expenses</h3>
          <p className="stat-value">${transactions.filter(t => t.type === 'expense').reduce((sum, t) => sum + parseFloat(t.amount), 0).toFixed(2)}</p>
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
                  <p>Amount: ${transaction.amount}</p>
                  <p>Type: <span className={transaction.type === 'expense' ? 'badge badge-danger' : 'badge badge-success'}>{transaction.type === 'expense' ? 'Expense' : 'Income'}</span></p>
                  <p>Category: {categories.find(c => c._id === transaction.category)?.name || 'Unknown'}</p>
                  <p>Date: {new Date(transaction.date).toLocaleDateString()}</p>
                </div>
                <div className="item-actions">
                  <button className="btn btn-danger btn-sm" onClick={() => handleDeleteTransaction(transaction._id)}>Delete</button>
                </div>
              </div>
            ))
          ) : (
            <div className="empty-state">
              <p>No transactions yet. Add your first transaction above.</p>
              <button className="btn btn-primary">Add Transaction</button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}