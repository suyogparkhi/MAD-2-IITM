<template>
  <div class="admin-login-view">
    <h2 class="text-center mb-4">Admin Login</h2>
    
    <div v-if="error" class="alert alert-danger">
      {{ error }}
    </div>
    
    <form @submit.prevent="handleAdminLogin">
      <div class="mb-3">
        <label for="username" class="form-label">Admin Username</label>
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
        <label for="password" class="form-label">Admin Password</label>
        <input
          type="password"
          class="form-control"
          id="password"
          v-model="password"
          required
          autocomplete="current-password"
        >
      </div>
      
      <div class="d-grid">
        <button type="submit" class="btn btn-primary" :disabled="loading">
          <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
          Login as Admin
        </button>
      </div>
    </form>
    
    <div class="mt-4 text-center">
      <router-link to="/login" class="btn btn-outline-secondary">Back to Regular Login</router-link>
    </div>
    
    <div v-if="debugInfo" class="mt-4 p-3 bg-light">
      <h5>Debug Information</h5>
      <pre>{{ debugInfo }}</pre>
    </div>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'
import axios from 'axios'

export default {
  name: 'AdminLoginView',
  data() {
    return {
      username: 'admin',
      password: 'admin123',
      debugInfo: null
    }
  },
  computed: {
    ...mapGetters('auth', ['loading', 'error'])
  },
  methods: {
    ...mapActions('auth', ['login', 'clearError']),
    async handleAdminLogin() {
      try {
        this.debugInfo = `Attempting admin login with: ${this.username}\nAPI URL: ${axios.defaults.baseURL}`;
        console.log('Attempting admin login with:', this.username);
        console.log('API URL:', axios.defaults.baseURL);
        
        // Use the store action directly
        await this.login({
          username: this.username,
          password: this.password,
          rememberMe: true
        });
        
        // Redirect to admin dashboard
        this.$router.push('/admin');
      } catch (error) {
        this.debugInfo += `\nLogin action failed: ${error.message}`;
        if (error.response) {
          this.debugInfo += `\nStatus: ${error.response.status}`;
          this.debugInfo += `\nData: ${JSON.stringify(error.response.data, null, 2)}`;
        }
        console.error('Admin login failed', error);
      }
    }
  },
  created() {
    // Clear any previous errors
    this.clearError();
    
    // Pre-fill admin credentials
    this.username = 'admin';
    this.password = 'admin123';
  }
}
</script>

<style scoped>
.admin-login-view {
  max-width: 500px;
  margin: 0 auto;
  padding: 20px;
}

pre {
  font-size: 12px;
  white-space: pre-wrap;
  word-wrap: break-word;
}
</style> 