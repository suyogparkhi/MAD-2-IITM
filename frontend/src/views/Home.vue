<template>
  <div>
    <!-- Hero Section -->
    <section class="hero-section">
      <b-container>
        <b-row class="align-items-center">
          <b-col lg="6" md="12" class="text-left">
            <h1 class="display-4 font-weight-bold mb-4">Professional Home Services at Your Fingertips</h1>
            <p class="lead mb-4">
              From plumbing to cleaning, electrical work to gardening - find trusted professionals for all your household needs in one place.
            </p>
            <div class="d-flex flex-wrap">
              <b-button to="/auth/login" variant="primary" size="lg" class="mr-3 mb-3">Get Started</b-button>
              <b-button to="/auth/register/professional" variant="outline-primary" size="lg" class="mb-3">Join as Professional</b-button>
            </div>
          </b-col>
          <b-col lg="6" md="12" class="mt-5 mt-lg-0">
            <img src="https://images.unsplash.com/photo-1581578731548-c64695cc6952?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80" alt="Home Services" class="img-fluid rounded shadow-lg">
          </b-col>
        </b-row>
      </b-container>
    </section>

    <!-- Services Section -->
    <section id="services" class="py-5 bg-light">
      <b-container>
        <h2 class="text-center mb-5 section-title">Our Services</h2>
        <b-row>
          <b-col lg="3" md="6" class="mb-4" v-for="(service, index) in services" :key="index">
            <b-card class="h-100 service-card text-center border-0 shadow-sm">
              <div class="service-icon mb-3">
                <i :class="service.icon"></i>
              </div>
              <h4 class="mb-3">{{ service.title }}</h4>
              <p class="text-muted">{{ service.description }}</p>
            </b-card>
          </b-col>
        </b-row>
        <div class="text-center mt-4">
          <b-button variant="outline-primary" size="lg">View All Services</b-button>
        </div>
      </b-container>
    </section>

    <!-- How It Works Section -->
    <section id="how-it-works" class="py-5">
      <b-container>
        <h2 class="text-center mb-5 section-title">How It Works</h2>
        <b-row>
          <b-col lg="4" md="4" class="mb-4 mb-lg-0" v-for="(step, index) in steps" :key="index">
            <div class="text-center px-4">
              <div class="step-number mb-4">{{ index + 1 }}</div>
              <h4 class="mb-3">{{ step.title }}</h4>
              <p class="text-muted">{{ step.description }}</p>
            </div>
          </b-col>
        </b-row>
      </b-container>
    </section>

    <!-- Why Choose Us Section -->
    <section class="py-5 bg-primary text-white">
      <b-container>
        <h2 class="text-center mb-5 section-title">Why Choose Us</h2>
        <b-row>
          <b-col lg="4" md="6" class="mb-4" v-for="(feature, index) in features" :key="index">
            <div class="d-flex">
              <div class="feature-icon mr-3">
                <i :class="feature.icon"></i>
              </div>
              <div>
                <h4 class="mb-2">{{ feature.title }}</h4>
                <p>{{ feature.description }}</p>
              </div>
            </div>
          </b-col>
        </b-row>
      </b-container>
    </section>

    <!-- Testimonials Section -->
    <section id="testimonials" class="py-5">
      <b-container>
        <h2 class="text-center mb-5 section-title">What Our Customers Say</h2>
        <b-row>
          <b-col lg="4" md="6" class="mb-4" v-for="(testimonial, index) in testimonials" :key="index">
            <b-card class="h-100 testimonial-card border-0 shadow-sm">
              <div class="testimonial-rating mb-3">
                <i class="fas fa-star text-warning" v-for="n in 5" :key="n"></i>
              </div>
              <p class="testimonial-text mb-4">{{ testimonial.text }}</p>
              <div class="d-flex align-items-center">
                <img :src="testimonial.image" :alt="testimonial.name" class="testimonial-image mr-3">
                <div>
                  <h5 class="mb-0">{{ testimonial.name }}</h5>
                  <p class="text-muted mb-0">{{ testimonial.location }}</p>
                </div>
              </div>
            </b-card>
          </b-col>
        </b-row>
      </b-container>
    </section>

    <!-- CTA Section -->
    <section class="py-5 bg-light">
      <b-container>
        <b-row class="justify-content-center">
          <b-col lg="10" class="text-center">
            <h2 class="mb-4">Ready to Get Started?</h2>
            <p class="lead mb-4">Join thousands of satisfied customers who have transformed their homes with our services.</p>
            <div>
              <b-button to="/auth/login" variant="primary" size="lg" class="mr-3 mb-3">Find a Professional</b-button>
              <b-button to="/auth/register/professional" variant="outline-primary" size="lg" class="mb-3">Become a Professional</b-button>
            </div>
          </b-col>
        </b-row>
      </b-container>
    </section>
  </div>
</template>

<script>
export default {
  name: 'Home',
  data() {
    return {
      services: [
        {
          title: 'Cleaning',
          icon: 'fas fa-broom',
          description: 'Professional home cleaning services for a spotless living space.'
        },
        {
          title: 'Plumbing',
          icon: 'fas fa-faucet',
          description: 'Expert plumbers to fix leaks, clogs, and all water-related issues.'
        },
        {
          title: 'Electrical',
          icon: 'fas fa-bolt',
          description: 'Certified electricians for installations, repairs, and maintenance.'
        },
        {
          title: 'Painting',
          icon: 'fas fa-paint-roller',
          description: 'Transform your space with our professional painting services.'
        },
        {
          title: 'Gardening',
          icon: 'fas fa-leaf',
          description: 'Keep your garden beautiful with our expert landscaping services.'
        },
        {
          title: 'Carpentry',
          icon: 'fas fa-hammer',
          description: 'Custom woodwork, repairs, and installations by skilled carpenters.'
        },
        {
          title: 'Appliance Repair',
          icon: 'fas fa-tools',
          description: 'Quick and reliable repairs for all your household appliances.'
        },
        {
          title: 'Home Security',
          icon: 'fas fa-shield-alt',
          description: 'Protect your home with modern security system installations.'
        }
      ],
      steps: [
        {
          title: 'Book a Service',
          description: 'Browse through our wide range of services and book the one you need with just a few clicks.'
        },
        {
          title: 'Get Matched',
          description: 'We\'ll match you with the best professional based on your requirements and their expertise.'
        },
        {
          title: 'Job Done',
          description: 'The professional will arrive at your doorstep and complete the job to your satisfaction.'
        }
      ],
      features: [
        {
          title: 'Verified Professionals',
          icon: 'fas fa-user-check',
          description: 'All our professionals undergo thorough background checks and skill verification.'
        },
        {
          title: 'Guaranteed Quality',
          icon: 'fas fa-medal',
          description: 'We stand behind our work with a 100% satisfaction guarantee on all services.'
        },
        {
          title: '24/7 Support',
          icon: 'fas fa-headset',
          description: 'Our customer support team is available round the clock to assist you.'
        },
        {
          title: 'Competitive Pricing',
          icon: 'fas fa-tag',
          description: 'Get the best value for your money with our transparent and competitive pricing.'
        },
        {
          title: 'Insured Services',
          icon: 'fas fa-shield-alt',
          description: 'All services are fully insured, giving you peace of mind during the job.'
        },
        {
          title: 'Easy Scheduling',
          icon: 'fas fa-calendar-alt',
          description: 'Book services at your convenience with our flexible scheduling options.'
        }
      ],
      testimonials: [
        {
          name: 'Sarah Johnson',
          location: 'New York',
          image: 'https://randomuser.me/api/portraits/women/1.jpg',
          text: 'The cleaning service was exceptional! The team was thorough, professional, and left my home spotless. Will definitely use again.'
        },
        {
          name: 'Michael Brown',
          location: 'Chicago',
          image: 'https://randomuser.me/api/portraits/men/2.jpg',
          text: 'I had an emergency plumbing issue and the professional arrived within an hour. Fixed the problem quickly and at a reasonable price.'
        },
        {
          name: 'Emily Davis',
          location: 'Los Angeles',
          image: 'https://randomuser.me/api/portraits/women/3.jpg',
          text: 'The gardening team transformed my backyard completely. Their attention to detail and creativity exceeded my expectations.'
        }
      ]
    }
  }
}
</script>

<style scoped>
.hero-section {
  padding: 100px 0;
  background-color: #f8f9fa;
}

.section-title {
  position: relative;
  padding-bottom: 15px;
  margin-bottom: 30px;
  font-weight: 700;
}

.section-title:after {
  content: '';
  position: absolute;
  display: block;
  width: 50px;
  height: 3px;
  background: #007bff;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
}

.service-card {
  transition: transform 0.3s ease;
  border-radius: 10px;
  overflow: hidden;
}

.service-card:hover {
  transform: translateY(-10px);
}

.service-icon {
  font-size: 2.5rem;
  color: #007bff;
}

.step-number {
  width: 60px;
  height: 60px;
  line-height: 60px;
  border-radius: 50%;
  background-color: #007bff;
  color: white;
  font-size: 24px;
  font-weight: bold;
  margin: 0 auto;
}

.feature-icon {
  font-size: 2rem;
  color: #ffc107;
}

.testimonial-card {
  padding: 25px;
  border-radius: 10px;
}

.testimonial-image {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  object-fit: cover;
}

.testimonial-text {
  font-style: italic;
}
</style> 