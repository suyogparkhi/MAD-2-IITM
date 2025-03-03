<template>
    <div class="card shadow-sm h-100">
      <div class="card-body">
        <div class="d-flex align-items-center justify-content-between mb-3">
          <h5 class="card-title text-muted mb-0">{{ title }}</h5>
          <div class="stat-icon" :class="iconColor">
            <i :class="icon"></i>
          </div>
        </div>
        <h2 class="stat-value">{{ value }}</h2>
        <p class="card-text" v-if="description">{{ description }}</p>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: 'StatCard',
    props: {
      title: {
        type: String,
        required: true
      },
      value: {
        type: [String, Number],
        required: true
      },
      icon: {
        type: String,
        default: 'bi bi-bar-chart'
      },
      iconColor: {
        type: String,
        default: 'text-primary'
      },
      description: {
        type: String,
        default: ''
      }
    }
  }
  </script>
  
  <style scoped>
  .stat-icon {
    font-size: 1.5rem;
  }
  
  .stat-value {
    font-size: 2rem;
    font-weight: 700;
  }
  </style>