// src/store/modules/admin.js
import Vue from 'vue'

const state = {
  dashboardData: null,
  professionals: [],
  customers: [],
  requests: [],
  loading: false,
  error: null
}

const getters = {
  dashboardData: state => state.dashboardData,
  professionals: state => state.professionals,
  customers: state => state.customers,
  requests: state => state.requests,
  loading: state => state.loading,
  error: state => state.error
}

const actions = {
  // Dashboard data
  async fetchDashboardData({ commit }) {
    commit('SET_LOADING', true)
    commit('CLEAR_ERROR')
    
    try {
      const response = await Vue.prototype.$http.get('/admin/dashboard')
      commit('SET_DASHBOARD_DATA', response.data)
    } catch (error) {
      console.error('Error fetching dashboard data:', error)
      commit('SET_ERROR', 'Failed to load dashboard data. Please try again.')
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  // Professionals
  async fetchProfessionals({ commit }) {
    commit('SET_LOADING', true)
    commit('CLEAR_ERROR')
    
    try {
      const response = await Vue.prototype.$http.get('/admin/professionals')
      commit('SET_PROFESSIONALS', response.data)
    } catch (error) {
      console.error('Error fetching professionals:', error)
      commit('SET_ERROR', 'Failed to load professionals. Please try again.')
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  async updateProfessionalStatus({ commit, dispatch }, { professionalId, isActive }) {
    commit('SET_LOADING', true)
    commit('CLEAR_ERROR')
    
    try {
      await Vue.prototype.$http.put(`/admin/professionals/${professionalId}/verify`, {
        status: isActive ? 'approved' : 'rejected'
      })
      
      // Refresh professionals list
      await dispatch('fetchProfessionals')
      
      return true
    } catch (error) {
      console.error('Error updating professional status:', error)
      commit('SET_ERROR', 'Failed to update professional status. Please try again.')
      return false
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  // Customers
  async fetchCustomers({ commit }) {
    commit('SET_LOADING', true)
    commit('CLEAR_ERROR')
    
    try {
      const response = await Vue.prototype.$http.get('/admin/customers')
      commit('SET_CUSTOMERS', response.data)
    } catch (error) {
      console.error('Error fetching customers:', error)
      commit('SET_ERROR', 'Failed to load customers. Please try again.')
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  async updateCustomerStatus({ commit, dispatch }, { customerId, isActive }) {
    commit('SET_LOADING', true)
    commit('CLEAR_ERROR')
    
    try {
      await Vue.prototype.$http.put(`/admin/customers/${customerId}/status`, {
        is_active: isActive
      })
      
      // Refresh customers list
      await dispatch('fetchCustomers')
      
      return true
    } catch (error) {
      console.error('Error updating customer status:', error)
      commit('SET_ERROR', 'Failed to update customer status. Please try again.')
      return false
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  // Service Requests
  async fetchRequests({ commit }) {
    commit('SET_LOADING', true)
    commit('CLEAR_ERROR')
    
    try {
      const response = await Vue.prototype.$http.get('/admin/service-requests')
      commit('SET_REQUESTS', response.data)
    } catch (error) {
      console.error('Error fetching service requests:', error)
      commit('SET_ERROR', 'Failed to load service requests. Please try again.')
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  async updateRequestStatus({ commit, dispatch }, { requestId, status }) {
    commit('SET_LOADING', true)
    commit('CLEAR_ERROR')
    
    try {
      await Vue.prototype.$http.put(`/admin/service-requests/${requestId}/status`, {
        status
      })
      
      // Refresh requests list
      await dispatch('fetchRequests')
      
      return true
    } catch (error) {
      console.error('Error updating request status:', error)
      commit('SET_ERROR', 'Failed to update request status. Please try again.')
      return false
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  async assignProfessional({ commit, dispatch }, { requestId, professionalId }) {
    commit('SET_LOADING', true)
    commit('CLEAR_ERROR')
    
    try {
      await Vue.prototype.$http.put(`/admin/service-requests/${requestId}/assign`, {
        professional_id: professionalId
      })
      
      // Refresh requests list
      await dispatch('fetchRequests')
      
      return true
    } catch (error) {
      console.error('Error assigning professional:', error)
      commit('SET_ERROR', 'Failed to assign professional. Please try again.')
      return false
    } finally {
      commit('SET_LOADING', false)
    }
  }
}

const mutations = {
  SET_DASHBOARD_DATA(state, data) {
    state.dashboardData = data
  },
  SET_PROFESSIONALS(state, professionals) {
    state.professionals = professionals
  },
  SET_CUSTOMERS(state, customers) {
    state.customers = customers
  },
  SET_REQUESTS(state, requests) {
    state.requests = requests
  },
  SET_LOADING(state, status) {
    state.loading = status
  },
  SET_ERROR(state, error) {
    state.error = error
  },
  CLEAR_ERROR(state) {
    state.error = null
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
} 