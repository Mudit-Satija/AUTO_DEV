<template>
  <div class="dashboard">
    <h1>Dashboard</h1>
    <p>Welcome to your dashboard.</p>
    <button @click="logout">Logout</button>
  </div>
</template>

<script>
import api from '../services/api'

export default {
  name: 'Dashboard',
  methods: {
    logout() {
      localStorage.removeItem('token')
      this.$router.push('/login')
    }
  }
}
</script>

<style scoped>
.dashboard {
  padding: 2rem;
  text-align: center;
}

.dashboard button {
  margin-top: 1rem;
  padding: 0.5rem 1rem;
  background-color: #e74c3c;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.dashboard button:hover {
  background-color: #c0392b;
}
</style>