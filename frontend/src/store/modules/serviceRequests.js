import Vue from 'vue'

export default {
    namespaced: true,
    state: {
        requests: [],          // Customer's service requests
        professionalRequests: [], // Professional's service requests
        availableRequests: [], // Available requests for professionals
        adminRequests: [],    // All requests for admin
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
        professionalRequests: state => state.professionalRequests,
        availableRequests: state => state.availableRequests,
        adminRequests: state => state.adminRequests,
        currentRequest: state => state.currentRequest,
        loading: state => state.loading,
        error: state => state.error,
        filters: state => state.filters,
        requestsByStatus: (state) => (status) => {
            return state.requests.filter(req => req.service_status === status)
        },
        pendingRequests: (state) => {
            return state.requests.filter(req => ['requested', 'assigned', 'accepted'].includes(req.service_status))
        },
        completedRequests: (state) => {
            return state.requests.filter(req => ['completed', 'closed'].includes(req.service_status))
        }
    },
    mutations: {
        SET_REQUESTS(state, requests) {
            state.requests = requests
        },
        SET_PROFESSIONAL_REQUESTS(state, requests) {
            state.professionalRequests = requests
        },
        SET_AVAILABLE_REQUESTS(state, requests) {
            state.availableRequests = requests
        },
        SET_ADMIN_REQUESTS(state, requests) {
            state.adminRequests = requests
        },
        SET_CURRENT_REQUEST(state, request) {
            state.currentRequest = request
        },
        ADD_REQUEST(state, request) {
            // Add to customer requests
            state.requests.unshift(request)
        },
        UPDATE_REQUEST(state, updatedRequest) {
            // Update in customer requests
            const customerIndex = state.requests.findIndex(req => req.id === updatedRequest.id)
            if (customerIndex !== -1) {
                state.requests[customerIndex] = { ...state.requests[customerIndex], ...updatedRequest }
            }
            
            // Update in professional requests
            const professionalIndex = state.professionalRequests.findIndex(req => req.id === updatedRequest.id)
            if (professionalIndex !== -1) {
                state.professionalRequests[professionalIndex] = { 
                    ...state.professionalRequests[professionalIndex], 
                    ...updatedRequest 
                }
            }
            
            // Update in admin requests
            const adminIndex = state.adminRequests.findIndex(req => req.id === updatedRequest.id)
            if (adminIndex !== -1) {
                state.adminRequests[adminIndex] = { ...state.adminRequests[adminIndex], ...updatedRequest }
            }
            
            // If this is an available request being accepted, remove it from available requests
            if (updatedRequest.service_status === 'accepted') {
                state.availableRequests = state.availableRequests.filter(req => req.id !== updatedRequest.id)
            }
            
            // Update current request if it's the one being viewed
            if (state.currentRequest && state.currentRequest.id === updatedRequest.id) {
                state.currentRequest = { ...state.currentRequest, ...updatedRequest }
            }
        },
        REMOVE_REQUEST(state, requestId) {
            // Remove from all request arrays
            state.requests = state.requests.filter(req => req.id !== requestId)
            state.professionalRequests = state.professionalRequests.filter(req => req.id !== requestId)
            state.availableRequests = state.availableRequests.filter(req => req.id !== requestId)
            state.adminRequests = state.adminRequests.filter(req => req.id !== requestId)
            
            // Clear current request if it's the one being removed
            if (state.currentRequest && state.currentRequest.id === requestId) {
                state.currentRequest = null
            }
        },
        SET_LOADING(state, status) {
            state.loading = status
        },
        SET_ERROR(state, error) {
            state.error = error
        },
        CLEAR_ERROR(state) {
            state.error = null
        },
        SET_FILTERS(state, filters) {
            state.filters = { ...state.filters, ...filters }
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
                
                commit('ADD_REQUEST', response.data)
                
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
        
        async addReview({ commit, dispatch }, { serviceRequestId, rating, comments }) {
            commit('SET_LOADING', true)
            commit('CLEAR_ERROR')
            
            try {
                const response = await Vue.prototype.$http.post(`/customer/service-requests/${serviceRequestId}/review`, {
                    rating,
                    comments
                })
                
                // Update the request to include review data
                commit('UPDATE_REQUEST', {
                    id: serviceRequestId,
                    review: {
                        rating,
                        comments,
                        date_posted: new Date().toISOString()
                    }
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
                commit('SET_PROFESSIONAL_REQUESTS', response.data)
                return response.data
            } catch (error) {
                const errorMessage = error.response?.data?.message || 'Failed to fetch professional service requests'
                commit('SET_ERROR', errorMessage)
                throw error
            } finally {
                commit('SET_LOADING', false)
            }
        },
        
        async fetchAvailableRequests({ commit }) {
            commit('SET_LOADING', true)
            commit('CLEAR_ERROR')
            
            try {
                const response = await Vue.prototype.$http.get('/professional/available-requests')
                commit('SET_AVAILABLE_REQUESTS', response.data)
                return response.data
            } catch (error) {
                const errorMessage = error.response?.data?.message || 'Failed to fetch available requests'
                commit('SET_ERROR', errorMessage)
                throw error
            } finally {
                commit('SET_LOADING', false)
            }
        },
        
        async updateServiceRequest({ commit, dispatch }, { id, action }) {
            commit('SET_LOADING', true)
            commit('CLEAR_ERROR')
            
            try {
                const response = await Vue.prototype.$http.put(`/professional/service-requests/${id}/action`, { action })
                
                // Update status based on action
                let newStatus = '';
                switch(action) {
                    case 'accept':
                        newStatus = 'accepted';
                        break;
                    case 'reject':
                        newStatus = 'requested'; // Reset to requested when rejected
                        break;
                    case 'complete':
                        newStatus = 'completed';
                        break;
                    default:
                        newStatus = '';
                }
                
                if (newStatus) {
                    commit('UPDATE_REQUEST', {
                        id,
                        service_status: newStatus,
                        ...(action === 'complete' ? { date_of_completion: new Date().toISOString() } : {})
                    });
                }
                
                const actionMsgs = {
                    'accept': 'accepted',
                    'reject': 'rejected',
                    'complete': 'marked as completed'
                };
                
                dispatch('setNotification', {
                    message: `Service request ${actionMsgs[action] || action} successfully`,
                    type: 'success'
                }, { root: true });
                
                return response.data;
            } catch (error) {
                const errorMessage = error.response?.data?.message || `Failed to ${action} service request`;
                commit('SET_ERROR', errorMessage);
                
                dispatch('setNotification', {
                    message: errorMessage,
                    type: 'error'
                }, { root: true });
                
                throw error;
            } finally {
                commit('SET_LOADING', false);
            }
        },
        
        // Admin actions
        async fetchAdminRequests({ commit }) {
            commit('SET_LOADING', true)
            commit('CLEAR_ERROR')
            
            try {
                const response = await Vue.prototype.$http.get('/admin/service-requests')
                commit('SET_ADMIN_REQUESTS', response.data)
                return response.data
            } catch (error) {
                const errorMessage = error.response?.data?.message || 'Failed to fetch service requests'
                commit('SET_ERROR', errorMessage)
                throw error
            } finally {
                commit('SET_LOADING', false)
            }
        },
        
        async searchRequests({ commit }, searchParams) {
            commit('SET_LOADING', true)
            commit('CLEAR_ERROR')
            
            try {
                const queryParams = new URLSearchParams();
                
                // Add search parameters to the query
                if (searchParams.status) queryParams.append('status', searchParams.status);
                if (searchParams.serviceId) queryParams.append('service_id', searchParams.serviceId);
                if (searchParams.customerId) queryParams.append('customer_id', searchParams.customerId);
                if (searchParams.professionalId) queryParams.append('professional_id', searchParams.professionalId);
                if (searchParams.startDate) queryParams.append('start_date', searchParams.startDate);
                if (searchParams.endDate) queryParams.append('end_date', searchParams.endDate);
                if (searchParams.query) queryParams.append('query', searchParams.query);
                
                const response = await Vue.prototype.$http.get(`/admin/service-requests/search?${queryParams.toString()}`);
                
                // Don't override all admin requests, just return the search results
                return response.data;
            } catch (error) {
                const errorMessage = error.response?.data?.message || 'Failed to search service requests';
                commit('SET_ERROR', errorMessage);
                throw error;
            } finally {
                commit('SET_LOADING', false);
            }
        },
        
        async assignProfessional({ commit, dispatch }, { requestId, professionalId }) {
            commit('SET_LOADING', true)
            commit('CLEAR_ERROR')
            
            try {
                const response = await Vue.prototype.$http.put(`/admin/service-requests/${requestId}/assign`, { 
                    professional_id: professionalId 
                })
                
                // Update the request with the new professional and status
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
        
        async updateRequestAdmin({ commit, dispatch }, { requestId, updateData }) {
            commit('SET_LOADING', true)
            commit('CLEAR_ERROR')
            
            try {
                const response = await Vue.prototype.$http.put(`/admin/service-requests/${requestId}`, updateData)
                
                // Update request in store
                commit('UPDATE_REQUEST', {
                    id: requestId,
                    ...updateData
                })
                
                dispatch('setNotification', {
                    message: 'Service request updated successfully',
                    type: 'success'
                }, { root: true })
                
                return response.data
            } catch (error) {
                const errorMessage = error.response?.data?.message || 'Failed to update service request'
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
        
        clearFilters({ commit }) {
            commit('SET_FILTERS', {
                status: 'all',
                dateRange: null
            })
        },
        
        // Error handling
        clearError({ commit }) {
            commit('CLEAR_ERROR')
        }
    }
}