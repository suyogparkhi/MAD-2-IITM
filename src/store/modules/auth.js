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
      if (state.rememberMe && token) {
        localStorage.setItem('token', token)
      } else if (!token) {
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
        
        // Try different endpoint formats to handle potential routing issues
        let response = null
        let error = null
        
        try {
          // Try with full URL
          response = await axios.post('http://localhost:5000/api/auth/login', { 
            username, 
            password 
          }, {
            withCredentials: true
          })
        } catch (err) {
          console.log('First attempt failed, trying alternative endpoint')
          error = err
          
          try {
            // Try with relative URL
            response = await axios.post('/api/auth/login', { 
              username, 
              password 
            }, {
              withCredentials: true
            })
          } catch (err2) {
            console.log('Second attempt failed, trying without /api prefix')
            
            try {
              // Try without /api prefix
              response = await axios.post('http://localhost:5000/auth/login', { 
                username, 
                password 
              }, {
                withCredentials: true
              })
            } catch (err3) {
              // If all attempts fail, throw the original error
              console.error('All login attempts failed')
              throw error
            }
          }
        }
        
        console.log('Login response:', response.data)
        
        commit('SET_USER', response.data.user)
        
        if (response.data.token) {
          commit('SET_TOKEN', response.data.token)
        }
        
        dispatch('setNotification', {
          message: 'Login successful. Welcome back!',
          type: 'success'
        }, { root: true })
        
        return response.data
      } catch (error) {
        console.error('Login error details:', error.response || error)
        
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
        const response = await axios.post('http://localhost:5000/api/auth/register/customer', userData, {
          withCredentials: true
        })
        
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
        const response = await axios.post('http://localhost:5000/api/auth/register/professional', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          },
          withCredentials: true
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
      } catch (error) {
        console.error('Logout error:', error)
      } finally {
        commit('CLEAR_AUTH')
        commit('SET_LOADING', false)
        
        dispatch('setNotification', {
          message: 'You have been logged out successfully.',
          type: 'success'
        }, { root: true })
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