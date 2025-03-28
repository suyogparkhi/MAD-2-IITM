<!-- src/views/admin/Reports.vue -->
<template>
  <div class="reports-view">
    <h2 class="mb-4">Reports</h2>
    
    <b-card no-body>
      <b-tabs pills card>
        <!-- Export Data Tab -->
        <b-tab title="Export Data" active>
          <b-card-body>
            <h4 class="mb-4">Export Service Requests Data</h4>
            <p class="text-muted mb-4">
              Generate CSV exports of service requests data for analysis or record-keeping.
            </p>
            
            <b-form @submit.prevent="triggerExport">
              <b-row>
                <b-col md="4">
                  <b-form-group label="Date Range">
                    <b-form-select v-model="exportForm.dateRange" :options="dateRangeOptions"></b-form-select>
                  </b-form-group>
                </b-col>
                <b-col md="4">
                  <b-form-group label="Status">
                    <b-form-select v-model="exportForm.status" :options="statusOptions"></b-form-select>
                  </b-form-group>
                </b-col>
                <b-col md="4">
                  <b-form-group label="Service Type">
                    <b-form-select v-model="exportForm.serviceId" :options="serviceOptions"></b-form-select>
                  </b-form-group>
                </b-col>
              </b-row>
              
              <b-form-group label="Email (optional)" description="Enter your email to receive a copy of the export">
                <b-form-input v-model="exportForm.email" type="email" placeholder="your@email.com"></b-form-input>
              </b-form-group>
              
              <div class="mt-3">
                <b-button type="submit" variant="primary" :disabled="exportLoading">
                  <b-spinner small v-if="exportLoading" class="mr-2"></b-spinner>
                  <i class="fas fa-file-export mr-2" v-else></i>
                  Generate CSV Export
                </b-button>
              </div>
            </b-form>
            
            <div v-if="exportError" class="mt-3 alert alert-danger">
              {{ exportError }}
            </div>
            
            <div v-if="exportJobs.length > 0" class="mt-4">
              <h5>Recent Export Jobs</h5>
              <b-table 
                :items="exportJobs" 
                :fields="exportJobFields"
                striped 
                hover
                responsive
              >
                <!-- Date Column -->
                <template #cell(created_at)="data">
                  {{ formatDate(data.item.created_at) }}
                </template>
                
                <!-- Status Column -->
                <template #cell(status)="data">
                  <b-badge :variant="getJobStatusVariant(data.item.status)">
                    {{ data.item.status }}
                  </b-badge>
                </template>
                
                <!-- Actions Column -->
                <template #cell(actions)="data">
                  <b-button 
                    v-if="data.item.status === 'completed'" 
                    size="sm" 
                    variant="success" 
                    :href="data.item.file_url" 
                    target="_blank"
                  >
                    <i class="fas fa-download mr-1"></i> Download
                  </b-button>
                  <span v-else-if="data.item.status === 'failed'" class="text-danger">
                    Failed
                  </span>
                  <b-spinner small v-else></b-spinner>
                </template>
              </b-table>
            </div>
          </b-card-body>
        </b-tab>
        
        <!-- Monthly Reports Tab -->
        <b-tab title="Monthly Reports">
          <b-card-body>
            <h4 class="mb-4">Monthly Activity Reports</h4>
            <p class="text-muted mb-4">
              View and download monthly activity reports that are automatically generated on the first day of each month.
            </p>
            
            <div v-if="reportsLoading" class="text-center py-4">
              <b-spinner variant="primary" label="Loading..."></b-spinner>
              <p class="mt-3">Loading reports...</p>
            </div>
            
            <div v-else-if="reportsError" class="alert alert-danger">
              {{ reportsError }}
              <b-button @click="fetchMonthlyReports" variant="outline-danger" size="sm" class="ml-2">
                Try Again
              </b-button>
            </div>
            
            <div v-else-if="monthlyReports.length === 0" class="text-center py-4">
              <i class="fas fa-file-alt fa-3x text-muted mb-3"></i>
              <h5>No Reports Available</h5>
              <p class="text-muted">Monthly reports will be generated automatically on the first day of each month.</p>
            </div>
            
            <div v-else>
              <b-table 
                :items="monthlyReports" 
                :fields="reportFields"
                striped 
                hover
                responsive
              >
                <!-- Month Column -->
                <template #cell(month)="data">
                  {{ formatMonth(data.item.month) }}
                </template>
                
                <!-- Generated Date Column -->
                <template #cell(created_at)="data">
                  {{ formatDate(data.item.created_at) }}
                </template>
                
                <!-- Actions Column -->
                <template #cell(actions)="data">
                  <b-button-group>
                    <b-button size="sm" variant="primary" :href="data.item.html_url" target="_blank">
                      <i class="fas fa-eye mr-1"></i> View HTML
                    </b-button>
                    <b-button size="sm" variant="success" :href="data.item.pdf_url" target="_blank">
                      <i class="fas fa-file-pdf mr-1"></i> Download PDF
                    </b-button>
                  </b-button-group>
                </template>
              </b-table>
            </div>
          </b-card-body>
        </b-tab>
        
        <!-- Manual Report Generation Tab -->
        <b-tab title="Generate Report">
          <b-card-body>
            <h4 class="mb-4">Generate Custom Report</h4>
            <p class="text-muted mb-4">
              Generate a custom report for a specific time period.
            </p>
            
            <b-form @submit.prevent="generateCustomReport">
              <b-row>
                <b-col md="6">
                  <b-form-group label="Start Date">
                    <b-form-datepicker v-model="customReportForm.startDate" :max="today"></b-form-datepicker>
                  </b-form-group>
                </b-col>
                <b-col md="6">
                  <b-form-group label="End Date">
                    <b-form-datepicker v-model="customReportForm.endDate" :min="customReportForm.startDate" :max="today"></b-form-datepicker>
                  </b-form-group>
                </b-col>
              </b-row>
              
              <b-form-group label="Report Type">
                <b-form-select v-model="customReportForm.type" :options="reportTypeOptions"></b-form-select>
              </b-form-group>
              
              <div class="mt-3">
                <b-button type="submit" variant="primary" :disabled="customReportLoading">
                  <b-spinner small v-if="customReportLoading" class="mr-2"></b-spinner>
                  <i class="fas fa-file-alt mr-2" v-else></i>
                  Generate Report
                </b-button>
              </div>
            </b-form>
            
            <div v-if="customReportError" class="mt-3 alert alert-danger">
              {{ customReportError }}
            </div>
          </b-card-body>
        </b-tab>
      </b-tabs>
    </b-card>
  </div>
</template>

<script>
import { mapActions, mapGetters } from 'vuex'
import { format } from 'date-fns'

export default {
  name: 'AdminReportsView',
  data() {
    return {
      activeTab: 0,
      exportForm: {
        dateRange: 'all',
        status: 'all',
        serviceId: 'all',
        email: ''
      },
      customReportForm: {
        startDate: null,
        endDate: null,
        type: 'service_performance'
      },
      dateRangeOptions: [
        { value: 'all', text: 'All Time' },
        { value: 'today', text: 'Today' },
        { value: 'this_week', text: 'This Week' },
        { value: 'this_month', text: 'This Month' },
        { value: 'last_month', text: 'Last Month' }
      ],
      statusOptions: [
        { value: 'all', text: 'All Statuses' },
        { value: 'requested', text: 'Requested' },
        { value: 'assigned', text: 'Assigned' },
        { value: 'accepted', text: 'Accepted' },
        { value: 'completed', text: 'Completed' },
        { value: 'closed', text: 'Closed' }
      ],
      reportTypeOptions: [
        { value: 'service_performance', text: 'Service Performance' },
        { value: 'customer_activity', text: 'Customer Activity' },
        { value: 'professional_performance', text: 'Professional Performance' }
      ],
      serviceOptions: [
        { value: 'all', text: 'All Services' }
        // Will be populated in created()
      ],
      exportJobFields: [
        { key: 'id', label: 'ID' },
        { key: 'job_type', label: 'Type' },
        { key: 'created_at', label: 'Created' },
        { key: 'status', label: 'Status' },
        { key: 'actions', label: 'Actions' }
      ],
      reportFields: [
        { key: 'month', label: 'Month' },
        { key: 'requests_count', label: 'Requests' },
        { key: 'completed_count', label: 'Completed' },
        { key: 'revenue', label: 'Revenue' },
        { key: 'avg_rating', label: 'Avg. Rating' },
        { key: 'actions', label: 'Actions' }
      ],
      statusPollingIntervals: {},
      currentDate: new Date()
    }
  },
  computed: {
    ...mapGetters({
      services: 'services/services',
      exportJobs: 'reports/exportJobs',
      monthlyReports: 'reports/monthlyReports',
      exportLoading: 'reports/exportLoading',
      exportError: 'reports/exportError',
      reportsLoading: 'reports/reportsLoading',
      reportsError: 'reports/reportsError'
    }),
    ...mapGetters('services', ['allServices']),
    today() {
      return new Date().toISOString().split('T')[0]
    },
    formattedMonthlyReports() {
      return this.monthlyReports.map(report => ({
        ...report,
        avg_rating: report.avg_rating ? report.avg_rating.toFixed(1) : 'N/A',
        revenue: `$${report.revenue.toLocaleString()}`
      }))
    }
  },
  methods: {
    ...mapActions({
      fetchServices: 'services/fetchServices',
      fetchExportJobs: 'reports/fetchExportJobs',
      createExportJob: 'reports/createExportJob',
      fetchMonthlyReports: 'reports/fetchMonthlyReports',
      generateReport: 'reports/generateReport',
      checkExportStatus: 'reports/checkExportStatus'
    }),
    ...mapActions('services', ['fetchServices']),
    formatDate(dateString) {
      if (!dateString) return 'N/A'
      const date = new Date(dateString)
      return date.toLocaleString()
    },
    formatMonth(monthString) {
      return format(new Date(monthString), 'MMMM yyyy')
    },
    getJobStatusVariant(status) {
      const variants = {
        'pending': 'warning',
        'processing': 'info',
        'completed': 'success',
        'failed': 'danger'
      }
      return variants[status] || 'secondary'
    },
    async triggerExport() {
      try {
        const job = await this.createExportJob({
          dateRange: this.exportForm.dateRange,
          status: this.exportForm.status,
          serviceId: this.exportForm.serviceId === 'all' ? null : this.exportForm.serviceId,
          email: this.exportForm.email || null
        })
        
        this.$bvToast.toast('Export job started successfully. You will be notified when it completes.', {
          title: 'Export Started',
          variant: 'success',
          solid: true
        })
        
        // Start polling the job status
        this.startStatusPolling(job.id)
        
      } catch (error) {
        console.error('Failed to start export job', error)
      }
    },
    startStatusPolling(jobId) {
      // Clear any existing interval for this job
      if (this.statusPollingIntervals[jobId]) {
        clearInterval(this.statusPollingIntervals[jobId])
      }
      
      // Poll every 5 seconds
      this.statusPollingIntervals[jobId] = setInterval(async () => {
        try {
          const jobStatus = await this.checkExportStatus(jobId)
          
          // If job is completed or failed, stop polling
          if (['completed', 'failed'].includes(jobStatus.status)) {
            clearInterval(this.statusPollingIntervals[jobId])
            delete this.statusPollingIntervals[jobId]
            
            // Refresh jobs list
            this.fetchExportJobs()
            
            // Show notification
            const message = jobStatus.status === 'completed' 
              ? 'Export completed successfully. You can download it now.'
              : `Export failed: ${jobStatus.error_message || 'Unknown error'}`
            
            this.$bvToast.toast(message, {
              title: jobStatus.status === 'completed' ? 'Export Complete' : 'Export Failed',
              variant: jobStatus.status === 'completed' ? 'success' : 'danger',
              solid: true
            })
          }
        } catch (error) {
          console.error('Failed to check job status:', error)
        }
      }, 5000)
    },
    downloadExport(fileUrl) {
      if (!fileUrl) return
      
      // Create a link to download the file
      window.open(fileUrl, '_blank')
    },
    async generateCustomReport() {
      try {
        const result = await this.generateReport({
          startDate: this.customReportForm.startDate,
          endDate: this.customReportForm.endDate,
          reportType: this.customReportForm.type
        })
        
        this.$bvToast.toast('Report generation started successfully.', {
          title: 'Report Generation',
          variant: 'success',
          solid: true
        })
        
        // Start polling if there's a job ID
        if (result && result.report_id) {
          this.startStatusPolling(result.report_id)
        }
      } catch (error) {
        console.error('Failed to generate report', error)
      }
    },
    async loadData() {
      await Promise.all([
        this.fetchServices(),
        this.fetchExportJobs(),
        this.fetchMonthlyReports()
      ])
      
      // Add services to dropdown options
      this.serviceOptions = [
        { value: 'all', text: 'All Services' },
        ...this.services.map(service => ({
          value: service.id,
          text: service.name
        }))
      ]
      
      // Check for ongoing jobs and start polling
      this.exportJobs.forEach(job => {
        if (['pending', 'processing'].includes(job.status)) {
          this.startStatusPolling(job.id)
        }
      })
    }
  },
  created() {
    this.loadData()
  },
  beforeDestroy() {
    // Clear all polling intervals when component is destroyed
    Object.values(this.statusPollingIntervals).forEach(interval => {
      clearInterval(interval)
    })
  }
}
</script>

<style scoped>
.reports-view {
  min-height: 70vh;
}
</style> 