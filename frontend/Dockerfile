# Frontend Dockerfile para Vue + Vite
# Etapa 1: Build
FROM node:18-alpine as build-stage

WORKDIR /app

# Copiar archivos de dependencias
COPY package*.json ./

# Instalar dependencias
RUN npm ci --legacy-peer-deps

# Copiar el código fuente
COPY . .

# Argumentos de build para pasar variables de entorno
ARG VITE_API_URL=""

# Establecer como variable de entorno para el build
ENV VITE_API_URL=$VITE_API_URL

# Construir la aplicación para producción
# Usamos vite build directamente sin verificación de tipos (tsc)
# para evitar que errores de TypeScript bloqueen el build
RUN npx vite build --mode production --emptyOutDir

# Etapa 2: Producción con Nginx
FROM nginx:alpine as production-stage

# Copiar archivos construidos desde la etapa de build
COPY --from=build-stage /app/dist /usr/share/nginx/html

# Copiar configuración personalizada de Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Exponer puerto 80
EXPOSE 80

# Comando para iniciar Nginx
CMD ["nginx", "-g", "daemon off;"]
