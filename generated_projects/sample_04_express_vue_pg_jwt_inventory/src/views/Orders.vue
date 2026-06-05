<template>
  <div class="orders">
    <h1>Orders</h1>
    <ul>
      <li v-for="order in orders" :key="order.id">
        <strong>Order #{{ order.id }}</strong> - {{ order.status }} - {{ order.total }}
      </li>
    </ul>
    <button @click="fetchOrders">Refresh Orders</button>
  </div>
</template>

<script>
import api from '../services/api'

export default {
  name: 'Orders',
  data() {
    return {
      orders: []
    }
  },
  async mounted() {
    await this.fetchOrders()
  },
  methods: {
    async fetchOrders() {
      try {
        const response = await api.get('/api/orders')
        this.orders = response.data
      } catch (err) {
        alert('Failed to fetch orders: ' + (err.response?.data?.message || err.message))
      }
    }
  }
}
</script>

<style scoped>
.orders {
  padding: 2rem;
}

.orders ul {
  list-style-type: none;
  padding: 0;
}

.orders li {
  padding: 0.75rem;
  margin-bottom: 0.5rem;
  background-color: #f9f9f9;
  border-radius: 4px;
  border-left: 4px solid #3498db;
}

.orders button {
  margin-top: 1rem;
  padding: 0.75rem 1.5rem;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.orders button:hover {
  background-color: #2980b9;
}
</style>