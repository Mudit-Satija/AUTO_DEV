import api from '../services/api'
import { useState, useEffect } from 'react'

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

  if (loading) return <div className="app-wrapper">Loading...</div>
  if (error) return <div className="app-wrapper">Error: {error}</div>

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
        <h2>Product List</h2>
        <div className="items-grid">
          {products.length > 0 ? (
            products.map(product => (
              <div key={product._id} className="item-card">
                <div className="item-header">
                  <h3 className="item-title">{product.name}</h3>
                </div>
                <div className="item-details">
                  <p><strong>Price:</strong> ${product.price.toFixed(2)}</p>
                  <p><strong>Category:</strong> {product.category || 'Uncategorized'}</p>
                  <p><strong>Stock:</strong> {product.stock || 0}</p>
                  <p><strong>Created:</strong> {new Date(product.createdAt).toLocaleDateString()}</p>
                </div>
                <div className="item-actions">
                  <button className="btn btn-secondary">Edit</button>
                  <button className="btn btn-danger">Delete</button>
                </div>
              </div>
            ))
          ) : (
            <div className="empty-state">
              <p>No products found. Add your first product.</p>
              <button className="btn btn-primary">Add Product</button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Products