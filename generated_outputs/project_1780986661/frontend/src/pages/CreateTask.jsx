import React, { useState } from 'react'
import api from '../services/api'

const CreateTask = () => {
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      await api.post('/tasks', { title, description })
      alert('Task created successfully!')
      setTitle('')
      setDescription('')
    } catch (error) {
      console.error('Error creating task:', error)
      alert('Failed to create task.')
    }
  }

  return (
    <div>
      <h1>Create Task</h1>
      <form onSubmit={handleSubmit}>
        <div>
          <label>Title:</label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
          />
        </div>
        <div>
          <label>Description:</label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            required
          />
        </div>
        <button type="submit">Create Task</button>
      </form>
    </div>
  )
}

export default CreateTask