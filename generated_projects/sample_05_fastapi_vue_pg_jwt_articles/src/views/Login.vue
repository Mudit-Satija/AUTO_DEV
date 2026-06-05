<template>
  <div class="login">
    <h2>Login</h2>
    <form @submit.prevent="handleLogin">
      <div>
        <label for="email">Email:</label>
        <input
          id="email"
          v-model="email"
          type="email"
          required
          placeholder="your@email.com"
        />
      </div>
      <div>
        <label for="password">Password:</label>
        <input
          id="password"
          v-model="password"
          type="password"
          required
          placeholder="your password"
        />
      </div>
      <button type="submit" :disabled="loading">Login</button>
    </form>
    <div v-if="error" class="error">{{ error }}</div>
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
      loading: false,
      error: null
    }
  },
  methods: {
    async handleLogin() {
      this.loading = true
      this.error = null
      try {
        const response = await api.post('/login', {
          email: this.email,
          password: this.password
        })
        localStorage.setItem('token', response.data.token)
        this.$router.push('/articles')
      } catch (err) {
        this.error = 'Login failed. Please check your credentials.'
        console.error(err)
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.login {
  max-width: 400px;
  margin: 50px auto;
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 8px;
}

.login h2 {
  text-align: center;
}

.login div {
  margin-bottom: 15px;
}

.login label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

.login input {
  width: 100%;
  padding: 8px;
  box-sizing: border-box;
}

.login button {
  width: 100%;
  padding: 10px;
  background-color: #42b983;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.login button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.error {
  color: red;
  margin-top: 10px;
  text-align: center;
}
</style>