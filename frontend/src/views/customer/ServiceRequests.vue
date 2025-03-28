<!-- src/views/customer/ServiceRequests.vue -->
<template>
  <div class="service-requests-view">
    <h2 class="mb-4">My Service Requests</h2>
    
    <!-- Filters -->
    <div class="mb-4">
      <b-row>
        <b-col md="4">
          <b-form-group label="Filter by Status">
            <b-form-select v-model="statusFilter" :options="statusOptions"></b-form-select>
          </b-form-group>
        </b-col>
        <b-col md="4">
          <b-form-group label="Sort by">
            <b-form-select v-model="sortBy" :options="sortOptions"></b-form-select>
          </b-form-group>
        </b-col>
        <b-col md="4" class="d-flex align-items-end">
          <b-button variant="primary" @click="refreshRequests" class="w-100">
            <i class="fas fa-sync-alt mr-2"></i> Refresh
          </b-button>
        </b-col>
      </b-row>
    </div>
    
    <!-- Loading state -->
    <div v-if="loading" class="text-center py-5">
      <b-spinner variant="primary" label="Loading..."></b-spinner>
      <p class="mt-3">Loading your service requests...</p>
    </div>
    
    <!-- Error state -->
    <b-alert v-if="error" show variant="danger">
      {{ error }}
      <b-button @click="refreshRequests" variant="outline-danger" size="sm" class="ml-2">
        Try Again
      </b-button>
    </b-alert>
    
    <!-- Empty state -->
    <b-card v-if="!loading && !error && filteredRequests.length === 0" class="text-center py-5">
      <i class="fas fa-clipboard-list fa-3x text-muted mb-3"></i>
      <h4>No Service Requests Found</h4>
      <p class="text-muted">You haven't made any service requests yet or none match your current filters.</p>
      <b-button to="/customer/services" variant="primary">Browse Services</b-button>
    </b-card>
    
    <!-- Service requests list -->
    <div v-if="!loading && !error && filteredRequests.length > 0">
      <b-card v-for="request in filteredRequests" :key="request.id" class="mb-3 service-request-card">
        <b-row>
          <b-col md="8">
            <h5 class="mb-2">{{ request.service ? request.service.name : 'Unknown Service' }}</h5>
            <div class="mb-2">
              <b-badge :variant="getStatusVariant(request.service_status)">
                {{ request.service_status }}
              </b-badge>
              <span class="text-muted ml-2">
                <i class="far fa-calendar-alt"></i> 
                {{ formatDate(request.date_of_request) }}
              </span>
            </div>
            <p v-if="request.remarks" class="mb-2">
              <strong>Remarks:</strong> {{ request.remarks }}
            </p>
            <div v-if="request.professional" class="professional-info mt-3">
              <p class="mb-1"><strong>Professional:</strong> {{ request.professional.user.username }}</p>
            </div>
          </b-col>
          <b-col md="4" class="d-flex flex-column justify-content-between">
            <div class="text-right">
              <h5 class="text-primary mb-0">${{ request.service ? request.service.base_price.toFixed(2) : '0.00' }}</h5>
              <small class="text-muted">Est. time: {{ request.service ? request.service.time_required : 'N/A' }} mins</small>
            </div>
            <div class="mt-3 text-right">
              <!-- Actions based on status -->
              <div v-if="request.service_status === 'completed'">
                <b-button variant="success" size="sm" @click="closeRequest(request.id)" class="mr-2">
                  <i class="fas fa-check-circle mr-1"></i> Close
                </b-button>
                <b-button variant="outline-primary" size="sm" @click="showReviewModal(request)">
                  <i class="fas fa-star mr-1"></i> Review
                </b-button>
              </div>
              <div v-else-if="request.service_status === 'requested'">
                <b-button variant="outline-danger" size="sm" @click="cancelRequest(request.id)">
                  <i class="fas fa-times-circle mr-1"></i> Cancel
                </b-button>
              </div>
              <div v-else-if="request.service_status === 'assigned'">
                <p class="text-info mb-2"><small>Waiting for professional to accept</small></p>
              </div>
              <div v-else-if="request.service_status === 'accepted'">
                <p class="text-success mb-2"><small>Professional has accepted</small></p>
              </div>
              <div v-else-if="request.service_status === 'closed'">
                <b-button variant="outline-secondary" size="sm" disabled>
                  <i class="fas fa-lock mr-1"></i> Closed
                </b-button>
              </div>
            </div>
          </b-col>
        </b-row>
      </b-card>
      
      <!-- Pagination -->
      <div class="d-flex justify-content-center mt-4">
        <b-pagination
          v-model="currentPage"
          :total-rows="filteredRequests.length"
          :per-page="perPage"
          aria-controls="service-requests"
        ></b-pagination>
      </div>
    </div>
    
    <!-- Review Modal -->
    <b-modal id="review-modal" title="Leave a Review" hide-footer>
      <b-form @submit.prevent="submitReview">
        <b-form-group label="Rating">
          <div class="star-rating">
            <i v-for="star in 5" :key="star" 
               :class="['fas', star <= reviewForm.rating ? 'fa-star' : 'fa-star-o', 'rating-star']"
               @click="reviewForm.rating = star"></i>
          </div>
        </b-form-group>
        <b-form-group label="Comments">
          <b-form-textarea
            v-model="reviewForm.comments"
            placeholder="Share your experience with this service..."
            rows="4"
          ></b-form-textarea>
        </b-form-group>
        <div class="d-flex justify-content-end">
          <b-button variant="secondary" @click="$bvModal.hide('review-modal')" class="mr-2">
            Cancel
          </b-button>
          <b-button type="submit" variant="primary" :disabled="reviewForm.rating === 0">
            Submit Review
          </b-button>
        </div>
      </b-form>
    </b-modal>
  </div>
</template>

<script>
import { mapActions, mapGetters } from 'vuex'
import { format } from 'date-fns'

export default {
  name: 'ServiceRequestsView',
  data() {
    return {
      statusFilter: 'all',
      sortBy: 'newest',
      currentPage: 1,
      perPage: 5,
      reviewForm: {
        rating: 0,
        comments: '',
        serviceRequestId: null
      },
      statusOptions: [
        { value: 'all', text: 'All Requests' },
        { value: 'requested', text: 'Requested' },
        { value: 'assigned', text: 'Assigned' },
        { value: 'accepted', text: 'Accepted' },
        { value: 'completed', text: 'Completed' },
        { value: 'closed', text: 'Closed' }
      ],
      sortOptions: [
        { value: 'newest', text: 'Newest First' },
        { value: 'oldest', text: 'Oldest First' }
      ]
    }
  },
  computed: {
    ...mapGetters('serviceRequests', [
      'requests',
      'loading',
      'error'
    ]),
    filteredRequests() {
      let requests = Array.isArray(this.requests) ? [...this.requests] : []
      
      // Apply status filter
      if (this.statusFilter !== 'all') {
        requests = requests.filter(req => req.service_status === this.statusFilter)
      }
      
      // Apply sorting
      requests.sort((a, b) => {
        const dateA = new Date(a.date_of_request || null)
        const dateB = new Date(b.date_of_request || null)
        return this.sortBy === 'newest' ? dateB - dateA : dateA - dateB
      })
      
      return requests
    },
    paginatedRequests() {
      const start = (this.currentPage - 1) * this.perPage
      const end = start + this.perPage
      return this.filteredRequests.slice(start, end)
    }
  },
  methods: {
    ...mapActions('serviceRequests', [
      'fetchCustomerRequests',
      'closeServiceRequest',
      'cancelServiceRequest',
      'addReview'
    ]),
    refreshRequests() {
      this.fetchCustomerRequests()
    },
    formatDate(dateString) {
      try {
        if (!dateString) return 'N/A'
        return format(new Date(dateString), 'MMM dd, yyyy')
      } catch (error) {
        console.error('Error formatting date:', error)
        return 'Invalid Date'
      }
    },
    getStatusVariant(status) {
      const variants = {
        'requested': 'info',
        'assigned': 'warning',
        'accepted': 'primary',
        'completed': 'success',
        'closed': 'secondary',
        'rejected': 'danger'
      }
      return variants[status] || 'light'
    },
    async closeRequest(requestId) {
      try {
        await this.closeServiceRequest(requestId)
        this.$bvToast.toast('Service request closed successfully', {
          title: 'Success',
          variant: 'success',
          solid: true
        })
      } catch (error) {
        this.$bvToast.toast('Failed to close service request', {
          title: 'Error',
          variant: 'danger',
          solid: true
        })
      }
    },
    async cancelRequest(requestId) {
      if (confirm('Are you sure you want to cancel this service request?')) {
        try {
          await this.cancelServiceRequest(requestId)
          this.$bvToast.toast('Service request cancelled successfully', {
            title: 'Success',
            variant: 'success',
            solid: true
          })
        } catch (error) {
          this.$bvToast.toast('Failed to cancel service request', {
            title: 'Error',
            variant: 'danger',
            solid: true
          })
        }
      }
    },
    showReviewModal(request) {
      this.reviewForm.serviceRequestId = request.id
      this.reviewForm.rating = 0
      this.reviewForm.comments = ''
      this.$bvModal.show('review-modal')
    },
    async submitReview() {
      try {
        await this.addReview({
          serviceRequestId: this.reviewForm.serviceRequestId,
          rating: this.reviewForm.rating,
          comments: this.reviewForm.comments
        })
        this.$bvModal.hide('review-modal')
        this.$bvToast.toast('Review submitted successfully', {
          title: 'Thank you!',
          variant: 'success',
          solid: true
        })
        this.refreshRequests()
      } catch (error) {
        this.$bvToast.toast('Failed to submit review', {
          title: 'Error',
          variant: 'danger',
          solid: true
        })
      }
    }
  },
  created() {
    this.refreshRequests()
  }
}
</script>

<style scoped>
.service-request-card {
  transition: transform 0.2s;
}

.service-request-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.rating-star {
  color: #ffc107;
  cursor: pointer;
  font-size: 1.5rem;
  margin-right: 5px;
}

.star-rating {
  display: flex;
  justify-content: center;
  margin-bottom: 1rem;
}
</style> 