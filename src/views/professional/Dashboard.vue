<!-- src/views/professional/Dashboard.vue -->
<template>
    <div class="professional-dashboard">
      <div class="d-flex justify-content-between align-items-center mb-4">
        <h1>Professional Dashboard</h1>
        <router-link to="/professional/profile" class="btn btn-outline-primary">
          <i class="bi bi-person-circle me-1"></i> View Profile
        </router-link>
      </div>
      
      <!-- Verification Alert (if not yet approved) -->
      <div v-if="!isApproved" class="alert alert-warning mb-4">
        <div class="d-flex align-items-center">
          <i class="bi bi-exclamation-triangle-fill me-2 fs-4"></i>
          <div>
            <h5 class="alert-heading mb-1">Verification Pending</h5>
            <p class="mb-0">Your account is currently under review. You'll be able to accept service requests once an admin approves your profile.</p>
          </div>
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
      
      <!-- Dashboard Content (only visible if approved) -->
      <div v-else-if="isApproved">
        <!-- Stats Cards -->
        <div class="row g-3 mb-4">
          <div class="col-md-6 col-lg-3">
            <div class="card bg-light h-100">
              <div class="card-body">
                <h5 class="card-title text-primary">Available</h5>
                <p class="display-4">{{ dashboardData.available_requests || 0 }}</p>
                <p class="card-text text-muted">Requests waiting for acceptance</p>
              </div>
            </div>
          </div>
          
          <div class="col-md-6 col-lg-3">
            <div class="card bg-light h-100">
              <div class="card-body">
                <h5 class="card-title text-warning">In Progress</h5>
                <p class="display-4">{{ dashboardData.accepted_requests || 0 }}</p>
                <p class="card-text text-muted">Jobs you're currently working on</p>
              </div>
            </div>
          </div>
          
          <div class="col-md-6 col-lg-3">
            <div class="card bg-light h-100">
              <div class="card-body">
                <h5 class="card-title text-success">Completed</h5>
                <p class="display-4">{{ dashboardData.completed_requests || 0 }}</p>
                <p class="card-text text-muted">Successfully finished jobs</p>
              </div>
            </div>
          </div>
          
          <div class="col-md-6 col-lg-3">
            <div class="card bg-light h-100">
              <div class="card-body">
                <h5 class="card-title text-info">Rating</h5>
                <p class="display-4">{{ dashboardData.average_rating ? dashboardData.average_rating.toFixed(1) : 'N/A' }}</p>
                <p class="card-text text-muted">Your average customer rating</p>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Available Service Requests -->
        <div class="card mb-4">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h5 class="mb-0">Available Service Requests</h5>
            <router-link to="/professional/requests" class="btn btn-sm btn-outline-primary">View All</router-link>
          </div>
          <div class="card-body p-0">
            <div v-if="availableRequests.length === 0" class="text-center py-5">
              <p class="mb-0">No available service requests for your service type at the moment.</p>
            </div>
            <div v-else>
              <div class="list-group list-group-flush">
                <div 
                  v-for="request in availableRequests" 
                  :key="request.id"
                  class="list-group-item"
                >
                  <div class="d-flex justify-content-between align-items-start">
                    <div>
                      <h6 class="mb-1">{{ request.service_name }}</h6>
                      <p class="mb-1 text-muted small">
                        <i class="bi bi-geo-alt me-1"></i>
                        {{ request.customer_address }}, {{ request.customer_pin_code }}
                      </p>
                      <p class="mb-1">
                        <small>Requested on: {{ formatDate(request.date_of_request) }}</small>
                      </p>
                      <div v-if="request.remarks" class="mt-2 small">
                        <strong>Customer Notes:</strong> {{ request.remarks }}
                      </div>
                    </div>
                    <div>
                      <button 
                        @click="acceptRequest(request.id)" 
                        class="btn btn-success btn-sm me-1"
                        :disabled="actionLoading"
                      >
                        Accept
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Current Jobs -->
        <div class="card mb-4">
          <div class="card-header">
            <h5 class="mb-0">Current Jobs</h5>
          </div>
          <div class="card-body p-0">
            <div v-if="currentJobs.length === 0" class="text-center py-5">
              <p class="mb-0">You don't have any active jobs at the moment.</p>
            </div>
            <div v-else class="table-responsive">
              <table class="table table-hover align-middle mb-0">
                <thead class="table-light">
                  <tr>
                    <th>Service</th>
                    <th>Customer</th>
                    <th>Location</th>
                    <th>Date Requested</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="job in currentJobs" :key="job.id">
                    <td>{{ job.service_name }}</td>
                    <td>{{ job.customer_name }}</td>
                    <td>{{ job.customer_address }}</td>
                    <td>{{ formatDate(job.date_of_request) }}</td>
                    <td>
                      <button 
                        @click="completeJob(job.id)" 
                        class="btn btn-sm btn-outline-success"
                        :disabled="actionLoading"
                      >
                        Mark Complete
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
        
        <!-- Recent Completed Jobs -->
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">Recently Completed Jobs</h5>
          </div>
          <div class="card-body p-0">
            <div v-if="completedJobs.length === 0" class="text-center py-5">
              <p class="mb-0">You don't have any completed jobs yet.</p>
            </div>
            <div v-else class="table-responsive">
              <table class="table table-hover align-middle mb-0">
                <thead class="table-light">
                  <tr>
                    <th>Service</th>
                    <th>Customer</th>
                    <th>Date Completed</th>
                    <th>Status</th>
                    <th>Rating</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="job in completedJobs" :key="job.id">
                    <td>{{ job.service_name }}</td>
                    <td>{{ job.customer_name }}</td>
                    <td>{{ formatDate(job.date_of_completion) }}</td>
                    <td>
                      <span class="badge" :class="job.service_status === 'completed' ? 'bg-success' : 'bg-secondary'">
                        {{ job.service_status === 'completed' ? 'Completed' : 'Closed' }}
                      </span>
                    </td>
                    <td>
                      <div v-if="job.rating" class="d-flex align-items-center">
                        <span class="me-1">{{ job.rating }}</span>
                        <i class="bi bi-star-fill text-warning"></i>
                      </div>
                      <span v-else class="text-muted">No rating yet</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import { mapGetters, mapActions } from 'vuex'
  
  export default {
    name: 'ProfessionalDashboard',
    data() {
      return {
        dashboardData: {},
        availableRequests: [],
        currentJobs: [],
        completedJobs: [],
        actionLoading: false
      }
    },
    computed: {
      ...mapGetters('professionals', ['currentProfessional', 'loading', 'error']),
      
      isApproved() {
        return this.currentProfessional && this.currentProfessional.verification_status === 'approved'
      }
    },
    methods: {
      ...mapActions('professionals', ['fetchProfessionalProfile', 'fetchProfessionalDashboard']),
      ...mapActions('serviceRequests', ['updateRequestStatus']),
      
      async fetchDashboardData() {
        try {
          // Fetch professional profile
          await this.fetchProfessionalProfile()
          
          // Only proceed if approved
          if (this.isApproved) {
            // Fetch dashboard data
            const dashboardData = await this.fetchProfessionalDashboard()
            this.dashboardData = dashboardData
            
            // Fetch available requests
            const availableResponse = await this.$http.get('/professional/available-requests')
            this.availableRequests = availableResponse.data
            
            // Fetch current jobs
            const currentJobsResponse = await this.$http.get('/professional/service-requests?status=accepted')
            this.currentJobs = currentJobsResponse.data
            
            // Fetch completed jobs
            const completedJobsResponse = await this.$http.get('/professional/service-requests?status=completed,closed&limit=5')
            this.completedJobs = completedJobsResponse.data
          }
        } catch (error) {
          console.error('Failed to fetch dashboard data', error)
        }
      },
      
      async acceptRequest(requestId) {
        this.actionLoading = true
        try {
          await this.updateRequestStatus({ 
            requestId, 
            action: 'accept' 
          })
          
          // Refresh dashboard data
          await this.fetchDashboardData()
          
          this.$store.dispatch('setNotification', {
            message: 'Service request accepted successfully.',
            type: 'success'
          })
        } catch (error) {
          console.error('Failed to accept request', error)
          
          this.$store.dispatch('setNotification', {
            message: 'Failed to accept service request.',
            type: 'error'
          })
        } finally {
          this.actionLoading = false
        }
      },
      
      async completeJob(requestId) {
        this.actionLoading = true
        try {
          await this.updateRequestStatus({ 
            requestId, 
            action: 'complete' 
          })
          
          // Refresh dashboard data
          await this.fetchDashboardData()
          
          this.$store.dispatch('setNotification', {
            message: 'Job marked as completed successfully.',
            type: 'success'
          })
        } catch (error) {
          console.error('Failed to complete job', error)
          
          this.$store.dispatch('setNotification', {
            message: 'Failed to mark job as completed.',
            type: 'error'
          })
        } finally {
          this.actionLoading = false
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
      }
    },
    created() {
      this.fetchDashboardData()
    }
  }
  </script>
  
  <style scoped>
  .professional-dashboard {
    min-height: 80vh;
  }
  </style>