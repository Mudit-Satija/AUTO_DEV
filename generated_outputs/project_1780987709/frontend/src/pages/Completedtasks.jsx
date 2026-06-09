import React, { useState, useEffect } from 'react'
import api from '../services/api'

const CompletedTasks = () => {
  const [tasks, setTasks] = useState([])

  useEffect(() => {
    const fetchCompletedTasks = async () => {
      try {
        const response = await api.get('/tasks/completed')
        setTasks(response.data)
      } catch (error) {
        console.error('Error fetching completed tasks:', error)
      }
    }

    fetchCompletedTasks()
  }, [])

  return (
    <div>
      <h1>Completed Tasks</h1>
      {tasks.length > 0 ? (
        <ul>
          {tasks.map(task => (
            <li key={task._id}>{task.title}</li>
          ))}
        </ul>
      ) : (
        <p>No completed tasks found.</p>
      )}
    </div>
  )
}

export default CompletedTasks