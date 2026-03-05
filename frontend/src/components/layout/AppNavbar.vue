<template>
  <nav class="app-navbar">
    <div class="container">
      <div class="navbar-content">
        <!-- Botón para móvil -->
        <button class="mobile-menu-button" @click="toggleMobileMenu">
          <i class="material-icons">{{ mobileMenuOpen ? 'close' : 'menu' }}</i>
        </button>
        
        <!-- Enlaces de navegación -->
        <ul class="nav-links" :class="{ 'mobile-open': mobileMenuOpen }">
          <li v-for="link in navLinks" :key="link.path">
            <router-link :to="link.path" @click="closeMobileMenu">
              <i v-if="link.icon" class="material-icons">{{ link.icon }}</i>
              {{ link.name }}
            </router-link>
          </li>
          
          <!-- 🆕 ENLACE DE GESTIÓN CON LÓGICA CORREGIDA -->
          <li v-if="esSuperAdministrador">
            <router-link to="/gestion-informacion" @click="closeMobileMenu">
              <i class="material-icons">admin_panel_settings</i>
              Gestión de Información
            </router-link>
          </li>
        </ul>
        
        <!-- Indicador de notificaciones -->
        <div class="right-section">
          <div class="notification-indicator" @click="openNotificaciones">
            <i class="material-icons">notifications</i>
            <span v-if="contadorNotificacionesHoy > 0" class="notification-count">
              {{ contadorNotificacionesHoy >999 ? '999+' : contadorNotificacionesHoy }}
            </span>
          </div>
          
          <!-- Perfil de usuario (solo visible si está autenticado) -->
          <div v-if="isAuthenticated" class="user-profile" @click="toggleUserMenu">
            <div class="profile-avatar">
              <span>{{ userInitials }}</span>
            </div>
            <div class="profile-info">
              <span class="profile-name">{{ userName }}</span>
              <!-- 🆕 MOSTRAR ROL DEL USUARIO -->
              <span class="profile-role">{{ userRoleText }}</span>
            </div>
            <i class="material-icons">arrow_drop_down</i>
            
            <!-- Menú desplegable de usuario -->
            <div class="user-menu" v-if="userMenuOpen">
              <ul>
                <li>
                  <router-link to="/perfil">
                    <i class="material-icons">person</i>
                    Mi Perfil
                  </router-link>
                </li>
                <!-- 🆕 ENLACE ADICIONAL PARA ADMIN EN EL MENÚ -->
              <li v-if="esSuperAdministrador">
                <router-link to="/gestion-informacion">
                  <i class="material-icons">admin_panel_settings</i>
                  Panel de Administración
                </router-link>
              </li>
                <li>
                  <button @click="handleLogout">
                    <i class="material-icons">exit_to_app</i>
                    Cerrar Sesión
                  </button>
                </li>
              </ul>
            </div>
          </div>
          
          <!-- Botón de login (solo visible si no está autenticado) -->
          <router-link v-else to="/login" class="login-button">
            <i class="material-icons">account_circle</i>
            Iniciar Sesión
          </router-link>
        </div>
      </div>
    </div>
  </nav>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted, onBeforeUnmount,watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { useNotificacionesStore } from '@/store/notificaciones'
import { startOfDay, endOfDay, isWithinInterval, parseISO, format } from 'date-fns'

export default defineComponent({
  name: 'AppNavbar',
  
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
    const notificacionesStore = useNotificacionesStore()

    // Estados reactivos
    const mobileMenuOpen = ref(false)
    const userMenuOpen = ref(false)
    // 🆕 COMPUTED PARA AUTENTICACIÓN Y ROLES - MEJORADO
    const isAuthenticated = computed(() => authStore.isAuthenticated)
    
    // 🎯 COMPUTED MEJORADO PARA ADMIN
    const esSuperAdministrador = computed(() => {
  const resultado = authStore.isSuperAdmin;  // ✅ CORRECTO - solo super admins
  
  if (resultado || authStore.user) {
    console.log('🔍 [NavBar] Verificación SUPER admin:', {
      resultado,
      username: authStore.user?.username,
      rol_tipo: authStore.user?.rol_tipo,
      isSuperAdmin: authStore.user?.isSuperAdmin,
      isSuperUser: authStore.user?.isSuperUser,
      groups: authStore.user?.groups
    });
  }
  
  return resultado;
});
    
    const esProfesional = computed(() => authStore.isProfesional);
    
    // Computed: Contador de notificaciones HOY
    const contadorNotificacionesHoy = computed(() => {
      const ahora = new Date()
      const hace24Horas = new Date(ahora.getTime() - 24 * 60 * 60 * 1000)
      
      const clavesMesRelevantes = []
      const mesActual = format(ahora, 'yyyy-MM')
      clavesMesRelevantes.push(mesActual)
      
      // Agregar mes anterior si aplica (para cubrir notificaciones cerca de medianoche)
      const mesAnterior = new Date(ahora)
      mesAnterior.setMonth(ahora.getMonth() - 1)
      clavesMesRelevantes.push(format(mesAnterior, 'yyyy-MM'))

      let total = 0
      
      clavesMesRelevantes.forEach(clave => {
        const cacheMes = notificacionesStore.cachePorMes[clave]
        
        if (cacheMes) {
          const notificaciones = [
            ...cacheMes.preoperacion.data,
            ...cacheMes.postoperacion.data
          ]
          
          total += notificaciones.filter(n => 
            n.fecha_cambio && 
            parseISO(n.fecha_cambio) >= hace24Horas
          ).length
        }
      })
      
      return total
    })

    // Computed: Datos usuario
    const userName = computed(() => {
      if (!authStore.user) return ''
      return authStore.user.firstName || authStore.user.username
    })

    const userInitials = computed(() => {
      if (!authStore.user) return ''
      if (authStore.user.firstName && authStore.user.lastName) {
        return `${authStore.user.firstName[0]}${authStore.user.lastName[0]}`
      }
      return authStore.user.username[0].toUpperCase()
    })

    // 🆕 TEXTO DEL ROL DE USUARIO
  const userRoleText = computed(() => {
    if (!authStore.user) return '';
    
    // Usar los computed del authStore que ya tienen la lógica correcta
    if (authStore.isSuperAdmin) return 'Super Administrador';
    if (authStore.isAdmin) return 'Administrador';
    if (authStore.isProfesional) return 'Profesional';
    return 'Usuario';
  });



    // Nav links
    const navLinks = [
      { name: 'Inicio', path: '/', icon: 'home' },
      { name: 'Disposición Información', path: '/disposicion-informacion', icon: 'description' },
      { name: 'Indicadores', path: '/indicadores', icon: 'pie_chart' },
      { name: 'Geoportal', path: '/geoportal', icon: 'map' }
    ]

    // Métodos: Menús
    const toggleMobileMenu = () => {
      mobileMenuOpen.value = !mobileMenuOpen.value
      if (mobileMenuOpen.value) userMenuOpen.value = false
    }

    const closeMobileMenu = () => {
      mobileMenuOpen.value = false
    }

    const toggleUserMenu = () => {
      userMenuOpen.value = !userMenuOpen.value
    }

    // Métodos: Notificaciones
    const openNotificaciones = () => {
      router.push('/notificaciones')
    }

    // Métodos: Logout
    const handleLogout = async () => {
      await authStore.logout()
      router.push('/')
    }

    // Cerrar menús al hacer clic fuera
    const handleClickOutside = (event: MouseEvent) => {
      const userProfileElement = document.querySelector('.user-profile')
      if (userMenuOpen.value && userProfileElement && !userProfileElement.contains(event.target as Node)) {
        userMenuOpen.value = false
      }
    }

    watch(
      () => authStore.isAdmin, // Observar cambios en isAdmin
      (newVal) => {
        if (newVal) {
          // Forzar actualización del componente
          mobileMenuOpen.value = !mobileMenuOpen.value;
          mobileMenuOpen.value = !mobileMenuOpen.value; // Truco para re-renderizar
        }
      }
    );

    // Event listeners
    onMounted(() => {
      document.addEventListener('click', handleClickOutside)
      
      // 🆕 LOG PARA DEBUG AL MONTAR
      console.log('🚀 AppNavbar montado. Estado de autenticación:', {
        isAuthenticated: authStore.isAuthenticated,
        user: authStore.user,
        rol_tipo: authStore.user?.rol_tipo,
        esSuperAdministrador: esSuperAdministrador.value 
      });
    })


    onBeforeUnmount(() => {
      document.removeEventListener('click', handleClickOutside)
    })

    return {
      mobileMenuOpen,
      userMenuOpen,
      navLinks,
      isAuthenticated,
      esSuperAdministrador,      // ⭐ ESTE ES EL COMPUTED CRÍTICO
      esProfesional,       // 🆕 NUEVO
      userName,
      userInitials,
      userRoleText,        // 🆕 NUEVO
      contadorNotificacionesHoy,
      toggleMobileMenu,
      closeMobileMenu,
      toggleUserMenu,
      openNotificaciones,
      handleLogout,
      watch,
    }
  }
})
</script>

<style scoped>
.app-navbar {
  background-color: #343a40;
  color: white;
  padding: 0;
}

.container {
  width: 100%;
  max-width: 1400px; /* 🆕 Aumentado de 1200px para dar más espacio */
  margin: 0 auto;
  padding: 0 1rem;
}

.navbar-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: relative;
}

.mobile-menu-button {
  display: none;
  background: none;
  border: none;
  color: white;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0.5rem;
}

.nav-links {
  display: flex;
  list-style: none;
  margin: 0;
  padding: 0;
}

.nav-links li {
  margin: 0;
}

/* 🆕 ESTILOS MEJORADOS PARA LOS ENLACES */
.nav-links a {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  padding: 1rem 2rem; /* 🆕 Aumentado de 1.5rem a 2rem el padding horizontal */
  transition: background-color 0.3s, color 0.3s;
  white-space: nowrap; /* 🆕 Evita que el texto se parta en múltiples líneas */
  min-width: max-content; /* 🆕 Asegura que el botón sea lo suficientemente ancho */
  text-align: center; /* 🆕 Centra el texto */
  justify-content: center; /* 🆕 Centra el contenido del flex */
  font-size: 0.95rem; /* 🆕 Tamaño de fuente ligeramente más pequeño para ahorrar espacio */
  font-weight: 500; /* 🆕 Peso de fuente medio para mejor legibilidad */
}

.nav-links a:hover,
.nav-links a.router-link-active {
  background-color: rgba(255, 255, 255, 0.1);
  color: white;
  transform: translateY(-1px); /* 🆕 Efecto sutil de elevación */
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); /* 🆕 Sombra sutil */
}

.nav-links i {
  font-size: 1.2rem;
  flex-shrink: 0; /* 🆕 Evita que los iconos se compriman */
}

.right-section {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.notification-indicator {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  padding: 0.5rem;
}

.notification-indicator i {
  font-size: 1.5rem;
  color: rgba(255, 255, 255, 0.8);
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  position: relative;
}

.user-profile:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.profile-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background-color: #007bff;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
}

/* 🆕 ESTILOS PARA INFO DE PERFIL MEJORADA */
.profile-info {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.profile-name {
  color: white;
  font-weight: 500;
  line-height: 1.2;
}

.profile-role {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.75rem;
  line-height: 1;
}

.user-menu {
  position: absolute;
  top: 100%;
  right: 0;
  background-color: white;
  border-radius: 4px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  min-width: 200px;
  z-index: 1000;
  margin-top: 0.5rem;
}

.user-menu ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.user-menu li {
  margin: 0;
}

.user-menu a,
.user-menu button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  color: #495057;
  text-decoration: none;
  width: 100%;
  text-align: left;
  background: none;
  border: none;
  font-size: 0.95rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.user-menu a:hover,
.user-menu button:hover {
  background-color: #f8f9fa;
  color: #007bff;
}

.user-menu i {
  font-size: 1.2rem;
}

.login-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  background-color: #28a745;
  color: white;
  text-decoration: none;
  font-size: 0.9rem;
  white-space: nowrap;
}

.login-button:hover {
  background-color: #218838;
  text-decoration: none;
}

/* 🆕 MEJORAS PARA RESPONSIVE */
@media (max-width: 1200px) {
  .container {
    max-width: 1140px;
  }
  
  .nav-links a {
    padding: 1rem 1.5rem; /* 🆕 Padding reducido en pantallas medianas */
    font-size: 0.9rem; /* 🆕 Fuente ligeramente más pequeña */
  }
}

@media (max-width: 992px) {
  .profile-info {
    display: none;
  }
  
  .nav-links a {
    padding: 1rem 1.2rem; /* 🆕 Padding aún más reducido */
    font-size: 0.85rem;
  }
}

@media (max-width: 768px) {
  .mobile-menu-button {
    display: block;
  }
  
  .nav-links {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background-color: #343a40;
    flex-direction: column;
    max-height: 0;
    overflow: hidden;
    transition: max-height 0.3s ease-out;
    z-index: 1000;
  }
  
  .nav-links.mobile-open {
    max-height: 500px;
  }
  
  /* 🆕 ESTILOS MEJORADOS PARA MÓVIL */
  .nav-links a {
    padding: 1.25rem 1rem; /* 🆕 Más padding vertical en móvil */
    justify-content: flex-start; /* 🆕 Alineación a la izquierda en móvil */
    border-bottom: 1px solid rgba(255, 255, 255, 0.1); /* 🆕 Separador sutil */
    font-size: 1rem; /* 🆕 Fuente normal en móvil */
  }
  
  .nav-links li:last-child a {
    border-bottom: none; /* 🆕 Sin borde en el último elemento */
  }
}

.notification-indicator {
  position: relative;
  cursor: pointer;
  padding: 8px;
  margin-right: 15px;
}

.notification-count {
  position: absolute;
  top: -5px;
  right: -5px;
  background: #ff4757;
  color: white;
  border-radius: 50%;
  min-width: 20px;
  height: 20px;
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2px;
  font-weight: bold;
  box-shadow: 0 2px 5px rgba(0,0,0,0.2);
}
</style>