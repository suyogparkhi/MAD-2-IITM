<!-- src/views/professional/Profile.vue -->
<template>
  <div class="profile-view">
    <h2 class="mb-4">My Professional Profile</h2>
    
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
                    <b-badge variant="primary">Professional</b-badge>
                    <b-badge :variant="getVerificationStatusVariant(professional.verification_status)" class="ml-2">
                      {{ professional.verification_status }}
                    </b-badge>
                  </p>
                  <p class="text-muted">
                    <small>Member since {{ formatDate(user.created_at) }}</small>
                  </p>
                </b-col>
                <b-col md="8">
                  <h4 class="mb-3">Professional Information</h4>
                  <b-list-group flush>
                    <b-list-group-item class="d-flex justify-content-between align-items-center">
                      <div>
                        <strong>Service Type</strong>
                        <p class="mb-0">{{ professional.service ? professional.service.name : 'Not assigned' }}</p>
                      </div>
                    </b-list-group-item>
                    <b-list-group-item class="d-flex justify-content-between align-items-center">
                      <div>
                        <strong>Experience</strong>
                        <p class="mb-0">{{ professional.experience || 0 }} years</p>
                      </div>
                    </b-list-group-item>
                    <b-list-group-item class="d-flex justify-content-between align-items-center">
                      <div>
                        <strong>Description</strong>
                        <p class="mb-0">{{ professional.description || 'No description provided' }}</p>
                      </div>
                    </b-list-group-item>
                    <b-list-group-item class="d-flex justify-content-between align-items-center">
                      <div>
                        <strong>Address</strong>
                        <p class="mb-0">{{ professional.address || 'Not provided' }}</p>
                      </div>
                    </b-list-group-item>
                    <b-list-group-item class="d-flex justify-content-between align-items-center">
                      <div>
                        <strong>Pin Code</strong>
                        <p class="mb-0">{{ professional.pin_code || 'Not provided' }}</p>
                      </div>
                    </b-list-group-item>
                    <b-list-group-item v-if="professional.documents" class="d-flex justify-content-between align-items-center">
                      <div>
                        <strong>Documents</strong>
                        <p class="mb-0">
                          <a :href="professional.documents" target="_blank">View Documents</a>
                        </p>
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
                    <b-button variant="outline-primary" @click="showDocumentModal" class="ml-2">
                      <i class="fas fa-file-upload mr-2"></i> Upload Documents
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
                <p class="text-muted">You haven't completed any services yet.</p>
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
                  
                  <!-- Completion Date Column -->
                  <template #cell(date_of_completion)="data">
                    {{ data.item.date_of_completion ? formatDate(data.item.date_of_completion) : 'Not completed' }}
                  </template>
                  
                  <!-- Status Column -->
                  <template #cell(service_status)="data">
                    <b-badge :variant="getStatusVariant(data.item.service_status)">
                      {{ data.item.service_status }}
                    </b-badge>
                  </template>
                  
                  <!-- Customer Column -->
                  <template #cell(customer)="data">
                    {{ data.item.customer.user.username }}
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
          
          <!-- Reviews Tab -->
          <b-tab title="Reviews">
            <b-card-body>
              <h4 class="mb-4">Customer Reviews</h4>
              
              <div v-if="reviews.length === 0" class="text-center py-4">
                <i class="fas fa-star fa-3x text-muted mb-3"></i>
                <h5>No Reviews Yet</h5>
                <p class="text-muted">You haven't received any reviews yet.</p>
              </div>
              
              <div v-else>
                <b-card v-for="review in reviews" :key="review.id" class="mb-3 review-card">
                  <div class="d-flex align-items-start">
                    <div class="review-avatar mr-3">
                      <i class="fas fa-user-circle fa-3x text-primary"></i>
                    </div>
                    <div class="flex-grow-1">
                      <div class="d-flex justify-content-between align-items-center mb-2">
                        <h5 class="mb-0">{{ review.serviceRequest.customer.user.username }}</h5>
                        <small class="text-muted">{{ formatDate(review.created_at) }}</small>
                      </div>
                      <div class="mb-2">
                        <i v-for="n in 5" :key="n" 
                           :class="['fas', n <= review.rating ? 'fa-star' : 'fa-star-o', 'text-warning']"></i>
                      </div>
                      <p class="mb-0">{{ review.comments }}</p>
                      <small class="text-muted">
                        Service: {{ review.serviceRequest.service.name }}
                      </small>
                    </div>
                  </div>
                </b-card>
              </div>
            </b-card-body>
          </b-tab>
        </b-tabs>
      </b-card>
    </div>
    
    <!-- Edit Profile Modal -->
    <b-modal id="edit-profile-modal" title="Edit Professional Profile" hide-footer>
      <b-form @submit.prevent="updateProfile">
        <b-form-group label="Username">
          <b-form-input v-model="editForm.username" required></b-form-input>
        </b-form-group>
        <b-form-group label="Email">
          <b-form-input v-model="editForm.email" type="email" required></b-form-input>
        </b-form-group>
        <b-form-group label="Experience (years)">
          <b-form-input v-model="editForm.experience" type="number" min="0"></b-form-input>
        </b-form-group>
        <b-form-group label="Description">
          <b-form-textarea v-model="editForm.description" rows="3"></b-form-textarea>
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
    
    <!-- Upload Documents Modal -->
    <b-modal id="document-upload-modal" title="Upload Verification Documents" hide-footer>
      <b-form @submit.prevent="uploadDocuments">
        <b-form-group label="Documents" description="Upload your identification and qualification documents">
          <b-form-file
            v-model="documentForm.file"
            placeholder="Choose a file or drop it here..."
            drop-placeholder="Drop file here..."
            accept=".pdf,.jpg,.jpeg,.png"
          ></b-form-file>
        </b-form-group>
        <div class="d-flex justify-content-end mt-3">
          <b-button variant="secondary" @click="$bvModal.hide('document-upload-modal')" class="mr-2">
            Cancel
          </b-button>
          <b-button type="submit" variant="primary" :disabled="!documentForm.file">
            Upload
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
  name: 'ProfessionalProfileView',
  data() {
    return {
      editForm: {
        username: '',
        email: '',
        experience: 0,
        description: '',
        address: '',
        pin_code: ''
      },
      passwordForm: {
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      },
      documentForm: {
        file: null
      },
      serviceHistoryFields: [
        { key: 'service_name', label: 'Service' },
        { key: 'date_of_request', label: 'Request Date' },
        { key: 'date_of_completion', label: 'Completion Date' },
        { key: 'service_status', label: 'Status' },
        { key: 'customer', label: 'Customer' },
        { key: 'rating', label: 'Rating' }
      ],
      reviews: [] // Will be populated from service requests with reviews
    }
  },
  computed: {
    ...mapGetters('auth', ['user', 'professional', 'loading', 'error']),
    ...mapGetters('serviceRequests', ['professionalRequests']),
    passwordsMatch() {
      return this.passwordForm.newPassword === this.passwordForm.confirmPassword
    },
    serviceRequests() {
      return this.professionalRequests || []
    }
  },
  methods: {
    ...mapActions('auth', [
      'fetchProfile', 
      'updateProfessionalProfile', 
      'changeUserPassword',
      'uploadProfessionalDocuments'
    ]),
    ...mapActions('serviceRequests', ['fetchProfessionalRequests']),
    formatDate(dateString) {
      return format(new Date(dateString), 'MMM dd, yyyy')
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
    getVerificationStatusVariant(status) {
      const variants = {
        'pending': 'warning',
        'approved': 'success',
        'rejected': 'danger'
      }
      return variants[status] || 'light'
    },
    showEditModal() {
      this.editForm = {
        username: this.user.username,
        email: this.user.email,
        experience: this.professional.experience || 0,
        description: this.professional.description || '',
        address: this.professional.address || '',
        pin_code: this.professional.pin_code || ''
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
    showDocumentModal() {
      this.documentForm = {
        file: null
      }
      this.$bvModal.show('document-upload-modal')
    },
    async updateProfile() {
      try {
        await this.updateProfessionalProfile({
          username: this.editForm.username,
          email: this.editForm.email,
          experience: this.editForm.experience,
          description: this.editForm.description,
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
      }
    },
    async changePassword() {
      if (!this.passwordsMatch) {
        return
      }
      
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
      }
    },
    async uploadDocuments() {
      if (!this.documentForm.file) {
        return
      }
      
      try {
        const formData = new FormData()
        formData.append('document', this.documentForm.file)
        
        await this.uploadProfessionalDocuments(formData)
        this.$bvModal.hide('document-upload-modal')
        this.$bvToast.toast('Documents uploaded successfully', {
          title: 'Success',
          variant: 'success',
          solid: true
        })
      } catch (error) {
        this.$bvToast.toast('Failed to upload documents', {
          title: 'Error',
          variant: 'danger',
          solid: true
        })
      }
    },
    processReviews() {
      // Extract reviews from service requests
      this.reviews = this.serviceRequests
        .filter(req => req.review && req.service_status === 'closed')
        .map(req => ({
          ...req.review,
          serviceRequest: req
        }))
        .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
    }
  },
  created() {
    this.fetchProfile()
    this.fetchProfessionalRequests().then(() => {
      this.processReviews()
    })
  },
  watch: {
    professionalRequests() {
      this.processReviews()
    }
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

.review-avatar {
  display: inline-block;
  padding: 10px;
  border-radius: 50%;
  background-color: #f8f9fa;
}

.fa-star, .fa-star-o {
  color: #ffc107;
  font-size: 0.9rem;
}

.review-card {
  transition: transform 0.2s;
}

.review-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}
</style> 