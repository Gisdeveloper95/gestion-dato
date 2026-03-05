<template>
  <div class="app-container">
    <AppHeader />
    <AppNavbar />
    <main class="main-content">
      <router-view></router-view>
    </main>
    <AppFooter />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import { useAuthStore } from './store/auth';
import AppHeader from './components/layout/AppHeader.vue';
import AppNavbar from './components/layout/AppNavbar.vue';
import AppFooter from './components/layout/AppFooter.vue';

const authStore = useAuthStore();

onMounted(async () => {
  console.log("🚀 App.vue iniciado");
  
  try {
    await authStore.checkAuth();
    
    if (authStore.user) {
      console.log("✅ Usuario cargado:", authStore.user.username, "- Admin:", authStore.isAdmin);
    }
  } catch (error) {
    console.error("❌ Error verificando autenticación:", error);
  }
});
</script>

<style>
.app-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.main-content {
  flex: 1;
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

@media (max-width: 768px) {
  .main-content {
    padding: 10px;
  }
}
</style>