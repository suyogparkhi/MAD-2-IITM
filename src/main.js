import Vue from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import axios from 'axios'

// Import Bootstrap and Bootstrap Vue
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap'
import { BootstrapVue, IconsPlugin } from 'bootstrap-vue'
import 'bootstrap-vue/dist/bootstrap-vue.css'

// Import Font Awesome
import '@fortawesome/fontawesome-free/css/all.min.css'

// Use Bootstrap Vue
Vue.use(BootstrapVue)
Vue.use(IconsPlugin)

// Configure axios
axios.defaults.baseURL = process.env.VUE_APP_API_URL || 'http://localhost:5000/api'
axios.defaults.withCredentials = true

// Add axios to Vue prototype for global access
Vue.prototype.$http = axios

// Add authentication interceptor
axios.interceptors.response.use(
  response => response,
  error => {
    if (error.response && error.response.status === 401) {
      // Unauthorized, redirect to login
      store.dispatch('auth/logout')
      router.push('/auth/login')
    }
    return Promise.reject(error)
  }
)

// Log the API URL being used (for debugging)
console.log('API URL:', axios.defaults.baseURL)

Vue.config.productionTip = false

// Initialize Vue application
new Vue({
  router,
  store,
  render: h => h(App)
}).$mount('#app')