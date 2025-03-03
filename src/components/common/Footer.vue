<template>
  <footer class="bg-dark text-white py-5 mt-5">
    <b-container>
      <b-row>
        <b-col lg="4" md="6" class="mb-4 mb-md-0">
          <h5 class="text-uppercase mb-4">A-Z Household Services</h5>
          <p>
            Your one-stop platform for all household services. 
            Connect with professionals or become one yourself.
          </p>
          <div class="mt-4">
            <b-button variant="outline-light" class="mr-2" size="sm">
              <i class="fab fa-facebook-f"></i>
            </b-button>
            <b-button variant="outline-light" class="mr-2" size="sm">
              <i class="fab fa-twitter"></i>
            </b-button>
            <b-button variant="outline-light" class="mr-2" size="sm">
              <i class="fab fa-instagram"></i>
            </b-button>
            <b-button variant="outline-light" size="sm">
              <i class="fab fa-linkedin-in"></i>
            </b-button>
          </div>
        </b-col>

        <b-col lg="2" md="6" class="mb-4 mb-md-0">
          <h5 class="text-uppercase mb-4">Links</h5>
          <ul class="list-unstyled">
            <li class="mb-2"><router-link to="/" class="text-white">Home</router-link></li>
            <li class="mb-2"><a href="#services" class="text-white">Services</a></li>
            <li class="mb-2"><a href="#how-it-works" class="text-white">How It Works</a></li>
            <li class="mb-2"><a href="#testimonials" class="text-white">Testimonials</a></li>
          </ul>
        </b-col>

        <b-col lg="3" md="6" class="mb-4 mb-md-0">
          <h5 class="text-uppercase mb-4">For Professionals</h5>
          <ul class="list-unstyled">
            <li class="mb-2"><router-link to="/auth/register/professional" class="text-white">Join as Professional</router-link></li>
            <li class="mb-2"><a href="#" class="text-white">How to Get Jobs</a></li>
            <li class="mb-2"><a href="#" class="text-white">Pricing</a></li>
            <li class="mb-2"><a href="#" class="text-white">FAQ</a></li>
          </ul>
        </b-col>

        <b-col lg="3" md="6">
          <h5 class="text-uppercase mb-4">Contact</h5>
          <ul class="list-unstyled">
            <li class="mb-2">
              <i class="fas fa-map-marker-alt mr-2"></i> 123 Service Street, City
            </li>
            <li class="mb-2">
              <i class="fas fa-envelope mr-2"></i> info@azhousehold.com
            </li>
            <li class="mb-2">
              <i class="fas fa-phone mr-2"></i> +1 (555) 123-4567
            </li>
          </ul>
        </b-col>
      </b-row>
    </b-container>
    <div class="text-center py-3 mt-4 border-top border-secondary">
      <p class="mb-0">© 2025 A-Z Household Services. All rights reserved.</p>
    </div>
  </footer>
</template>

<script>
export default {
  name: 'AppFooter'
}
</script>

<style scoped>
footer a {
  text-decoration: none;
  transition: color 0.3s ease;
}

footer a:hover {
  color: #007bff !important;
  text-decoration: none;
}

.social-icons a {
  display: inline-block;
  margin-right: 10px;
}
</style> 