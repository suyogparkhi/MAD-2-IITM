import Vue from 'vue'
import Vuex from 'vuex'
import auth from './modules/auth'
import services from './modules/services'
import professionals from './modules/professionals'
// import customers from './modules/customers'
import serviceRequests from './modules/serviceRequests'
import reports from './modules/reports'
import admin from './modules/admin'

// Create placeholder modules
const placeholderModule = {
  namespaced: true,
  state: {},
  getters: {},
  mutations: {},
  actions: {}
}

Vue.use(Vuex)

export default new Vuex.Store({
  // Root state
  state: {
    loading: false,
    error: null,
    notification: null,
    appConfig: {
      appName: 'A-Z Household Services',
      appVersion: '2.0.0',
      apiBaseUrl: process.env.VUE_APP_API_URL || '/api'
    }
  },
  
  // Root getters
  getters: {
    loading: state => state.loading,
    error: state => state.error,
    notification: state => state.notification,
    appConfig: state => state.appConfig
  },
  
  // Root mutations
  mutations: {
    SET_LOADING(state, loading) {
      state.loading = loading
    },
    SET_ERROR(state, error) {
      state.error = error
    },
    CLEAR_ERROR(state) {
      state.error = null
    },
    SET_NOTIFICATION(state, notification) {
      state.notification = notification
    },
    CLEAR_NOTIFICATION(state) {
      state.notification = null
    },
    SET_APP_CONFIG(state, config) {
      state.appConfig = { ...state.appConfig, ...config }
    }
  },
  
  // Root actions
  actions: {
    setLoading({ commit }, loading) {
      commit('SET_LOADING', loading)
    },
    
    setError({ commit }, error) {
      commit('SET_ERROR', error)
    },
    
    clearError({ commit }) {
      commit('CLEAR_ERROR')
    },
    
    setNotification({ commit }, { message, type = 'success', timeout = 5000 }) {
      // Generate unique ID for the notification
      const id = `notification-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
      
      commit('SET_NOTIFICATION', {
        id,
        message,
        type,
        timeout
      })
      
      // Auto-clear notification after timeout
      if (timeout > 0) {
        setTimeout(() => {
          commit('CLEAR_NOTIFICATION')
        }, timeout)
      }
    },
    
    clearNotification({ commit }) {
      commit('CLEAR_NOTIFICATION')
    },
    
    async loadAppConfig({ commit }) {
      try {
        // In a real app, this might come from an API endpoint
        const config = {
          features: {
            enabledServices: true,
            enabledReviews: true,
            enabledReports: true
          },
          ui: {
            theme: 'light',
            primaryColor: '#007bff',
            secondaryColor: '#6c757d'
          }
        }
        
        commit('SET_APP_CONFIG', config)
        return config
      } catch (error) {
        console.error('Failed to load app config:', error)
        return null
      }
    }
  },
  
  // Modules
  modules: {
    auth,
    services,
    professionals,
    customers: placeholderModule,
    serviceRequests,
    reports,
    admin
  }
})