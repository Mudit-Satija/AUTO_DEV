import React, { useState, useEffect } from 'react'
import api from '../services/api'

const Categories = () => {
  const [categories, setCategories] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const response = await api.get('/categories')
        setCategories(response.data)
      } catch (err) {
        setError(err.response?.data?.message || 'Failed to fetch categories')
      } finally {
        setLoading(false)
      }
    }

    fetchCategories()
  }, [])

  if (loading) return <div>Loading categories...</div>
  if (error) return <div>Error: {error}</div>

  return (
    <div>
      <h1>Categories</h1>
      <ul>
        {categories.map(category => (
          <li key={category._id}>{category.name}</li>
        ))}
      </ul>
    </div>
  )
}

export default Categories