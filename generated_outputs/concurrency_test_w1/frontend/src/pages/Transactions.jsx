import React, { useState, useEffect } from 'react';
import api from '../services/api';

const Transactions = () => {
  const [transactions, setTransactions] = useState([]);
  const [categories, setCategories] = useState([]);
  const [newTransaction, setNewTransaction] = useState({
    description: '',
    amount: '',
    type: 'expense',
    categoryId: '',
    date: new Date().toISOString().split('T')[0]
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    const fetchTransactionsAndCategories = async () => {
      try {
        setLoading(true);
        const [transactionsRes, categoriesRes] = await Promise.all([
          api.get('/api/transactions'),
          api.get('/api/categories')
        ]);
        setTransactions(transactionsRes.data);
        setCategories(categoriesRes.data);
        setError('');
      } catch (err) {
        setError('Failed to load transactions and categories. Please try again later.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchTransactionsAndCategories();
  }, []);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setNewTransaction(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!newTransaction.description || !newTransaction.amount || !newTransaction.categoryId || !newTransaction.date) return;

    try {
      await api.post('/api/transactions', newTransaction);
      setSuccess('Transaction added successfully!');
      setNewTransaction({
        description: '',
        amount: '',
        type: 'expense',
        categoryId: '',
        date: new Date().toISOString().split('T')[0]
      });
      const transactionsRes = await api.get('/api/transactions');
      setTransactions(transactionsRes.data);
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError('Failed to add transaction. Please check your inputs and try again.');
      console.error(err);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this transaction?')) return;

    try {
      await api.delete(`/api/transactions/${id}`);
      const transactionsRes = await api.get('/api/transactions');
      setTransactions(transactionsRes.data);
      setSuccess('Transaction deleted successfully!');
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError('Failed to delete transaction. Please try again later.');
      console.error(err);
    }
  };

  if (loading) return <div className="app-wrapper">Loading...</div>;
  if (error) return <div className="app-wrapper"><div className="empty-state"><p>{error}</p><button className="btn btn-primary" onClick={() => window.location.reload()}>Retry</button></div></div>;

  const totalIncome = transactions
    .filter(t => t.type === 'income')
    .reduce((sum, t) => sum + t.amount, 0);

  const totalExpenses = transactions
    .filter(t => t.type === 'expense')
    .reduce((sum, t) => sum + t.amount, 0);

  return (
    <div className="app-wrapper">
      <div className="page-header">
        <h1>Transactions</h1>
      </div>
      <div className="form-card">
        <form onSubmit={handleSubmit}>
          <div className="form-row">
            <div className="form-group">
              <label className="form-label" htmlFor="description">Description</label>
              <input
                type="text"
                id="description"
                name="description"
                value={newTransaction.description}
                onChange={handleInputChange}
                className="form-input"
                placeholder="e.g. Grocery shopping"
                required
              />
            </div>
            <div className="form-group">
              <label className="form-label" htmlFor="amount">Amount ($)</label>
              <input
                type="number"
                id="amount"
                name="amount"
                value={newTransaction.amount}
                onChange={handleInputChange}
                className="form-input"
                step="0.01"
                min="0"
                required
              />
            </div>
            <div className="form-group">
              <label className="form-label" htmlFor="type">Type</label>
              <select
                id="type"
                name="type"
                value={newTransaction.type}
                onChange={handleInputChange}
                className="form-select"
                required
              >
                <option value="expense">Expense</option>
                <option value="income">Income</option>
              </select>
            </div>
            <div className="form-group">
              <label className="form-label" htmlFor="categoryId">Category</label>
              <select
                id="categoryId"
                name="categoryId"
                value={newTransaction.categoryId}
                onChange={handleInputChange}
                className="form-select"
                required
              >
                <option value="">Select a category</option>
                {categories.map(category => (
                  <option key={category._id} value={category._id}>{category.name}</option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label className="form-label" htmlFor="date">Date</label>
              <input
                type="date"
                id="date"
                name="date"
                value={newTransaction.date}
                onChange={handleInputChange}
                className="form-input"
                required
              />
            </div>
          </div>
          <div className="form-actions">
            <button type="submit" className="btn btn-primary">Add Transaction</button>
          </div>
        </form>
        {success && <p style={{ color: 'green', marginTop: '0.5rem' }}>{success}</p>}
      </div>
      <div className="stats-grid">
        <div className="stat-card">
          <h3>Total Income</h3>
          <p className="stat-value">${totalIncome.toFixed(2)}</p>
        </div>
        <div className="stat-card">
          <h3>Total Expenses</h3>
          <p className="stat-value">${totalExpenses.toFixed(2)}</p>
        </div>
        <div className="stat-card">
          <h3>Net Balance</h3>
          <p className="stat-value">${(totalIncome - totalExpenses).toFixed(2)}</p>
        </div>
        <div className="stat-card">
          <h3>Transactions</h3>
          <p className="stat-value">{transactions.length}</p>
        </div>
      </div>
      <div className="section">
        <h2>All Transactions</h2>
        <div className="items-grid">
          {transactions.length > 0 ? (
            transactions.map(transaction => {
              const category = categories.find(c => c._id === transaction.categoryId) || { name: 'Unknown' };
              return (
                <div key={transaction._id} className="item-card">
                  <div className="item-title">{transaction.description}</div>
                  <div className="item-details">
                    <p>Category: {category.name}</p>
                    <p>Date: {new Date(transaction.date).toLocaleDateString()}</p>
                    <p className={transaction.type === 'income' ? 'badge badge-success' : 'badge badge-danger'}>
                      {transaction.type === 'income' ? '+' : '-'}${transaction.amount.toFixed(2)}
                    </p>
                  </div>
                  <div className="item-actions">
                    <button
                      className="btn btn-danger btn-sm"
                      onClick={() => handleDelete(transaction._id)}
                    >
                      Delete
                    </button>
                  </div>
                </div>
              );
            })
          ) : (
            <div className="empty-state">
              <p>No transactions recorded yet. Add your first transaction above.</p>
              <button className="btn btn-primary" onClick={() => document.querySelector('#description')?.focus()}>Add Transaction</button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Transactions;