<!-- src/views/admin/Customers.vue -->
<template>
  <div class="admin-customers">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1>Manage Customers</h1>
    </div>
    
    <!-- Loading State -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-2">Loading customers...</p>
    </div>
    
    <!-- Error State -->
    <div v-else-if="error" class="alert alert-danger">
      {{ error }}
      <button @click="loadCustomers" class="btn btn-sm btn-outline-danger ms-2">Try Again</button>
    </div>
    
    <!-- Customers Table -->
    <div v-else class="card">
      <div class="card-header">
        <div class="row align-items-center">
          <div class="col">
            <h5 class="mb-0">All Customers</h5>
          </div>
          <div class="col-md-4">
            <input 
              type="text" 
              class="form-control" 
              placeholder="Search customers..." 
              v-model="searchQuery"
              @input="handleSearch"
            >
          </div>
        </div>
      </div>
      <div class="card-body p-0">
        <div v-if="filteredCustomers.length === 0" class="text-center py-5">
          <p class="mb-0">No customers found</p>
        </div>
        <div v-else class="table-responsive">
          <table class="table table-hover align-middle mb-0">
            <thead class="table-light">
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Email</th>
                <th>Phone</th>
                <th>Requests</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="customer in filteredCustomers" :key="customer.id">
                <td>{{ customer.id }}</td>
                <td>
                  <div class="d-flex align-items-center">
                    <div class="avatar-placeholder me-2">
                      {{ getInitials(customer.name) }}
                    </div>
                    <div>
                      {{ customer.name }}
                    </div>
                  </div>
                </td>
                <td>{{ customer.email }}</td>
                <td>{{ customer.phone || 'N/A' }}</td>
                <td>
                  <span v-if="customer.requests_count">
                    {{ customer.requests_count }} requests
                  </span>
                  <span v-else class="text-muted">No requests</span>
                </td>
                <td>
                  <span 
                    class="badge" 
                    :class="customer.is_active ? 'bg-success' : 'bg-danger'"
                  >
                    {{ customer.is_active ? 'Active' : 'Inactive' }}
                  </span>
                </td>
                <td>
                  <div class="btn-group">
                    <button 
                      @click="viewCustomer(customer)" 
                      class="btn btn-sm btn-outline-primary"
                    >
                      View
                    </button>
                    <button 
                      @click="toggleStatus(customer)" 
                      class="btn btn-sm"
                      :class="customer.is_active ? 'btn-outline-danger' : 'btn-outline-success'"
                    >
                      {{ customer.is_active ? 'Deactivate' : 'Activate' }}
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
    
    <!-- Customer Details Modal -->
    <div class="modal fade" id="customerModal" tabindex="-1" aria-labelledby="customerModalLabel" aria-hidden="true">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="customerModalLabel">Customer Details</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body" v-if="selectedCustomer">
            <div class="row">
              <div class="col-md-6">
                <h6 class="mb-3">Personal Information</h6>
                <div class="mb-2">
                  <strong>Name:</strong> {{ selectedCustomer.name }}
                </div>
                <div class="mb-2">
                  <strong>Email:</strong> {{ selectedCustomer.email }}
                </div>
                <div class="mb-2">
                  <strong>Phone:</strong> {{ selectedCustomer.phone || 'Not provided' }}
                </div>
                <div class="mb-2">
                  <strong>Address:</strong> {{ selectedCustomer.address || 'Not provided' }}
                </div>
                <div class="mb-2">
                  <strong>PIN Code:</strong> {{ selectedCustomer.pin_code || 'Not provided' }}
                </div>
                <div class="mb-2">
                  <strong>Status:</strong> 
                  <span 
                    class="badge" 
                    :class="selectedCustomer.is_active ? 'bg-success' : 'bg-danger'"
                  >
                    {{ selectedCustomer.is_active ? 'Active' : 'Inactive' }}
                  </span>
                </div>
                <div class="mb-2">
                  <strong>Joined:</strong> {{ formatDate(selectedCustomer.created_at) }}
                </div>
              </div>
              <div class="col-md-6">
                <h6 class="mb-3">Recent Service Requests</h6>
                <div v-if="!selectedCustomer.requests || selectedCustomer.requests.length === 0" class="text-muted">
                  No service requests found
                </div>
                <div v-else>
                  <div v-for="request in selectedCustomer.requests" :key="request.id" class="card mb-2">
                    <div class="card-body py-2 px-3">
                      <div class="d-flex justify-content-between align-items-center">
                        <div>
                          <strong>{{ request.service_name }}</strong>
                          <div class="small text-muted">{{ formatDate(request.requested_date) }} | {{ request.status }}</div>
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
              :class="selectedCustomer && selectedCustomer.is_active ? 'btn-danger' : 'btn-success'"
              @click="toggleStatus(selectedCustomer)"
              v-if="selectedCustomer"
            >
              {{ selectedCustomer && selectedCustomer.is_active ? 'Deactivate Account' : 'Activate Account' }}
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
  name: 'AdminCustomers',
  data() {
    return {
      searchQuery: '',
      selectedCustomer: null,
      customerModal: null
    }
  },
  computed: {
    ...mapGetters('admin', ['customers', 'loading', 'error']),
    
    filteredCustomers() {
      if (!this.searchQuery) return this.customers
      
      const query = this.searchQuery.toLowerCase()
      return this.customers.filter(customer => 
        customer.name.toLowerCase().includes(query) || 
        (customer.email && customer.email.toLowerCase().includes(query)) ||
        (customer.phone && customer.phone.includes(query))
      )
    }
  },
  methods: {
    ...mapActions('admin', ['fetchCustomers', 'updateCustomerStatus']),
    
    async loadCustomers() {
      try {
        await this.fetchCustomers()
      } catch (error) {
        console.error('Failed to fetch customers', error)
      }
    },
    
    handleSearch() {
      // Debounce search if needed
    },
    
    viewCustomer(customer) {
      this.selectedCustomer = customer
      this.customerModal.show()
    },
    
    async toggleStatus(customer) {
      try {
        await this.updateCustomerStatus({
          customerId: customer.id,
          isActive: !customer.is_active
        })
        
        this.$store.dispatch('setNotification', {
          message: `Customer ${customer.is_active ? 'deactivated' : 'activated'} successfully`,
          type: 'success'
        }, { root: true })
        
        // Close modal if open
        if (this.customerModal && this.customerModal._isShown) {
          this.customerModal.hide()
        }
        
        // Refresh the list
        await this.loadCustomers()
      } catch (error) {
        console.error('Failed to update customer status', error)
        
        this.$store.dispatch('setNotification', {
          message: 'Failed to update customer status',
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
    }
  },
  mounted() {
    this.customerModal = new bootstrap.Modal(document.getElementById('customerModal'))
  },
  created() {
    this.loadCustomers()
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