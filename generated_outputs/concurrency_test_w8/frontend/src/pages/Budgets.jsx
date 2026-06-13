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
        setError('Failed to load budgets');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchBudgets();
  }, []);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setNewBudget(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await api.post('/api/budgets', newBudget);
      setNewBudget({ category: '', amount: '', period: 'monthly' });
      const res = await api.get('/api/budgets');
      setBudgets(res.data);
    } catch (err) {
      setError('Failed to create budget');
      console.error(err);
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
          <div className="form-row">
            <div className="form-group">
              <label className="form-label" htmlFor="category">Category</label>
              <select
                id="category"
                name="category"
                className="form-select"
                value={newBudget.category}
                onChange={handleInputChange}
                required
              >
                <option value="">Select category</option>
                <option value="food">Food</option>
                <option value="transportation">Transportation</option>
                <option value="housing">Housing</option>
                <option value="utilities">Utilities</option>
                <option value="entertainment">Entertainment</option>
                <option value="healthcare">Healthcare</option>
                <option value="education">Education</option>
                <option value="savings">Savings</option>
                <option value="other">Other</option>
              </select>
            </div>
            <div className="form-group">
              <label className="form-label" htmlFor="amount">Amount ($)</label>
              <input
                type="number"
                id="amount"
                name="amount"
                className="form-input"
                value={newBudget.amount}
                onChange={handleInputChange}
                required
                min="0"
                step="0.01"
              />
            </div>
            <div className="form-group">
              <label className="form-label" htmlFor="period">Period</label>
              <select
                id="period"
                name="period"
                className="form-select"
                value={newBudget.period}
                onChange={handleInputChange}
              >
                <option value="monthly">Monthly</option>
                <option value="weekly">Weekly</option>
                <option value="yearly">Yearly</option>
              </select>
            </div>
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
      </div>
      <div className="section">
        <h2>Budget Overview</h2>
        <div className="items-grid">
          {budgets.length > 0 ? (
            budgets.map((budget, index) => (
              <div key={index} className="item-card">
                <div className="item-title">{budget.category}</div>
                <div className="item-details">
                  <span>Amount: ${budget.amount.toFixed(2)}</span>
                  <span>Period: {budget.period}</span>
                  <span>Spent: ${budget.spent?.toFixed(2) || '0.00'}</span>
                  <span className={budget.spent > budget.amount ? 'badge badge-danger' : 'badge badge-success'}>
                    {budget.spent > budget.amount ? 'Over' : 'Under'} Budget
                  </span>
                </div>
                <div className="item-actions">
                  <button className="btn btn-secondary btn-sm">Edit</button>
                  <button className="btn btn-danger btn-sm">Delete</button>
                </div>
              </div>
            ))
          ) : (
            <div className="empty-state">
              <p>No budgets set yet. Add your first budget above.</p>
              <button className="btn btn-primary">Add Budget</button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Budgets;