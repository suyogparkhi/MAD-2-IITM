<!-- src/views/professional/Dashboard.vue -->
<template>
  <div class="professional-dashboard">
    <h1 class="mb-4">Professional Dashboard</h1>
    
    <div class="row">
      <!-- Summary Cards -->
      <div class="col-md-4 mb-4">
        <div class="card h-100">
          <div class="card-body">
            <h5 class="card-title">Pending Requests</h5>
            <p class="card-text display-4">{{ stats.pending || 0 }}</p>
            <router-link to="/professional/requests" class="btn btn-primary">View Requests</router-link>
          </div>
        </div>
      </div>
      
      <div class="col-md-4 mb-4">
        <div class="card h-100">
          <div class="card-body">
            <h5 class="card-title">Completed Services</h5>
            <p class="card-text display-4">{{ stats.completed || 0 }}</p>
            <router-link to="/professional/requests?status=completed" class="btn btn-primary">View History</router-link>
          </div>
        </div>
      </div>
      
      <div class="col-md-4 mb-4">
        <div class="card h-100">
          <div class="card-body">
            <h5 class="card-title">Average Rating</h5>
            <p class="card-text display-4">{{ stats.rating || 'N/A' }}</p>
            <router-link to="/professional/profile" class="btn btn-primary">View Profile</router-link>
          </div>
        </div>
      </div>
    </div>
    
    <div class="row">
      <!-- Pending Service Requests -->
      <div class="col-12 mb-4">
        <div class="card">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h5 class="mb-0">Pending Service Requests</h5>
            <router-link to="/professional/requests" class="btn btn-sm btn-outline-primary">View All</router-link>
          </div>
          <div class="card-body">
            <div v-if="loading" class="text-center">
              <div class="spinner-border" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>
            
            <div v-else-if="pendingRequests.length === 0" class="text-center">
              <p>No pending service requests</p>
            </div>
            
            <div v-else class="table-responsive">
              <table class="table table-hover">
                <thead>
                  <tr>
                    <th>Service</th>
                    <th>Customer</th>
                    <th>Date Requested</th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="request in pendingRequests" :key="request.id">
                    <td>{{ request.service.name }}</td>
                    <td>{{ request.customer.user.fullname }}</td>
                    <td>{{ formatDate(request.date_of_request) }}</td>
                    <td><span :class="getStatusClass(request.service_status)">{{ request.service_status }}</span></td>
                    <td>
                      <div class="btn-group">
                        <button 
                          v-if="request.service_status === 'assigned'"
                          @click="acceptRequest(request.id)" 
                          class="btn btn-sm btn-success"
                        >
                          Accept
                        </button>
                        <button 
                          v-if="request.service_status === 'assigned'"
                          @click="rejectRequest(request.id)" 
                          class="btn btn-sm btn-danger"
                        >
                          Reject
                        </button>
                        <button 
                          v-if="request.service_status === 'accepted'"
                          @click="completeRequest(request.id)" 
                          class="btn btn-sm btn-primary"
                        >
                          Mark Complete
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
import bootstrap from 'bootstrap/dist/js/bootstrap.bundle.min.js'

export default {
  name: 'ProfessionalDashboard',
  data() {
    return {
      stats: {
        pending: 0,
        completed: 0,
        rating: null
      },
      pendingRequests: [],
      loading: false
    }
  },
  computed: {
    ...mapGetters('auth', ['user'])
  },
  methods: {
    formatDate(dateString) {
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
    },
    
    getStatusClass(status) {
      const statusClasses = {
        'requested': 'text-primary',
        'assigned': 'text-info',
        'accepted': 'text-success',
        'rejected': 'text-danger',
        'completed': 'text-success',
        'closed': 'text-secondary'
      }
      
      return statusClasses[status] || ''
    },
    
    async fetchDashboardData() {
      this.loading = true
      
      try {
        // Fetch dashboard stats
        const statsResponse = await this.$http.get('/professional/dashboard/stats')
        this.stats = statsResponse.data
        
        // Fetch pending requests
        const requestsResponse = await this.$http.get('/professional/service-requests/pending')
        this.pendingRequests = requestsResponse.data
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error)
        this.$store.dispatch('setNotification', {
          message: 'Failed to load dashboard data',
          type: 'error'
        }, { root: true })
      } finally {
        this.loading = false
      }
    },
    
    async acceptRequest(requestId) {
      try {
        await this.$http.put(`/professional/service-requests/${requestId}/accept`)
        
        this.$store.dispatch('setNotification', {
          message: 'Service request accepted successfully',
          type: 'success'
        }, { root: true })
        
        // Refresh the list
        this.fetchDashboardData()
      } catch (error) {
        console.error('Failed to accept request:', error)
        this.$store.dispatch('setNotification', {
          message: 'Failed to accept request',
          type: 'error'
        }, { root: true })
      }
    },
    
    async rejectRequest(requestId) {
      try {
        await this.$http.put(`/professional/service-requests/${requestId}/reject`)
        
        this.$store.dispatch('setNotification', {
          message: 'Service request rejected successfully',
          type: 'success'
        }, { root: true })
        
        // Refresh the list
        this.fetchDashboardData()
      } catch (error) {
        console.error('Failed to reject request:', error)
        this.$store.dispatch('setNotification', {
          message: 'Failed to reject request',
          type: 'error'
        }, { root: true })
      }
    },
    
    async completeRequest(requestId) {
      try {
        await this.$http.put(`/professional/service-requests/${requestId}/complete`)
        
        this.$store.dispatch('setNotification', {
          message: 'Service request marked as completed successfully',
          type: 'success'
        }, { root: true })
        
        // Refresh the list
        this.fetchDashboardData()
      } catch (error) {
        console.error('Failed to complete request:', error)
        this.$store.dispatch('setNotification', {
          message: 'Failed to complete request',
          type: 'error'
        }, { root: true })
      }
    }
  },
  created() {
    this.fetchDashboardData()
  }
}
</script>

<style scoped>
.card {
  transition: transform 0.3s;
}

.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}
</style>