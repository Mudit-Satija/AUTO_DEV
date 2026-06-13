import api from '../services/api'
import React, { useState, useEffect } from 'react'

const Products = () => {
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const res = await api.get('/products')
        setProducts(res.data)
        setLoading(false)
      } catch (err) {
        setError(err.response?.data?.message || err.message)
        setLoading(false)
      }
    }

    fetchProducts()
  }, [])

  if (loading) return <div>Loading...</div>
  if (error) return <div className="app-wrapper"><div className="page-header"><h1>Products</h1></div><div className="empty-state"><p>{error}</p><button className="btn btn-primary" onClick={() => window.location.reload()}>Retry</button></div></div>

  return (
    <div className="app-wrapper">
      <div className="page-header">
        <h1>Products</h1>
      </div>
      <div className="form-card">
        <div className="form-group">
          <label className="form-label">Product Name</label>
          <input className="form-input" type="text" placeholder="Enter product name" />
        </div>
        <div className="form-group">
          <label className="form-label">Price</label>
          <input className="form-input" type="number" placeholder="Enter price" />
        </div>
        <div className="form-group">
          <label className="form-label">Category</label>
          <select className="form-select">
            <option value="">Select category</option>
            <option value="electronics">Electronics</option>
            <option value="clothing">Clothing</option>
            <option value="books">Books</option>
          </select>
        </div>
        <div className="form-actions">
          <button className="btn btn-primary">Add Product</button>
        </div>
      </div>
      <div className="stats-grid">
        <div className="stat-card">
          <h3>Total Products</h3>
          <p className="stat-value">{products.length}</p>
        </div>
        <div className="stat-card">
          <h3>Total Inventory</h3>
          <p className="stat-value">{products.reduce((sum, product) => sum + (product.stock || 0), 0)}</p>
        </div>
      </div>
      <div className="section">
        <h2>All Products</h2>
        <div className="items-grid">
          {products.length > 0 ? (
            products.map((product) => (
              <div key={product._id} className="item-card">
                <div className="item-title">{product.name}</div>
                <div className="item-details">
                  <p>Price: ${product.price.toFixed(2)}</p>
                  <p>Stock: {product.stock || 0}</p>
                  <p>Category: {product.category || 'Uncategorized'}</p>
                </div>
                <div className="item-actions">
                  <button className="btn btn-sm btn-secondary">Edit</button>
                  <button className="btn btn-sm btn-danger">Delete</button>
                </div>
              </div>
            ))
          ) : (
            <div className="empty-state">
              <p>No products found</p>
              <button className="btn btn-primary">Add Your First Product</button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Products