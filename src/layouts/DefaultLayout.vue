<template>
    <div class="default-layout">
      <Navbar />
      <div class="container-fluid">
        <div class="row">
          <Sidebar v-if="showSidebar" class="col-md-3 col-lg-2 d-md-block sidebar"/>
          <main class="col-md-9 ms-sm-auto col-lg-10 px-md-4 py-4">
            <router-view />
          </main>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import Navbar from '@/components/common/Navbar.vue'
  import Sidebar from '@/components/common/Sidebar.vue'
  import { mapGetters } from 'vuex'
  
  export default {
    name: 'DefaultLayout',
    components: {
      Navbar,
      Sidebar
    },
    computed: {
      ...mapGetters('auth', [
        'isAuthenticated', 
        'userRole'
      ]),
      showSidebar() {
        // Show sidebar for authenticated users
        return this.isAuthenticated
      }
    }
  }
  </script>
  
  <style scoped>
  .sidebar {
    position: fixed;
    top: 56px; /* Navbar height */
    bottom: 0;
    left: 0;
    z-index: 100;
    padding: 48px 0 0;
    box-shadow: inset -1px 0 0 rgba(0, 0, 0, .1);
    background-color: #f8f9fa;
  }
  
  @media (max-width: 767.98px) {
    .sidebar {
      top: 0;
      padding-top: 56px;
    }
  }
  </style>
  
  
  