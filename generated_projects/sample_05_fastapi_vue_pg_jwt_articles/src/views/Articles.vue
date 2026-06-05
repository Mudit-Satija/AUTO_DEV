<template>
  <div class="articles">
    <h2>Articles</h2>
    <div v-if="loading">Loading...</div>
    <div v-else-if="error">{{ error }}</div>
    <ul v-else>
      <li v-for="article in articles" :key="article.id">
        <h3>{{ article.title }}</h3>
        <p>{{ article.content }}</p>
      </li>
    </ul>
    <button @click="fetchArticles">Refresh</button>
  </div>
</template>

<script>
import api from '../services/api'

export default {
  name: 'Articles',
  data() {
    return {
      articles: [],
      loading: false,
      error: null
    }
  },
  methods: {
    async fetchArticles() {
      this.loading = true
      this.error = null
      try {
        const response = await api.get('/articles')
        this.articles = response.data
      } catch (err) {
        this.error = 'Failed to fetch articles'
        console.error(err)
      } finally {
        this.loading = false
      }
    }
  },
  mounted() {
    this.fetchArticles()
  }
}
</script>

<style scoped>
.articles {
  padding: 20px;
}

.articles ul {
  list-style-type: none;
  padding: 0;
}

.articles li {
  margin-bottom: 20px;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
}
</style>