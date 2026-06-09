import React, { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import api from '../services/api'

const TaskDetails = () => {
  const { id } = useParams()
  const [task, setTask] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchTask = async () => {
      try {
        const response = await api.get(`/tasks/${id}`)
        setTask(response.data)
      } catch (error) {
        console.error('Error fetching task:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchTask()
  }, [id])

  if (loading) {
    return <p>Loading task details...</p>
  }

  if (!task) {
    return <p>Task not found.</p>
  }

  return (
    <div>
      <h1>Task Details</h1>
      <h2>{task.title}</h2>
      <p>{task.description}</p>
      <p>Status: {task.completed ? 'Completed' : 'Pending'}</p>
    </div>
  )
}

export default TaskDetails