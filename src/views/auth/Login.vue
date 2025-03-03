<!-- src/views/auth/Login.vue -->
<template>
    <div class="login-view">
      <h2 class="text-center mb-4">Login</h2>
      
      <div v-if="error" class="alert alert-danger">
        {{ error }}
      </div>
      
      <form @submit.prevent="handleLogin">
        <div class="mb-3">
          <label for="username" class="form-label">Username</label>
          <input
            type="text"
            class="form-control"
            id="username"
            v-model="username"
            required
            autocomplete="username"
          >
        </div>
        
        <div class="mb-3">
          <label for="password" class="form-label">Password</label>
          <input
            type="password"
            class="form-control"
            id="password"
            v-model="password"
            required
            autocomplete="current-password"
          >
        </div>
        
        <div class="mb-3 form-check">
          <input
            type="checkbox"
            class="form-check-input"
            id="rememberMe"
            v-model="rememberMe"
          >
          <label class="form-check-label" for="rememberMe">Remember me</label>
        </div>
        
        <div class="d-grid">
          <button type="submit" class="btn btn-primary" :disabled="loading">
            <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
            Login
          </button>
        </div>
      </form>
      
      <div class="mt-4 text-center">
        <p>Don't have an account?</p>
        <div class="btn-group">
          <router-link to="/register/customer" class="btn btn-outline-primary">Register as Customer</router-link>
          <router-link to="/register/professional" class="btn btn-outline-secondary">Register as Professional</router-link>
        </div>
      </div>
      
      <div class="mt-4 text-center">
        <p class="text-muted">Are you an administrator?</p>
        <router-link to="/admin-login" class="btn btn-dark">Admin Login</router-link>
      </div>
    </div>
  </template>
  
  <script>
  import { mapGetters, mapActions } from 'vuex'
  
  export default {
    name: 'LoginView',
    data() {
      return {
        username: '',
        password: '',
        rememberMe: false
      }
    },
    computed: {
      ...mapGetters('auth', ['loading', 'error'])
    },
    methods: {
      ...mapActions('auth', ['login', 'clearError']),
      async handleLogin() {
        try {
          await this.login({
            username: this.username,
            password: this.password,
            rememberMe: this.rememberMe
          })
          
          // Redirect based on user role
          const userRole = this.$store.getters['auth/userRole']
          if (userRole === 'admin') {
            this.$router.push('/admin')
          } else if (userRole === 'professional') {
            this.$router.push('/professional')
          } else if (userRole === 'customer') {
            this.$router.push('/customer')
          }
        } catch (error) {
          // Error is handled in the store
          console.error('Login failed', error)
        }
      }
    },
    created() {
      // Clear any previous errors
      this.clearError()
    }
  }
  </script>
  
  <style scoped>
  .login-view {
    max-width: 400px;
    margin: 0 auto;
    padding: 20px;
  }
  </style>