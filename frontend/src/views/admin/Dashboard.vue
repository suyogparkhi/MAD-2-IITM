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
        <div class="row g-4 mb-4">
          <div class="col-md-3">
            <div class="card h-100">
              <div class="card-body">
                <div class="d-flex justify-content-between align-items-center">
                  <div>
                    <h6 class="text-muted mb-1">Total Services</h6>
                    <h3 class="mb-0">{{ dashboardStats.services_count || 0 }}</h3>
                  </div>
                  <div class="icon-bg bg-light-primary">
                    <i class="bi bi-tools text-primary"></i>
                  </div>
                </div>
                <div class="mt-3">
                  <router-link to="/admin/services" class="btn btn-sm btn-outline-primary">
                    View Services
                  </router-link>
                </div>
              </div>
            </div>
          </div>
          
          <div class="col-md-3">
            <div class="card h-100">
              <div class="card-body">
                <div class="d-flex justify-content-between align-items-center">
                  <div>
                    <h6 class="text-muted mb-1">Professionals</h6>
                    <h3 class="mb-0">{{ dashboardStats.professionals_count || 0 }}</h3>
                  </div>
                  <div class="icon-bg bg-light-success">
                    <i class="bi bi-person-badge text-success"></i>
                  </div>
                </div>
                <div class="mt-3">
                  <router-link to="/admin/professionals" class="btn btn-sm btn-outline-success">
                    View Professionals
                  </router-link>
                </div>
              </div>
            </div>
          </div>
          
          <div class="col-md-3">
            <div class="card h-100">
              <div class="card-body">
                <div class="d-flex justify-content-between align-items-center">
                  <div>
                    <h6 class="text-muted mb-1">Customers</h6>
                    <h3 class="mb-0">{{ dashboardStats.customers_count || 0 }}</h3>
                  </div>
                  <div class="icon-bg bg-light-info">
                    <i class="bi bi-people text-info"></i>
                  </div>
                </div>
                <div class="mt-3">
                  <router-link to="/admin/customers" class="btn btn-sm btn-outline-info">
                    View Customers
                  </router-link>
                </div>
              </div>
            </div>
          </div>
          
          <div class="col-md-3">
            <div class="card h-100">
              <div class="card-body">
                <div class="d-flex justify-content-between align-items-center">
                  <div>
                    <h6 class="text-muted mb-1">Service Requests</h6>
                    <h3 class="mb-0">{{ dashboardStats.requests_count || 0 }}</h3>
                  </div>
                  <div class="icon-bg bg-light-warning">
                    <i class="bi bi-clipboard-check text-warning"></i>
                  </div>
                </div>
                <div class="mt-3">
                  <router-link to="/admin/requests" class="btn btn-sm btn-outline-warning">
                    View Requests
                  </router-link>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Request Status Chart -->
        <div class="row g-4 mb-4">
          <div class="col-md-8">
            <div class="card h-100">
              <div class="card-header">
                <h5 class="mb-0">Service Requests by Status</h5>
              </div>
              <div class="card-body">
                <div v-if="!dashboardStats.request_status_counts" class="text-center py-4">
                  <p class="text-muted mb-0">No request data available</p>
                </div>
                <div v-else class="chart-container">
                  <canvas ref="requestStatusChart"></canvas>
                </div>
              </div>
            </div>
          </div>
          
          <div class="col-md-4">
            <div class="card h-100">
              <div class="card-header">
                <h5 class="mb-0">Popular Services</h5>
              </div>
              <div class="card-body p-0">
                <div v-if="!dashboardStats.popular_services || dashboardStats.popular_services.length === 0" class="text-center py-4">
                  <p class="text-muted mb-0">No service data available</p>
                </div>
                <ul v-else class="list-group list-group-flush">
                  <li 
                    v-for="(service, index) in dashboardStats.popular_services" 
                    :key="index"
                    class="list-group-item d-flex justify-content-between align-items-center"
                  >
                    <div>
                      <span class="fw-medium">{{ service.name }}</span>
                      <div class="small text-muted">{{ service.request_count }} requests</div>
                    </div>
                    <span 
                      class="badge rounded-pill"
                      :class="getPopularityBadgeClass(index)"
                    >
                      #{{ index + 1 }}
                    </span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Recent Activity -->
        <div class="row">
          <div class="col-md-12">
            <div class="card">
              <div class="card-header d-flex justify-content-between align-items-center">
                <h5 class="mb-0">Recent Activity</h5>
                <router-link to="/admin/requests" class="btn btn-sm btn-outline-primary">
                  View All
                </router-link>
              </div>
              <div class="card-body p-0">
                <div v-if="!dashboardStats.recent_requests || dashboardStats.recent_requests.length === 0" class="text-center py-4">
                  <p class="text-muted mb-0">No recent activity</p>
                </div>
                <div v-else class="table-responsive">
                  <table class="table table-hover align-middle mb-0">
                    <thead class="table-light">
                      <tr>
                        <th>ID</th>
                        <th>Service</th>
                        <th>Customer</th>
                        <th>Date</th>
                        <th>Status</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="request in dashboardStats.recent_requests" :key="request.id">
                        <td>{{ request.id }}</td>
                        <td>{{ request.service_name }}</td>
                        <td>{{ request.customer_name }}</td>
                        <td>{{ formatDate(request.requested_date) }}</td>
                        <td>
                          <span 
                            class="badge"
                            :class="getStatusBadgeClass(request.status)"
                          >
                            {{ formatStatus(request.status) }}
                          </span>
                        </td>
                        <td>
                          <router-link 
                            :to="`/admin/requests?id=${request.id}`" 
                            class="btn btn-sm btn-outline-primary"
                          >
                            View
                          </router-link>
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
    </div>
  </template>
  
  <script>
  import { mapGetters, mapActions } from 'vuex'
  import Chart from 'chart.js/auto'
  import { format, parseISO } from 'date-fns'
  
  export default {
    name: 'AdminDashboard',
    data() {
      return {
        requestStatusChart: null,
        dashboardData: null
      }
    },
    computed: {
      ...mapGetters('admin', ['loading', 'error']),
      dashboardStats() {
        return this.$store.getters['admin/dashboardData'] || {
          services_count: 0,
          professionals_count: 0,
          customers_count: 0,
          requests_count: 0,
          request_status_counts: {},
          popular_services: [],
          recent_requests: []
        }
      }
    },
    methods: {
      ...mapActions('admin', ['fetchDashboardData']),
      
      async refreshData() {
        try {
          await this.fetchDashboardData();
          this.$nextTick(() => {
            if (this.$refs.requestStatusChart) {
              this.initRequestStatusChart();
            }
          });
        } catch (error) {
          console.error('Error refreshing dashboard data:', error);
        }
      },
      
      initRequestStatusChart() {
        if (!this.dashboardStats || !this.dashboardStats.request_status_counts || !this.$refs.requestStatusChart) {
          return;
        }
        
        const statusCounts = this.dashboardStats.request_status_counts
        const labels = Object.keys(statusCounts).map(status => this.formatStatus(status))
        const data = Object.values(statusCounts)
        
        const backgroundColors = [
          'rgba(255, 193, 7, 0.7)',  // pending - warning
          'rgba(13, 202, 240, 0.7)',  // assigned - info
          'rgba(13, 110, 253, 0.7)',  // in_progress - primary
          'rgba(25, 135, 84, 0.7)',   // completed - success
          'rgba(220, 53, 69, 0.7)'    // cancelled - danger
        ]
        
        const ctx = this.$refs.requestStatusChart.getContext('2d')
        
        // Destroy previous chart if it exists
        if (this.requestStatusChart) {
          this.requestStatusChart.destroy()
        }
        
        this.requestStatusChart = new Chart(ctx, {
          type: 'bar',
          data: {
            labels: labels,
            datasets: [{
              label: 'Number of Requests',
              data: data,
              backgroundColor: backgroundColors,
              borderColor: backgroundColors.map(color => color.replace('0.7', '1')),
              borderWidth: 1
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                display: false
              }
            },
            scales: {
              y: {
                beginAtZero: true,
                ticks: {
                  precision: 0
                }
              }
            }
          }
        })
      },
      
      formatDate(dateString) {
        if (!dateString) return 'N/A'
        try {
          const date = new Date(dateString)
          if (isNaN(date.getTime())) {
            return 'Invalid Date'
          }
          return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
          })
        } catch (error) {
          console.error('Error formatting date:', error)
          return 'Invalid Date'
        }
      },
      
      formatStatus(status) {
        if (!status) return 'Unknown'
        
        const statusMap = {
          'pending': 'Pending',
          'assigned': 'Assigned',
          'in_progress': 'In Progress',
          'completed': 'Completed',
          'cancelled': 'Cancelled'
        }
        
        return statusMap[status] || status.charAt(0).toUpperCase() + status.slice(1)
      },
      
      getStatusBadgeClass(status) {
        const statusClasses = {
          'pending': 'bg-warning',
          'assigned': 'bg-info',
          'in_progress': 'bg-primary',
          'completed': 'bg-success',
          'cancelled': 'bg-danger'
        }
        
        return statusClasses[status] || 'bg-secondary'
      },
      
      getPopularityBadgeClass(index) {
        const classes = [
          'bg-success',
          'bg-primary',
          'bg-info',
          'bg-warning',
          'bg-secondary'
        ]
        
        return classes[index] || 'bg-secondary'
      }
    },
    async mounted() {
      await this.fetchDashboardData()
      
      // Initialize chart after data is loaded and DOM is updated
      this.$nextTick(() => {
        if (this.dashboardStats && this.$refs.requestStatusChart) {
          this.initRequestStatusChart()
        }
      })
    },
    watch: {
      dashboardStats: {
        handler() {
          this.$nextTick(() => {
            if (this.$refs.requestStatusChart) {
              this.initRequestStatusChart()
            }
          })
        },
        deep: true
      }
    }
  }
  </script>
  
  <style scoped>
  .card {
    box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
    margin-bottom: 1.5rem;
  }
  
  .icon-bg {
    width: 48px;
    height: 48px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  .icon-bg i {
    font-size: 1.5rem;
  }
  
  .bg-light-primary {
    background-color: rgba(13, 110, 253, 0.1);
  }
  
  .bg-light-success {
    background-color: rgba(25, 135, 84, 0.1);
  }
  
  .bg-light-info {
    background-color: rgba(13, 202, 240, 0.1);
  }
  
  .bg-light-warning {
    background-color: rgba(255, 193, 7, 0.1);
  }
  
  .chart-container {
    height: 300px;
    position: relative;
  }
  
  .table th, .table td {
    padding: 0.75rem;
  }
  </style>