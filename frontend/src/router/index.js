import Vue from 'vue'
import VueRouter from 'vue-router'
import store from '../store'

// Layouts
import DefaultLayout from '../layouts/DefaultLayout.vue'
import AuthLayout from '../layouts/AuthLayout.vue'
import LandingLayout from '../layouts/LandingLayout.vue'

// Home view
import Home from '../views/Home.vue'
import TestHome from '../views/TestHome.vue'

// Auth views
import Login from '../views/auth/Login.vue'
// import Register from '../views/auth/Register.vue'
import ProfessionalRegister from '../views/auth/ProfessionalRegister.vue'
import CustomerRegister from '../views/auth/CustomerRegister.vue'
import AdminLogin from '../views/auth/AdminLogin.vue'

// Admin views
import AdminDashboard from '../views/admin/Dashboard.vue'
import AdminServices from '../views/admin/Services.vue'
import AdminProfessionals from '../views/admin/Professionals.vue'
import AdminCustomers from '../views/admin/Customers.vue'
import AdminRequests from '../views/admin/Requests.vue'
import AdminReports from '../views/admin/Reports.vue'

// Professional views
import ProfessionalDashboard from '../views/professional/Dashboard.vue'
import ProfessionalRequests from '../views/professional/ServiceRequests.vue'
import ProfessionalProfile from '../views/professional/Profile.vue'

// Customer views
import CustomerDashboard from '../views/customer/Dashboard.vue'
import CustomerServices from '../views/customer/Services.vue'
import CustomerRequests from '../views/customer/ServiceRequests.vue'
import CustomerProfile from '../views/customer/Profile.vue'
import CustomerProfessionals from '../views/customer/Professionals.vue'

Vue.use(VueRouter)

// Route meta for authentication checks
const authGuard = (to, from, next) => {
  const isAuthenticated = store.getters['auth/isAuthenticated']
  if (!isAuthenticated) {
    next('/auth/login')
  } else {
    next()
  }
}

const adminGuard = (to, from, next) => {
  const isAdmin = store.getters['auth/isAdmin']
  if (!isAdmin) {
    next('/')
  } else {
    next()
  }
}

const professionalGuard = (to, from, next) => {
  const isProfessional = store.getters['auth/isProfessional']
  if (!isProfessional) {
    next('/')
  } else {
    next()
  }
}

const customerGuard = (to, from, next) => {
  const isCustomer = store.getters['auth/isCustomer']
  if (!isCustomer) {
    next('/')
  } else {
    next()
  }
}

// Create a placeholder component for missing views
const PlaceholderComponent = {
  template: '<div class="container mt-5"><h2>Component Under Development</h2><p>This page is currently being developed.</p></div>'
}

const routes = [
  // Landing page route
  {
    path: '/',
    component: LandingLayout,
    children: [
      {
        path: '',
        name: 'Home',
        component: Home
      }
    ]
  },
  
  // Auth routes
  {
    path: '/auth',
    component: AuthLayout,
    children: [
      {
        path: 'login',
        name: 'Login',
        component: Login
      },
      {
        path: 'register',
        name: 'Register',
        component: PlaceholderComponent
      },
      {
        path: 'register/professional',
        name: 'ProfessionalRegister',
        component: ProfessionalRegister
      },
      {
        path: 'register/customer',
        name: 'CustomerRegister',
        component: CustomerRegister
      }
    ]
  },
  
  // Direct routes for backward compatibility
  {
    path: '/login',
    component: AuthLayout,
    children: [
      {
        path: '',
        component: Login
      }
    ]
  },
  {
    path: '/register/professional',
    component: AuthLayout,
    children: [
      {
        path: '',
        component: ProfessionalRegister
      }
    ]
  },
  {
    path: '/register/customer',
    component: AuthLayout,
    children: [
      {
        path: '',
        component: CustomerRegister
      }
    ]
  },
  
  // Admin login route (separate from nested routes)
  {
    path: '/admin-login',
    component: AuthLayout,
    children: [
      {
        path: '',
        name: 'AdminLogin',
        component: AdminLogin
      }
    ]
  },
  
  // Admin routes
  {
    path: '/admin',
    component: DefaultLayout,
    beforeEnter: adminGuard,
    children: [
      {
        path: '',
        name: 'AdminDashboard',
        component: AdminDashboard
      },
      {
        path: 'services',
        name: 'AdminServices',
        component: AdminServices
      },
      {
        path: 'professionals',
        name: 'AdminProfessionals',
        component: AdminProfessionals
      },
      {
        path: 'customers',
        name: 'AdminCustomers',
        component: AdminCustomers
      },
      {
        path: 'requests',
        name: 'AdminRequests',
        component: AdminRequests
      },
      {
        path: 'reports',
        name: 'AdminReports',
        component: AdminReports
      }
    ]
  },
  
  // Professional routes
  {
    path: '/professional',
    component: DefaultLayout,
    beforeEnter: professionalGuard,
    children: [
      {
        path: '',
        name: 'ProfessionalDashboard',
        component: ProfessionalDashboard
      },
      {
        path: 'requests',
        name: 'ProfessionalRequests',
        component: ProfessionalRequests
      },
      {
        path: 'profile',
        name: 'ProfessionalProfile',
        component: ProfessionalProfile
      }
    ]
  },
  
  // Customer routes
  {
    path: '/customer',
    component: DefaultLayout,
    beforeEnter: customerGuard,
    children: [
      {
        path: '',
        name: 'CustomerDashboard',
        component: CustomerDashboard
      },
      {
        path: 'services',
        name: 'CustomerServices',
        component: CustomerServices
      },
      {
        path: 'professionals',
        name: 'CustomerProfessionals',
        component: CustomerProfessionals
      },
      {
        path: 'service-requests',
        name: 'CustomerRequests',
        component: CustomerRequests
      },
      {
        path: 'profile',
        name: 'CustomerProfile',
        component: CustomerProfile
      }
    ]
  },
  
  // Catch-all route for 404
  {
    path: '*',
    component: DefaultLayout,
    children: [
      {
        path: '',
        name: '404',
        component: {
          template: `
            <div class="container text-center py-5">
              <h1 class="display-1">404</h1>
              <h2 class="mb-4">Page Not Found</h2>
              <p class="lead mb-4">The page you are looking for might have been removed, had its name changed, or is temporarily unavailable.</p>
              <router-link to="/" class="btn btn-primary">Go to Homepage</router-link>
            </div>
          `
        }
      }
    ]
  }
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { x: 0, y: 0 }
    }
  }
})

export default router