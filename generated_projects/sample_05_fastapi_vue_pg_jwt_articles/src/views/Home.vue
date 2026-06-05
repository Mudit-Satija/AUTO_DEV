<template>
  <div class="home">
    <h1>Welcome to the Vue FastAPI JWT App</h1>
    <p>This is the home page.</p>
    <p>Use the navigation above to view articles or login.</p>
  </div>
</template>

<script>
export default {
  name: 'Home'
}
</script>

<style scoped>
.home {
  text-align: center;
  padding: 40px;
}

.home h1 {
  color: #42b983;
}
</style>