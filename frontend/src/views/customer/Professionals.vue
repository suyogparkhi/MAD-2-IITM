<template>
  <div class="customer-professionals">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1>Find Professionals</h1>
    </div>
    
    <!-- Search and Filter Bar -->
    <div class="card mb-4">
      <div class="card-body">
        <div class="row g-3">
          <!-- Search Box -->
          <div class="col-md-4">
            <div class="input-group">
              <input 
                type="text" 
                class="form-control" 
                placeholder="Search professionals..."
                v-model="searchQuery"
                @input="handleSearch"
              >
              <button 
                class="btn btn-primary" 
                type="button"
                @click="filterProfessionals"
              >
                <i class="bi bi-search"></i>
              </button>
            </div>
          </div>
          
          <!-- Service Filter -->
          <div class="col-md-3">
            <select class="form-select" v-model="serviceId" @change="filterProfessionals">
              <option value="">All Services</option>
              <option 
                v-for="service in services" 
                :key="service.id" 
                :value="service.id"
              >
                {{ service.name }}
              </option>
            </select>
          </div>
          
          <!-- Rating Filter -->
          <div class="col-md-3">
            <select class="form-select" v-model="minRating" @change="filterProfessionals">
              <option value="">All Ratings</option>
              <option value="4">4+ Stars</option>
              <option value="4.5">4.5+ Stars</option>
              <option value="5">5 Stars</option>
            </select>
          </div>
          
          <!-- Sort By -->
          <div class="col-md-2">
            <select class="form-select" v-model="sortBy" @change="sortProfessionals">
              <option value="name">Name (A-Z)</option>
              <option value="rating">Top Rated</option>
              <option value="experience">Most Experienced</option>
            </select>
          </div>
        </div>
      </div>
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
    
    <!-- Professionals Grid -->
    <div v-else>
      <!-- Filtered Results Info -->
      <div class="d-flex justify-content-between align-items-center mb-3">
        <p class="mb-0" v-if="filteredProfessionals.length > 0">
          Showing {{ filteredProfessionals.length }} professionals
        </p>
        <button 
          v-if="isFiltered" 
          @click="resetFilters" 
          class="btn btn-sm btn-outline-secondary"
        >
          <i class="bi bi-x-circle me-1"></i> Clear Filters
        </button>
      </div>
      
      <!-- Professionals List -->
      <div v-if="filteredProfessionals.length > 0" class="row g-4">
        <div 
          v-for="professional in filteredProfessionals" 
          :key="professional.id"
          class="col-md-6 col-lg-4"
        >
          <div class="card h-100 shadow-sm">
            <div class="card-body">
              <div class="d-flex justify-content-between mb-3">
                <h5 class="card-title mb-0">{{ professional.name }}</h5>
                <span class="badge bg-info">{{ professional.service_name }}</span>
              </div>
              
              <div class="d-flex mb-3">
                <div class="me-3">
                  <div class="avatar-placeholder">
                    {{ getInitials(professional.name) }}
                  </div>
                </div>
                <div>
                  <div v-if="professional.avg_rating" class="mb-1">
                    <span class="text-warning">
                      <i class="bi bi-star-fill"></i>
                    </span>
                    <strong>{{ professional.avg_rating.toFixed(1) }}</strong>
                    <span class="text-muted">({{ professional.review_count }} reviews)</span>
                  </div>
                  <div class="mb-1">
                    <i class="bi bi-briefcase me-1"></i>
                    <span>{{ professional.experience || 0 }} years experience</span>
                  </div>
                  <div>
                    <i class="bi bi-check-circle me-1"></i>
                    <span>{{ professional.completed_services || 0 }} jobs completed</span>
                  </div>
                </div>
              </div>
              
              <p class="card-text">{{ truncateText(professional.description || 'No description provided.', 100) }}</p>
              
              <div class="mt-auto d-flex justify-content-end">
                <button 
                  @click="viewProfile(professional)" 
                  class="btn btn-sm btn-outline-primary me-2"
                >
                  View Profile
                </button>
                <button 
                  @click="requestService(professional)" 
                  class="btn btn-sm btn-primary"
                >
                  Request Service
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Empty State -->
      <div v-else class="text-center py-5">
        <div class="mb-3">
          <i class="bi bi-search" style="font-size: 3rem;"></i>
        </div>
        <h4 class="mb-3">No Professionals Found</h4>
        <p class="text-muted mb-4">Try adjusting your search or filter criteria.</p>
        <button @click="resetFilters" class="btn btn-primary">
          <i class="bi bi-arrow-clockwise me-1"></i> Reset Filters
        </button>
      </div>
    </div>
    
    <!-- Professional Profile Modal -->
    <div class="modal fade" id="professionalProfileModal" tabindex="-1" aria-hidden="true" ref="professionalProfileModal">
      <div class="modal-dialog">
        <div class="modal-content" v-if="selectedProfessional">
          <div class="modal-header">
            <h5 class="modal-title">{{ selectedProfessional.name }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <div class="text-center mb-3">
              <div class="avatar-placeholder mx-auto mb-2" style="width: 80px; height: 80px; font-size: 2rem;">
                {{ getInitials(selectedProfessional.name) }}
              </div>
              <h4>{{ selectedProfessional.name }}</h4>
              <span class="badge bg-info">{{ selectedProfessional.service_name }}</span>
            </div>
            
            <div class="mb-3">
              <h6>About</h6>
              <p>{{ selectedProfessional.description || 'No description provided.' }}</p>
            </div>
            
            <div class="row mb-3">
              <div class="col-md-4 text-center">
                <div class="h4 mb-0">{{ selectedProfessional.experience || 0 }}</div>
                <div class="small text-muted">Years Exp.</div>
              </div>
              <div class="col-md-4 text-center">
                <div class="h4 mb-0">{{ selectedProfessional.completed_services || 0 }}</div>
                <div class="small text-muted">Completed</div>
              </div>
              <div class="col-md-4 text-center">
                <div class="h4 mb-0">{{ selectedProfessional.avg_rating ? selectedProfessional.avg_rating.toFixed(1) : 'N/A' }}</div>
                <div class="small text-muted">Rating</div>
              </div>
            </div>
            
            <hr>
            
            <div class="d-grid gap-2">
              <button 
                @click="requestService(selectedProfessional)" 
                class="btn btn-primary"
              >
                Request Service
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Service Request Modal -->
    <div class="modal fade" id="serviceRequestModal" tabindex="-1" aria-hidden="true" ref="serviceRequestModal">
      <div class="modal-dialog">
        <div class="modal-content" v-if="selectedProfessional">
          <div class="modal-header">
            <h5 class="modal-title">Request Service</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="submitRequest">
              <div class="mb-3">
                <label class="form-label">Professional</label>
                <input type="text" class="form-control" disabled :value="selectedProfessional.name">
              </div>
              
              <div class="mb-3">
                <label class="form-label">Service</label>
                <select class="form-select" v-model="requestForm.service_id" required>
                  <option :value="selectedProfessional.service_id">{{ selectedProfessional.service_name }}</option>
                </select>
              </div>
              
              <div class="mb-3">
                <label class="form-label">Additional Instructions</label>
                <textarea
                  class="form-control"
                  v-model="requestForm.remarks"
                  rows="3"
                  placeholder="Provide any specific requirements or details..."
                ></textarea>
              </div>
              
              <div class="d-grid gap-2">
                <button 
                  type="submit" 
                  class="btn btn-primary" 
                  :disabled="requestLoading"
                >
                  <span v-if="requestLoading" class="spinner-border spinner-border-sm me-1"></span>
                  Submit Request
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'
import { Modal } from 'bootstrap'

export default {
  name: 'CustomerProfessionals',
  data() {
    return {
      searchQuery: '',
      serviceId: '',
      minRating: '',
      sortBy: 'name',
      professionalProfileModal: null,
      serviceRequestModal: null,
      requestForm: {
        service_id: null,
        professional_id: null,
        remarks: ''
      },
      requestLoading: false
    }
  },
  computed: {
    ...mapGetters('professionals', [
      'professionals',
      'filteredProfessionals',
      'selectedProfessional',
      'loading',
      'error'
    ]),
    ...mapGetters('services', ['services']),
    
    isFiltered() {
      return this.searchQuery || this.serviceId || this.minRating
    }
  },
  methods: {
    ...mapActions('professionals', [
      'fetchProfessionals',
      'filterProfessionals',
      'clearFilters',
      'selectProfessional'
    ]),
    ...mapActions('services', ['fetchServices']),
    ...mapActions('serviceRequests', ['createServiceRequest']),
    
    async loadProfessionals() {
      try {
        await this.fetchProfessionals()
      } catch (error) {
        console.error('Failed to fetch professionals', error)
      }
    },
    
    handleSearch() {
      // Debounce implementation would go here
      this.filterProfessionals()
    },
    
    filterProfessionals() {
      this.$store.dispatch('professionals/filterProfessionals', {
        query: this.searchQuery,
        serviceId: this.serviceId ? parseInt(this.serviceId) : null,
        minRating: this.minRating ? parseFloat(this.minRating) : null
      })
      
      this.sortProfessionals()
    },
    
    sortProfessionals() {
      const professionals = [...this.filteredProfessionals]
      
      switch (this.sortBy) {
        case 'name':
          professionals.sort((a, b) => a.name.localeCompare(b.name))
          break
        case 'rating':
          professionals.sort((a, b) => {
            const ratingA = a.avg_rating || 0
            const ratingB = b.avg_rating || 0
            return ratingB - ratingA
          })
          break
        case 'experience':
          professionals.sort((a, b) => {
            const expA = a.experience || 0
            const expB = b.experience || 0
            return expB - expA
          })
          break
      }
      
      this.$store.commit('professionals/SET_FILTERED_PROFESSIONALS', professionals)
    },
    
    resetFilters() {
      this.searchQuery = ''
      this.serviceId = ''
      this.minRating = ''
      this.sortBy = 'name'
      
      this.$store.dispatch('professionals/clearFilters')
      this.sortProfessionals()
    },
    
    viewProfile(professional) {
      this.$store.commit('professionals/SET_SELECTED_PROFESSIONAL', professional)
      this.professionalProfileModal.show()
    },
    
    requestService(professional) {
      this.$store.commit('professionals/SET_SELECTED_PROFESSIONAL', professional)
      
      this.requestForm = {
        service_id: professional.service_id,
        professional_id: professional.id,
        remarks: ''
      }
      
      // Hide profile modal if it's open
      if (this.professionalProfileModal._isShown) {
        this.professionalProfileModal.hide()
      }
      
      // Show request modal
      setTimeout(() => {
        this.serviceRequestModal.show()
      }, 500)
    },
    
    async submitRequest() {
      this.requestLoading = true
      
      try {
        await this.createServiceRequest(this.requestForm)
        
        this.$store.dispatch('setNotification', {
          message: 'Service request submitted successfully',
          type: 'success'
        }, { root: true })
        
        this.serviceRequestModal.hide()
        
        // Clear form
        this.requestForm = {
          service_id: null,
          professional_id: null,
          remarks: ''
        }
        
        // Redirect to service requests page
        this.$router.push('/customer/service-requests')
      } catch (error) {
        console.error('Failed to submit service request:', error)
        
        this.$store.dispatch('setNotification', {
          message: 'Failed to submit service request. Please try again.',
          type: 'error'
        }, { root: true })
      } finally {
        this.requestLoading = false
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
    
    truncateText(text, length) {
      if (!text) return ''
      if (text.length <= length) return text
      return text.substring(0, length) + '...'
    }
  },
  async mounted() {
    this.professionalProfileModal = new Modal(document.getElementById('professionalProfileModal'))
    this.serviceRequestModal = new Modal(document.getElementById('serviceRequestModal'))
    
    // Fetch services if not already loaded
    if (!this.services || this.services.length === 0) {
      await this.fetchServices()
    }
    
    // Load professionals
    await this.loadProfessionals()
  }
}
</script>

<style scoped>
.card {
  transition: transform 0.2s, box-shadow 0.2s;
}

.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15) !important;
}

.avatar-placeholder {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background-color: #6c757d;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  font-weight: bold;
}
</style> 