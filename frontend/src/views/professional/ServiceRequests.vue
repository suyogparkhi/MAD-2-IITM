<!-- src/views/professional/ServiceRequests.vue -->
<template>
  <div class="service-requests-view">
    <h2 class="mb-4">Service Requests</h2>
    
    <!-- Tabs for request types -->
    <b-tabs content-class="mt-3" fill>
      <b-tab title="My Requests" active>
        <!-- My Requests Tab Content -->
        <div class="my-3">
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
            <p class="mt-3">Loading service requests...</p>
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
            <p class="text-muted">There are no service requests assigned to you matching your current filters.</p>
            <p>Check the <b-link @click="activateAvailableTab">Available Requests</b-link> tab to find new work.</p>
          </b-card>
          
          <!-- Service requests list -->
          <div v-if="!loading && !error && filteredRequests.length > 0">
            <b-card v-for="request in paginatedRequests" :key="request.id" class="mb-3 service-request-card">
              <b-row>
                <b-col md="8">
                  <h5 class="mb-2">{{ request.service_name }}</h5>
                  <div class="mb-2">
                    <b-badge :variant="getStatusVariant(request.service_status)">
                      {{ formatStatus(request.service_status) }}
                    </b-badge>
                    <span class="text-muted ml-2">
                      <i class="far fa-calendar-alt"></i> 
                      {{ formatDate(request.date_of_request) }}
                    </span>
                  </div>
                  <p v-if="request.remarks" class="mb-2">
                    <strong>Remarks:</strong> {{ request.remarks }}
                  </p>
                  <div class="customer-info mt-3">
                    <p class="mb-1"><strong>Customer:</strong> {{ request.customer_name }}</p>
                    <p class="mb-0" v-if="request.customer_address">
                      <strong>Location:</strong> {{ request.customer_address }} ({{ request.customer_pin_code || 'No Pin Code' }})
                    </p>
                  </div>
                </b-col>
                <b-col md="4" class="d-flex flex-column justify-content-between">
                  <div class="text-right">
                    <h5 class="text-primary mb-0">
                      <i class="fas fa-dollar-sign"></i> {{ getServicePrice(request) }}
                    </h5>
                    <small class="text-muted">Est. time: {{ getServiceTime(request) }}</small>
                  </div>
                  <div class="mt-3 text-right">
                    <!-- Actions based on status -->
                    <div v-if="request.service_status === 'assigned'">
                      <b-button variant="success" size="sm" @click="acceptRequest(request.id)" class="mr-2">
                        <i class="fas fa-check mr-1"></i> Accept
                      </b-button>
                      <b-button variant="danger" size="sm" @click="rejectRequest(request.id)">
                        <i class="fas fa-times mr-1"></i> Reject
                      </b-button>
                    </div>
                    <div v-else-if="request.service_status === 'accepted'">
                      <b-button variant="primary" size="sm" @click="completeRequest(request.id)">
                        <i class="fas fa-check-circle mr-1"></i> Mark as Completed
                      </b-button>
                    </div>
                    <div v-else-if="request.service_status === 'completed'">
                      <p class="text-success mb-2"><small>Waiting for customer to close</small></p>
                    </div>
                    <div v-else-if="request.service_status === 'closed' && request.review">
                      <div class="text-center">
                        <div class="mb-2">
                          <i v-for="n in 5" :key="n" 
                             :class="['fas', n <= request.review.rating ? 'fa-star' : 'fa-star',
                                     n <= request.review.rating ? 'text-warning' : 'text-muted']"></i>
                        </div>
                        <p class="mb-0 small">{{ request.review.comments || 'No comments' }}</p>
                      </div>
                    </div>
                    <b-button variant="outline-secondary" size="sm" @click="viewRequestDetails(request)" class="mt-2">
                      <i class="fas fa-eye mr-1"></i> Details
                    </b-button>
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
        </div>
      </b-tab>
      
      <b-tab title="Available Requests" ref="availableTab">
        <!-- Available Requests Tab Content -->
        <div class="my-3">
          <!-- Refresh button for available requests -->
          <div class="d-flex justify-content-end mb-3">
            <b-button variant="outline-primary" @click="fetchAvailableRequests">
              <i class="fas fa-sync-alt mr-2"></i> Refresh Available Requests
            </b-button>
          </div>
          
          <!-- Loading state -->
          <div v-if="availableRequestsLoading" class="text-center py-5">
            <b-spinner variant="primary" label="Loading..."></b-spinner>
            <p class="mt-3">Loading available requests...</p>
          </div>
          
          <!-- Error state -->
          <b-alert v-if="availableRequestsError" show variant="danger">
            {{ availableRequestsError }}
            <b-button @click="fetchAvailableRequests" variant="outline-danger" size="sm" class="ml-2">
              Try Again
            </b-button>
          </b-alert>
          
          <!-- Empty state -->
          <b-card v-if="!availableRequestsLoading && !availableRequestsError && availableRequests.length === 0" 
                class="text-center py-5">
            <i class="fas fa-search fa-3x text-muted mb-3"></i>
            <h4>No Available Requests Found</h4>
            <p class="text-muted">There are no unassigned service requests matching your expertise currently.</p>
            <p>Check back later for new service requests.</p>
          </b-card>
          
          <!-- Available requests list -->
          <div v-if="!availableRequestsLoading && !availableRequestsError && availableRequests.length > 0">
            <b-card v-for="request in availableRequests" :key="request.id" class="mb-3 service-request-card available-request">
              <b-row>
                <b-col md="8">
                  <h5 class="mb-2">{{ request.service_name }}</h5>
                  <div class="mb-2">
                    <b-badge variant="info">
                      Available
                    </b-badge>
                    <span class="text-muted ml-2">
                      <i class="far fa-calendar-alt"></i> 
                      {{ formatDate(request.date_of_request) }}
                    </span>
                  </div>
                  <p v-if="request.remarks" class="mb-2">
                    <strong>Remarks:</strong> {{ request.remarks }}
                  </p>
                  <div class="customer-info mt-3">
                    <p class="mb-1"><strong>Customer:</strong> {{ request.customer_name }}</p>
                    <p class="mb-0" v-if="request.customer_address">
                      <strong>Location:</strong> {{ request.customer_address }} ({{ request.customer_pin_code || 'No Pin Code' }})
                    </p>
                  </div>
                </b-col>
                <b-col md="4" class="d-flex flex-column justify-content-between">
                  <div class="text-right">
                    <h5 class="text-primary mb-0">
                      <i class="fas fa-dollar-sign"></i> {{ getServicePrice(request) }}
                    </h5>
                    <small class="text-muted">Est. time: {{ getServiceTime(request) }}</small>
                  </div>
                  <div class="mt-3 text-right">
                    <b-button variant="success" size="sm" @click="acceptAvailableRequest(request.id)">
                      <i class="fas fa-check mr-1"></i> Accept Request
                    </b-button>
                  </div>
                </b-col>
              </b-row>
            </b-card>
          </div>
        </div>
      </b-tab>
    </b-tabs>
    
    <!-- Service Details Modal -->
    <b-modal id="service-details-modal" title="Service Request Details" hide-footer size="lg">
      <div v-if="selectedRequest">
        <div class="mb-4">
          <h5 class="border-bottom pb-2">Request Information</h5>
          <div class="row">
            <div class="col-md-6">
              <p><strong>Request ID:</strong> #{{ selectedRequest.id }}</p>
              <p><strong>Service:</strong> {{ selectedRequest.service_name }}</p>
              <p><strong>Status:</strong> 
                <b-badge :variant="getStatusVariant(selectedRequest.service_status)">
                  {{ formatStatus(selectedRequest.service_status) }}
                </b-badge>
              </p>
            </div>
            <div class="col-md-6">
              <p><strong>Requested:</strong> {{ formatDateTime(selectedRequest.date_of_request) }}</p>
              <p v-if="selectedRequest.date_of_completion">
                <strong>Completed:</strong> {{ formatDateTime(selectedRequest.date_of_completion) }}
              </p>
              <p v-if="selectedRequest.remarks"><strong>Remarks:</strong> {{ selectedRequest.remarks }}</p>
            </div>
          </div>
        </div>
        
        <div class="mb-4">
          <h5 class="border-bottom pb-2">Customer Information</h5>
          <div class="row">
            <div class="col-md-6">
              <p><strong>Customer Name:</strong> {{ selectedRequest.customer_name }}</p>
              <p v-if="selectedRequest.customer_email"><strong>Email:</strong> {{ selectedRequest.customer_email }}</p>
            </div>
            <div class="col-md-6">
              <p v-if="selectedRequest.customer_address">
                <strong>Address:</strong> {{ selectedRequest.customer_address }}
              </p>
              <p v-if="selectedRequest.customer_pin_code">
                <strong>Pin Code:</strong> {{ selectedRequest.customer_pin_code }}
              </p>
            </div>
          </div>
        </div>
        
        <div v-if="selectedRequest.review" class="mb-4">
          <h5 class="border-bottom pb-2">Customer Review</h5>
          <div class="d-flex align-items-center mb-2">
            <div class="mr-2">
              <i v-for="n in 5" :key="n" 
                 :class="['fas', n <= selectedRequest.review.rating ? 'fa-star' : 'fa-star',
                         n <= selectedRequest.review.rating ? 'text-warning' : 'text-muted']"></i>
            </div>
            <div><strong>{{ selectedRequest.review.rating }}/5</strong></div>
          </div>
          <p>{{ selectedRequest.review.comments || 'No comments provided.' }}</p>
        </div>
        
        <div class="text-right">
          <!-- Action buttons based on status -->
          <template v-if="selectedRequest.service_status === 'assigned'">
            <b-button variant="success" @click="acceptRequest(selectedRequest.id)" class="mr-2">
              <i class="fas fa-check mr-1"></i> Accept
            </b-button>
            <b-button variant="danger" @click="rejectRequest(selectedRequest.id)" class="mr-2">
              <i class="fas fa-times mr-1"></i> Reject
            </b-button>
          </template>
          <template v-if="selectedRequest.service_status === 'accepted'">
            <b-button variant="primary" @click="completeRequest(selectedRequest.id)" class="mr-2">
              <i class="fas fa-check-circle mr-1"></i> Mark as Completed
            </b-button>
          </template>
          <b-button @click="$bvModal.hide('service-details-modal')" variant="secondary">
            Close
          </b-button>
        </div>
      </div>
    </b-modal>
  </div>
</template>

<script>
import { mapActions, mapGetters } from 'vuex'
import { format } from 'date-fns'

export default {
  name: 'ProfessionalServiceRequestsView',
  data() {
    return {
      statusFilter: 'all',
      sortBy: 'newest',
      currentPage: 1,
      perPage: 5,
      selectedRequest: null,
      statusOptions: [
        { value: 'all', text: 'All Requests' },
        { value: 'assigned', text: 'Assigned' },
        { value: 'accepted', text: 'Accepted' },
        { value: 'completed', text: 'Completed' },
        { value: 'closed', text: 'Closed' }
      ],
      sortOptions: [
        { value: 'newest', text: 'Newest First' },
        { value: 'oldest', text: 'Oldest First' }
      ],
      availableRequests: [],
      availableRequestsLoading: false,
      availableRequestsError: null
    }
  },
  computed: {
    ...mapGetters('serviceRequests', [
      'professionalRequests',
      'loading',
      'error'
    ]),
    filteredRequests() {
      let requests = [...this.professionalRequests]
      
      // Apply status filter
      if (this.statusFilter !== 'all') {
        requests = requests.filter(req => req.service_status === this.statusFilter)
      }
      
      // Apply sorting
      requests.sort((a, b) => {
        const dateA = new Date(a.date_of_request)
        const dateB = new Date(b.date_of_request)
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
  created() {
    this.refreshRequests()
    this.fetchAvailableRequests()
  },
  methods: {
    ...mapActions('serviceRequests', [
      'fetchProfessionalRequests',
      'updateServiceRequest'
    ]),
    refreshRequests() {
      this.fetchProfessionalRequests()
    },
    activateAvailableTab() {
      this.$refs.availableTab.activate();
    },
    formatDate(dateString) {
      if (!dateString) return 'N/A'
      try {
        return format(new Date(dateString), 'MMM dd, yyyy')
      } catch (e) {
        return 'Invalid date'
      }
    },
    formatDateTime(dateString) {
      if (!dateString) return 'N/A'
      try {
        return format(new Date(dateString), 'MMM dd, yyyy hh:mm a')
      } catch (e) {
        return 'Invalid date'
      }
    },
    formatStatus(status) {
      if (!status) return 'Unknown'
      const statusMap = {
        'requested': 'Requested',
        'assigned': 'Assigned',
        'accepted': 'Accepted',
        'completed': 'Completed',
        'closed': 'Closed'
      }
      return statusMap[status] || status.charAt(0).toUpperCase() + status.slice(1)
    },
    getStatusVariant(status) {
      const variants = {
        'requested': 'info',
        'assigned': 'warning',
        'accepted': 'primary',
        'completed': 'success',
        'closed': 'secondary'
      }
      return variants[status] || 'light'
    },
    getServicePrice(request) {
      return request.service && request.service.base_price 
        ? `$${request.service.base_price.toFixed(2)}` 
        : '$50.00' // Default price if not available
    },
    getServiceTime(request) {
      return request.service && request.service.time_required 
        ? `${request.service.time_required} mins` 
        : '60 mins' // Default time if not available
    },
    async acceptRequest(requestId) {
      try {
        await this.updateServiceRequest({
          id: requestId,
          action: 'accept'
        })
        this.$bvToast.toast('Service request accepted successfully', {
          title: 'Success',
          variant: 'success',
          solid: true
        })
        this.refreshRequests()
        this.$bvModal.hide('service-details-modal')
      } catch (error) {
        this.$bvToast.toast(`Error: ${error.message || 'Failed to accept request'}`, {
          title: 'Error',
          variant: 'danger',
          solid: true
        })
      }
    },
    async rejectRequest(requestId) {
      try {
        await this.updateServiceRequest({
          id: requestId,
          action: 'reject'
        })
        this.$bvToast.toast('Service request rejected', {
          title: 'Success',
          variant: 'success',
          solid: true
        })
        this.refreshRequests()
        this.$bvModal.hide('service-details-modal')
      } catch (error) {
        this.$bvToast.toast(`Error: ${error.message || 'Failed to reject request'}`, {
          title: 'Error',
          variant: 'danger',
          solid: true
        })
      }
    },
    async completeRequest(requestId) {
      try {
        await this.updateServiceRequest({
          id: requestId,
          action: 'complete'
        })
        this.$bvToast.toast('Service request marked as completed', {
          title: 'Success',
          variant: 'success',
          solid: true
        })
        this.refreshRequests()
        this.$bvModal.hide('service-details-modal')
      } catch (error) {
        this.$bvToast.toast(`Error: ${error.message || 'Failed to complete request'}`, {
          title: 'Error',
          variant: 'danger',
          solid: true
        })
      }
    },
    viewRequestDetails(request) {
      this.selectedRequest = request
      this.$bvModal.show('service-details-modal')
    },
    async fetchAvailableRequests() {
      this.availableRequestsLoading = true
      this.availableRequestsError = null
      
      try {
        const response = await this.$http.get('/professional/available-requests')
        this.availableRequests = response.data
      } catch (error) {
        this.availableRequestsError = error.response?.data?.message || 'Failed to load available requests'
        console.error('Error fetching available requests:', error)
      } finally {
        this.availableRequestsLoading = false
      }
    },
    async acceptAvailableRequest(requestId) {
      try {
        await this.$http.put(`/professional/service-requests/${requestId}/action`, {
          action: 'accept'
        })
        
        this.$bvToast.toast('Service request accepted successfully', {
          title: 'Success',
          variant: 'success',
          solid: true
        })
        
        // Refresh both tabs
        this.fetchAvailableRequests()
        this.refreshRequests()
        
        // Switch to My Requests tab using the correct ref
        this.$nextTick(() => {
          // Get the tabs component which is the parent of our tab
          const tabsComponent = this.$refs.availableTab.$parent;
          tabsComponent.setActiveTab(0);
        });
      } catch (error) {
        this.$bvToast.toast(`Error: ${error.response?.data?.message || 'Failed to accept request'}`, {
          title: 'Error',
          variant: 'danger',
          solid: true
        })
      }
    }
  }
}
</script>

<style scoped>
.service-request-card {
  border-radius: 10px;
  transition: all 0.3s ease;
  border-left: 4px solid #6c757d;
}

.service-request-card:hover {
  box-shadow: 0 5px 15px rgba(0,0,0,0.08);
  transform: translateY(-2px);
}

.service-request-card.available-request {
  border-left-color: #17a2b8;
}

.rating-star {
  cursor: pointer;
  font-size: 1.5rem;
  margin-right: 0.25rem;
}

/* Status badges */
.badge {
  padding: 0.5em 0.8em;
  border-radius: 0.25rem;
  font-weight: 500;
  font-size: 0.8rem;
}
</style> 