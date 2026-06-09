import React, { useEffect, useState } from 'react'
import api from '../services/api'

const Home = () => {
  const [message, setMessage] = useState('')

  useEffect(() => {
    const fetchWelcome = async () => {
      try {
        const response = await api.get('/home')
        setMessage(response.data.message)
      } catch (error) {
        console.error('Error fetching home data:', error)
        setMessage('Failed to load home data.')
      }
    }

    fetchWelcome()
  }, [])

  return (
    <div>
      <h1>Welcome</h1>
      <p>{message}</p>
    </div>
  )
}

export default Home