<!-- src/views/admin/Dashboard.vue -->
<template>
    <div class="admin-dashboard">
      <div class="d-flex justify-content-between align-items-center mb-4">
        <h1>Admin Dashboard</h1>
        <div>
          <button @click="refreshData" class="btn btn-outline-primary">
            <i class="bi bi-arrow-clockwise me-1"></i> Refresh
          </button>
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
        <button @click="refreshData" class="btn btn-sm btn-outline-danger ms-2">Try Again</button>
      </div>
      
      <!-- Dashboard Content -->
      <div v-else>
        <!-- Stats Cards -->
        <div class="row g-3 mb-4">
          <!-- Total Services -->
          <div class="col-md-4 col-lg-3">
            <div class="card bg-light h-100">
              <div class="card-body">
                <h5 class="card-title text-primary">Services</h5>
                <p class="display-4">{{ dashboardData.total_services || 0 }}</p>
                <router-link to="/admin/services" class="btn btn-sm btn-outline-primary">Manage Services</router-link>
              </div>
            </div>
          </div>
          
          <!-- Total Professionals -->
          <div class="col-md-4 col-lg-3">
            <div class="card bg-light h-100">
              <div class="card-body">
                <h5 class="card-title text-success">Professionals</h5>
                <p class="display-4">{{ dashboardData.total_professionals || 0 }}</p>
                <div class="d-flex align-items-center">
                  <span class="badge bg-warning me-2">{{ dashboardData.pending_approvals || 0 }} Pending</span>
                  <router-link to="/admin/professionals" class="btn btn-sm btn-outline-success">View All</router-link>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Total Customers -->
          <div class="col-md-4 col-lg-3">
            <div class="card bg-light h-100">
              <div class="card-body">
                <h5 class="card-title text-info">Customers</h5>
                <p class="display-4">{{ dashboardData.total_customers || 0 }}</p>
                <router-link to="/admin/customers" class="btn btn-sm btn-outline-info">View Customers</router-link>
              </div>
            </div>
          </div>
          
          <!-- Service Requests -->
          <div class="col-md-4 col-lg-3">
            <div class="card bg-light h-100">
              <div class="card-body">
                <h5 class="card-title text-danger">Service Requests</h5>
                <p class="display-4">{{ dashboardData.total_service_requests || 0 }}</p>
                <router-link to="/admin/requests" class="btn btn-sm btn-outline-danger">Manage Requests</router-link>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Request Status Overview -->
        <div class="row mb-4">
          <div class="col-lg-6">
            <div class="card">
              <div class="card-header">
                <h5 class="mb-0">Service Request Status</h5>
              </div>
              <div class="card-body">
                <div class="chart-container" style="position: relative; height:300px;">
                  <!-- Insert chart component here (e.g., bar chart showing request status counts) -->
                  <div class="d-flex justify-content-between text-center w-100">
                    <div class="px-2">
                      <div class="p-3 bg-primary text-white rounded mb-2">
                        {{ dashboardData.service_request_stats?.requested || 0 }}
                      </div>
                      <div>Requested</div>
                    </div>
                    <div class="px-2">
                      <div class="p-3 bg-info text-white rounded mb-2">
                        {{ dashboardData.service_request_stats?.assigned || 0 }}
                      </div>
                      <div>Assigned</div>
                    </div>
                    <div class="px-2">
                      <div class="p-3 bg-warning text-white rounded mb-2">
                        {{ dashboardData.service_request_stats?.accepted || 0 }}
                      </div>
                      <div>In Progress</div>
                    </div>
                    <div class="px-2">
                      <div class="p-3 bg-success text-white rounded mb-2">
                        {{ dashboardData.service_request_stats?.completed || 0 }}
                      </div>
                      <div>Completed</div>
                    </div>
                    <div class="px-2">
                      <div class="p-3 bg-secondary text-white rounded mb-2">
                        {{ dashboardData.service_request_stats?.closed || 0 }}
                      </div>
                      <div>Closed</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div class="col-lg-6">
            <div class="card">
              <div class="card-header">
                <h5 class="mb-0">Recent Activity</h5>
              </div>
              <div class="card-body p-0">
                <div class="list-group list-group-flush">
                  <!-- Placeholder for recent activities -->
                  <div class="list-group-item" v-if="!recentActivity.length">
                    <div class="d-flex justify-content-center align-items-center p-3">
                      <p class="text-muted mb-0">No recent activity found</p>
                    </div>
                  </div>
                  <div class="list-group-item" v-for="(item, index) in recentActivity" :key="index">
                    <div class="d-flex w-100 justify-content-between">
                      <h6 class="mb-1">{{ item.title }}</h6>
                      <small class="text-muted">{{ item.time }}</small>
                    </div>
                    <p class="mb-1">{{ item.description }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Pending Approvals Section -->
        <div class="card mb-4">
          <div class="card-header">
            <h5 class="mb-0">Pending Professional Approvals</h5>
          </div>
          <div class="card-body">
            <div v-if="pendingProfessionals.length === 0" class="text-center py-3">
              <p class="mb-0">No pending approvals at this time.</p>
            </div>
            <div v-else class="table-responsive">
              <table class="table table-hover">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Service</th>
                    <th>Experience</th>
                    <th>Documents</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="professional in pendingProfessionals" :key="professional.id">
                    <td>{{ professional.username }}</td>
                    <td>{{ professional.service_name }}</td>
                    <td>{{ professional.experience }} years</td>
                    <td>
                      <button class="btn btn-sm btn-outline-secondary">
                        View Documents
                      </button>
                    </td>
                    <td>
                      <div class="btn-group">
                        <button 
                          @click="approveProfessional(professional.id)" 
                          class="btn btn-sm btn-success"
                          :disabled="actionLoading"
                        >
                          Approve
                        </button>
                        <button 
                          @click="rejectProfessional(professional.id)" 
                          class="btn btn-sm btn-danger"
                          :disabled="actionLoading"
                        >
                          Reject
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
        
        <!-- Export Reports Section -->
        <div class="card">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h5 class="mb-0">Generate Reports</h5>
            <router-link to="/admin/reports" class="btn btn-sm btn-outline-primary">
              View All Reports
            </router-link>
          </div>
          <div class="card-body">
            <div class="row g-3">
              <div class="col-md-6 col-lg-3">
                <div class="card h-100">
                  <div class="card-body">
                    <h6 class="card-title">Service Requests</h6>
                    <p class="card-text small">Export service requests data with filtering options.</p>
                    <button 
                      @click="exportServiceRequests" 
                      class="btn btn-sm btn-primary w-100"
                      :disabled="exportLoading"
                    >
                      <span v-if="exportLoading" class="spinner-border spinner-border-sm me-1"></span>
                      Export CSV
                    </button>
                  </div>
                </div>
              </div>
              
              <div class="col-md-6 col-lg-3">
                <div class="card h-100">
                  <div class="card-body">
                    <h6 class="card-title">Professionals</h6>
                    <p class="card-text small">Export service professionals data and statistics.</p>
                    <button 
                      @click="exportProfessionals" 
                      class="btn btn-sm btn-primary w-100"
                      :disabled="exportLoading"
                    >
                      <span v-if="exportLoading" class="spinner-border spinner-border-sm me-1"></span>
                      Export CSV
                    </button>
                  </div>
                </div>
              </div>
              
              <div class="col-md-6 col-lg-3">
                <div class="card h-100">
                  <div class="card-body">
                    <h6 class="card-title">Customers</h6>
                    <p class="card-text small">Export customer data and activity reports.</p>
                    <button 
                      @click="exportCustomers" 
                      class="btn btn-sm btn-primary w-100"
                      :disabled="exportLoading"
                    >
                      <span v-if="exportLoading" class="spinner-border spinner-border-sm me-1"></span>
                      Export CSV
                    </button>
                  </div>
                </div>
              </div>
              
              <div class="col-md-6 col-lg-3">
                <div class="card h-100">
                  <div class="card-body">
                    <h6 class="card-title">Monthly Report</h6>
                    <p class="card-text small">Generate comprehensive monthly activity report.</p>
                    <button 
                      @click="generateMonthlyReport" 
                      class="btn btn-sm btn-primary w-100"
                      :disabled="exportLoading"
                    >
                      <span v-if="exportLoading" class="spinner-border spinner-border-sm me-1"></span>
                      Generate Report
                    </button>
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
    name: 'AdminDashboard',
    data() {
      return {
        dashboardData: {},
        recentActivity: [],
        actionLoading: false,
        exportLoading: false
      }
    },
    computed: {
      ...mapGetters(['loading', 'error']),
      ...mapGetters('professionals', ['pendingProfessionals'])
    },
    methods: {
      ...mapActions('professionals', ['fetchProfessionals', 'verifyProfessional']),
      ...mapActions('reports', ['exportServiceRequests', 'generateAdminReport', 'generateMonthlyReport']),
      
      async refreshData() {
        try {
          // Fetch dashboard data
          const response = await this.$http.get('/admin/dashboard-summary')
          this.dashboardData = response.data
          
          // Fetch recent activity
          const activityResponse = await this.$http.get('/admin/recent-activity')
          this.recentActivity = activityResponse.data
          
          // Fetch pending professionals
          await this.fetchProfessionals()
        } catch (error) {
          console.error('Failed to refresh dashboard data', error)
          this.$store.dispatch('setNotification', {
            message: 'Failed to refresh dashboard data.',
            type: 'error'
          })
        }
      },
      
      async approveProfessional(professionalId) {
        this.actionLoading = true
        try {
          await this.verifyProfessional({ 
            professionalId, 
            status: 'approved' 
          })
          
          // Refresh data after approval
          await this.refreshData()
          
          this.$store.dispatch('setNotification', {
            message: 'Professional approved successfully.',
            type: 'success'
          })
        } catch (error) {
          console.error('Failed to approve professional', error)
        } finally {
          this.actionLoading = false
        }
      },
      
      async rejectProfessional(professionalId) {
        this.actionLoading = true
        try {
          await this.verifyProfessional({ 
            professionalId, 
            status: 'rejected' 
          })
          
          // Refresh data after rejection
          await this.refreshData()
          
          this.$store.dispatch('setNotification', {
            message: 'Professional rejected.',
            type: 'success'
          })
        } catch (error) {
          console.error('Failed to reject professional', error)
        } finally {
          this.actionLoading = false
        }
      },
      
      async exportServiceRequests() {
        this.exportLoading = true
        try {
          await this.generateAdminReport({ 
            reportType: 'requests',
            email: this.$store.getters['auth/user'].email
          })
          
          this.$store.dispatch('setNotification', {
            message: 'Service requests export started. You will receive an email when it\'s ready.',
            type: 'success'
          })
        } catch (error) {
          console.error('Failed to export service requests', error)
        } finally {
          this.exportLoading = false
        }
      },
      
      async exportProfessionals() {
        this.exportLoading = true
        try {
          await this.generateAdminReport({ 
            reportType: 'professionals',
            email: this.$store.getters['auth/user'].email
          })
          
          this.$store.dispatch('setNotification', {
            message: 'Professionals export started. You will receive an email when it\'s ready.',
            type: 'success'
          })
        } catch (error) {
          console.error('Failed to export professionals', error)
        } finally {
          this.exportLoading = false
        }
      },
      
      async exportCustomers() {
        this.exportLoading = true
        try {
          await this.generateAdminReport({ 
            reportType: 'customers',
            email: this.$store.getters['auth/user'].email
          })
          
          this.$store.dispatch('setNotification', {
            message: 'Customers export started. You will receive an email when it\'s ready.',
            type: 'success'
          })
        } catch (error) {
          console.error('Failed to export customers', error)
        } finally {
          this.exportLoading = false
        }
      }
    },
    async created() {
      await this.refreshData()
    }
  }
  </script>
  
  <style scoped>
  .card {
    box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
    transition: all 0.3s ease;
  }
  
  .card:hover {
    box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.1);
  }
  </style>