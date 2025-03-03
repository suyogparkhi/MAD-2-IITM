<!-- src/views/admin/Services.vue -->
<template>
    <div class="admin-services">
      <div class="d-flex justify-content-between align-items-center mb-4">
        <h1>Services Management</h1>
        <button @click="showAddServiceModal" class="btn btn-primary">
          <i class="bi bi-plus-circle me-1"></i> Add New Service
        </button>
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
      
      <!-- Services Table -->
      <div v-else-if="services.length > 0" class="card shadow-sm">
        <div class="card-header bg-white">
          <div class="row g-2 align-items-center">
            <div class="col-md-6">
              <input 
                type="text" 
                class="form-control" 
                placeholder="Search services..." 
                v-model="searchQuery"
                @input="filterServices"
              >
            </div>
            <div class="col-md-6 text-md-end">
              <span class="text-muted">Total: {{ services.length }} services</span>
            </div>
          </div>
        </div>
        
        <div class="table-responsive">
          <table class="table table-hover align-middle mb-0">
            <thead class="table-light">
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Base Price</th>
                <th>Time Required</th>
                <th>Professionals</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="service in filteredServices" :key="service.id">
                <td>{{ service.id }}</td>
                <td>
                  <div class="fw-bold">{{ service.name }}</div>
                  <div class="small text-muted">{{ truncateText(service.description, 60) }}</div>
                </td>
                <td>${{ service.base_price.toFixed(2) }}</td>
                <td>{{ service.time_required || 'Varies' }}</td>
                <td>{{ service.professionals_count || 0 }}</td>
                <td>
                  <div class="btn-group">
                    <button 
                      @click="editService(service)" 
                      class="btn btn-sm btn-outline-primary"
                    >
                      <i class="bi bi-pencil"></i>
                    </button>
                    <button 
                      @click="showDeleteConfirmation(service)"
                      class="btn btn-sm btn-outline-danger"
                    >
                      <i class="bi bi-trash"></i>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      
      <!-- Empty State -->
      <div v-else class="text-center py-5">
        <div class="mb-3">
          <i class="bi bi-tools" style="font-size: 3rem;"></i>
        </div>
        <h4 class="mb-3">No Services Found</h4>
        <p class="text-muted mb-4">Get started by adding your first service.</p>
        <button @click="showAddServiceModal" class="btn btn-primary">
          <i class="bi bi-plus-circle me-1"></i> Add New Service
        </button>
      </div>
      
      <!-- Add/Edit Service Modal -->
      <div class="modal fade" id="serviceModal" tabindex="-1" aria-hidden="true" ref="serviceModal">
        <div class="modal-dialog">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title">{{ isEditMode ? 'Edit Service' : 'Add New Service' }}</h5>
              <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
              <form @submit.prevent="isEditMode ? updateService() : createService()">
                <div class="mb-3">
                  <label for="serviceName" class="form-label">Service Name</label>
                  <input
                    type="text"
                    class="form-control"
                    id="serviceName"
                    v-model="serviceForm.name"
                    placeholder="e.g., Plumbing, AC Repair, Cleaning"
                    required
                  >
                </div>
                
                <div class="mb-3">
                  <label for="serviceDescription" class="form-label">Description</label>
                  <textarea
                    class="form-control"
                    id="serviceDescription"
                    v-model="serviceForm.description"
                    rows="3"
                    placeholder="Provide details about the service..."
                  ></textarea>
                </div>
                
                <div class="row mb-3">
                  <div class="col-md-6">
                    <label for="servicePrice" class="form-label">Base Price ($)</label>
                    <input
                      type="number"
                      class="form-control"
                      id="servicePrice"
                      v-model.number="serviceForm.base_price"
                      min="0"
                      step="0.01"
                      placeholder="0.00"
                      required
                    >
                  </div>
                  <div class="col-md-6">
                    <label for="serviceTime" class="form-label">Time Required</label>
                    <input
                      type="text"
                      class="form-control"
                      id="serviceTime"
                      v-model="serviceForm.time_required"
                      placeholder="e.g., 2 hours, 1 day"
                    >
                  </div>
                </div>
                
                <div class="modal-footer px-0 pb-0">
                  <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                  <button type="submit" class="btn btn-primary" :disabled="formLoading">
                    <span v-if="formLoading" class="spinner-border spinner-border-sm me-1"></span>
                    {{ isEditMode ? 'Update Service' : 'Add Service' }}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Delete Confirmation Modal -->
      <div class="modal fade" id="deleteModal" tabindex="-1" aria-hidden="true" ref="deleteModal">
        <div class="modal-dialog modal-sm">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title">Confirm Delete</h5>
              <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
              Are you sure you want to delete <strong>{{ serviceToDelete?.name }}</strong>?
              <div class="alert alert-warning mt-2 mb-0">
                <small class="mb-0">
                  <i class="bi bi-exclamation-triangle me-1"></i>
                  This action cannot be undone.
                </small>
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
              <button 
                type="button" 
                class="btn btn-danger" 
                @click="deleteService" 
                :disabled="formLoading"
              >
                <span v-if="formLoading" class="spinner-border spinner-border-sm me-1"></span>
                Delete
              </button>
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
    name: 'AdminServices',
    data() {
      return {
        searchQuery: '',
        filteredServices: [],
        serviceForm: {
          name: '',
          description: '',
          base_price: 0,
          time_required: ''
        },
        isEditMode: false,
        formLoading: false,
        serviceToDelete: null,
        serviceModal: null,
        deleteModal: null
      }
    },
    computed: {
      ...mapGetters('services', [
        'services',
        'loading',
        'error'
      ])
    },
    methods: {
      ...mapActions('services', [
        'fetchAdminServices',
        'createService',
        'updateService',
        'deleteService'
      ]),
      
      filterServices() {
        if (!this.searchQuery) {
          this.filteredServices = [...this.services]
          return
        }
        
        const query = this.searchQuery.toLowerCase()
        this.filteredServices = this.services.filter(service => 
          service.name.toLowerCase().includes(query) ||
          (service.description && service.description.toLowerCase().includes(query))
        )
      },
      
      showAddServiceModal() {
        // Reset form
        this.serviceForm = {
          name: '',
          description: '',
          base_price: 0,
          time_required: ''
        }
        this.isEditMode = false
        
        // Show modal
        this.serviceModal.show()
      },
      
      editService(service) {
        // Populate form with service data
        this.serviceForm = {
          id: service.id,
          name: service.name,
          description: service.description || '',
          base_price: service.base_price,
          time_required: service.time_required || ''
        }
        this.isEditMode = true
        
        // Show modal
        this.serviceModal.show()
      },
      
      showDeleteConfirmation(service) {
        this.serviceToDelete = service
        this.deleteModal.show()
      },
      
      async handleCreateService() {
        this.formLoading = true
        try {
          await this.createService(this.serviceForm)
          
          // Hide modal on success
          this.serviceModal.hide()
          
          // Refresh the services list
          await this.fetchAdminServices()
          
          // Reset form
          this.serviceForm = {
            name: '',
            description: '',
            base_price: 0,
            time_required: ''
          }
          
          this.$store.dispatch('setNotification', {
            message: 'Service created successfully.',
            type: 'success'
          })
        } catch (error) {
          console.error('Failed to create service', error)
        } finally {
          this.formLoading = false
        }
      },
      
      async handleUpdateService() {
        this.formLoading = true
        try {
          const serviceId = this.serviceForm.id
          const serviceData = {
            name: this.serviceForm.name,
            description: this.serviceForm.description,
            base_price: this.serviceForm.base_price,
            time_required: this.serviceForm.time_required
          }
          
          await this.updateService({ 
            serviceId, 
            serviceData 
          })
          
          // Hide modal on success
          this.serviceModal.hide()
          
          // Refresh the services list
          await this.fetchAdminServices()
          
          this.$store.dispatch('setNotification', {
            message: 'Service updated successfully.',
            type: 'success'
          })
        } catch (error) {
          console.error('Failed to update service', error)
        } finally {
          this.formLoading = false
        }
      },
      
      async handleDeleteService() {
        this.formLoading = true
        try {
          if (!this.serviceToDelete) return
          
          await this.deleteService(this.serviceToDelete.id)
          
          // Hide modal on success
          this.deleteModal.hide()
          
          // Refresh the services list
          await this.fetchAdminServices()
          
          this.$store.dispatch('setNotification', {
            message: 'Service deleted successfully.',
            type: 'success'
          })
        } catch (error) {
          console.error('Failed to delete service', error)
        } finally {
          this.formLoading = false
          this.serviceToDelete = null
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
      await this.fetchAdminServices()
      
      // Initialize filtered services
      this.filteredServices = [...this.services]
    },
    mounted() {
      // Initialize Bootstrap modals
      this.serviceModal = new Modal(this.$refs.serviceModal)
      this.deleteModal = new Modal(this.$refs.deleteModal)
    }
  }
  </script>
  
  <style scoped>
  .admin-services {
    min-height: 80vh;
  }
  </style>