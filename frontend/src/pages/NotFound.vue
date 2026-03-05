<template>
    <div class="not-found-page">
      <div class="container">
        <h1>Página no encontrada</h1>
        <p>Lo sentimos, la página que estás buscando no existe.</p>
        <router-link to="/" class="btn btn-primary">Volver al inicio</router-link>
      </div>
    </div>
  </template>
  
  <script setup lang="ts">
  // Aquí iría la lógica si fuera necesaria
  </script>
  
  <style scoped>
  .not-found-page {
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