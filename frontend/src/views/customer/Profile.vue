<!-- src/views/customer/Profile.vue -->
<template>
  <div class="profile-view">
    <h2 class="mb-4">My Profile</h2>
    
    <!-- Loading state -->
    <div v-if="loading" class="text-center py-5">
      <b-spinner variant="primary" label="Loading..."></b-spinner>
      <p class="mt-3">Loading your profile...</p>
    </div>
    
    <!-- Error state -->
    <b-alert v-if="error" show variant="danger">
      {{ error }}
      <b-button @click="fetchProfile" variant="outline-danger" size="sm" class="ml-2">
        Try Again
      </b-button>
    </b-alert>
    
    <div v-if="!loading && !error">
      <b-card no-body>
        <b-tabs pills card>
          <!-- Profile Information Tab -->
          <b-tab title="Profile Information" active>
            <b-card-body>
              <b-row>
                <b-col md="4" class="text-center mb-4 mb-md-0">
                  <div class="profile-avatar">
                    <i class="fas fa-user-circle fa-6x text-primary"></i>
                  </div>
                  <h4 class="mt-3">{{ user.username }}</h4>
                  <p class="text-muted">{{ user.email }}</p>
                  <p>
                    <b-badge variant="primary">Customer</b-badge>
                  </p>
                  <p class="text-muted">
                    <small>Member since {{ formatDate(user.created_at) }}</small>
                  </p>
                </b-col>
                <b-col md="8">
                  <h4 class="mb-3">Personal Information</h4>
                  <b-list-group flush>
                    <b-list-group-item class="d-flex justify-content-between align-items-center">
                      <div>
                        <strong>Username</strong>
                        <p class="mb-0">{{ user.username }}</p>
                      </div>
                    </b-list-group-item>
                    <b-list-group-item class="d-flex justify-content-between align-items-center">
                      <div>
                        <strong>Email</strong>
                        <p class="mb-0">{{ user.email }}</p>
                      </div>
                    </b-list-group-item>
                    <b-list-group-item class="d-flex justify-content-between align-items-center">
                      <div>
                        <strong>Address</strong>
                        <p class="mb-0">{{ customer.address || 'Not provided' }}</p>
                      </div>
                    </b-list-group-item>
                    <b-list-group-item class="d-flex justify-content-between align-items-center">
                      <div>
                        <strong>Pin Code</strong>
                        <p class="mb-0">{{ customer.pin_code || 'Not provided' }}</p>
                      </div>
                    </b-list-group-item>
                  </b-list-group>
                  
                  <div class="mt-4">
                    <b-button variant="primary" @click="showEditModal">
                      <i class="fas fa-edit mr-2"></i> Edit Profile
                    </b-button>
                    <b-button variant="outline-secondary" @click="showPasswordModal" class="ml-2">
                      <i class="fas fa-key mr-2"></i> Change Password
                    </b-button>
                  </div>
                </b-col>
              </b-row>
            </b-card-body>
          </b-tab>
          
          <!-- Service History Tab -->
          <b-tab title="Service History">
            <b-card-body>
              <h4 class="mb-4">Service Request History</h4>
              
              <div v-if="serviceRequests.length === 0" class="text-center py-4">
                <i class="fas fa-history fa-3x text-muted mb-3"></i>
                <h5>No Service History</h5>
                <p class="text-muted">You haven't requested any services yet.</p>
                <b-button to="/customer/services" variant="primary">Browse Services</b-button>
              </div>
              
              <div v-else>
                <b-table 
                  :items="serviceRequests" 
                  :fields="serviceHistoryFields"
                  striped 
                  hover
                  responsive
                >
                  <!-- Service Name Column -->
                  <template #cell(service_name)="data">
                    {{ data.item.service.name }}
                  </template>
                  
                  <!-- Date Column -->
                  <template #cell(date_of_request)="data">
                    {{ formatDate(data.item.date_of_request) }}
                  </template>
                  
                  <!-- Status Column -->
                  <template #cell(service_status)="data">
                    <b-badge :variant="getStatusVariant(data.item.service_status)">
                      {{ data.item.service_status }}
                    </b-badge>
                  </template>
                  
                  <!-- Professional Column -->
                  <template #cell(professional)="data">
                    <span v-if="data.item.professional">
                      {{ data.item.professional.user.username }}
                    </span>
                    <span v-else class="text-muted">Not assigned</span>
                  </template>
                  
                  <!-- Rating Column -->
                  <template #cell(rating)="data">
                    <div v-if="data.item.review">
                      <i v-for="n in 5" :key="n" 
                         :class="['fas', n <= data.item.review.rating ? 'fa-star' : 'fa-star-o', 'text-warning']"></i>
                    </div>
                    <span v-else class="text-muted">No review</span>
                  </template>
                </b-table>
              </div>
            </b-card-body>
          </b-tab>
        </b-tabs>
      </b-card>
    </div>
    
    <!-- Edit Profile Modal -->
    <b-modal id="edit-profile-modal" title="Edit Profile" hide-footer>
      <b-form @submit.prevent="updateProfile">
        <b-form-group label="Username">
          <b-form-input v-model="editForm.username" required></b-form-input>
        </b-form-group>
        <b-form-group label="Email">
          <b-form-input v-model="editForm.email" type="email" required></b-form-input>
        </b-form-group>
        <b-form-group label="Address">
          <b-form-textarea v-model="editForm.address" rows="3"></b-form-textarea>
        </b-form-group>
        <b-form-group label="Pin Code">
          <b-form-input v-model="editForm.pin_code"></b-form-input>
        </b-form-group>
        <div class="d-flex justify-content-end">
          <b-button variant="secondary" @click="$bvModal.hide('edit-profile-modal')" class="mr-2">
            Cancel
          </b-button>
          <b-button type="submit" variant="primary">
            Save Changes
          </b-button>
        </div>
      </b-form>
    </b-modal>
    
    <!-- Change Password Modal -->
    <b-modal id="change-password-modal" title="Change Password" hide-footer>
      <b-form @submit.prevent="changePassword">
        <b-form-group label="Current Password">
          <b-form-input v-model="passwordForm.currentPassword" type="password" required></b-form-input>
        </b-form-group>
        <b-form-group label="New Password">
          <b-form-input v-model="passwordForm.newPassword" type="password" required></b-form-input>
        </b-form-group>
        <b-form-group label="Confirm New Password">
          <b-form-input v-model="passwordForm.confirmPassword" type="password" required></b-form-input>
          <b-form-invalid-feedback :state="passwordsMatch">
            Passwords do not match
          </b-form-invalid-feedback>
        </b-form-group>
        <div class="d-flex justify-content-end">
          <b-button variant="secondary" @click="$bvModal.hide('change-password-modal')" class="mr-2">
            Cancel
          </b-button>
          <b-button type="submit" variant="primary" :disabled="!passwordsMatch">
            Change Password
          </b-button>
        </div>
      </b-form>
    </b-modal>
  </div>
</template>

<script>
import { mapActions, mapGetters } from 'vuex'
import { format } from 'date-fns'
import Vue from 'vue'

export default {
  name: 'CustomerProfileView',
  data() {
    return {
      editForm: {
        username: '',
        email: '',
        address: '',
        pin_code: ''
      },
      passwordForm: {
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      },
      serviceHistoryFields: [
        { key: 'service_name', label: 'Service' },
        { key: 'date_of_request', label: 'Date' },
        { key: 'service_status', label: 'Status' },
        { key: 'professional', label: 'Professional' },
        { key: 'rating', label: 'Rating' }
      ]
    }
  },
  computed: {
    ...mapGetters('auth', ['user', 'customer', 'loading', 'error']),
    ...mapGetters('serviceRequests', ['customerRequests']),
    passwordsMatch() {
      return this.passwordForm.newPassword === this.passwordForm.confirmPassword
    }
  },
  methods: {
    ...mapActions('auth', ['fetchProfile', 'updateCustomerProfile', 'changeUserPassword']),
    ...mapActions('serviceRequests', ['fetchCustomerRequests']),
    formatDate(dateString) {
      if (!dateString) return 'N/A'
      try {
        return format(new Date(dateString), 'MMMM d, yyyy')
      } catch (error) {
        console.error('Error formatting date:', error)
        return 'N/A'
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
    showEditModal() {
      this.editForm = {
        username: this.user.username,
        email: this.user.email,
        address: this.customer.address || '',
        pin_code: this.customer.pin_code || ''
      }
      this.$bvModal.show('edit-profile-modal')
    },
    showPasswordModal() {
      this.passwordForm = {
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      }
      this.$bvModal.show('change-password-modal')
    },
    async updateProfile() {
      this.updating = true
      
      try {
        await this.updateCustomerProfile({
          username: this.editForm.username,
          email: this.editForm.email,
          address: this.editForm.address,
          pin_code: this.editForm.pin_code
        })
        this.$bvModal.hide('edit-profile-modal')
        this.$bvToast.toast('Profile updated successfully', {
          title: 'Success',
          variant: 'success',
          solid: true
        })
      } catch (error) {
        this.$bvToast.toast('Failed to update profile', {
          title: 'Error',
          variant: 'danger',
          solid: true
        })
      } finally {
        this.updating = false
      }
    },
    async changePassword() {
      if (this.passwordForm.newPassword !== this.passwordForm.confirmPassword) {
        return
      }
      
      this.changingPassword = true
      
      try {
        await this.changeUserPassword({
          currentPassword: this.passwordForm.currentPassword,
          newPassword: this.passwordForm.newPassword
        })
        this.$bvModal.hide('change-password-modal')
        this.$bvToast.toast('Password changed successfully', {
          title: 'Success',
          variant: 'success',
          solid: true
        })
      } catch (error) {
        this.$bvToast.toast('Failed to change password', {
          title: 'Error',
          variant: 'danger',
          solid: true
        })
      } finally {
        this.changingPassword = false
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
    async fetchProfile() {
      this.loading = true
      this.error = null
      
      try {
        const response = await Vue.prototype.$http.get('/auth/user-info')
        this.profile = response.data
        
        // If created_at is not in the response, set it to null to avoid date formatting errors
        if (!this.profile.created_at) {
          this.profile.created_at = null
        }
      } catch (error) {
        console.error('Failed to fetch profile:', error)
        this.error = 'Failed to load profile information. Please try again.'
      } finally {
        this.loading = false
      }
    }
  },
  created() {
    this.fetchProfile()
    this.fetchCustomerRequests()
  }
}
</script>

<style scoped>
.profile-avatar {
  display: inline-block;
  padding: 20px;
  border-radius: 50%;
  background-color: #f8f9fa;
}

.fa-star, .fa-star-o {
  font-size: 0.9rem;
}
</style> 