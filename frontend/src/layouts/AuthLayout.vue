<template>
  <div class="auth-layout">
    <app-navbar />
    <main>
      <div class="container">
        <div class="row justify-content-center">
          <div class="col-md-8 col-lg-6">
            <div class="text-center my-5">
              <h1 class="brand-title">A-Z Household Services</h1>
            </div>
            <div class="card shadow">
              <div class="card-body p-4">
                <router-view />
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
    <app-footer />
  </div>
</template>

<script>
import AppNavbar from '@/components/common/Navbar.vue'
import AppFooter from '@/components/common/Footer.vue'

export default {
  name: 'AuthLayout',
  components: {
    AppNavbar,
    AppFooter
  }
}
</script>

<style scoped>
.auth-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f5f5f5;
}

main {
  flex: 1;
  padding-top: 40px;
  padding-bottom: 40px;
}

.brand-title {
  color: #007bff;
  font-weight: 700;
}
</style>