import React, { useState, useEffect } from 'react';
import api from '../services/api';

const Budgets = () => {
  const [budgets, setBudgets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [newBudget, setNewBudget] = useState({
    category: '',
    amount: '',
    period: 'monthly'
  });

  useEffect(() => {
    const fetchBudgets = async () => {
      try {
        setLoading(true);
        const res = await api.get('/api/budgets');
        setBudgets(res.data);
        setError('');
      } catch (err) {
        setError('Failed to load budgets. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchBudgets();
  }, []);

  const handleInputChange = (e) => {
    setNewBudget({
      ...newBudget,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await api.post('/api/budgets', newBudget);
      setNewBudget({ category: '', amount: '', period: 'monthly' });
      const res = await api.get('/api/budgets');
      setBudgets(res.data);
    } catch (err) {
      setError('Failed to create budget. Please check your inputs and try again.');
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this budget?')) return;
    try {
      await api.delete(`/api/budgets/${id}`);
      const res = await api.get('/api/budgets');
      setBudgets(res.data);
    } catch (err) {
      setError('Failed to delete budget. Please try again later.');
    }
  };

  if (loading) return <div className="app-wrapper">Loading...</div>;
  if (error) return <div className="app-wrapper"><div className="empty-state"><p>{error}</p><button className="btn btn-primary" onClick={() => window.location.reload()}>Retry</button></div></div>;

  return (
    <div className="app-wrapper">
      <div className="page-header">
        <h1>Budgets</h1>
      </div>
      <div className="form-card">
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Category</label>
            <select
              name="category"
              value={newBudget.category}
              onChange={handleInputChange}
              className="form-select"
              required
            >
              <option value="">Select a category</option>
              <option value="Food">Food</option>
              <option value="Transportation">Transportation</option>
              <option value="Housing">Housing</option>
              <option value="Utilities">Utilities</option>
              <option value="Entertainment">Entertainment</option>
              <option value="Healthcare">Healthcare</option>
              <option value="Education">Education</option>
              <option value="Other">Other</option>
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">Amount ($)</label>
            <input
              type="number"
              name="amount"
              value={newBudget.amount}
              onChange={handleInputChange}
              className="form-input"
              placeholder="Enter budget amount"
              required
              min="0"
              step="0.01"
            />
          </div>
          <div className="form-group">
            <label className="form-label">Period</label>
            <select
              name="period"
              value={newBudget.period}
              onChange={handleInputChange}
              className="form-select"
              required
            >
              <option value="monthly">Monthly</option>
              <option value="weekly">Weekly</option>
              <option value="annually">Annually</option>
            </select>
          </div>
          <div className="form-actions">
            <button type="submit" className="btn btn-primary">Add Budget</button>
          </div>
        </form>
      </div>
      <div className="stats-grid">
        <div className="stat-card">
          <h3>Total Budgeted</h3>
          <p className="stat-value">${budgets.reduce((sum, b) => sum + parseFloat(b.amount || 0), 0).toFixed(2)}</p>
        </div>
        <div className="stat-card">
          <h3>Active Budgets</h3>
          <p className="stat-value">{budgets.length}</p>
        </div>
        <div className="stat-card">
          <h3>Over Budget</h3>
          <p className="stat-value">{budgets.filter(b => b.spent > b.amount).length}</p>
        </div>
        <div className="stat-card">
          <h3>Under Budget</h3>
          <p className="stat-value">{budgets.filter(b => b.spent < b.amount).length}</p>
        </div>
      </div>
      <div className="section">
        <h2>Current Budgets</h2>
        {budgets.length === 0 ? (
          <div className="empty-state">
            <p>No budgets set yet. Add a budget to get started.</p>
            <button className="btn btn-primary" onClick={() => document.querySelector('form').reset()}>Add Budget</button>
          </div>
        ) : (
          <div className="items-grid">
            {budgets.map((budget) => (
              <div key={budget._id} className="item-card">
                <div className="item-title">{budget.category}</div>
                <div className="item-details">
                  <span>Amount: ${budget.amount.toFixed(2)}</span>
                  <span>Period: {budget.period}</span>
                  <span>Spent: ${budget.spent?.toFixed(2) || 0}</span>
                </div>
                <div className="item-actions">
                  <button
                    className="btn btn-danger btn-sm"
                    onClick={() => handleDelete(budget._id)}
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Budgets;