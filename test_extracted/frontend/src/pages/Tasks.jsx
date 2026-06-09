import React, { useEffect, useState } from 'react'
import api from '../services/api'

const Tasks = () => {
  const [tasks, setTasks] = useState([])

  useEffect(() => {
    const fetchTasks = async () => {
      try {
        const response = await api.get('/tasks')
        setTasks(response.data)
      } catch (error) {
        console.error('Failed to fetch tasks:', error)
      }
    }

    fetchTasks()
  }, [])

  return (
    <div>
      <h1>Tasks</h1>
      <ul>
        {tasks.map((task) => (
          <li key={task._id}>{task.title}</li>
        ))}
      </ul>
    </div>
  )
}

export default Tasks