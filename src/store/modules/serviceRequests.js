import Vue from 'vue'

export default {
    namespaced: true,
    state: {
      requests: [],
      currentRequest: null,
      loading: false,
      error: null,
      filters: {
        status: 'all',
        dateRange: null
      }
    },
    getters: {
      requests: state => state.requests,
      currentRequest: state => state.currentRequest,
      loading: state => state.loading,
      error: state => state.error,
      filters: state => state.filters,
      filteredRequests: state => {
        if (state.filters.status === 'all') {
          return state.requests
        }
        return state.requests.filter(req => req.service_status === state.filters.status)
      },
      requestCountByStatus: state => status => {
        return state.requests.filter(req => req.service_status === status).length
      }
    },
    mutations: {
      SET_REQUESTS(state, requests) {
        state.requests = requests
      },
      SET_CURRENT_REQUEST(state, request) {
        state.currentRequest = request
      },
      ADD_REQUEST(state, request) {
        state.requests.push(request)
      },
      UPDATE_REQUEST(state, updatedRequest) {
        const index = state.requests.findIndex(r => r.id === updatedRequest.id)
        if (index !== -1) {
          const updated = { ...state.requests[index], ...updatedRequest }
          state.requests.splice(index, 1, updated)
        }
        
        if (state.currentRequest && state.currentRequest.id === updatedRequest.id) {
          state.currentRequest = { ...state.currentRequest, ...updatedRequest }
        }
      },
      REMOVE_REQUEST(state, requestId) {
        state.requests = state.requests.filter(r => r.id !== requestId)
        if (state.currentRequest && state.currentRequest.id === requestId) {
          state.currentRequest = null
        }
      },
      SET_FILTERS(state, filters) {
        state.filters = { ...state.filters, ...filters }
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
      async fetchCustomerRequests({ commit, dispatch }) {
        commit('SET_LOADING', true)
        commit('CLEAR_ERROR')
        
        try {
          const response = await Vue.prototype.$http.get('/customer/service-requests')
          commit('SET_REQUESTS', response.data)
          return response.data
        } catch (error) {
          const errorMessage = error.response?.data?.message || 'Failed to fetch service requests'
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
      
      async fetchRequestDetails({ commit, dispatch }, requestId) {
        commit('SET_LOADING', true)
        commit('CLEAR_ERROR')
        
        try {
          const response = await Vue.prototype.$http.get(`/customer/service-requests/${requestId}`)
          commit('SET_CURRENT_REQUEST', response.data)
          return response.data
        } catch (error) {
          const errorMessage = error.response?.data?.message || 'Failed to fetch request details'
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
      
      async createServiceRequest({ commit, dispatch }, requestData) {
        commit('SET_LOADING', true)
        commit('CLEAR_ERROR')
        
        try {
          const response = await Vue.prototype.$http.post('/customer/service-requests', requestData)
          commit('ADD_REQUEST', response.data.request_id ? { id: response.data.request_id, ...requestData } : requestData)
          
          dispatch('setNotification', {
            message: 'Service request created successfully',
            type: 'success'
          }, { root: true })
          
          return response.data
        } catch (error) {
          const errorMessage = error.response?.data?.message || 'Failed to create service request'
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
      
      async closeServiceRequest({ commit, dispatch }, requestId) {
        commit('SET_LOADING', true)
        commit('CLEAR_ERROR')
        
        try {
          const response = await Vue.prototype.$http.put(`/customer/service-requests/${requestId}`, {
            action: 'close'
          })
          
          commit('UPDATE_REQUEST', { 
            id: requestId, 
            service_status: 'closed' 
          })
          
          dispatch('setNotification', {
            message: 'Service request closed successfully',
            type: 'success'
          }, { root: true })
          
          return response.data
        } catch (error) {
          const errorMessage = error.response?.data?.message || 'Failed to close service request'
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
      
      async cancelServiceRequest({ commit, dispatch }, requestId) {
        commit('SET_LOADING', true)
        commit('CLEAR_ERROR')
        
        try {
          await Vue.prototype.$http.put(`/customer/service-requests/${requestId}/cancel`)
          commit('REMOVE_REQUEST', requestId)
          
          dispatch('setNotification', {
            message: 'Service request cancelled successfully',
            type: 'success'
          }, { root: true })
          
          return true
        } catch (error) {
          const errorMessage = error.response?.data?.message || 'Failed to cancel service request'
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
      
      async addReview({ commit, dispatch }, { requestId, reviewData }) {
        commit('SET_LOADING', true)
        commit('CLEAR_ERROR')
        
        try {
          const response = await Vue.prototype.$http.post(`/customer/service-requests/${requestId}/review`, reviewData)
          
          // Update the request to show it has a review now
          commit('UPDATE_REQUEST', { 
            id: requestId,
            has_review: true
          })
          
          dispatch('setNotification', {
            message: 'Review submitted successfully',
            type: 'success'
          }, { root: true })
          
          return response.data
        } catch (error) {
          const errorMessage = error.response?.data?.message || 'Failed to submit review'
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
      
      // Professional actions
      async fetchProfessionalRequests({ commit, dispatch }) {
        commit('SET_LOADING', true)
        commit('CLEAR_ERROR')
        
        try {
          const response = await Vue.prototype.$http.get('/professional/service-requests')
          commit('SET_REQUESTS', response.data)
          return response.data
        } catch (error) {
          const errorMessage = error.response?.data?.message || 'Failed to fetch service requests'
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
      
      async fetchAvailableRequests({ commit, dispatch }) {
        commit('SET_LOADING', true)
        commit('CLEAR_ERROR')
        
        try {
          const response = await Vue.prototype.$http.get('/professional/available-requests')
          return response.data
        } catch (error) {
          const errorMessage = error.response?.data?.message || 'Failed to fetch available requests'
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
      
      async updateRequestStatus({ commit, dispatch }, { requestId, action }) {
        commit('SET_LOADING', true)
        commit('CLEAR_ERROR')
        
        try {
          const response = await Vue.prototype.$http.put(`/professional/service-requests/${requestId}/action`, { action })
          
          // Update the request status based on the action
          let status = ''
          switch (action) {
            case 'accept': status = 'accepted'; break
            case 'reject': status = 'requested'; break
            case 'complete': status = 'completed'; break
            default: status = ''
          }
          
          if (status) {
            commit('UPDATE_REQUEST', { 
              id: requestId,
              service_status: status
            })
          }
          
          dispatch('setNotification', {
            message: `Request ${action}ed successfully`,
            type: 'success'
          }, { root: true })
          
          return response.data
        } catch (error) {
          const errorMessage = error.response?.data?.message || 'Failed to update request status'
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
      async fetchAllRequests({ commit, dispatch }) {
        commit('SET_LOADING', true)
        commit('CLEAR_ERROR')
        
        try {
          const response = await Vue.prototype.$http.get('/admin/service-requests')
          commit('SET_REQUESTS', response.data)
          return response.data
        } catch (error) {
          const errorMessage = error.response?.data?.message || 'Failed to fetch all service requests'
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
      
      async searchRequests({ commit, dispatch }, searchParams) {
        commit('SET_LOADING', true)
        commit('CLEAR_ERROR')
        
        try {
          const queryParams = new URLSearchParams()
          
          if (searchParams.status) queryParams.append('status', searchParams.status)
          if (searchParams.serviceId) queryParams.append('service_id', searchParams.serviceId)
          if (searchParams.professionalId) queryParams.append('professional_id', searchParams.professionalId)
          if (searchParams.customerId) queryParams.append('customer_id', searchParams.customerId)
          if (searchParams.startDate) queryParams.append('start_date', searchParams.startDate)
          if (searchParams.endDate) queryParams.append('end_date', searchParams.endDate)
          if (searchParams.query) queryParams.append('query', searchParams.query)
          
          const response = await Vue.prototype.$http.get(`/admin/service-requests/search?${queryParams.toString()}`)
          commit('SET_REQUESTS', response.data)
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
      
      async assignProfessional({ commit, dispatch }, { requestId, professionalId }) {
        commit('SET_LOADING', true)
        commit('CLEAR_ERROR')
        
        try {
          const response = await Vue.prototype.$http.put(`/admin/service-requests/${requestId}/assign`, {
            professional_id: professionalId
          })
          
          commit('UPDATE_REQUEST', {
            id: requestId,
            professional_id: professionalId,
            service_status: 'assigned'
          })
          
          dispatch('setNotification', {
            message: 'Professional assigned successfully',
            type: 'success'
          }, { root: true })
          
          return response.data
        } catch (error) {
          const errorMessage = error.response?.data?.message || 'Failed to assign professional'
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
      
      setFilters({ commit }, filters) {
        commit('SET_FILTERS', filters)
      },
      
      clearFilters({ commit }) {
        commit('SET_FILTERS', {
          status: 'all',
          dateRange: null
        })
      },
      
      clearError({ commit }) {
        commit('CLEAR_ERROR')
      }
    }
  }