<!-- src/views/customer/Dashboard.vue -->
<template>
    <div class="customer-dashboard">
      <div class="d-flex justify-content-between align-items-center mb-4">
        <h1>Customer Dashboard</h1>
        <div>
          <router-link to="/customer/services" class="btn btn-primary">
            <i class="bi bi-plus-circle me-1"></i> Book a Service
          </router-link>
        </div>
      </div>
      
      <!-- Loading State -->
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <p class="mt-2">Loading dashboard data...</p>
      </div>
      
      <!-- Error State -->
      <div v-else-if="error" class="alert alert-danger">
        {{ error }}
        <button @click="fetchDashboardData" class="btn btn-sm btn-outline-danger ms-2">Try Again</button>
      </div>
      
      <!-- Dashboard Content -->
      <div v-else>
        <!-- Stats Cards -->
        <div class="row g-3 mb-4">
          <div class="col-md-6 col-lg-3">
            <div class="card bg-light h-100">
              <div class="card-body">
                <h5 class="card-title text-primary">Requested</h5>
                <p class="display-4">{{ dashboardData.requested || 0 }}</p>
                <p class="card-text text-muted">Pending service requests</p>
              </div>
            </div>
          </div>
          
          <div class="col-md-6 col-lg-3">
            <div class="card bg-light h-100">
              <div class="card-body">
                <h5 class="card-title text-warning">In Progress</h5>
                <p class="display-4">{{ dashboardData.accepted || 0 }}</p>
                <p class="card-text text-muted">Services being processed</p>
              </div>
            </div>
          </div>
          
          <div class="col-md-6 col-lg-3">
            <div class="card bg-light h-100">
              <div class="card-body">
                <h5 class="card-title text-success">Completed</h5>
                <p class="display-4">{{ dashboardData.completed || 0 }}</p>
                <p class="card-text text-muted">Finished service requests</p>
              </div>
            </div>
          </div>
          
          <div class="col-md-6 col-lg-3">
            <div class="card bg-light h-100">
              <div class="card-body">
                <h5 class="card-title text-secondary">Total</h5>
                <p class="display-4">{{ dashboardData.total_requests || 0 }}</p>
                <p class="card-text text-muted">All-time service requests</p>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Recent Service Requests -->
        <div class="card mb-4">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h5 class="mb-0">Recent Service Requests</h5>
            <router-link to="/customer/requests" class="btn btn-sm btn-outline-primary">
              View All
            </router-link>
          </div>
          <div class="card-body p-0">
            <div v-if="recentRequests.length === 0" class="text-center py-5">
              <p class="mb-0">You don't have any service requests yet.</p>
              <router-link to="/customer/services" class="btn btn-primary mt-3">
                Browse Services
              </router-link>
            </div>
            <div v-else class="table-responsive">
              <table class="table table-hover">
                <thead class="table-light">
                  <tr>
                    <th>Service</th>
                    <th>Date Requested</th>
                    <th>Professional</th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="request in recentRequests" :key="request.id">
                    <td>
                      <div class="fw-bold">{{ request.service_name }}</div>
                    </td>
                    <td>{{ formatDate(request.date_of_request) }}</td>
                    <td>
                      <span v-if="request.professional_name">{{ request.professional_name }}</span>
                      <span v-else class="text-muted">Not assigned</span>
                    </td>
                    <td>
                      <span class="badge" :class="getStatusBadgeClass(request.service_status)">
                        {{ formatStatus(request.service_status) }}
                      </span>
                    </td>
                    <td>
                      <div class="btn-group">
                        <router-link 
                          :to="`/customer/requests/${request.id}`"
                          class="btn btn-sm btn-outline-primary"
                        >
                          View
                        </router-link>
                        <button 
                          v-if="request.service_status === 'completed'"
                          @click="closeRequest(request.id)"
                          class="btn btn-sm btn-outline-success"
                        >
                          Close
                        </button>
                        <button 
                          v-if="request.service_status === 'requested'"
                          @click="cancelRequest(request.id)"
                          class="btn btn-sm btn-outline-danger"
                        >
                          Cancel
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
        
        <!-- Popular Services -->
        <div class="card">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h5 class="mb-0">Popular Services</h5>
            <router-link to="/customer/services" class="btn btn-sm btn-outline-primary">
              Browse All
            </router-link>
          </div>
          <div class="card-body">
            <div class="row g-3">
              <div 
                v-for="service in popularServices" 
                :key="service.id"
                class="col-md-6 col-lg-3"
              >
                <div class="card h-100">
                  <div class="card-body">
                    <h5 class="card-title">{{ service.name }}</h5>
                    <p class="card-text small">{{ truncateText(service.description, 80) }}</p>
                    <div class="d-flex justify-content-between align-items-center">
                      <span class="fw-bold text-primary">${{ service.base_price.toFixed(2) }}</span>
                      <router-link 
                        :to="`/customer/services/${service.id}`"
                        class="btn btn-sm btn-primary"
                      >
                        Book Now
                      </router-link>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import { mapGetters, mapActions } from 'vuex'
  
  export default {
    name: 'CustomerDashboard',
    data() {
      return {
        dashboardData: {},
        recentRequests: [],
        popularServices: [],
        requestLoading: false
      }
    },
    computed: {
      ...mapGetters(['loading', 'error'])
    },
    methods: {
      ...mapActions('customers', ['fetchCustomerDashboard']),
      ...mapActions('serviceRequests', ['closeServiceRequest', 'cancelServiceRequest']),
      
      async fetchDashboardData() {
        try {
          // Fetch dashboard summary
          const dashboardData = await this.fetchCustomerDashboard()
          this.dashboardData = dashboardData
          
          // Fetch recent service requests
          const response = await this.$http.get('/customer/service-requests?limit=5')
          this.recentRequests = response.data
          
          // Fetch popular services
          const servicesResponse = await this.$http.get('/customer/services/popular')
          this.popularServices = servicesResponse.data
        } catch (error) {
          console.error('Failed to fetch dashboard data', error)
        }
      },
      
      async closeRequest(requestId) {
        this.requestLoading = true
        try {
          await this.closeServiceRequest(requestId)
          
          // Refresh data
          await this.fetchDashboardData()
          
          this.$store.dispatch('setNotification', {
            message: 'Service request closed successfully.',
            type: 'success'
          })
        } catch (error) {
          console.error('Failed to close service request', error)
        } finally {
          this.requestLoading = false
        }
      },
      
      async cancelRequest(requestId) {
        this.requestLoading = true
        try {
          await this.cancelServiceRequest(requestId)
          
          // Refresh data
          await this.fetchDashboardData()
          
          this.$store.dispatch('setNotification', {
            message: 'Service request cancelled successfully.',
            type: 'success'
          })
        } catch (error) {
          console.error('Failed to cancel service request', error)
        } finally {
          this.requestLoading = false
        }
      },
      
      formatDate(dateString) {
        if (!dateString) return 'N/A'
        
        const date = new Date(dateString)
        return date.toLocaleDateString('en-US', {
          year: 'numeric',
          month: 'short',
          day: 'numeric'
        })
      },
      
      formatStatus(status) {
        if (!status) return 'Unknown'
        
        // Capitalize first letter and replace underscores with spaces
        return status.charAt(0).toUpperCase() + status.slice(1).replace(/_/g, ' ')
      },
      
      getStatusBadgeClass(status) {
        switch (status) {
          case 'requested': return 'bg-primary'
          case 'assigned': return 'bg-info'
          case 'accepted': return 'bg-warning'
          case 'completed': return 'bg-success'
          case 'closed': return 'bg-secondary'
          default: return 'bg-secondary'
        }
      },
      
      truncateText(text, maxLength) {
        if (!text) return ''
        if (text.length <= maxLength) return text
        return text.slice(0, maxLength) + '...'
      }
    },
    async created() {
      await this.fetchDashboardData()
    }
  }
  </script>
  
  <style scoped>
  .customer-dashboard {
    min-height: 80vh;
  }
  </style>