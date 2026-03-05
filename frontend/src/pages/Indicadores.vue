<template>
  <div class="powerbi-container">
    <iframe
      :src="reportUrl"
      width="100%"
      height="900"
      frameborder="0"
      allowFullScreen="true"
    ></iframe>
  </div>
</template>

<script>
export default {
  name: 'PowerBIEmbed',
  data() {
    return {
      reportUrl: 'https://app.powerbi.com/view?r=eyJrIjoiMzM1MzQ4ZGEtNjY5OS00MmZiLTg2MzktN2M2ODE3MTI3YzQ0IiwidCI6ImVkNDlmZTlhLTZlZWEtNDdlNi1iZjUyLWVlOWVjYjVkYTgwNyJ9&pageName=04d565125790ba341400'
    }
  }
}
</script>

<style scoped>
.powerbi-container {
  max-width: 100%;
  overflow: hidden;
  border: 1px solid #ccc;
  border-radius: 8px;
}

iframe {
  border: none;
}
</style>
