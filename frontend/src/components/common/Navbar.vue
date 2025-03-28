<template>
  <div>
    <b-navbar toggleable="lg" variant="primary" type="dark" class="navbar-custom" fixed="top">
      <div class="container">
        <b-navbar-brand to="/" class="d-flex align-items-center">
          <i class="fas fa-tools mr-2"></i>
          <span class="brand-text">A-Z Household Services</span>
        </b-navbar-brand>

        <b-navbar-toggle target="nav-collapse"></b-navbar-toggle>

        <b-collapse id="nav-collapse" is-nav>
          <b-navbar-nav class="ml-auto">
            <b-nav-item to="/services" v-if="isAuthenticated && userRole === 'customer'">Services</b-nav-item>
            <b-nav-item to="/about">About</b-nav-item>
            <b-nav-item to="/contact">Contact</b-nav-item>
            
            <!-- Not authenticated menu -->
            <template v-if="!isAuthenticated">
              <b-nav-item to="/auth/login" class="auth-button login-btn">Login</b-nav-item>
              <b-nav-item to="/auth/register/customer" class="auth-button register-btn">Register</b-nav-item>
            </template>
            
            <!-- User dropdown when authenticated -->
            <b-nav-item-dropdown right v-if="isAuthenticated" class="user-dropdown">
              <template #button-content>
                <i class="fas fa-user-circle mr-1"></i>
                <span>{{ username }}</span>
              </template>
              <b-dropdown-item :to="dashboardLink">
                <i class="fas fa-tachometer-alt mr-2"></i> Dashboard
              </b-dropdown-item>
              <b-dropdown-item :to="profileLink">
                <i class="fas fa-user mr-2"></i> Profile
              </b-dropdown-item>
              <b-dropdown-divider></b-dropdown-divider>
              <b-dropdown-item @click="logout">
                <i class="fas fa-sign-out-alt mr-2"></i> Logout
              </b-dropdown-item>
            </b-nav-item-dropdown>
          </b-navbar-nav>
        </b-collapse>
      </div>
    </b-navbar>
    
    <!-- Spacer to prevent content from hiding under fixed navbar -->
    <div class="navbar-spacer"></div>
  </div>
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
          return '/admin/profile';
        case 'professional':
          return '/professional/profile';
        case 'customer':
          return '/customer/profile';
        default:
          return '/';
      }
    },
    dashboardLink() {
      switch (this.userRole) {
        case 'admin':
          return '/admin';
        case 'professional':
          return '/professional';
        case 'customer':
          return '/customer';
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
      this.$bvToast.toast('Successfully logged out', {
        title: 'Logout',
        variant: 'success',
        solid: true
      });
    }
  }
}
</script>

<style scoped>
.navbar-custom {
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 0.7rem 1rem;
}

.brand-text {
  font-weight: 600;
  font-size: 1.2rem;
  letter-spacing: 0.5px;
}

.auth-button {
  margin-left: 10px;
  font-weight: 500;
}

.login-btn:hover, .register-btn:hover {
  color: white !important;
  text-decoration: none;
}

.user-dropdown .dropdown-menu {
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  border: none;
  padding: 8px 0;
}

.user-dropdown .dropdown-item {
  padding: 8px 20px;
  color: #333;
}

.user-dropdown .dropdown-item:hover {
  background-color: #f8f9fa;
}

.navbar-spacer {
  height: 70px;
}
</style>
  
  
 