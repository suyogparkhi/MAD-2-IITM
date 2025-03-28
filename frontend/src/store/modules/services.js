import Vue from 'vue'

export default {
  namespaced: true,
  
  state: {
    services: [],
    currentService: null,
    loading: false,
    error: null,
    filters: {
      searchQuery: '',
      priceRange: null,
      category: null
    }
  },
  
  getters: {
    services: state => state.services,
    allServices: state => state.services,
    currentService: state => state.currentService,
    loading: state => state.loading,
    error: state => state.error,
    filters: state => state.filters,
    
    serviceById: state => id => {
      return state.services.find(service => service.id === id)
    },
    
    filteredServices: state => {
      let result = [...state.services]
      
      // Apply search filter
      if (state.filters.searchQuery) {
        const query = state.filters.searchQuery.toLowerCase()
        result = result.filter(service => 
          service.name.toLowerCase().includes(query) || 
          (service.description && service.description.toLowerCase().includes(query))
        )
      }
      
      // Apply price range filter
      if (state.filters.priceRange) {
        const [min, max] = state.filters.priceRange
        result = result.filter(service => 
          service.base_price >= min && 
          (max === null || service.base_price <= max)
        )
      }
      
      // Apply category filter
      if (state.filters.category) {
        result = result.filter(service => 
          service.category === state.filters.category
        )
      }
      
      return result
    }
  },
  
  mutations: {
    SET_SERVICES(state, services) {
      state.services = services
    },
    
    SET_CURRENT_SERVICE(state, service) {
      state.currentService = service
    },
    
    ADD_SERVICE(state, service) {
      state.services.push(service)
    },
    
    UPDATE_SERVICE(state, updatedService) {
      const index = state.services.findIndex(s => s.id === updatedService.id)
      if (index !== -1) {
        state.services.splice(index, 1, updatedService)
      }
      
      if (state.currentService && state.currentService.id === updatedService.id) {
        state.currentService = updatedService
      }
    },
    
    REMOVE_SERVICE(state, serviceId) {
      state.services = state.services.filter(service => service.id !== serviceId)
      
      if (state.currentService && state.currentService.id === serviceId) {
        state.currentService = null
      }
    },
    
    SET_FILTERS(state, filters) {
      state.filters = { ...state.filters, ...filters }
    },
    
    RESET_FILTERS(state) {
      state.filters = {
        searchQuery: '',
        priceRange: null,
        category: null
      }
    },
    
    SET_LOADING(state, loading) {
      state.loading = loading
    },
    
    SET_ERROR(state, error) {
      state.error = error
    },
    
    CLEAR_ERROR(state) {
      state.error = null
    }
  },
  
  actions: {
    // Customer actions
    async fetchServices({ commit, dispatch }) {
      commit('SET_LOADING', true)
      commit('CLEAR_ERROR')
      
      try {
        // Use the public endpoint that doesn't require authentication
        const response = await Vue.prototype.$http.get('/customer/services-public')
        commit('SET_SERVICES', response.data)
        return response.data
      } catch (error) {
        const errorMessage = error.response?.data?.message || 'Failed to fetch services'
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
    
    // Public action for registration pages
    async fetchPublicServices({ commit, dispatch }) {
      commit('SET_LOADING', true)
      commit('CLEAR_ERROR')
      
      try {
        const response = await Vue.prototype.$http.get('/auth/services')
        commit('SET_SERVICES', response.data)
        return response.data
      } catch (error) {
        const errorMessage = error.response?.data?.message || 'Failed to fetch services'
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
    
    async fetchServiceDetails({ commit, dispatch, getters }, serviceId) {
      // If we already have this service in current service, no need to fetch
      if (getters.currentService && getters.currentService.id === serviceId) {
        return getters.currentService
      }
      
      commit('SET_LOADING', true)
      commit('CLEAR_ERROR')
      
      try {
        const response = await Vue.prototype.$http.get(`/customer/services/${serviceId}`)
        commit('SET_CURRENT_SERVICE', response.data)
        return response.data
      } catch (error) {
        const errorMessage = error.response?.data?.message || 'Failed to fetch service details'
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
    
    async searchServices({ commit, dispatch }, searchQuery) {
      commit('SET_LOADING', true)
      commit('CLEAR_ERROR')
      
      try {
        const response = await Vue.prototype.$http.get(`/customer/search-services?query=${encodeURIComponent(searchQuery)}`)
        commit('SET_SERVICES', response.data)
        return response.data
      } catch (error) {
        const errorMessage = error.response?.data?.message || 'Search failed'
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
    
    // Admin actions
    async fetchAdminServices({ commit, dispatch }) {
      commit('SET_LOADING', true)
      commit('CLEAR_ERROR')
      
      try {
        const response = await Vue.prototype.$http.get('/admin/services')
        commit('SET_SERVICES', response.data)
        return response.data
      } catch (error) {
        const errorMessage = error.response?.data?.message || 'Failed to fetch services'
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
    
    async createService({ commit, dispatch }, serviceData) {
      commit('SET_LOADING', true)
      commit('CLEAR_ERROR')
      
      try {
        const response = await Vue.prototype.$http.post('/admin/services', serviceData)
        const newService = response.data.service
        commit('ADD_SERVICE', newService)
        
        dispatch('setNotification', {
          message: 'Service created successfully',
          type: 'success'
        }, { root: true })
        
        return newService
      } catch (error) {
        const errorMessage = error.response?.data?.message || 'Failed to create service'
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
    
    async updateService({ commit, dispatch }, { serviceId, serviceData }) {
      commit('SET_LOADING', true)
      commit('CLEAR_ERROR')
      
      try {
        const response = await Vue.prototype.$http.put(`/admin/services/${serviceId}`, serviceData)
        const updatedService = response.data.service
        commit('UPDATE_SERVICE', updatedService)
        
        dispatch('setNotification', {
          message: 'Service updated successfully',
          type: 'success'
        }, { root: true })
        
        return updatedService
      } catch (error) {
        const errorMessage = error.response?.data?.message || 'Failed to update service'
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
    
    async deleteService({ commit, dispatch }, serviceId) {
      commit('SET_LOADING', true)
      commit('CLEAR_ERROR')
      
      try {
        await Vue.prototype.$http.delete(`/admin/services/${serviceId}`)
        commit('REMOVE_SERVICE', serviceId)
        
        dispatch('setNotification', {
          message: 'Service deleted successfully',
          type: 'success'
        }, { root: true })
        
        return true
      } catch (error) {
        const errorMessage = error.response?.data?.message || 'Failed to delete service'
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
    
    // Filter actions
    setFilters({ commit }, filters) {
      commit('SET_FILTERS', filters)
    },
    
    resetFilters({ commit }) {
      commit('RESET_FILTERS')
    },
    
    clearError({ commit }) {
      commit('CLEAR_ERROR')
    }
  }
}