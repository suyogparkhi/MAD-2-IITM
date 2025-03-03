<template>
  <div class="landing-layout">
    <app-navbar />
    <main>
      <router-view />
    </main>
    <app-footer />
  </div>
</template>

<script>
import AppNavbar from '@/components/common/Navbar.vue'
import AppFooter from '@/components/common/Footer.vue'

export default {
  name: 'LandingLayout',
  components: {
    AppNavbar,
    AppFooter
  }
}
</script>

<style scoped>
.landing-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

main {
  flex: 1;
}
</style> 