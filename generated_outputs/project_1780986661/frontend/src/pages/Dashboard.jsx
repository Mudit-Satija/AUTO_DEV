import React, { useState, useEffect } from 'react'
import api from '../services/api'

const Dashboard = () => {
  const [tasks, setTasks] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchTasks = async () => {
      try {
        const response = await api.get('/tasks')
        setTasks(response.data)
      } catch (error) {
        console.error('Error fetching tasks:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchTasks()
  }, [])

  if (loading) {
    return <p>Loading tasks...</p>
  }

  return (
    <div>
      <h1>Dashboard</h1>
      {tasks.length === 0 ? (
        <p>No tasks found. Create one to get started!</p>
      ) : (
        <ul>
          {tasks.map(task => (
            <li key={task._id}>
              <strong>{task.title}</strong> - {task.description}
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

export default Dashboard