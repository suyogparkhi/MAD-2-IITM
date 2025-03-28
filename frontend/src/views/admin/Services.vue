<!-- src/views/admin/Services.vue -->
<template>
    <div class="admin-services">
      <div class="d-flex justify-content-between align-items-center mb-4">
        <h1>Manage Services</h1>
        <button class="btn btn-primary" @click="showAddServiceModal">
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
      <div v-else class="card">
        <div class="card-header">
          <div class="row align-items-center">
            <div class="col">
              <h5 class="mb-0">All Services</h5>
            </div>
            <div class="col-md-4">
              <input 
                type="text" 
                class="form-control" 
                placeholder="Search services..." 
                v-model="searchQuery"
                @input="handleSearch"
              >
            </div>
          </div>
        </div>
        <div class="card-body p-0">
          <div v-if="filteredServices.length === 0" class="text-center py-5">
            <p class="mb-0">No services found</p>
          </div>
          <div v-else class="table-responsive">
            <table class="table table-hover align-middle mb-0">
              <thead class="table-light">
                <tr>
                  <th>ID</th>
                  <th>Name</th>
                  <th>Description</th>
                  <th>Base Price</th>
                  <th>Time Required</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="service in filteredServices" :key="service.id">
                  <td>{{ service.id }}</td>
                  <td>{{ service.name }}</td>
                  <td>{{ truncateText(service.description, 50) }}</td>
                  <td>${{ service.base_price.toFixed(2) }}</td>
                  <td>{{ service.time_required }}</td>
                  <td>
                    <div class="btn-group">
                      <button 
                        @click="editService(service)" 
                        class="btn btn-sm btn-outline-primary"
                      >
                        Edit
                      </button>
                      <button 
                        @click="confirmDeleteService(service)" 
                        class="btn btn-sm btn-outline-danger"
                      >
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
      
      <!-- Add/Edit Service Modal -->
      <div class="modal fade" id="serviceModal" tabindex="-1" aria-labelledby="serviceModalLabel" aria-hidden="true">
        <div class="modal-dialog">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title" id="serviceModalLabel">
                {{ isEditing ? 'Edit Service' : 'Add New Service' }}
              </h5>
              <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
              <form @submit.prevent="saveService">
                <div class="mb-3">
                  <label for="serviceName" class="form-label">Service Name</label>
                  <input 
                    type="text" 
                    class="form-control" 
                    id="serviceName" 
                    v-model="serviceForm.name"
                    required
                  >
                </div>
                
                <div class="mb-3">
                  <label for="serviceDescription" class="form-label">Description</label>
                  <textarea 
                    class="form-control" 
                    id="serviceDescription" 
                    rows="3"
                    v-model="serviceForm.description"
                    required
                  ></textarea>
                </div>
                
                <div class="mb-3">
                  <label for="servicePrice" class="form-label">Base Price ($)</label>
                  <input 
                    type="number" 
                    class="form-control" 
                    id="servicePrice" 
                    v-model.number="serviceForm.base_price"
                    min="0"
                    step="0.01"
                    required
                  >
                </div>
                
                <div class="mb-3">
                  <label for="serviceTime" class="form-label">Time Required</label>
                  <input 
                    type="text" 
                    class="form-control" 
                    id="serviceTime" 
                    v-model="serviceForm.time_required"
                    placeholder="e.g. 2 hours"
                    required
                  >
                </div>
              </form>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
              <button 
                type="button" 
                class="btn btn-primary" 
                @click="saveService"
                :disabled="formSubmitting"
              >
                <span v-if="formSubmitting" class="spinner-border spinner-border-sm me-1"></span>
                {{ isEditing ? 'Update Service' : 'Add Service' }}
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Delete Confirmation Modal -->
      <div class="modal fade" id="deleteModal" tabindex="-1" aria-labelledby="deleteModalLabel" aria-hidden="true">
        <div class="modal-dialog">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title" id="deleteModalLabel">Confirm Delete</h5>
              <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
              <p>Are you sure you want to delete the service <strong>{{ serviceToDelete?.name }}</strong>?</p>
              <p class="text-danger">This action cannot be undone.</p>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
              <button 
                type="button" 
                class="btn btn-danger" 
                @click="deleteService"
                :disabled="formSubmitting"
              >
                <span v-if="formSubmitting" class="spinner-border spinner-border-sm me-1"></span>
                Delete Service
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
  
  export default {
    name: 'AdminServices',
    data() {
      return {
        searchQuery: '',
        serviceForm: {
          name: '',
          description: '',
          base_price: 0,
          time_required: ''
        },
        isEditing: false,
        serviceToDelete: null,
        formSubmitting: false,
        serviceModal: null,
        deleteModal: null
      }
    },
    computed: {
      ...mapGetters('services', ['services', 'loading', 'error']),
      
      filteredServices() {
        if (!this.searchQuery) return this.services
        
        const query = this.searchQuery.toLowerCase()
        return this.services.filter(service => 
          service.name.toLowerCase().includes(query) || 
          (service.description && service.description.toLowerCase().includes(query))
        )
      }
    },
    methods: {
      ...mapActions('services', ['fetchAdminServices', 'createService', 'updateService', 'deleteService']),
      
      async fetchServices() {
        try {
          await this.fetchAdminServices()
        } catch (error) {
          console.error('Failed to fetch services', error)
        }
      },
      
      handleSearch() {
        // Debounce search if needed
      },
      
      showAddServiceModal() {
        this.isEditing = false
        this.serviceForm = {
          name: '',
          description: '',
          base_price: 0,
          time_required: ''
        }
        this.serviceModal.show()
      },
      
      editService(service) {
        this.isEditing = true
        this.serviceForm = { ...service }
        this.serviceModal.show()
      },
      
      confirmDeleteService(service) {
        this.serviceToDelete = service
        this.deleteModal.show()
      },
      
      async saveService() {
        this.formSubmitting = true
        
        try {
          if (this.isEditing) {
            await this.updateService({
              serviceId: this.serviceForm.id,
              serviceData: this.serviceForm
            })
            
            this.$store.dispatch('setNotification', {
              message: 'Service updated successfully',
              type: 'success'
            }, { root: true })
          } else {
            await this.createService(this.serviceForm)
            
            this.$store.dispatch('setNotification', {
              message: 'Service created successfully',
              type: 'success'
            }, { root: true })
          }
          
          this.serviceModal.hide()
          await this.fetchServices()
        } catch (error) {
          console.error('Failed to save service', error)
          
          this.$store.dispatch('setNotification', {
            message: 'Failed to save service',
            type: 'error'
          }, { root: true })
        } finally {
          this.formSubmitting = false
        }
      },
      
      async deleteService() {
        this.formSubmitting = true
        
        try {
          await this.deleteService(this.serviceToDelete.id)
          
          this.$store.dispatch('setNotification', {
            message: 'Service deleted successfully',
            type: 'success'
          }, { root: true })
          
          this.deleteModal.hide()
          await this.fetchServices()
        } catch (error) {
          console.error('Failed to delete service', error)
          
          this.$store.dispatch('setNotification', {
            message: 'Failed to delete service',
            type: 'error'
          }, { root: true })
        } finally {
          this.formSubmitting = false
        }
      },
      
      truncateText(text, maxLength) {
        if (!text) return ''
        if (text.length <= maxLength) return text
        return text.slice(0, maxLength) + '...'
      }
    },
    mounted() {
      this.serviceModal = new bootstrap.Modal(document.getElementById('serviceModal'))
      this.deleteModal = new bootstrap.Modal(document.getElementById('deleteModal'))
    },
    created() {
      this.fetchServices()
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
  </style>