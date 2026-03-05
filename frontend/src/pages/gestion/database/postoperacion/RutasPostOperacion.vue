<template>
  <div class="construccion-container">
    <!-- Header -->
    <div class="construccion-header">
      <div class="construccion-icon">
        <i class="fas fa-hammer"></i>
      </div>
      <h1 class="construccion-title">{{ pageTitle }}</h1>
      <p class="construccion-subtitle">{{ pageDescription }}</p>
    </div>

    <!-- Content -->
    <div class="construccion-content">
      <div class="construccion-card">
        <div class="construccion-info">
          <i class="fas fa-tools construccion-tools-icon"></i>
          <h2>Página en Construcción</h2>
          <p>Esta funcionalidad se encuentra en desarrollo activo.</p>
          
          <div class="construccion-features">
            <h3>Características planificadas:</h3>
            <ul>
              <li><i class="fas fa-check"></i> {{ feature1 }}</li>
              <li><i class="fas fa-check"></i> {{ feature2 }}</li>
              <li><i class="fas fa-check"></i> {{ feature3 }}</li>
            </ul>
          </div>
          
          <div class="construccion-status">
            <span class="status-badge">
              <i class="fas fa-clock"></i>
              Próximamente
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

// Props específicos de cada página
const pageTitle = ref('Rutas de Directorios POST')
const pageDescription = ref('Configuración de rutas y directorios para post-operación')
const feature1 = ref('Gestión de rutas de red')
const feature2 = ref('Validación de directorios')
const feature3 = ref('Configuración por municipio')
</script>

<style scoped>
.construccion-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 2rem;
}

.construccion-header {
  text-align: center;
  margin-bottom: 3rem;
}

.construccion-icon {
  font-size: 4rem;
  color: #f6ad55;
  margin-bottom: 1rem;
  animation: bounce 2s infinite;
}

.construccion-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: #2d3748;
  margin: 0 0 0.5rem 0;
}

.construccion-subtitle {
  font-size: 1.1rem;
  color: #718096;
  margin: 0;
}

.construccion-content {
  display: flex;
  justify-content: center;
}

.construccion-card {
  background: white;
  border-radius: 16px;
  padding: 3rem;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  max-width: 600px;
  width: 100%;
}

.construccion-info {
  text-align: center;
}

.construccion-tools-icon {
  font-size: 3rem;
  color: #4299e1;
  margin-bottom: 1.5rem;
}

.construccion-info h2 {
  font-size: 1.8rem;
  color: #2d3748;
  margin-bottom: 1rem;
}

.construccion-info p {
  color: #718096;
  font-size: 1.1rem;
  margin-bottom: 2rem;
}

.construccion-features {
  text-align: left;
  margin-bottom: 2rem;
}

.construccion-features h3 {
  color: #4a5568;
  margin-bottom: 1rem;
}

.construccion-features ul {
  list-style: none;
  padding: 0;
}

.construccion-features li {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
  color: #718096;
}

.construccion-features li i {
  color: #48bb78;
}

.construccion-status {
  margin-top: 2rem;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: #faf089;
  color: #744210;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-weight: 500;
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-10px);
  }
  60% {
    transform: translateY(-5px);
  }
}

@media (max-width: 768px) {
  .construccion-container {
    padding: 1rem;
  }
  
  .construccion-card {
    padding: 2rem;
  }
  
  .construccion-title {
    font-size: 2rem;
  }
}
</style>
