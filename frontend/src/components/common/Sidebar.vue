<template>
    <nav class="col-md-3 col-lg-2 d-md-block bg-light sidebar collapse">
      <div class="position-sticky pt-3">
        <!-- Admin Sidebar -->
        <div v-if="isAdmin">
          <h6 class="sidebar-heading d-flex justify-content-between align-items-center px-3 mt-4 mb-1 text-muted">
            <span>Admin Panel</span>
          </h6>
          <ul class="nav flex-column">
            <li class="nav-item">
              <router-link class="nav-link" to="/admin">
                <i class="bi bi-speedometer2 me-2"></i>
                Dashboard
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/admin/services">
                <i class="bi bi-tools me-2"></i>
                Services
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/admin/professionals">
                <i class="bi bi-person-badge me-2"></i>
                Professionals
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/admin/customers">
                <i class="bi bi-people me-2"></i>
                Customers
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/admin/requests">
                <i class="bi bi-list-check me-2"></i>
                Service Requests
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/admin/reports">
                <i class="bi bi-file-earmark-text me-2"></i>
                Reports
              </router-link>
            </li>
          </ul>
        </div>
        
        <!-- Professional Sidebar -->
        <div v-if="isProfessional">
          <h6 class="sidebar-heading d-flex justify-content-between align-items-center px-3 mt-4 mb-1 text-muted">
            <span>Professional Panel</span>
          </h6>
          <ul class="nav flex-column">
            <li class="nav-item">
              <router-link class="nav-link" to="/professional">
                <i class="bi bi-speedometer2 me-2"></i>
                Dashboard
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/professional/requests">
                <i class="bi bi-list-check me-2"></i>
                Service Requests
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/professional/profile">
                <i class="bi bi-person-circle me-2"></i>
                Profile
              </router-link>
            </li>
          </ul>
        </div>
        
        <!-- Customer Sidebar -->
        <div v-if="isCustomer">
          <h6 class="sidebar-heading d-flex justify-content-between align-items-center px-3 mt-4 mb-1 text-muted">
            <span>Customer Panel</span>
          </h6>
          <ul class="nav flex-column">
            <li class="nav-item">
              <router-link class="nav-link" to="/customer">
                <i class="bi bi-speedometer2 me-2"></i>
                Dashboard
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/customer/services">
                <i class="bi bi-tools me-2"></i>
                Browse Services
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/customer/professionals">
                <i class="bi bi-person-badge me-2"></i>
                Find Professionals
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/customer/service-requests">
                <i class="bi bi-list-check me-2"></i>
                My Requests
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/customer/profile">
                <i class="bi bi-person-circle me-2"></i>
                Profile
              </router-link>
            </li>
          </ul>
        </div>
      </div>
    </nav>
  </template>
  
  <script>
  import { mapGetters } from 'vuex'
  
  export default {
    name: 'Sidebar',
    computed: {
      ...mapGetters('auth', [
        'isAdmin',
        'isProfessional',
        'isCustomer'
      ])
    }
  }
  </script>
  
  <style scoped>
  .sidebar {
    height: 100vh;
  }
  
  .nav-link {
    color: #333;
    font-weight: 500;
  }
  
  .nav-link.router-link-active {
    color: #007bff;
  }
  </style>
  
  