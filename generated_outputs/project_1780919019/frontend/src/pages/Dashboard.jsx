import React, { useEffect, useState } from 'react'
import api from '../services/api'

const Dashboard = () => {
  const [user, setUser] = useState(null)

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const response = await api.get('/users/me')
        setUser(response.data)
      } catch (error) {
        console.error('Failed to fetch user:', error)
      }
    }

    fetchUser()
  }, [])

  return (
    <div>
      <h1>Dashboard</h1>
      {user ? <p>Welcome, {user.username}!</p> : <p>Loading...</p>}
    </div>
  )
}

export default Dashboard