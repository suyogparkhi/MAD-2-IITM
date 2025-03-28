<!-- src/views/auth/CustomerRegister.vue -->
<template>
    <div class="customer-register">
      <h2 class="text-center mb-4">Register as Customer</h2>
      
      <div v-if="error" class="alert alert-danger">
        {{ error }}
      </div>
      
      <form @submit.prevent="handleRegister">
        <div class="mb-3">
          <label for="username" class="form-label">Username</label>
          <input
            type="text"
            class="form-control"
            id="username"
            v-model="form.username"
            required
          >
        </div>
        
        <div class="mb-3">
          <label for="email" class="form-label">Email</label>
          <input
            type="email"
            class="form-control"
            id="email"
            v-model="form.email"
            required
          >
        </div>
        
        <div class="mb-3">
          <label for="password" class="form-label">Password</label>
          <input
            type="password"
            class="form-control"
            id="password"
            v-model="form.password"
            required
          >
        </div>
        
        <div class="mb-3">
          <label for="fullname" class="form-label">Full Name</label>
          <input
            type="text"
            class="form-control"
            id="fullname"
            v-model="form.fullname"
            required
          >
        </div>
        
        <div class="mb-3">
          <label for="address" class="form-label">Address</label>
          <textarea
            class="form-control"
            id="address"
            v-model="form.address"
            rows="3"
            required
          ></textarea>
        </div>
        
        <div class="mb-3">
          <label for="pin_code" class="form-label">PIN Code</label>
          <input
            type="text"
            class="form-control"
            id="pin_code"
            v-model="form.pin_code"
            required
          >
        </div>
        
        <div class="d-grid gap-2">
          <button type="submit" class="btn btn-primary" :disabled="loading">
            <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
            Register
          </button>
          <router-link to="/login" class="btn btn-outline-secondary">
            Already have an account? Login
          </router-link>
        </div>
      </form>
    </div>
  </template>
  
  <script>
  import { mapGetters, mapActions } from 'vuex'
  
  export default {
    name: 'CustomerRegisterView',
    data() {
      return {
        form: {
          username: '',
          email: '',
          password: '',
          fullname: '',
          address: '',
          pin_code: ''
        }
      }
    },
    computed: {
      ...mapGetters('auth', ['loading', 'error'])
    },
    methods: {
      ...mapActions('auth', ['registerCustomer', 'clearError']),
      async handleRegister() {
        try {
          await this.registerCustomer(this.form)
          this.$router.push('/login')
        } catch (error) {
          // Error is handled in store
          console.error('Registration failed', error)
        }
      }
    },
    created() {
      // Clear any previous errors
      this.clearError()
    }
  }
  </script>