<template>
  <div class="login">
    <h1>Login</h1>
    <form @submit.prevent="handleLogin">
      <div>
        <label for="email">Email:</label>
        <input id="email" v-model="email" type="email" required />
      </div>
      <div>
        <label for="password">Password:</label>
        <input id="password" v-model="password" type="password" required />
      </div>
      <button type="submit">Login</button>
    </form>
    <p v-if="error" class="error">{{ error }}</p>
  </div>
</template>

<script>
import api from '../services/api'

export default {
  name: 'Login',
  data() {
    return {
      email: '',
      password: '',
      error: ''
    }
  },
  methods: {
    async handleLogin() {
      this.error = ''
      try {
        const response = await api.post('/api/auth/login', {
          email: this.email,
          password: this.password
        })
        localStorage.setItem('token', response.data.token)
        this.$router.push('/dashboard')
      } catch (err) {
        this.error = err.response?.data?.message || 'Login failed'
      }
    }
  }
}
</script>

<style scoped>
.login {
  padding: 2rem;
  max-width: 400px;
  margin: 0 auto;
}

.login h1 {
  text-align: center;
}

.login form div {
  margin-bottom: 1rem;
}

.login form label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: bold;
}

.login form input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.login button {
  width: 100%;
  padding: 0.75rem;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
}

.login button:hover {
  background-color: #2980b9;
}

.error {
  color: #e74c3c;
  margin-top: 1rem;
  text-align: center;
}
</style>