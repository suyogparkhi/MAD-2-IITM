<template>
  <nav class="navbar navbar-expand-lg navbar-light bg-light">
    <div class="container">
      <router-link class="navbar-brand" to="/">A-Z Household Services</router-link>
      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav ms-auto">
          <li class="nav-item" v-if="!isAuthenticated">
            <router-link class="nav-link" to="/auth/login">Login</router-link>
          </li>
          <li class="nav-item" v-if="!isAuthenticated">
            <router-link class="nav-link" to="/auth/register/customer">Register</router-link>
          </li>
          <li class="nav-item dropdown" v-if="isAuthenticated">
            <a class="nav-link dropdown-toggle" href="#" id="navbarDropdown" role="button" data-bs-toggle="dropdown" aria-expanded="false">
              {{ username }}
            </a>
            <div class="dropdown-menu dropdown-menu-end">
              <router-link class="dropdown-item" :to="profileLink">Profile</router-link>
              <div class="dropdown-divider"></div>
              <a class="dropdown-item" href="#" @click.prevent="logout">Logout</a>
            </div>
          </li>
        </ul>
      </div>
    </div>
  </nav>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'

export default {
  name: 'AppNavbar',
  computed: {
    ...mapGetters({
      isAuthenticated: 'auth/isAuthenticated',
      username: 'auth/username',
      userRole: 'auth/userRole'
    }),
    profileLink() {
      switch (this.userRole) {
        case 'admin':
          return '/admin';
        case 'professional':
          return '/professional/profile';
        case 'customer':
          return '/customer/profile';
        default:
          return '/';
      }
    }
  },
  methods: {
    ...mapActions({
      logoutAction: 'auth/logout'
    }),
    async logout() {
      await this.logoutAction();
      this.$router.push('/auth/login');
    }
  }
}
</script>

<style scoped>
.navbar {
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
</style>
  
  
 