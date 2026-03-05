<template>
  <div class="sigi-container">
    <div v-if="loading" class="loading">
      Cargando dashboard...
    </div>
    <iframe
      :src="reportUrl"
      width="100%"
      height="900"
      frameborder="0"
      allowFullScreen="true"
      @load="onIframeLoad"
      @error="onIframeError"
    ></iframe>
  </div>
</template>

<script>
export default {
  name: 'SIGIEmbed', // Cambié el nombre para reflejar el contenido real
  data() {
    return {
      reportUrl: 'https://sigi.igac.gov.co/portal/apps/experiencebuilder/experience/?id=81c41eb910b0448b8451636d3ea6d6c6',
      loading: true
    }
  },
  methods: {
    onIframeLoad() {
      this.loading = false;
      console.log('Iframe cargado exitosamente');
    },
    onIframeError() {
      this.loading = false;
      console.error('Error al cargar el iframe');
    }
  }
}
</script>

<style scoped>
.sigi-container { /* Corregí la inconsistencia de nombres */
  max-width: 100%;
  overflow: hidden;
  border: 1px solid #ccc;
  border-radius: 8px;
  position: relative;
}

.loading {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 10;
}

iframe {
  border: none;
}
</style>