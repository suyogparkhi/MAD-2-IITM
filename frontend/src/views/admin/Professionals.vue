<!-- src/views/admin/Professionals.vue -->
<template>
  <div class="admin-professionals">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1>Manage Professionals</h1>
    </div>
    
    <!-- Loading State -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-2">Loading professionals...</p>
    </div>
    
    <!-- Error State -->
    <div v-else-if="error" class="alert alert-danger">
      {{ error }}
      <button @click="loadProfessionals" class="btn btn-sm btn-outline-danger ms-2">Try Again</button>
    </div>
    
    <!-- Professionals Table -->
    <div v-else class="card">
      <div class="card-header">
        <div class="row align-items-center">
          <div class="col">
            <h5 class="mb-0">All Professionals</h5>
          </div>
          <div class="col-md-4">
            <input 
              type="text" 
              class="form-control" 
              placeholder="Search professionals..." 
              v-model="searchQuery"
              @input="handleSearch"
            >
          </div>
        </div>
      </div>
      <div class="card-body p-0">
        <div v-if="filteredProfessionals.length === 0" class="text-center py-5">
          <p class="mb-0">No professionals found</p>
        </div>
        <div v-else class="table-responsive">
          <table class="table table-hover align-middle mb-0">
            <thead class="table-light">
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Email</th>
                <th>Phone</th>
                <th>Services</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="professional in filteredProfessionals" :key="professional.id">
                <td>{{ professional.id }}</td>
                <td>
                  <div class="d-flex align-items-center">
                    <div class="avatar-placeholder me-2">
                      {{ getInitials(professional.username || '') }}
                    </div>
                    <div>
                      {{ professional.username }}
                    </div>
                  </div>
                </td>
                <td>{{ professional.email }}</td>
                <td>{{ professional.phone || 'N/A' }}</td>
                <td>
                  <span v-if="professional.services && professional.services.length">
                    {{ professional.services.length }} services
                  </span>
                  <span v-else class="text-muted">{{ professional.service_name || 'No service' }}</span>
                </td>
                <td>
                  <span 
                    class="badge" 
                    :class="getStatusBadgeClass(professional.verification_status)"
                  >
                    {{ formatVerificationStatus(professional.verification_status) }}
                  </span>
                </td>
                <td>
                  <div class="btn-group">
                    <button 
                      @click="viewProfessional(professional)" 
                      class="btn btn-sm btn-outline-primary"
                    >
                      View
                    </button>
                    <button 
                      @click="toggleStatus(professional)" 
                      class="btn btn-sm"
                      :class="professional.verification_status === 'approved' ? 'btn-outline-danger' : 'btn-outline-success'"
                    >
                      {{ professional.verification_status === 'approved' ? 'Reject' : 'Approve' }}
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
    
    <!-- Professional Details Modal -->
    <div class="modal fade" id="professionalModal" tabindex="-1" aria-labelledby="professionalModalLabel" aria-hidden="true">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="professionalModalLabel">Professional Details</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body" v-if="selectedProfessional">
            <div class="row">
              <div class="col-md-6">
                <h6 class="mb-3">Personal Information</h6>
                <div class="mb-2">
                  <strong>Name:</strong> {{ selectedProfessional.username }}
                </div>
                <div class="mb-2">
                  <strong>Email:</strong> {{ selectedProfessional.email }}
                </div>
                <div class="mb-2">
                  <strong>Phone:</strong> {{ selectedProfessional.phone || 'Not provided' }}
                </div>
                <div class="mb-2">
                  <strong>Address:</strong> {{ selectedProfessional.address || 'Not provided' }}
                </div>
                <div class="mb-2">
                  <strong>PIN Code:</strong> {{ selectedProfessional.pin_code || 'Not provided' }}
                </div>
                <div class="mb-2">
                  <strong>Status:</strong> 
                  <span 
                    class="badge" 
                    :class="getStatusBadgeClass(selectedProfessional.verification_status)"
                  >
                    {{ formatVerificationStatus(selectedProfessional.verification_status) }}
                  </span>
                </div>
                <div class="mb-2">
                  <strong>Joined:</strong> {{ formatDate(selectedProfessional.created_at) }}
                </div>
                <div class="mb-2" v-if="selectedProfessional.documents">
                  <strong>Documents:</strong>
                  <div class="mt-2">
                    <a 
                      :href="getDocumentUrl(selectedProfessional.documents)" 
                      target="_blank" 
                      class="btn btn-sm btn-outline-primary"
                    >
                      <i class="bi bi-file-earmark-text me-1"></i>
                      View Document
                    </a>
                  </div>
                </div>
                <div class="mb-2" v-else>
                  <strong>Documents:</strong>
                  <div class="mt-2">
                    <span class="text-muted">No documents uploaded</span>
                  </div>
                </div>
              </div>
              <div class="col-md-6">
                <h6 class="mb-3">Services</h6>
                <div v-if="!selectedProfessional.services || selectedProfessional.services.length === 0" class="text-muted">
                  No services assigned
                </div>
                <div v-else>
                  <div v-for="service in selectedProfessional.services" :key="service.id" class="card mb-2">
                    <div class="card-body py-2 px-3">
                      <div class="d-flex justify-content-between align-items-center">
                        <div>
                          <strong>{{ service.name }}</strong>
                          <div class="small text-muted">{{ service.time_required }} | ${{ service.base_price }}</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
            <button 
              type="button" 
              class="btn"
              :class="selectedProfessional && selectedProfessional.verification_status === 'approved' ? 'btn-danger' : 'btn-success'"
              @click="toggleStatus(selectedProfessional)"
              v-if="selectedProfessional"
            >
              {{ selectedProfessional && selectedProfessional.verification_status === 'approved' ? 'Reject Professional' : 'Approve Professional' }}
            </button>
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
  name: 'AdminProfessionals',
  data() {
    return {
      searchQuery: '',
      selectedProfessional: null,
      professionalModal: null
    }
  },
  computed: {
    ...mapGetters('admin', ['professionals', 'loading', 'error']),
    
    filteredProfessionals() {
      if (!this.searchQuery) return this.professionals
      
      const query = this.searchQuery.toLowerCase()
      return this.professionals.filter(professional => 
        professional.name?.toLowerCase().includes(query) || 
        professional.username?.toLowerCase().includes(query) || 
        (professional.email && professional.email.toLowerCase().includes(query)) ||
        (professional.phone && professional.phone.includes(query))
      )
    }
  },
  methods: {
    ...mapActions('admin', ['fetchProfessionals', 'updateProfessionalStatus']),
    
    async loadProfessionals() {
      try {
        await this.fetchProfessionals()
        console.log('Loaded professionals:', this.professionals)
      } catch (error) {
        console.error('Failed to fetch professionals', error)
      }
    },
    
    handleSearch() {
      // Debounce search if needed
    },
    
    viewProfessional(professional) {
      this.selectedProfessional = professional
      console.log('Selected professional:', professional)
      this.professionalModal.show()
    },
    
    async toggleStatus(professional) {
      try {
        await this.updateProfessionalStatus({
          professionalId: professional.id,
          isActive: professional.verification_status !== 'approved'
        })
        
        this.$store.dispatch('setNotification', {
          message: `Professional ${professional.verification_status === 'approved' ? 'rejected' : 'approved'} successfully`,
          type: 'success'
        }, { root: true })
        
        // Close modal if open
        if (this.professionalModal && this.professionalModal._isShown) {
          this.professionalModal.hide()
        }
        
        // Refresh the list
        await this.loadProfessionals()
      } catch (error) {
        console.error('Failed to update professional status', error)
        
        this.$store.dispatch('setNotification', {
          message: 'Failed to update professional status',
          type: 'error'
        }, { root: true })
      }
    },
    
    getInitials(name) {
      if (!name) return 'NA'
      return name
        .split(' ')
        .map(part => part.charAt(0))
        .join('')
        .toUpperCase()
        .substring(0, 2)
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
    
    formatVerificationStatus(status) {
      switch (status) {
        case 'approved':
          return 'Approved'
        case 'rejected':
          return 'Rejected'
        case 'pending':
          return 'Pending'
        default:
          return 'Unknown'
      }
    },
    
    getStatusBadgeClass(status) {
      switch (status) {
        case 'approved':
          return 'bg-success'
        case 'rejected':
          return 'bg-danger'
        case 'pending':
          return 'bg-warning'
        default:
          return 'bg-secondary'
      }
    },
    
    getDocumentUrl(filename) {
      if (!filename) return '#';
      console.log('Document URL:', `${Vue.prototype.$http.defaults.baseURL.replace('/api', '')}/uploads/documents/${filename}`);
      // If running locally, we can use a relative URL
      // In production, this might need to be adjusted based on your server configuration
      return `${Vue.prototype.$http.defaults.baseURL.replace('/api', '')}/uploads/documents/${filename}`;
    }
  },
  mounted() {
    this.professionalModal = new bootstrap.Modal(document.getElementById('professionalModal'))
  },
  created() {
    this.loadProfessionals()
  }
}
</script>

<style scoped>
.card {
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
}

.table th, .table td {
  padding: 0.75rem;
}

.avatar-placeholder {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background-color: #6c757d;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  font-weight: bold;
}
</style> 