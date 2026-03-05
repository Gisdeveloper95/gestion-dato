import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './routes'
import './styles/main.css'

// Crear la instancia de Pinia (para el manejo de estado)
const pinia = createPinia()

// Crear la aplicación Vue
const app = createApp(App)

// Usar plugins
app.use(pinia)
app.use(router)

// Montar la aplicación
app.mount('#app')