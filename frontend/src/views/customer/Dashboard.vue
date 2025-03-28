<!-- src/views/customer/Dashboard.vue -->
<template>
  <div class="customer-dashboard">
    <h1 class="mb-4">Customer Dashboard</h1>
    
    <div class="row">
      <!-- Summary Cards -->
      <div class="col-md-4 mb-4">
        <div class="card h-100">
          <div class="card-body">
            <h5 class="card-title">Active Requests</h5>
            <p class="card-text display-4">{{ stats.active || 0 }}</p>
            <router-link to="/customer/requests" class="btn btn-primary">View Requests</router-link>
          </div>
        </div>
      </div>
      
      <div class="col-md-4 mb-4">
        <div class="card h-100">
          <div class="card-body">
            <h5 class="card-title">Completed Services</h5>
            <p class="card-text display-4">{{ stats.completed || 0 }}</p>
            <router-link to="/customer/requests?status=completed" class="btn btn-primary">View History</router-link>
          </div>
        </div>
      </div>
      
      <div class="col-md-4 mb-4">
        <div class="card h-100">
          <div class="card-body">
            <h5 class="card-title">Available Services</h5>
            <p class="card-text display-4">{{ stats.services || 0 }}</p>
            <router-link to="/customer/services" class="btn btn-primary">Browse Services</router-link>
          </div>
        </div>
      </div>
    </div>
    
    <div class="row">
      <!-- Active Service Requests -->
      <div class="col-12 mb-4">
        <div class="card">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h5 class="mb-0">Active Service Requests</h5>
            <router-link to="/customer/requests" class="btn btn-sm btn-outline-primary">View All</router-link>
          </div>
          <div class="card-body">
            <div v-if="loading" class="text-center">
              <div class="spinner-border" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>
            
            <div v-else-if="activeRequests.length === 0" class="text-center">
              <p>No active service requests</p>
              <router-link to="/customer/services" class="btn btn-primary mt-2">Request a Service</router-link>
            </div>
            
            <div v-else class="table-responsive">
              <table class="table table-hover">
                <thead>
                  <tr>
                    <th>Service</th>
                    <th>Professional</th>
                    <th>Date Requested</th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="request in activeRequests" :key="request.id">
                    <td>{{ request.service.name }}</td>
                    <td>{{ request.professional ? request.professional.user.fullname : 'Not assigned' }}</td>
                    <td>{{ formatDate(request.date_of_request) }}</td>
                    <td><span :class="getStatusClass(request.service_status)">{{ request.service_status }}</span></td>
                    <td>
                      <div class="btn-group">
                        <button 
                          v-if="request.service_status === 'completed'"
                          @click="closeRequest(request.id)" 
                          class="btn btn-sm btn-success"
                        >
                          Close & Review
                        </button>
                        <button 
                          v-if="['requested', 'assigned'].includes(request.service_status)"
                          @click="cancelRequest(request.id)" 
                          class="btn btn-sm btn-danger"
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
      </div>
    </div>
    
    <!-- Review Modal -->
    <div class="modal fade" id="reviewModal" tabindex="-1" aria-labelledby="reviewModalLabel" aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="reviewModalLabel">Review Service</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <form>
              <div class="mb-3">
                <label for="rating" class="form-label">Rating</label>
                <select class="form-select" id="rating" v-model="review.rating">
                  <option value="5">5 - Excellent</option>
                  <option value="4">4 - Very Good</option>
                  <option value="3">3 - Good</option>
                  <option value="2">2 - Fair</option>
                  <option value="1">1 - Poor</option>
                </select>
              </div>
              <div class="mb-3">
                <label for="comments" class="form-label">Comments</label>
                <textarea class="form-control" id="comments" rows="3" v-model="review.comments"></textarea>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button type="button" class="btn btn-primary" @click="submitReview">Submit Review</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'
import bootstrap from 'bootstrap/dist/js/bootstrap.bundle.min.js'
import Vue from 'vue'

export default {
  name: 'CustomerDashboard',
  data() {
    return {
      stats: {
        active: 0,
        completed: 0,
        services: 0
      },
      activeRequests: [],
      loading: false,
      review: {
        requestId: null,
        rating: 5,
        comments: ''
      }
    }
  },
  computed: {
    ...mapGetters('auth', ['user'])
  },
  methods: {
    ...mapActions({
      addReview: 'serviceRequests/addReview',
      closeServiceRequest: 'serviceRequests/closeServiceRequest',
      cancelServiceRequest: 'serviceRequests/cancelServiceRequest'
    }),
    formatDate(dateString) {
      if (!dateString) return 'N/A'
      try {
        const date = new Date(dateString)
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
      } catch (error) {
        console.error('Error formatting date:', error)
        return 'Invalid Date'
      }
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
        const statsResponse = await Vue.prototype.$http.get('/customer/dashboard/stats')
        this.stats = statsResponse.data
        
        // Fetch active requests
        const requestsResponse = await Vue.prototype.$http.get('/customer/service-requests/active')
        this.activeRequests = requestsResponse.data
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
    
    async closeRequest(requestId) {
      try {
        // First close the service request
        await this.closeServiceRequest(requestId);
        
        // Then set the request ID for review and open the modal
        this.review.requestId = requestId;
        
        // Show the review modal
        const modal = new bootstrap.Modal(document.getElementById('reviewModal'));
        modal.show();
      } catch (error) {
        console.error('Failed to close request:', error);
        this.$store.dispatch('setNotification', {
          message: error.response?.data?.message || 'Failed to close request',
          type: 'error'
        }, { root: true });
      }
    },
    
    async cancelRequest(requestId) {
      try {
        await this.cancelServiceRequest(requestId)
        
        this.$store.dispatch('setNotification', {
          message: 'Service request cancelled successfully',
          type: 'success'
        }, { root: true })
        
        // Refresh the list
        this.fetchDashboardData()
      } catch (error) {
        console.error('Failed to cancel request:', error)
        this.$store.dispatch('setNotification', {
          message: 'Failed to cancel request',
          type: 'error'
        }, { root: true })
      }
    },
    
    async submitReview() {
      try {
        // Use the mapped action
        await this.addReview({
          serviceRequestId: this.review.requestId,
          rating: this.review.rating,
          comments: this.review.comments
        });
        
        // Close the modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('reviewModal'))
        modal.hide()
        
        this.$store.dispatch('setNotification', {
          message: 'Review submitted successfully',
          type: 'success'
        }, { root: true })
        
        // Reset the review form
        this.review = {
          requestId: null,
          rating: 5,
          comments: ''
        }
        
        // Refresh the list
        this.fetchDashboardData()
      } catch (error) {
        console.error('Failed to submit review:', error)
        this.$store.dispatch('setNotification', {
          message: error.response?.data?.message || 'Failed to submit review',
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