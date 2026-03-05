<template>
  <footer class="app-footer">
    <div class="container">
      <div class="footer-content">
        <div class="footer-info">
          <div class="footer-logo">
            <img src="/assets/logo.ico" alt="Logo" class="logo" />
            <span class="title">Sistema de Gestión de Datos</span>
          </div>
          <p class="description">
            Plataforma para la gestión y seguimiento de información catastral y territorial.
          </p>
        </div>
        
        <div class="footer-links">
          <div class="links-column">
            <h3>Navegación</h3>
            <ul>
              <li><router-link to="/">Inicio</router-link></li>
              <li><router-link to="/disposicion-informacion">Disposición de Información</router-link></li>
              <li><router-link to="/estado-producto">Estado del Producto</router-link></li>
              <li><router-link to="/indicadores">Indicadores</router-link></li>
              <li><router-link to="/geoportal">Geoportal</router-link></li>
            </ul>
          </div>
          
          <div class="links-column">
            <h3>Recursos</h3>
            <ul>
              <li><a href="#" target="_blank">Manual de Usuario</a></li>
              <li><a href="#" target="_blank">Guía Técnica</a></li>
              <li><a href="#" target="_blank">Preguntas Frecuentes</a></li>
              <li><a href="#" target="_blank">Soporte Técnico</a></li>
            </ul>
          </div>
          
          <div class="links-column">
            <h3>Contacto</h3>
            <ul class="contact-list">
              <li>
                <i class="material-icons">email</i>
                <a href="mailto:elizabeth.eraso@igac.gov.co">elizabeth.eraso@igac.gov.co</a>
                
              </li>
              <li>
                <i class="material-icons">email</i>
                <a href="mailto:felipe.vargas@igac.gov.co">felipe.vargas@igac.gov.co</a>
                
              </li>
                            <li>
                <i class="material-icons">email</i>
                <a href="mailto:felipe.vargas@igac.gov.co">andres.osorio@igac.gov.co</a>
                
              </li>
              <li>
                <i class="material-icons">phone</i>
                <span>(+57) 123 456 7890</span>
              </li>
              <li>
                <i class="material-icons">location_on</i>
                <span>Bogotá, Colombia</span>
                
              </li>
                <li>
              <span>Carrera 30 # 48-51</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
      
      <div class="footer-bottom">
        <p class="copyright">
          © {{ currentYear }} Sistema de Gestión de Datos. Todos los derechos reservados.
        </p>
        <div class="social-links">
          <a href="#" target="_blank" aria-label="Facebook">
            <i class="material-icons">facebook</i>
          </a>
          <a href="#" target="_blank" aria-label="Twitter">
            <i class="material-icons">twitter</i>
          </a>
          <a href="#" target="_blank" aria-label="LinkedIn">
            <i class="material-icons">linkedin</i>
          </a>
          <a href="#" target="_blank" aria-label="YouTube">
            <i class="material-icons">youtube_activity</i>
          </a>
        </div>
      </div>
    </div>
  </footer>
</template>

<script lang="ts">
import { defineComponent, computed } from 'vue'

export default defineComponent({
  name: 'AppFooter',
  
  setup() {
    // Obtener el año actual para el copyright
    const currentYear = computed(() => new Date().getFullYear())
    
    return {
      currentYear
    }
  }
})
</script>

<style scoped>
.app-footer {
  background-color: #343a40;
  color: rgba(255, 255, 255, 0.8);
  padding: 3rem 0 1rem;
  margin-top: 2rem;
}

.container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

.footer-content {
  display: flex;
  flex-wrap: wrap;
  gap: 2rem;
  margin-bottom: 2rem;
}

.footer-info {
  flex: 1;
  min-width: 250px;
}

.footer-logo {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.logo {
  width: 40px;
  height: 40px;
  object-fit: contain;
}

.title {
  font-size: 1.2rem;
  font-weight: 600;
  color: white;
}

.description {
  font-size: 0.9rem;
  line-height: 1.5;
  margin: 0;
}

.footer-links {
  display: flex;
  flex-wrap: wrap;
  gap: 2rem;
  flex: 2;
}

.links-column {
  flex: 1;
  min-width: 160px;
}

.links-column h3 {
  color: white;
  font-size: 1.1rem;
  margin: 0 0 1rem;
}

.links-column ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.links-column li {
  margin-bottom: 0.5rem;
}

.links-column a {
  color: rgba(255, 255, 255, 0.7);
  text-decoration: none;
  transition: color 0.2s;
}

.links-column a:hover {
  color: white;
}

.contact-list li {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.contact-list i {
  font-size: 1.2rem;
}

.footer-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.copyright {
  font-size: 0.9rem;
  margin: 0;
}

.social-links {
  display: flex;
  gap: 1rem;
}

.social-links a {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background-color: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.7);
  text-decoration: none;
  transition: background-color 0.2s, color 0.2s;
}

.social-links a:hover {
  background-color: rgba(255, 255, 255, 0.2);
  color: white;
}

.social-links i {
  font-size: 1.2rem;
}

@media (max-width: 768px) {
  .footer-content {
    flex-direction: column;
  }
  
  .footer-bottom {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }
  
  .social-links {
    justify-content: center;
  }
}
</style>