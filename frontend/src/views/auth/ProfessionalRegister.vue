<!-- src/views/auth/ProfessionalRegister.vue -->
<template>
    <div class="professional-register">
      <h2 class="text-center mb-4">Register as Service Professional</h2>
      
      <div v-if="error" class="alert alert-danger">
        {{ error }}
      </div>
      
      <form @submit.prevent="handleRegister" enctype="multipart/form-data">
        <!-- Basic Information -->
        <h5 class="mb-3">Account Information</h5>
        <div class="mb-3">
          <label for="username" class="form-label">Username</label>
          <input
            type="text"
            class="form-control"
            id="username"
            v-model="form.username"
            required
          >
        </div>
        
        <div class="mb-3">
          <label for="email" class="form-label">Email</label>
          <input
            type="email"
            class="form-control"
            id="email"
            v-model="form.email"
            required
          >
        </div>
        
        <div class="mb-3">
          <label for="password" class="form-label">Password</label>
          <input
            type="password"
            class="form-control"
            id="password"
            v-model="form.password"
            required
          >
        </div>
        
        <div class="mb-3">
          <label for="fullname" class="form-label">Full Name</label>
          <input
            type="text"
            class="form-control"
            id="fullname"
            v-model="form.fullname"
            required
          >
        </div>
        
        <!-- Professional Information -->
        <h5 class="mb-3 mt-4">Professional Information</h5>
        <div class="mb-3">
          <label for="service_id" class="form-label">Service Type</label>
          <select 
            class="form-select" 
            id="service_id" 
            v-model="form.service_id"
            required
          >
            <option value="" disabled>Select a service</option>
            <option v-for="service in services" :key="service.id" :value="service.id">
              {{ service.name }}
            </option>
          </select>
        </div>
        
        <div class="mb-3">
          <label for="experience" class="form-label">Years of Experience</label>
          <input
            type="number"
            class="form-control"
            id="experience"
            v-model.number="form.experience"
            min="0"
            required
          >
        </div>
        
        <div class="mb-3">
          <label for="description" class="form-label">Professional Description</label>
          <textarea
            class="form-control"
            id="description"
            v-model="form.description"
            rows="3"
            placeholder="Describe your professional experience, skills, and qualifications..."
            required
          ></textarea>
        </div>
        
        <div class="mb-3">
          <label for="documents" class="form-label">Upload Verification Documents (PDF)</label>
          <input
            type="file"
            class="form-control"
            id="documents"
            @change="handleFileChange"
            accept=".pdf,.jpg,.jpeg,.png"
            required
          >
          <div class="form-text">Please upload your ID, certifications, or other relevant documents for verification.</div>
        </div>
        
        <!-- Contact Information -->
        <h5 class="mb-3 mt-4">Contact Information</h5>
        <div class="mb-3">
          <label for="phone" class="form-label">Phone Number</label>
          <input
            type="tel"
            class="form-control"
            id="phone"
            v-model="contactInfo.phone"
            placeholder="Enter your phone number"
          >
        </div>
        
        <div class="mb-3">
          <label for="address" class="form-label">Address</label>
          <textarea
            class="form-control"
            id="address"
            v-model="contactInfo.address"
            rows="3"
            required
          ></textarea>
        </div>
        
        <div class="mb-3">
          <label for="pin_code" class="form-label">PIN Code</label>
          <input
            type="text"
            class="form-control"
            id="pin_code"
            v-model="contactInfo.pin_code"
            required
          >
        </div>
        
        <div class="d-grid gap-2">
          <button type="submit" class="btn btn-primary" :disabled="loading">
            <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
            Submit Registration
          </button>
          <router-link to="/login" class="btn btn-outline-secondary">
            Already have an account? Login
          </router-link>
        </div>
      </form>
    </div>
  </template>
  
  <script>
  import { mapGetters, mapActions } from 'vuex'
  
  export default {
    name: 'ProfessionalRegisterView',
    data() {
      return {
        form: {
          username: '',
          email: '',
          password: '',
          fullname: '',
          service_id: '',
          experience: 0,
          description: ''
        },
        contactInfo: {
          address: '',
          pin_code: '',
          phone: ''
        },
        documentFile: null
      }
    },
    computed: {
      ...mapGetters('auth', ['loading', 'error']),
      ...mapGetters('services', ['services'])
    },
    methods: {
      ...mapActions('auth', ['registerProfessional', 'clearError']),
      ...mapActions('services', ['fetchServices', 'fetchPublicServices']),
      
      handleFileChange(event) {
        this.documentFile = event.target.files[0]
      },
      
      async handleRegister() {
        try {
          // Create FormData for multipart/form-data submission
          const formData = new FormData()
          
          // Add all form fields
          Object.keys(this.form).forEach(key => {
            formData.append(key, this.form[key])
          })
          
          // Add contact information
          formData.append('address', this.contactInfo.address)
          formData.append('pin_code', this.contactInfo.pin_code)
          formData.append('phone', this.contactInfo.phone)
          
          // Add document file
          if (this.documentFile) {
            formData.append('documents', this.documentFile)
          }
          
          await this.registerProfessional(formData)
          
          // Show success message and redirect to login
          this.$store.dispatch('setNotification', {
            message: 'Registration submitted successfully! Your account will be reviewed by an administrator.',
            type: 'success',
            timeout: 5000
          })
          
          this.$router.push('/login')
        } catch (error) {
          // Error is handled in store
          console.error('Registration failed', error)
        }
      }
    },
    async created() {
      // Clear any previous errors
      this.clearError()
      
      // Fetch available services for the dropdown
      try {
        await this.fetchPublicServices()
      } catch (error) {
        console.error('Failed to fetch services', error)
      }
    }
  }
  </script>