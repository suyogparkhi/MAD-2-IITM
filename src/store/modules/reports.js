import Vue from 'vue'

export default {
    namespaced: true,
    state: {
      exportStatus: null,
      exportProgress: 0,
      loading: false,
      error: null,
      lastExport: null,
      reports: [],
      currentReport: null
    },
    getters: {
      exportStatus: state => state.exportStatus,
      exportProgress: state => state.exportProgress,
      loading: state => state.loading,
      error: state => state.error,
      lastExport: state => state.lastExport,
      reports: state => state.reports,
      currentReport: state => state.currentReport
    },
    mutations: {
      SET_EXPORT_STATUS(state, status) {
        state.exportStatus = status
      },
      SET_EXPORT_PROGRESS(state, progress) {
        state.exportProgress = progress
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
      SET_LAST_EXPORT(state, exportData) {
        state.lastExport = exportData
      },
      SET_REPORTS(state, reports) {
        state.reports = reports
      },
      SET_CURRENT_REPORT(state, report) {
        state.currentReport = report
      }
    },
    actions: {
      async exportServiceRequests({ commit, dispatch }, { professionalId, filterType, email }) {
        commit('SET_LOADING', true)
        commit('CLEAR_ERROR')
        commit('SET_EXPORT_STATUS', 'processing')
        commit('SET_EXPORT_PROGRESS', 0)
        
        try {
          const params = new URLSearchParams()
          if (professionalId) params.append('professional_id', professionalId)
          if (filterType) params.append('filter_type', filterType)
          if (email) params.append('email', email)
          
          const response = await Vue.prototype.$http.post(`/admin/export/service-requests?${params.toString()}`)
          
          commit('SET_EXPORT_STATUS', 'completed')
          commit('SET_EXPORT_PROGRESS', 100)
          commit('SET_LAST_EXPORT', {
            type: 'service-requests',
            timestamp: new Date().toISOString(),
            params: { professionalId, filterType, email },
            jobId: response.data.job_id || null
          })
          
          dispatch('setNotification', {
            message: 'Export started successfully. You will receive an email when it\'s complete.',
            type: 'success'
          }, { root: true })
          
          return response.data
        } catch (error) {
          const errorMessage = error.response?.data?.message || 'Failed to export data'
          commit('SET_ERROR', errorMessage)
          commit('SET_EXPORT_STATUS', 'failed')
          
          dispatch('setNotification', {
            message: errorMessage,
            type: 'error'
          }, { root: true })
          
          throw error
        } finally {
          commit('SET_LOADING', false)
        }
      },
      
      async generateAdminReport({ commit, dispatch }, { reportType, email }) {
        commit('SET_LOADING', true)
        commit('CLEAR_ERROR')
        commit('SET_EXPORT_STATUS', 'processing')
        commit('SET_EXPORT_PROGRESS', 0)
        
        try {
          const params = new URLSearchParams()
          if (reportType) params.append('report_type', reportType)
          if (email) params.append('email', email)
          
          const response = await Vue.prototype.$http.post(`/admin/export/report?${params.toString()}`)
          
          commit('SET_EXPORT_STATUS', 'completed')
          commit('SET_EXPORT_PROGRESS', 100)
          commit('SET_LAST_EXPORT', {
            type: 'admin-report',
            reportType,
            timestamp: new Date().toISOString(),
            params: { reportType, email },
            jobId: response.data.job_id || null
          })
          
          dispatch('setNotification', {
            message: 'Report generation started. You will receive an email when it\'s complete.',
            type: 'success'
          }, { root: true })
          
          return response.data
        } catch (error) {
          const errorMessage = error.response?.data?.message || 'Failed to generate report'
          commit('SET_ERROR', errorMessage)
          commit('SET_EXPORT_STATUS', 'failed')
          
          dispatch('setNotification', {
            message: errorMessage,
            type: 'error'
          }, { root: true })
          
          throw error
        } finally {
          commit('SET_LOADING', false)
        }
      },
      
      async generateMonthlyReport({ commit, dispatch }, { month, year, email }) {
        commit('SET_LOADING', true)
        commit('CLEAR_ERROR')
        commit('SET_EXPORT_STATUS', 'processing')
        
        try {
          const params = new URLSearchParams()
          if (month) params.append('month', month)
          if (year) params.append('year', year)
          if (email) params.append('email', email)
          
          const response = await Vue.prototype.$http.post(`/admin/export/monthly-report?${params.toString()}`)
          
          commit('SET_EXPORT_STATUS', 'completed')
          commit('SET_LAST_EXPORT', {
            type: 'monthly-report',
            timestamp: new Date().toISOString(),
            params: { month, year, email },
            jobId: response.data.job_id || null
          })
          
          dispatch('setNotification', {
            message: 'Monthly report generation started. You will receive an email when it\'s complete.',
            type: 'success'
          }, { root: true })
          
          return response.data
        } catch (error) {
          const errorMessage = error.response?.data?.message || 'Failed to generate monthly report'
          commit('SET_ERROR', errorMessage)
          commit('SET_EXPORT_STATUS', 'failed')
          
          dispatch('setNotification', {
            message: errorMessage,
            type: 'error'
          }, { root: true })
          
          throw error
        } finally {
          commit('SET_LOADING', false)
        }
      },
      
      async checkExportStatus({ commit, dispatch }, jobId) {
        if (!jobId) return null
        
        try {
          const response = await Vue.prototype.$http.get(`/admin/export/status/${jobId}`)
          
          const status = response.data.status
          commit('SET_EXPORT_STATUS', status)
          
          if (response.data.progress) {
            commit('SET_EXPORT_PROGRESS', response.data.progress)
          }
          
          return response.data
        } catch (error) {
          console.error('Failed to check export status:', error)
          return null
        }
      },
      
      async fetchReports({ commit, dispatch }) {
        commit('SET_LOADING', true)
        commit('CLEAR_ERROR')
        
        try {
          const response = await Vue.prototype.$http.get('/admin/exports')
          commit('SET_REPORTS', response.data)
          return response.data
        } catch (error) {
          const errorMessage = error.response?.data?.message || 'Failed to fetch reports'
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
      
      async fetchReport({ commit, dispatch }, reportId) {
        commit('SET_LOADING', true)
        commit('CLEAR_ERROR')
        
        try {
          const response = await Vue.prototype.$http.get(`/admin/exports/${reportId}`)
          commit('SET_CURRENT_REPORT', response.data)
          return response.data
        } catch (error) {
          const errorMessage = error.response?.data?.message || 'Failed to fetch report'
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
      
      async downloadReport({ commit, dispatch }, reportId) {
        commit('SET_LOADING', true)
        commit('CLEAR_ERROR')
        
        try {
          const response = await Vue.prototype.$http.get(`/admin/exports/${reportId}/download`, {
            responseType: 'blob'
          })
          
          // Create a download link and trigger it
          const url = window.URL.createObjectURL(new Blob([response.data]))
          const link = document.createElement('a')
          link.href = url
          
          // Get filename from content-disposition header if available
          const contentDisposition = response.headers['content-disposition']
          let filename = 'report.csv'
          
          if (contentDisposition) {
            const filenameMatch = contentDisposition.match(/filename="?([^"]*)"?/)
            if (filenameMatch && filenameMatch[1]) {
              filename = filenameMatch[1]
            }
          }
          
          link.setAttribute('download', filename)
          document.body.appendChild(link)
          link.click()
          link.remove()
          
          return true
        } catch (error) {
          const errorMessage = 'Failed to download report'
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
      
      resetExportStatus({ commit }) {
        commit('SET_EXPORT_STATUS', null)
        commit('SET_EXPORT_PROGRESS', 0)
      },
      
      clearError({ commit }) {
        commit('CLEAR_ERROR')
      }
    }
  }