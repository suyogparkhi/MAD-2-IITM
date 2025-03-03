<!-- src/views/customer/Services.vue -->
<template>
    <div class="customer-services">
      <div class="d-flex justify-content-between align-items-center mb-4">
        <h1>Browse Services</h1>
      </div>
      
      <!-- Search and Filter Bar -->
      <div class="card mb-4">
        <div class="card-body">
          <div class="row g-3">
            <!-- Search Box -->
            <div class="col-md-6">
              <div class="input-group">
                <input 
                  type="text" 
                  class="form-control" 
                  placeholder="Search services..."
                  v-model="searchQuery"
                  @input="filterServices"
                >
                <button 
                  class="btn btn-primary" 
                  type="button"
                  @click="filterServices"
                >
                  <i class="bi bi-search"></i>
                </button>
              </div>
            </div>
            
            <!-- Price Range Filter -->
            <div class="col-md-3">
              <select class="form-select" v-model="priceRange" @change="filterServices">
                <option value="">All Price Ranges</option>
                <option value="0-50">$0 - $50</option>
                <option value="50-100">$50 - $100</option>
                <option value="100-200">$100 - $200</option>
                <option value="200+">$200+</option>
              </select>
            </div>
            
            <!-- Sort By -->
            <div class="col-md-3">
              <select class="form-select" v-model="sortBy" @change="sortServices">
                <option value="name">Name (A-Z)</option>
                <option value="name_desc">Name (Z-A)</option>
                <option value="price_asc">Price (Low to High)</option>
                <option value="price_desc">Price (High to Low)</option>
                <option value="rating">Highest Rated</option>
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
        <p class="mt-2">Loading services...</p>
      </div>
      
      <!-- Error State -->
      <div v-else-if="error" class="alert alert-danger">
        {{ error }}
        <button @click="fetchServices" class="btn btn-sm btn-outline-danger ms-2">Try Again</button>
      </div>
      
      <!-- Services Grid -->
      <div v-else>
        <!-- Filtered Results Info -->
        <div class="d-flex justify-content-between align-items-center mb-3">
          <p class="mb-0" v-if="filteredServices.length > 0">
            Showing {{ filteredServices.length }} services
          </p>
          <button 
            v-if="isFiltered" 
            @click="resetFilters" 
            class="btn btn-sm btn-outline-secondary"
          >
            <i class="bi bi-x-circle me-1"></i> Clear Filters
          </button>
        </div>
        
        <!-- Services List -->
        <div v-if="filteredServices.length > 0" class="row g-4">
          <div 
            v-for="service in filteredServices" 
            :key="service.id"
            class="col-md-6 col-lg-4"
          >
            <div class="card h-100 shadow-sm">
              <div class="card-body">
                <h5 class="card-title">{{ service.name }}</h5>
                <div class="d-flex justify-content-between mb-2">
                  <span class="badge bg-primary">${{ service.base_price.toFixed(2) }}</span>
                  <small class="text-muted">{{ service.time_required || 'Time varies' }}</small>
                </div>
                <p class="card-text">{{ truncateText(service.description, 120) }}</p>
                
                <div class="mt-auto d-flex justify-content-between align-items-center">
                  <div>
                    <div v-if="service.rating" class="d-flex align-items-center">
                      <i class="bi bi-star-fill text-warning me-1"></i>
                      <span>{{ service.rating.toFixed(1) }} ({{ service.rating_count || 0 }})</span>
                    </div>
                    <div v-else class="text-muted small">No ratings yet</div>
                  </div>
                  <button 
                    @click="bookService(service)" 
                    class="btn btn-primary"
                  >
                    Book Now
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
          <h4 class="mb-3">No Services Found</h4>
          <p class="text-muted mb-4">Try adjusting your search or filter criteria.</p>
          <button @click="resetFilters" class="btn btn-primary">
            <i class="bi bi-arrow-clockwise me-1"></i> Reset Filters
          </button>
        </div>
      </div>
      
      <!-- Book Service Modal -->
      <div class="modal fade" id="bookServiceModal" tabindex="-1" aria-hidden="true" ref="bookServiceModal">
        <div class="modal-dialog">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title">Book Service: {{ selectedService?.name }}</h5>
              <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
              <form @submit.prevent="submitBooking">
                <div class="mb-3">
                  <label class="form-label">Service Details</label>
                  <div class="d-flex justify-content-between">
                    <span>{{ selectedService?.name }}</span>
                    <span class="fw-bold">${{ selectedService?.base_price.toFixed(2) }}</span>
                  </div>
                  <hr class="my-2">
                </div>
                
                <div class="mb-3">
                  <label for="remarks" class="form-label">Additional Instructions</label>
                  <textarea
                    class="form-control"
                    id="remarks"
                    v-model="bookingForm.remarks"
                    rows="3"
                    placeholder="Provide any specific requirements or details..."
                  ></textarea>
                </div>
                
                <div class="modal-footer px-0 pb-0">
                  <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                  <button type="submit" class="btn btn-primary" :disabled="formLoading">
                    <span v-if="formLoading" class="spinner-border spinner-border-sm me-1"></span>
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
    name: 'CustomerServices',
    data() {
      return {
        searchQuery: '',
        priceRange: '',
        sortBy: 'name',
        filteredServices: [],
        selectedService: null,
        bookingForm: {
          service_id: null,
          remarks: ''
        },
        formLoading: false,
        bookServiceModal: null
      }
    },
    computed: {
      ...mapGetters('services', [
        'services',
        'loading',
        'error'
      ]),
      
      isFiltered() {
        return this.searchQuery || this.priceRange !== ''
      }
    },
    methods: {
      ...mapActions('services', ['fetchServices']),
      ...mapActions('serviceRequests', ['createServiceRequest']),
      
      filterServices() {
        let filtered = [...this.services]
        
        // Apply search query filter
        if (this.searchQuery) {
          const query = this.searchQuery.toLowerCase()
          filtered = filtered.filter(service => 
            service.name.toLowerCase().includes(query) ||
            (service.description && service.description.toLowerCase().includes(query))
          )
        }
        
        // Apply price range filter
        if (this.priceRange) {
          const [min, max] = this.priceRange.split('-')
          
          if (max === '+') {
            // Handle "$200+" case
            filtered = filtered.filter(service => service.base_price >= parseFloat(min))
          } else {
            // Handle normal range case
            filtered = filtered.filter(service => 
              service.base_price >= parseFloat(min) && 
              service.base_price <= parseFloat(max)
            )
          }
        }
        
        // Update filtered services
        this.filteredServices = filtered
        
        // Apply sorting
        this.sortServices()
      },
      
      sortServices() {
        switch(this.sortBy) {
          case 'name':
            this.filteredServices.sort((a, b) => a.name.localeCompare(b.name))
            break
          case 'name_desc':
            this.filteredServices.sort((a, b) => b.name.localeCompare(a.name))
            break
          case 'price_asc':
            this.filteredServices.sort((a, b) => a.base_price - b.base_price)
            break
          case 'price_desc':
            this.filteredServices.sort((a, b) => b.base_price - a.base_price)
            break
          case 'rating':
            this.filteredServices.sort((a, b) => {
              const ratingA = a.rating || 0
              const ratingB = b.rating || 0
              return ratingB - ratingA
            })
            break
        }
      },
      
      resetFilters() {
        this.searchQuery = ''
        this.priceRange = ''
        this.sortBy = 'name'
        this.filteredServices = [...this.services]
        this.sortServices()
      },
      
      bookService(service) {
        this.selectedService = service
        this.bookingForm = {
          service_id: service.id,
          remarks: ''
        }
        this.bookServiceModal.show()
      },
      
      async submitBooking() {
        this.formLoading = true
        try {
          await this.createServiceRequest(this.bookingForm)
          
          // Hide modal
          this.bookServiceModal.hide()
          
          // Show success notification
          this.$store.dispatch('setNotification', {
            message: 'Service request submitted successfully!',
            type: 'success'
          })
          
          // Redirect to service requests page
          this.$router.push('/customer/requests')
        } catch (error) {
          console.error('Failed to submit service request', error)
          
          this.$store.dispatch('setNotification', {
            message: 'Failed to submit service request. Please try again.',
            type: 'error'
          })
        } finally {
          this.formLoading = false
        }
      },
      
      truncateText(text, maxLength) {
        if (!text) return ''
        if (text.length <= maxLength) return text
        return text.slice(0, maxLength) + '...'
      }
    },
    async created() {
      // Fetch services
      await this.fetchServices()
      
      // Initialize filtered services
      this.filteredServices = [...this.services]
      
      // Apply initial sorting
      this.sortServices()
    },
    mounted() {
      // Initialize Bootstrap modal
      this.bookServiceModal = new Modal(this.$refs.bookServiceModal)
    }
  }
  </script>
  
  <style scoped>
  .customer-services {
    min-height: 80vh;
  }
  </style>