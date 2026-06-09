import React, { useState, useEffect } from 'react'
import api from '../services/api'

const PendingTasks = () => {
  const [tasks, setTasks] = useState([])

  useEffect(() => {
    const fetchPendingTasks = async () => {
      try {
        const response = await api.get('/tasks/pending')
        setTasks(response.data)
      } catch (error) {
        console.error('Error fetching pending tasks:', error)
      }
    }

    fetchPendingTasks()
  }, [])

  return (
    <div>
      <h1>Pending Tasks</h1>
      {tasks.length > 0 ? (
        <ul>
          {tasks.map(task => (
            <li key={task._id}>{task.title}</li>
          ))}
        </ul>
      ) : (
        <p>No pending tasks found.</p>
      )}
    </div>
  )
}

export default PendingTasks