import Vue from 'vue'
import VueRouter from 'vue-router'
import store from '../store'

// Layouts
import DefaultLayout from '../layouts/DefaultLayout.vue'
import AuthLayout from '../layouts/AuthLayout.vue'

// Auth views
import Login from '../views/auth/Login.vue'
// import Register from '../views/auth/Register.vue'
import ProfessionalRegister from '../views/auth/ProfessionalRegister.vue'
import CustomerRegister from '../views/auth/CustomerRegister.vue'
import AdminLogin from '../views/auth/AdminLogin.vue'

// Admin views
// import AdminDashboard from '../views/admin/Dashboard.vue'
// import AdminServices from '../views/admin/Services.vue'
// import AdminProfessionals from '../views/admin/Professionals.vue'
// import AdminCustomers from '../views/admin/Customers.vue'
// import AdminRequests from '../views/admin/ServiceRequests.vue'
// import AdminReports from '../views/admin/Reports.vue'

// Professional views
// import ProfessionalDashboard from '../views/professional/Dashboard.vue'
// import ProfessionalRequests from '../views/professional/ServiceRequests.vue'
// import ProfessionalProfile from '../views/professional/Profile.vue'

// Customer views
// import CustomerDashboard from '../views/customer/Dashboard.vue'
// import CustomerServices from '../views/customer/Services.vue'
// import CustomerRequests from '../views/customer/ServiceRequests.vue'
// import CustomerProfile from '../views/customer/Profile.vue'

Vue.use(VueRouter)

// Route meta for authentication checks
const authGuard = (to, from, next) => {
  const isAuthenticated = store.getters['auth/isAuthenticated']
  if (!isAuthenticated) {
    next('/login')
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
  // Auth routes
  {
    path: '/',
    component: AuthLayout,
    children: [
      {
        path: '',
        redirect: '/login'
      },
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
        component: PlaceholderComponent
      },
      {
        path: 'services',
        name: 'AdminServices',
        component: PlaceholderComponent
      },
      {
        path: 'professionals',
        name: 'AdminProfessionals',
        component: PlaceholderComponent
      },
      {
        path: 'customers',
        name: 'AdminCustomers',
        component: PlaceholderComponent
      },
      {
        path: 'requests',
        name: 'AdminRequests',
        component: PlaceholderComponent
      },
      {
        path: 'reports',
        name: 'AdminReports',
        component: PlaceholderComponent
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
        component: PlaceholderComponent
      },
      {
        path: 'requests',
        name: 'ProfessionalRequests',
        component: PlaceholderComponent
      },
      {
        path: 'profile',
        name: 'ProfessionalProfile',
        component: PlaceholderComponent
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
        component: PlaceholderComponent
      },
      {
        path: 'services',
        name: 'CustomerServices',
        component: PlaceholderComponent
      },
      {
        path: 'requests',
        name: 'CustomerRequests',
        component: PlaceholderComponent
      },
      {
        path: 'profile',
        name: 'CustomerProfile',
        component: PlaceholderComponent
      }
    ]
  },
  
  // Default redirect to login
  {
    path: '*',
    redirect: '/login'
  }
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

// Global navigation guard
router.beforeEach((to, from, next) => {
  const isAuthenticated = store.getters['auth/isAuthenticated']
  const publicPages = ['/login', '/register', '/register/professional', '/register/customer']
  const authRequired = !publicPages.includes(to.path)
  
  if (authRequired && !isAuthenticated) {
    next('/login')
  } else {
    // If authenticated, redirect to appropriate dashboard
    if (isAuthenticated && to.path === '/') {
      const userRole = store.getters['auth/userRole']
      if (userRole === 'admin') {
        next('/admin')
      } else if (userRole === 'professional') {
        next('/professional')
      } else if (userRole === 'customer') {
        next('/customer')
      } else {
        next('/login')
      }
    } else {
      next()
    }
  }
})

export default router