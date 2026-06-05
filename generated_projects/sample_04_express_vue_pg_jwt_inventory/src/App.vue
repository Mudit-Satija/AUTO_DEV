<template>
  <div id="app">
    <nav>
      <router-link to="/dashboard">Dashboard</router-link> |
      <router-link to="/login">Login</router-link> |
      <router-link to="/orders">Orders</router-link>
    </nav>
    <router-view />
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}

nav {
  padding: 1rem;
  background-color: #f5f5f5;
  border-bottom: 1px solid #ddd;
}

nav a {
  margin-right: 1rem;
  text-decoration: none;
  color: #3498db;
}

nav a.router-link-active {
  color: #2980b9;
  font-weight: bold;
}
</style>