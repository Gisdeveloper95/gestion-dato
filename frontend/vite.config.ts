import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

// https://vitejs.dev/config/
export default ({ mode }) => {
  // Cargar variables de entorno según el modo (desarrollo, producción, etc.)
  const env = loadEnv(mode, process.cwd())

  // Definir la URL de la API basada en variables de entorno (vacío = paths relativos)
  const apiUrl = env.VITE_API_URL !== undefined ? env.VITE_API_URL : ''

  // Hosts permitidos (separados por coma en el .env)
  const allowedHosts = env.VITE_ALLOWED_HOSTS
    ? env.VITE_ALLOWED_HOSTS.split(',').map(h => h.trim())
    : ['localhost']
  
  return defineConfig({
    plugins: [vue()],
    resolve: {
      alias: {
        '@': resolve(__dirname, 'src'),
      },
    },
    optimizeDeps: {
      include: ['pdfjs-dist','xlsx']
    },
    build: {
        commonjsOptions: {
          include: [/xlsx/, /node_modules/],
        }
      },
    // Define variables de entorno que estarán disponibles en toda la aplicación
    define: {
      'import.meta.env.VITE_API_URL': JSON.stringify(apiUrl),
    },
    server: {
      host: env.VITE_SERVER_HOST || '0.0.0.0',
      port: env.VITE_SERVER_PORT ? parseInt(env.VITE_SERVER_PORT) : 5173,
      allowedHosts: allowedHosts,
      proxy: {
        '/api': {
          target: apiUrl,
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api/, ''),
        },
        '/preoperacion': {
          target: apiUrl,
          changeOrigin: true,
        },
        '/postoperacion': {
          target: apiUrl,
          changeOrigin: true,
        }
      },
    },
  })


  
}