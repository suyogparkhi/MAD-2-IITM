import Vue from 'vue'
import axios from 'axios'

export default {
  namespaced: true,
  
  state: {
    user: null,
    token: localStorage.getItem('token') || null,
    isAuthenticated: false,
    loading: false,
    error: null,
    rememberMe: false,
    registrationStep: 1
  },
  
  getters: {
    user: state => state.user,
    token: state => state.token,
    isAuthenticated: state => state.isAuthenticated,
    userRole: state => state.user ? state.user.role : null,
    username: state => state.user ? state.user.username : 'User',
    isAdmin: state => state.user && state.user.role === 'admin',
    isProfessional: state => state.user && state.user.role === 'professional',
    isCustomer: state => state.user && state.user.role === 'customer',
    loading: state => state.loading,
    error: state => state.error,
    registrationStep: state => state.registrationStep,
    rememberMe: state => state.rememberMe
  },
  
  mutations: {
    SET_USER(state, user) {
      state.user = user
      state.isAuthenticated = !!user
    },
    
    SET_TOKEN(state, token) {
      state.token = token
      if (token) {
        if (state.rememberMe) {
          localStorage.setItem('token', token)
        }
      } else {
        localStorage.removeItem('token')
      }
    },
    
    CLEAR_AUTH(state) {
      state.user = null
      state.token = null
      state.isAuthenticated = false
      localStorage.removeItem('token')
    },
    
    SET_LOADING(state, loading) {
      state.loading = loading
    },
    
    SET_ERROR(state, error) {
      state.error = error
    },
    
    CLEAR_ERROR(state) {
      state.error = null
    },
    
    SET_REGISTRATION_STEP(state, step) {
      state.registrationStep = step
    },
    
    SET_REMEMBER_ME(state, value) {
      state.rememberMe = value
    }
  },
  
  actions: {
    async login({ commit, dispatch }, { username, password, rememberMe = false }) {
      commit('SET_LOADING', true)
      commit('CLEAR_ERROR')
      commit('SET_REMEMBER_ME', rememberMe)
      
      try {
        console.log('Login attempt with:', { username })
        
        const response = await Vue.prototype.$http.post('/auth/login', { 
          username, 
          password 
        })
        
        console.log('Login response:', response.data)
        
        commit('SET_USER', response.data.user)
        
        if (response.data.token) {
          console.log('Token received, storing token')
          commit('SET_TOKEN', response.data.token)
        } else {
          console.log('No token in response, using session-based auth')
        }
        
        dispatch('setNotification', {
          message: 'Login successful. Welcome back!',
          type: 'success'
        }, { root: true })
        
        return response.data
      } catch (error) {
        console.error('Login error:', error)
        const errorMessage = error.response?.data?.message || 'Login failed. Please check your credentials.'
        commit('SET_ERROR', errorMessage)
        
        dispatch('setNotification', {
          message: errorMessage,
          type: 'error'
        }, { root: true })
        
        throw error
      } finally {
        commit('SET_LOADING', false)
      }
    },
    
    async registerCustomer({ commit, dispatch }, userData) {
      commit('SET_LOADING', true)
      commit('CLEAR_ERROR')
      
      try {
        const response = await Vue.prototype.$http.post('/auth/register/customer', userData)
        
        dispatch('setNotification', {
          message: 'Registration successful! You can now log in.',
          type: 'success'
        }, { root: true })
        
        return response.data
      } catch (error) {
        console.error('Customer registration error:', error.response || error)
        
        const errorMessage = error.response?.data?.message || 'Registration failed. Please try again.'
        commit('SET_ERROR', errorMessage)
        
        dispatch('setNotification', {
          message: errorMessage,
          type: 'error'
        }, { root: true })
        
        throw error
      } finally {
        commit('SET_LOADING', false)
      }
    },
    
    async registerProfessional({ commit, dispatch }, formData) {
      commit('SET_LOADING', true)
      commit('CLEAR_ERROR')
      
      try {
        const response = await Vue.prototype.$http.post('/auth/register/professional', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })
        
        dispatch('setNotification', {
          message: 'Registration successful! Your account will be reviewed by an administrator.',
          type: 'success'
        }, { root: true })
        
        return response.data
      } catch (error) {
        console.error('Professional registration error:', error.response || error)
        
        const errorMessage = error.response?.data?.message || 'Registration failed. Please try again.'
        commit('SET_ERROR', errorMessage)
        
        dispatch('setNotification', {
          message: errorMessage,
          type: 'error'
        }, { root: true })
        
        throw error
      } finally {
        commit('SET_LOADING', false)
      }
    },
    
    async checkAuth({ commit, state }) {
      // If there's no token or user is already authenticated, no need to check
      if (!state.token) {
        commit('CLEAR_AUTH')
        return null
      }
      
      if (state.isAuthenticated && state.user) {
        return state.user
      }
      
      commit('SET_LOADING', true)
      
      try {
        const response = await Vue.prototype.$http.get('/auth/user-info')
        commit('SET_USER', response.data)
        return response.data
      } catch (error) {
        console.error('Authentication check failed:', error)
        commit('CLEAR_AUTH')
        return null
      } finally {
        commit('SET_LOADING', false)
      }
    },
    
    async logout({ commit, dispatch }) {
      commit('SET_LOADING', true)
      
      try {
        await Vue.prototype.$http.post('/auth/logout')
        commit('CLEAR_AUTH')
        
        dispatch('setNotification', {
          message: 'You have been logged out successfully.',
          type: 'success'
        }, { root: true })
      } catch (error) {
        console.error('Logout error:', error)
        // Even if the logout API fails, we still want to clear the local auth state
        commit('CLEAR_AUTH')
      } finally {
        commit('SET_LOADING', false)
      }
    },
    
    setRegistrationStep({ commit }, step) {
      commit('SET_REGISTRATION_STEP', step)
    },
    
    resetRegistration({ commit }) {
      commit('SET_REGISTRATION_STEP', 1)
    },
    
    setRememberMe({ commit }, value) {
      commit('SET_REMEMBER_ME', value)
    },
    
    clearError({ commit }) {
      commit('CLEAR_ERROR')
    }
  }
}