import React, { useState, useEffect } from 'react'
import api from '../services/api'

const Tasks = () => {
  const [tasks, setTasks] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchTasks = async () => {
      try {
        const response = await api.get('/tasks')
        setTasks(response.data)
      } catch (err) {
        setError(err.response?.data?.message || 'Failed to fetch tasks')
      } finally {
        setLoading(false)
      }
    }

    fetchTasks()
  }, [])

  if (loading) return <div>Loading tasks...</div>
  if (error) return <div>Error: {error}</div>

  return (
    <div>
      <h1>Tasks</h1>
      <ul>
        {tasks.map(task => (
          <li key={task._id}>
            {task.title} - {task.category?.name || 'No category'}
          </li>
        ))}
      </ul>
    </div>
  )
}

export default Tasks