<template>
  <div id="app">
    <nav>
      <router-link to="/">Home</router-link> |
      <router-link to="/articles">Articles</router-link> |
      <router-link to="/login">Login</router-link>
    </nav>
    <router-view />
  </div>
</template>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}

nav {
  padding: 10px;
  border-bottom: 1px solid #eee;
}

nav a {
  margin-right: 15px;
  text-decoration: none;
  color: #42b983;
}

nav a.router-link-active {
  color: #42b983;
  font-weight: bold;
}
</style>