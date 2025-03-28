<template>
  <div class="stat-card" :class="[`stat-card-${variant}`]">
    <div class="stat-card-content">
      <div class="stat-card-icon" :class="[`stat-card-icon-${variant}`]">
        <i :class="icon"></i>
      </div>
      <div class="stat-card-info">
        <h3 class="stat-card-value">{{ value }}</h3>
        <div class="stat-card-title">{{ title }}</div>
        <div v-if="change !== null" class="stat-card-change" :class="changeClass">
          <i :class="changeIcon"></i> {{ Math.abs(change) }}%
        </div>
      </div>
    </div>
    <div v-if="showTrend" class="stat-card-footer">
      <div class="stat-card-trend">
        <span class="trend-label">{{ trendLabel }}</span>
        <span class="trend-period">{{ trendPeriod }}</span>
      </div>
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
      default: 'fas fa-chart-line'
    },
    variant: {
      type: String,
      default: 'primary',
      validator: value => ['primary', 'success', 'info', 'warning', 'danger'].includes(value)
    },
    change: {
      type: Number,
      default: null
    },
    showTrend: {
      type: Boolean,
      default: false
    },
    trendLabel: {
      type: String,
      default: 'Trend'
    },
    trendPeriod: {
      type: String,
      default: 'Last 30 days'
    }
  },
  computed: {
    changeClass() {
      return this.change >= 0 ? 'positive-change' : 'negative-change';
    },
    changeIcon() {
      return this.change >= 0 ? 'fas fa-arrow-up' : 'fas fa-arrow-down';
    }
  }
}
</script>

<style scoped>
.stat-card {
  background-color: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  padding: 1.5rem;
  height: 100%;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  overflow: hidden;
  position: relative;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}

.stat-card-content {
  display: flex;
  align-items: center;
}

.stat-card-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.6rem;
  margin-right: 1.25rem;
  flex-shrink: 0;
}

.stat-card-icon-primary {
  background-color: rgba(13, 110, 253, 0.1);
  color: #0d6efd;
}

.stat-card-icon-success {
  background-color: rgba(25, 135, 84, 0.1);
  color: #198754;
}

.stat-card-icon-info {
  background-color: rgba(13, 202, 240, 0.1);
  color: #0dcaf0;
}

.stat-card-icon-warning {
  background-color: rgba(255, 193, 7, 0.1);
  color: #ffc107;
}

.stat-card-icon-danger {
  background-color: rgba(220, 53, 69, 0.1);
  color: #dc3545;
}

.stat-card-primary::before {
  background-color: #0d6efd;
}

.stat-card-success::before {
  background-color: #198754;
}

.stat-card-info::before {
  background-color: #0dcaf0;
}

.stat-card-warning::before {
  background-color: #ffc107;
}

.stat-card-danger::before {
  background-color: #dc3545;
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 5px;
  height: 100%;
}

.stat-card-info {
  flex-grow: 1;
}

.stat-card-value {
  font-size: 1.8rem;
  font-weight: 600;
  margin-bottom: 0.3rem;
  line-height: 1;
  color: #212529;
}

.stat-card-title {
  color: #6c757d;
  font-size: 0.9rem;
  margin-bottom: 0.75rem;
}

.stat-card-change {
  font-size: 0.85rem;
  font-weight: 500;
  margin-top: 0.5rem;
}

.positive-change {
  color: #198754;
}

.negative-change {
  color: #dc3545;
}

.stat-card-footer {
  margin-top: 1.25rem;
  padding-top: 1rem;
  border-top: 1px solid rgba(0, 0, 0, 0.05);
}

.stat-card-trend {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.8rem;
}

.trend-label {
  color: #6c757d;
}

.trend-period {
  color: #adb5bd;
}
</style>