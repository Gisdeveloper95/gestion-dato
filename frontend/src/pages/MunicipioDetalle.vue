<template>
    <div class="under-construction">
      <div class="container">
        <h1>Página en construcción</h1>
        <p>Esta sección está actualmente en desarrollo. Disculpe las molestias.</p>
        <router-link to="/" class="btn">Volver al inicio</router-link>
      </div>
    </div>
  </template>
  
  <script setup lang="ts">
  // Aquí iría la lógica si fuera necesaria
  </script>
  
  <style scoped>
  .under-construction {
    text-align: center;
    padding: 3rem 0;
  }
  
  h1 {
    font-size: 2rem;
    margin-bottom: 1rem;
  }
  
  p {
    margin-bottom: 2rem;
  }
  </style>