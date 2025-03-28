<template>
  <footer>
    <div class="footer-main bg-dark text-white py-5">
      <b-container>
        <b-row>
          <b-col lg="4" md="6" class="mb-4 mb-lg-0">
            <div class="footer-brand d-flex align-items-center mb-4">
              <i class="fas fa-tools footer-logo mr-2"></i>
              <h4 class="mb-0 font-weight-bold">A-Z Household Services</h4>
            </div>
            <p class="mb-4">
              Your one-stop platform for all household services. 
              Connect with trusted professionals for quality service 
              delivery right at your doorstep.
            </p>
            <div class="social-icons">
              <a href="#" class="social-icon">
                <i class="fab fa-facebook-f"></i>
              </a>
              <a href="#" class="social-icon">
                <i class="fab fa-twitter"></i>
              </a>
              <a href="#" class="social-icon">
                <i class="fab fa-instagram"></i>
              </a>
              <a href="#" class="social-icon">
                <i class="fab fa-linkedin-in"></i>
              </a>
            </div>
          </b-col>

          <b-col lg="2" md="3" sm="6" class="mb-4 mb-md-0">
            <h5 class="footer-heading mb-4">Quick Links</h5>
            <ul class="footer-links">
              <li><router-link to="/">Home</router-link></li>
              <li><router-link to="/services">Services</router-link></li>
              <li><router-link to="/about">About Us</router-link></li>
              <li><router-link to="/contact">Contact</router-link></li>
              <li><router-link to="/faq">FAQ</router-link></li>
            </ul>
          </b-col>

          <b-col lg="3" md="3" sm="6" class="mb-4 mb-md-0">
            <h5 class="footer-heading mb-4">For Professionals</h5>
            <ul class="footer-links">
              <li><router-link to="/auth/register/professional">Join as Professional</router-link></li>
              <li><router-link to="/how-it-works">How to Get Jobs</router-link></li>
              <li><router-link to="/pricing">Pricing</router-link></li>
              <li><router-link to="/professional/resources">Resources</router-link></li>
              <li><router-link to="/support">Support</router-link></li>
            </ul>
          </b-col>

          <b-col lg="3" md="6">
            <h5 class="footer-heading mb-4">Contact Us</h5>
            <ul class="contact-info">
              <li>
                <i class="fas fa-map-marker-alt contact-icon"></i>
                <span>123 Service Street, Cityville, State 12345</span>
              </li>
              <li>
                <i class="fas fa-envelope contact-icon"></i>
                <span>support@azhousehold.com</span>
              </li>
              <li>
                <i class="fas fa-phone contact-icon"></i>
                <span>+1 (555) 123-4567</span>
              </li>
              <li>
                <i class="fas fa-clock contact-icon"></i>
                <span>Mon-Fri: 9:00 AM - 6:00 PM</span>
              </li>
            </ul>
          </b-col>
        </b-row>
      </b-container>
    </div>
    
    <div class="footer-bottom py-3 bg-primary text-white">
      <b-container>
        <div class="d-md-flex justify-content-between align-items-center text-center text-md-left">
          <p class="mb-md-0">© {{ currentYear }} A-Z Household Services. All rights reserved.</p>
          <div class="footer-bottom-links">
            <router-link to="/privacy">Privacy Policy</router-link>
            <router-link to="/terms">Terms of Service</router-link>
            <router-link to="/cookies">Cookies Policy</router-link>
          </div>
        </div>
      </b-container>
    </div>
  </footer>
</template>

<script>
export default {
  name: 'AppFooter',
  computed: {
    currentYear() {
      return new Date().getFullYear();
    }
  }
}
</script>

<style scoped>
.footer-logo {
  font-size: 1.8rem;
  color: #0d6efd;
}

.footer-brand h4 {
  font-size: 1.3rem;
  letter-spacing: 0.5px;
}

.footer-heading {
  font-size: 1.1rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
  position: relative;
  padding-bottom: 10px;
}

.footer-heading:after {
  content: '';
  position: absolute;
  left: 0;
  bottom: 0;
  height: 2px;
  width: 40px;
  background-color: #0d6efd;
}

.footer-links {
  list-style: none;
  padding: 0;
  margin: 0;
}

.footer-links li {
  margin-bottom: 10px;
}

.footer-links a {
  color: #f8f9fa;
  text-decoration: none;
  transition: all 0.3s ease;
  display: inline-block;
}

.footer-links a:hover {
  color: #0d6efd !important;
  transform: translateX(5px);
}

.social-icons {
  display: flex;
}

.social-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background-color: rgba(255,255,255,0.1);
  color: #fff;
  margin-right: 12px;
  transition: all 0.3s ease;
}

.social-icon:hover {
  background-color: #0d6efd;
  color: #fff;
  transform: translateY(-3px);
}

.contact-info {
  list-style: none;
  padding: 0;
  margin: 0;
}

.contact-info li {
  display: flex;
  margin-bottom: 15px;
}

.contact-icon {
  color: #0d6efd;
  font-size: 1rem;
  margin-right: 15px;
  margin-top: 4px;
}

.footer-bottom {
  font-size: 0.9rem;
}

.footer-bottom-links a {
  color: rgba(255,255,255,0.8);
  margin-left: 20px;
  text-decoration: none;
  transition: color 0.3s ease;
}

.footer-bottom-links a:hover {
  color: #fff;
}

@media (max-width: 767px) {
  .footer-heading {
    margin-top: 20px;
  }
  
  .footer-bottom-links {
    margin-top: 15px;
  }
  
  .footer-bottom-links a {
    margin-left: 10px;
    margin-right: 10px;
    font-size: 0.8rem;
  }
}
</style> 