import Vue from 'vue'

// Initial state
const state = {
  professionals: [],
  filteredProfessionals: [],
  selectedProfessional: null,
  loading: false,
  error: null
}

// Getters
const getters = {
  professionals: state => state.professionals,
  filteredProfessionals: state => state.filteredProfessionals,
  selectedProfessional: state => state.selectedProfessional,
  loading: state => state.loading,
  error: state => state.error,
  
  // Get professionals by service
  professionalsByService: state => serviceId => {
    return state.professionals.filter(professional => professional.service_id === serviceId)
  },
  
  // Get top rated professionals
  topRatedProfessionals: state => {
    return [...state.professionals]
      .filter(p => p.avg_rating) // Only professionals with ratings
      .sort((a, b) => b.avg_rating - a.avg_rating)
      .slice(0, 5) // Top 5
  }
}

// Actions
const actions = {
  // Fetch all professionals
  async fetchProfessionals({ commit, dispatch }, filters = {}) {
    commit('SET_LOADING', true)
    commit('CLEAR_ERROR')
    
    try {
      // Build query string from filters
      const queryParams = new URLSearchParams()
      
      if (filters.serviceId) {
        queryParams.set('service_id', filters.serviceId)
      }
      
      if (filters.query) {
        queryParams.set('query', filters.query)
      }
      
      // Determine which endpoint to use: admin or customer (support both contexts)
      const isAdminContext = filters.isAdmin || window.location.pathname.includes('/admin');
      console.log("Is admin context:", isAdminContext);
      
      // Create the URL based on the context
      const endpoint = isAdminContext ? '/admin/professionals-public' : '/customer/professionals';
      const url = `${endpoint}${queryParams.toString() ? '?' + queryParams.toString() : ''}`;
      
      console.log("Fetching professionals from:", url);
      
      // Make the request
      const response = await Vue.prototype.$http.get(url)
      
      console.log("Received professionals:", response.data);
      
      // Update state
      commit('SET_PROFESSIONALS', response.data)
      
      // Apply any filters
      if (filters) {
        dispatch('filterProfessionals', filters)
      }
      
      return response.data
    } catch (error) {
      console.error('Error fetching professionals:', error)
      commit('SET_ERROR', 'Failed to load professionals. Please try again.')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  // Filter professionals
  filterProfessionals({ commit, state }, filters = {}) {
    let filtered = [...state.professionals]
    
    // Filter by search query
    if (filters.query) {
      const query = filters.query.toLowerCase()
      filtered = filtered.filter(professional => 
        professional.name.toLowerCase().includes(query) ||
        (professional.description && professional.description.toLowerCase().includes(query))
      )
    }
    
    // Filter by service
    if (filters.serviceId) {
      filtered = filtered.filter(professional => 
        professional.service_id === parseInt(filters.serviceId)
      )
    }
    
    // Filter by minimum rating
    if (filters.minRating) {
      filtered = filtered.filter(professional => 
        professional.avg_rating && professional.avg_rating >= filters.minRating
      )
    }
    
    // Filter by experience
    if (filters.minExperience) {
      filtered = filtered.filter(professional => 
        professional.experience && professional.experience >= filters.minExperience
      )
    }
    
    commit('SET_FILTERED_PROFESSIONALS', filtered)
  },
  
  // Clear all filters
  clearFilters({ commit, state }) {
    commit('SET_FILTERED_PROFESSIONALS', state.professionals)
  },
  
  // Set selected professional
  selectProfessional({ commit }, professionalId) {
    const professional = state.professionals.find(p => p.id === professionalId)
    commit('SET_SELECTED_PROFESSIONAL', professional || null)
  }
}

// Mutations
const mutations = {
  SET_PROFESSIONALS(state, professionals) {
    state.professionals = professionals
    state.filteredProfessionals = professionals
  },
  SET_FILTERED_PROFESSIONALS(state, professionals) {
    state.filteredProfessionals = professionals
  },
  SET_SELECTED_PROFESSIONAL(state, professional) {
    state.selectedProfessional = professional
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