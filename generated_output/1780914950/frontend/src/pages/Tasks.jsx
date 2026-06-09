import React, { useState, useEffect } from 'react'
import api from '../services/api'

const Tasks = () => {
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

  if (loading) return <div>Loading tasks...</div>

  return (
    <div>
      <h1>Tasks</h1>
      <ul>
        {tasks.map(task => (
          <li key={task._id}>{task.title} - {task.categoryId}</li>
        ))}
      </ul>
    </div>
  )
}

export default Tasks