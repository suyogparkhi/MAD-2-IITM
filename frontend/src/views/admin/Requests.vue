<!-- src/views/admin/Requests.vue -->
<template>
  <div class="admin-requests">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1>Manage Service Requests</h1>
      <div>
        <b-button @click="refreshData" variant="outline-primary">
          <i class="fas fa-sync-alt mr-2"></i> Refresh
        </b-button>
      </div>
    </div>
    
    <!-- Loading State -->
    <div v-if="loading" class="text-center py-5">
      <b-spinner variant="primary" role="status">
        <span class="sr-only">Loading...</span>
      </b-spinner>
      <p class="mt-2">Loading service requests...</p>
    </div>
    
    <!-- Error State -->
    <b-alert v-else-if="error" show variant="danger">
      {{ error }}
      <b-button @click="refreshData" variant="outline-danger" size="sm" class="ml-2">Try Again</b-button>
    </b-alert>
    
    <!-- Filters -->
    <div v-else class="mb-4">
      <b-card no-body>
        <b-card-body>
          <b-row>
            <b-col md="3">
              <b-form-group label="Status">
                <b-form-select v-model="filters.status" @change="applyFilters">
                  <option value="">All Statuses</option>
                  <option value="requested">Requested</option>
                  <option value="assigned">Assigned</option>
                  <option value="accepted">Accepted</option>
                  <option value="completed">Completed</option>
                  <option value="closed">Closed</option>
                </b-form-select>
              </b-form-group>
            </b-col>
            <b-col md="3">
              <b-form-group label="Service">
                <b-form-select v-model="filters.serviceId" @change="applyFilters">
                  <option value="">All Services</option>
                  <option v-for="service in services" :key="service.id" :value="service.id">
                    {{ service.name }}
                  </option>
                </b-form-select>
              </b-form-group>
            </b-col>
            <b-col md="3">
              <b-form-group label="Date Range">
                <b-form-select v-model="filters.dateRange" @change="applyFilters">
                  <option value="">All Time</option>
                  <option value="today">Today</option>
                  <option value="week">This Week</option>
                  <option value="month">This Month</option>
                </b-form-select>
              </b-form-group>
            </b-col>
            <b-col md="3">
              <b-form-group label="Search">
                <b-input-group>
                  <b-form-input v-model="searchQuery" placeholder="Search requests..." @input="handleSearch" />
                  <b-input-group-append v-if="searchQuery">
                    <b-button variant="outline-secondary" @click="clearSearch">
                      <i class="fas fa-times"></i>
                    </b-button>
                  </b-input-group-append>
                </b-input-group>
              </b-form-group>
            </b-col>
          </b-row>
        </b-card-body>
      </b-card>
    </div>
    
    <!-- Requests Table -->
    <div v-if="!loading && !error">
      <b-card no-body>
        <div v-if="filteredRequests.length === 0" class="text-center py-5">
          <i class="fas fa-clipboard-list fa-3x text-muted mb-3"></i>
          <h4>No service requests found</h4>
          <p class="text-muted">Try changing your filters or wait for new service requests.</p>
        </div>
        <div v-else>
          <b-table 
            :items="paginatedRequests" 
            :fields="requestFields"
            responsive="sm"
            hover 
            striped
            sort-by="date_requested"
            sort-desc
            @row-clicked="viewRequest"
            class="mb-0"
          >
            <template #cell(id)="data">
              <span class="font-weight-bold">#{{ data.value }}</span>
            </template>
            
            <template #cell(service_name)="data">
              {{ data.value }}
            </template>
            
            <template #cell(customer_name)="data">
              {{ data.value }}
            </template>
            
            <template #cell(professional_name)="data">
              <span v-if="data.value">{{ data.value }}</span>
              <b-badge v-else variant="warning">Not Assigned</b-badge>
            </template>
            
            <template #cell(date_requested)="data">
              {{ formatDate(data.value) }}
            </template>
            
            <template #cell(status)="data">
              <b-badge :variant="getStatusBadgeClass(data.value)">
                {{ formatStatus(data.value) }}
              </b-badge>
            </template>
            
            <template #cell(actions)="data">
              <b-button size="sm" variant="primary" @click.stop="viewRequest(data.item)">
                <i class="fas fa-eye mr-1"></i> View
              </b-button>
              <b-button 
                v-if="data.item.status === 'requested'" 
                size="sm" 
                variant="success" 
                class="ml-1"
                @click.stop="showAssignModal(data.item)"
              >
                <i class="fas fa-user-plus mr-1"></i> Assign
              </b-button>
            </template>
          </b-table>
          
          <!-- Pagination -->
          <div class="d-flex justify-content-between align-items-center px-3 py-2 border-top">
            <small class="text-muted">
              Showing {{ filteredRequests.length ? (currentPage - 1) * perPage + 1 : 0 }} 
              to {{ Math.min(currentPage * perPage, filteredRequests.length) }}
              of {{ filteredRequests.length }} requests
            </small>
            <b-pagination
              v-model="currentPage"
              :total-rows="filteredRequests.length"
              :per-page="perPage"
              align="center"
              class="my-0"
              size="sm"
            ></b-pagination>
          </div>
        </div>
      </b-card>
    </div>
    
    <!-- Request Details Modal -->
    <b-modal 
      id="request-details-modal" 
      title="Service Request Details" 
      size="lg" 
      hide-footer
      @hidden="clearSelectedRequest"
    >
      <div v-if="selectedRequest">
        <div class="mb-4">
          <div class="d-flex justify-content-between align-items-center mb-3">
            <h4 class="mb-0">Request #{{ selectedRequest.id }}</h4>
            <b-badge :variant="getStatusBadgeClass(selectedRequest.status)" class="px-3 py-2">
              {{ formatStatus(selectedRequest.status) }}
            </b-badge>
          </div>
          
          <b-row>
            <b-col md="6">
              <h5 class="border-bottom pb-2 mb-3">Request Information</h5>
              <p><strong>Service:</strong> {{ selectedRequest.service_name }}</p>
              <p><strong>Requested Date:</strong> {{ formatDate(selectedRequest.date_requested) }}</p>
              <p v-if="selectedRequest.date_completed">
                <strong>Completed Date:</strong> {{ formatDate(selectedRequest.date_completed) }}
              </p>
              <p><strong>Notes/Remarks:</strong> {{ selectedRequest.remarks || 'No remarks provided' }}</p>
            </b-col>
            
            <b-col md="6">
              <h5 class="border-bottom pb-2 mb-3">Customer Information</h5>
              <p><strong>Name:</strong> {{ selectedRequest.customer_name }}</p>
              <p v-if="selectedRequest.customer_email"><strong>Email:</strong> {{ selectedRequest.customer_email }}</p>
              <p v-if="selectedRequest.customer_phone"><strong>Phone:</strong> {{ selectedRequest.customer_phone }}</p>
              <p v-if="selectedRequest.customer_address">
                <strong>Address:</strong> {{ selectedRequest.customer_address }}
              </p>
            </b-col>
          </b-row>
          
          <div v-if="selectedRequest.professional_name" class="mt-4">
            <h5 class="border-bottom pb-2 mb-3">Professional Information</h5>
            <p><strong>Name:</strong> {{ selectedRequest.professional_name }}</p>
            <p v-if="selectedRequest.professional_email">
              <strong>Email:</strong> {{ selectedRequest.professional_email }}
            </p>
            <p v-if="selectedRequest.professional_phone">
              <strong>Phone:</strong> {{ selectedRequest.professional_phone }}
            </p>
            <p v-if="selectedRequest.professional_experience">
              <strong>Experience:</strong> {{ selectedRequest.professional_experience }}
            </p>
          </div>
          
          <div v-if="selectedRequest.review" class="mt-4">
            <h5 class="border-bottom pb-2 mb-3">Customer Review</h5>
            <div class="d-flex align-items-center mb-2">
              <div class="mr-2">
                <i 
                  v-for="n in 5" 
                  :key="n" 
                  :class="['fas', n <= selectedRequest.review.rating ? 'fa-star' : 'fa-star',
                          n <= selectedRequest.review.rating ? 'text-warning' : 'text-muted']"
                ></i>
              </div>
              <strong>{{ selectedRequest.review.rating }}/5</strong>
            </div>
            <p>{{ selectedRequest.review.comments || 'No comments provided' }}</p>
          </div>
        </div>
        
        <div class="d-flex justify-content-between mt-4">
          <div>
            <b-button 
              v-if="selectedRequest.status === 'requested'" 
              variant="success" 
              @click="showAssignModal(selectedRequest)"
            >
              <i class="fas fa-user-plus mr-1"></i> Assign Professional
            </b-button>
          </div>
          <b-button variant="secondary" @click="$bvModal.hide('request-details-modal')">
            Close
          </b-button>
        </div>
      </div>
    </b-modal>
    
    <!-- Assign Professional Modal -->
    <b-modal 
      id="assign-professional-modal" 
      title="Assign Professional" 
      @ok="assignProfessional"
      @hidden="resetAssignForm"
      ok-title="Assign Professional"
      ok-variant="success"
    >
      <div v-if="assignForm.request">
        <p class="mb-3">
          <strong>Service Request:</strong> #{{ assignForm.request.id }} - {{ assignForm.request.service_name }}
        </p>
        
        <b-form-group label="Select Professional">
          <div v-if="professionalOptions.length === 0" class="text-center py-3">
            <p class="text-muted mb-0">No professionals available for this service.</p>
            <p class="small">Try adding professionals with expertise in this service.</p>
          </div>
          <b-form-select 
            v-else
            v-model="assignForm.professionalId"
            :options="professionalOptions"
            required
          ></b-form-select>
        </b-form-group>
        
        <div v-if="assignForm.professionalId" class="mt-4">
          <h6>Professional Details</h6>
          <div v-if="selectedProfessional" class="p-3 bg-light rounded">
            <p class="mb-1"><strong>Name:</strong> {{ selectedProfessional.name }}</p>
            <p class="mb-1"><strong>Experience:</strong> {{ selectedProfessional.experience }} years</p>
            <p class="mb-0">
              <strong>Rating:</strong> 
              <i v-for="n in 5" :key="n" 
                 :class="['fas', n <= selectedProfessional.rating ? 'fa-star' : 'fa-star',
                         n <= selectedProfessional.rating ? 'text-warning' : 'text-muted']"></i>
              <span class="ml-1">{{ selectedProfessional.rating.toFixed(1) }}</span>
            </p>
          </div>
        </div>
      </div>
      <template #modal-footer="{ ok, cancel }">
        <b-button variant="secondary" @click="cancel()">Cancel</b-button>
        <b-button 
          variant="success" 
          @click="ok()" 
          :disabled="!assignForm.professionalId"
        >
          <i class="fas fa-user-plus mr-1"></i> Assign Professional
        </b-button>
      </template>
    </b-modal>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'
import { format, subDays, startOfDay, startOfWeek, startOfMonth } from 'date-fns'

export default {
  name: 'AdminRequestsView',
  data() {
    return {
      filters: {
        status: '',
        serviceId: '',
        dateRange: ''
      },
      searchQuery: '',
      currentPage: 1,
      perPage: 10,
      selectedRequest: null,
      assignForm: {
        request: null,
        professionalId: null
      },
      requestFields: [
        { key: 'id', label: 'ID', sortable: true },
        { key: 'service_name', label: 'Service', sortable: true },
        { key: 'customer_name', label: 'Customer', sortable: true },
        { key: 'professional_name', label: 'Professional', sortable: true },
        { key: 'date_requested', label: 'Requested Date', sortable: true },
        { key: 'status', label: 'Status', sortable: true },
        { key: 'actions', label: 'Actions' }
      ]
    }
  },
  computed: {
    ...mapGetters({
      requests: 'serviceRequests/adminRequests',
      loading: 'serviceRequests/loading',
      error: 'serviceRequests/error',
      services: 'services/services',
      professionals: 'professionals/professionals'
    }),
    filteredRequests() {
      let filteredData = [...this.requests]
      
      // Apply status filter
      if (this.filters.status) {
        filteredData = filteredData.filter(req => req.status === this.filters.status)
      }
      
      // Apply service filter
      if (this.filters.serviceId) {
        filteredData = filteredData.filter(req => req.service_id === Number(this.filters.serviceId))
      }
      
      // Apply date filter
      if (this.filters.dateRange) {
        const now = new Date()
        let dateLimit
        
        if (this.filters.dateRange === 'today') {
          dateLimit = startOfDay(now)
        } else if (this.filters.dateRange === 'week') {
          dateLimit = startOfWeek(now)
        } else if (this.filters.dateRange === 'month') {
          dateLimit = startOfMonth(now)
        }
        
        if (dateLimit) {
          filteredData = filteredData.filter(req => {
            const requestDate = new Date(req.date_requested)
            return requestDate >= dateLimit
          })
        }
      }
      
      // Apply search filter
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase()
        filteredData = filteredData.filter(req => 
          String(req.id).includes(query) ||
          (req.service_name && req.service_name.toLowerCase().includes(query)) ||
          (req.customer_name && req.customer_name.toLowerCase().includes(query)) ||
          (req.professional_name && req.professional_name.toLowerCase().includes(query))
        )
      }
      
      return filteredData
    },
    paginatedRequests() {
      const start = (this.currentPage - 1) * this.perPage
      const end = start + this.perPage
      return this.filteredRequests.slice(start, end)
    },
    professionalOptions() {
      if (!this.assignForm.request) return []
      
      console.log("Request service_id:", this.assignForm.request.service_id);
      console.log("Available professionals:", this.professionals);
      
      // Filter professionals by the service of the request and verification status
      const serviceProfessionals = this.professionals.filter(p => {
        console.log(`Professional ${p.id} - service_id: ${p.service_id}, verification: ${p.verification_status}`);
        return p.service_id === this.assignForm.request.service_id &&
               p.verification_status === 'approved';
      });
      
      console.log("Filtered professionals:", serviceProfessionals);
      
      return [
        { value: null, text: 'Select a professional' },
        ...serviceProfessionals.map(p => ({
          value: p.id,
          text: `${p.user ? p.user.username : p.username} (${p.experience || 0} years experience)`
        }))
      ]
    },
    selectedProfessional() {
      if (!this.assignForm.professionalId) return null
      
      const professional = this.professionals.find(p => p.id === this.assignForm.professionalId)
      if (!professional) return null
      
      return {
        id: professional.id,
        name: professional.user ? professional.user.username : professional.username,
        experience: professional.experience || 0,
        rating: professional.avg_rating || 0
      }
    }
  },
  created() {
    this.refreshData()
  },
  methods: {
    ...mapActions({
      fetchRequests: 'serviceRequests/fetchAdminRequests',
      fetchServices: 'services/fetchServices',
      fetchProfessionals: 'professionals/fetchProfessionals',
      assignProfessionalToRequest: 'serviceRequests/assignProfessional'
    }),
    refreshData() {
      this.fetchRequests()
      this.fetchServices()
      this.fetchProfessionals()
    },
    applyFilters() {
      this.currentPage = 1
    },
    handleSearch() {
      this.currentPage = 1
    },
    clearSearch() {
      this.searchQuery = ''
    },
    formatDate(dateString) {
      if (!dateString) return 'N/A'
      try {
        return format(new Date(dateString), 'MMM dd, yyyy')
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
    getStatusBadgeClass(status) {
      const statusClasses = {
        'requested': 'info',
        'assigned': 'warning',
        'accepted': 'primary',
        'completed': 'success',
        'closed': 'secondary'
      }
      
      return statusClasses[status] || 'secondary'
    },
    viewRequest(request) {
      this.selectedRequest = { ...request }
      this.$bvModal.show('request-details-modal')
    },
    clearSelectedRequest() {
      this.selectedRequest = null
    },
    showAssignModal(request) {
      this.assignForm.request = request;
      this.assignForm.professionalId = null;
      console.log("Opening assign modal for request:", {
        id: request.id,
        service_id: request.service_id,
        service_name: request.service_name
      });
      
      // First fetch professionals if not already loaded
      this.fetchProfessionals({isAdmin: true}).then(() => {
        console.log("Professionals loaded, showing modal");
        this.$bvModal.show('assign-professional-modal');
      });
    },
    resetAssignForm() {
      this.assignForm = {
        request: null,
        professionalId: null
      }
    },
    async assignProfessional(bvModalEvent) {
      // Prevent modal from closing
      bvModalEvent.preventDefault()
      
      if (!this.assignForm.professionalId) {
        this.$bvToast.toast('Please select a professional', {
          title: 'Error',
          variant: 'danger',
          solid: true
        })
        return
      }
      
      console.log("Attempting to assign professional:", {
        requestId: this.assignForm.request.id,
        professionalId: this.assignForm.professionalId
      });
      
      try {
        await this.assignProfessionalToRequest({
          requestId: this.assignForm.request.id,
          professionalId: this.assignForm.professionalId
        })
        
        this.$bvToast.toast('Professional assigned successfully', {
          title: 'Success',
          variant: 'success',
          solid: true
        })
        
        // Close modal and refresh data
        this.$bvModal.hide('assign-professional-modal')
        this.refreshData()
      } catch (error) {
        console.error("Error assigning professional:", error);
        this.$bvToast.toast(error.message || 'Failed to assign professional', {
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
.badge {
  font-size: 0.875rem;
  padding: 0.35em 0.65em;
}

.table th {
  font-weight: 600;
}

.table tbody tr {
  cursor: pointer;
}

.table tbody tr:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

/* Override modal footer to ensure buttons align properly */
::v-deep .modal-footer {
  display: flex;
  justify-content: flex-end;
}
</style> 