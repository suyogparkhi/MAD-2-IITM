<template>
    <div class="auth-layout">
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
    </div>
  </template>
  
  <script>
  export default {
    name: 'AuthLayout'
  }
  </script>
  
  <style scoped>
  .auth-layout {
    min-height: 100vh;
    display: flex;
    align-items: center;
    background-color: #f5f5f5;
  }
  
  .brand-title {
    color: #007bff;
    font-weight: 700;
  }
  </style>