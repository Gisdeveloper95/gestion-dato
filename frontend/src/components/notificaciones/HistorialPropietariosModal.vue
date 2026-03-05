<template>
  <div class="historial-modal-overlay" v-if="visible" @click="cerrar">
    <div class="historial-modal-container" @click.stop>
      <div class="historial-modal-header">
        <h3>📋 Historial de Propietarios</h3>
        <button class="close-button" @click="cerrar">
          <i class="material-icons">close</i>
        </button>
      </div>
      
      <div class="historial-modal-body">
        <div class="archivo-info" v-if="nombreArchivoActual">
          <div class="archivo-header">
            <h4>📁 {{ nombreArchivoActual }}</h4>
            <span class="archivo-id">ID: {{ idArchivoActual }}</span>
          </div>
          <div class="archivo-tipo" :class="tipoArchivo">
            {{ tipoArchivo === 'preoperacion' ? '🔵 Preoperación' : '🟢 Postoperación' }}
          </div>
        </div>
        
        <!-- ✅ CARGANDO -->
        <div v-if="cargando" class="loading-container">
          <div class="spinner"></div>
          <span>Consultando historial de propietarios...</span>
          <small>Esto puede tomar unos segundos</small>
        </div>
        
        <!-- ✅ SERVICIO NO DISPONIBLE (error 500) -->
        <div v-else-if="!servicioDisponible" class="service-unavailable">
          <i class="material-icons">cloud_off</i>
          <div class="unavailable-content">
            <h4>Servicio temporalmente no disponible</h4>
            <p>{{ mensajeServicio }}</p>
            <div class="unavailable-actions">
              <button @click="verificarYRecargar" class="btn-check">
                <i class="material-icons">refresh</i>
                Verificar nuevamente
              </button>
              <button @click="cerrar" class="btn-close">
                <i class="material-icons">close</i>
                Cerrar
              </button>
            </div>
          </div>
        </div>
        
        <!-- ✅ SIN DATOS PERO SERVICIO OK -->
        <div v-else-if="historial.length === 0" class="empty-state">
          <i class="material-icons">folder_open</i>
          <div class="empty-content">
            <h4>Sin historial registrado</h4>
            <p>Este archivo no tiene cambios de propietario registrados.</p>
            <div class="empty-suggestions">
              <small>💡 <strong>Posibles razones:</strong></small>
              <ul>
                <li>Es un archivo nuevo</li>
                <li>No se han registrado cambios de propietario</li>
                <li>La funcionalidad de historial está en desarrollo</li>
              </ul>
            </div>
            <button @click="intentarAlternativo" class="btn-alternative" v-if="!intentoAlternativo">
              <i class="material-icons">search</i>
              Buscar info alternativa
            </button>
          </div>
        </div>
        
        <!-- ✅ ALERTA DE INCONSISTENCIA -->
        <div v-if="hayInconsistencia" class="inconsistencia-alert">
          <i class="material-icons">warning</i>
          <div class="alert-content">
            <h4>⚠️ Inconsistencia detectada</h4>
            <p>
              <strong>Usuario en notificación:</strong> {{ usuarioNotificacionActual }}<br>
              <strong>Propietario en historial:</strong> {{ historial.find(h => !h.fecha_fin)?.propietario_nuevo }}
            </p>
            <small>Los datos pueden no estar sincronizados correctamente.</small>
          </div>
        </div>
        
        <!-- ✅ DATOS DISPONIBLES -->
        <div v-else class="historial-container">
          <div class="historial-summary">
            <span class="summary-text">
              📊 {{ historial.length }} registro{{ historial.length !== 1 ? 's' : '' }} de historial
            </span>
            <span v-if="metodoAlternativo" class="metodo-badge">
              ℹ️ Info obtenida por método alternativo
            </span>
          </div>
          
          <div class="table-wrapper">
            <table class="historial-table">
              <thead>
                <tr>
                  <th>👤 Propietario Anterior</th>
                  <th>👤 Propietario Actual</th>
                  <th>📅 Fecha Inicio</th>
                  <th>📅 Fecha Fin</th>
                  <th>⏱️ Duración</th>
                  <th>🔄 Estado</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(item, index) in historial" :key="index" :class="getRowClass(item, index)">
                  <!-- Propietario Anterior -->
                  <td>
                    <div v-if="item.propietario_anterior" class="propietario anterior">
                      <i class="material-icons">person_outline</i>
                      <span>{{ item.propietario_anterior }}</span>
                    </div>
                    <div v-else class="no-data">
                      <i class="material-icons">remove</i>
                      <span>Sin propietario anterior</span>
                    </div>
                  </td>
                  
                  <!-- Propietario Actual -->
                  <td>
                    <div class="propietario actual">
                      <i class="material-icons">person</i>
                      <span>{{ item.propietario_nuevo }}</span>
                      <span v-if="!item.fecha_fin" class="actual-badge">ACTUAL</span>
                    </div>
                  </td>
                  
                  <!-- Fecha Inicio -->
                  <td>
                    <div class="fecha-info">
                      <div class="fecha">{{ formatearFecha(item.fecha_inicio) }}</div>
                      <div class="hora">{{ formatearHora(item.fecha_inicio) }}</div>
                    </div>
                  </td>
                  
                  <!-- Fecha Fin -->
                  <td>
                    <div v-if="item.fecha_fin" class="fecha-info">
                      <div class="fecha">{{ formatearFecha(item.fecha_fin) }}</div>
                      <div class="hora">{{ formatearHora(item.fecha_fin) }}</div>
                    </div>
                    <div v-else class="estado-actual">
                      <i class="material-icons">schedule</i>
                      <span>En curso</span>
                    </div>
                  </td>
                  
                  <!-- Duración -->
                  <td>
                    <div class="duracion-info">
                      <span class="duracion-valor">{{ item.duracion || calcularDuracion(item) }}</span>
                    </div>
                  </td>
                  
                  <!-- Estado -->
                  <td>
                    <span :class="'estado-badge ' + getEstadoClass(item)">
                      <i class="material-icons">{{ getEstadoIcon(item) }}</i>
                      {{ getEstadoTexto(item) }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
      
      <div class="historial-modal-footer">
        <div class="footer-info" v-if="historial.length > 0">
          <small>
            ✨ Última actualización: {{ new Date().toLocaleString() }}
          </small>
        </div>
        <button class="btn-secondary" @click="cerrar">
          <i class="material-icons">close</i>
          Cerrar
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent, ref, computed, onMounted } from "vue";
import { historialPropietariosAPI } from "@/api/historialPropietarios";
import moment from "moment";

export default defineComponent({
  name: "HistorialPropietariosModal",
  setup() {
    const visible = ref(false);
    const cargando = ref(false);
    const tipoArchivo = ref("");
    const idArchivoActual = ref(null);
    const nombreArchivoActual = ref("");
    const historial = ref([]);
    
    // ✅ ESTADOS MEJORADOS
    const servicioDisponible = ref(true);
    const mensajeServicio = ref("");
    const intentoAlternativo = ref(false);
    const metodoAlternativo = ref(false);
    const usuarioNotificacionActual = ref(null); // NUEVO: usuario de la notificación
    
    // ✅ COMPUTED: Detectar inconsistencias
    const hayInconsistencia = computed(() => {
      if (!usuarioNotificacionActual.value || historial.value.length === 0) return false;
      
      const propietarioActual = historial.value.find(h => !h.fecha_fin);
      if (!propietarioActual) return false;
      
      return usuarioNotificacionActual.value !== propietarioActual.propietario_nuevo;
    });

    onMounted(() => {
      moment.locale('es');
    });

    // ✅ VERIFICAR SERVICIO Y RECARGAR
    const verificarYRecargar = async () => {
      try {
        cargando.value = true;
        console.log("🔄 Verificando disponibilidad del servicio...");
        
        const verificacion = await historialPropietariosAPI.verificarDisponibilidad();
        servicioDisponible.value = verificacion.disponible;
        mensajeServicio.value = verificacion.mensaje;
        
        if (verificacion.disponible) {
          console.log("✅ Servicio disponible, recargando historial...");
          await cargarHistorial();
        } else {
          console.log("❌ Servicio sigue no disponible");
        }
      } catch (err) {
        console.error("❌ Error verificando servicio:", err);
        servicioDisponible.value = false;
        mensajeServicio.value = "No se pudo verificar el estado del servicio.";
      } finally {
        cargando.value = false;
      }
    };

    // ✅ INTENTAR MÉTODO ALTERNATIVO
    const intentarAlternativo = async () => {
      if (!idArchivoActual.value) return;
      
      try {
        cargando.value = true;
        intentoAlternativo.value = true;
        
        console.log("🔄 Intentando método alternativo...");
        
        const resultado = await historialPropietariosAPI.obtenerInfoUsuarioActual(
          tipoArchivo.value, 
          idArchivoActual.value
        );
        
        if (resultado.length > 0) {
          historial.value = resultado;
          metodoAlternativo.value = true;
          console.log("✅ Método alternativo funcionó");
        } else {
          console.log("❌ Método alternativo no encontró datos");
        }
        
      } catch (err) {
        console.error("❌ Error en método alternativo:", err);
      } finally {
        cargando.value = false;
      }
    };

    // ✅ CARGAR HISTORIAL PRINCIPAL
    const cargarHistorial = async () => {
      if (!idArchivoActual.value) return;
      
      try {
        cargando.value = true;
        
        console.log(`🔄 Cargando historial para ${tipoArchivo.value}, ID: ${idArchivoActual.value}`);
        
        // ✅ USAR MÉTODO COMPLETO QUE MANEJA ERRORES
        const resultado = await historialPropietariosAPI.obtenerHistorialCompleto(
          tipoArchivo.value, 
          idArchivoActual.value
        );
        
        historial.value = resultado.sort((a, b) => {
          return new Date(b.fecha_inicio).getTime() - new Date(a.fecha_inicio).getTime();
        });
        
        // Detectar si se usó método alternativo
        metodoAlternativo.value = resultado.some(r => r.detalles?.metodo === 'info_archivo_directo');
        
        console.log(`✅ Historial cargado: ${historial.value.length} registros`);
        
      } catch (err) {
        console.error("❌ Error cargando historial:", err);
        
        // ✅ VERIFICAR SI ES PROBLEMA DEL SERVICIO
        const verificacion = await historialPropietariosAPI.verificarDisponibilidad();
        servicioDisponible.value = verificacion.disponible;
        mensajeServicio.value = verificacion.mensaje;
        
      } finally {
        cargando.value = false;
      }
    };
    
    // ✅ FUNCIONES DE FORMATO (sin cambios)
    const formatearFecha = (fechaStr) => {
      if (!fechaStr) return 'N/A';
      try {
        const fecha = moment(fechaStr);
        return fecha.isValid() ? fecha.format('DD/MM/YYYY') : 'Fecha inválida';
      } catch (error) {
        return 'Error de formato';
      }
    };

    const formatearHora = (fechaStr) => {
      if (!fechaStr) return '';
      try {
        const fecha = moment(fechaStr);
        return fecha.isValid() ? fecha.format('HH:mm:ss') : '';
      } catch (error) {
        return '';
      }
    };
    
    const calcularDuracion = (item) => {
      if (!item.fecha_inicio) return 'N/A';
      try {
        const inicio = moment(item.fecha_inicio);
        const fin = item.fecha_fin ? moment(item.fecha_fin) : moment();
        const dias = fin.diff(inicio, 'days');
        
        if (dias < 1) {
          const horas = fin.diff(inicio, 'hours');
          if (horas < 1) {
            const minutos = fin.diff(inicio, 'minutes');
            return minutos < 1 ? 'Menos de 1 min' : `${minutos} min`;
          }
          return `${horas}h`;
        }
        return `${dias}d`;
      } catch (error) {
        return 'Error';
      }
    };

    const getRowClass = (item, index) => {
      const classes = [];
      if (!item.fecha_fin) classes.push('propietario-actual');
      if (index % 2 === 0) classes.push('fila-par');
      return classes.join(' ');
    };

    const getEstadoClass = (item) => {
      return !item.fecha_fin ? 'estado-activo' : 'estado-finalizado';
    };

    const getEstadoIcon = (item) => {
      return !item.fecha_fin ? 'play_circle_filled' : 'check_circle';
    };

    const getEstadoTexto = (item) => {
      return !item.fecha_fin ? 'Actual' : 'Finalizado';
    };
    
    // ✅ MOSTRAR MODAL (mejorado con detección de inconsistencias)
    const mostrar = (tipo, idArchivo, nombreArchivo, usuarioNotificacion = null) => {
      console.log("🔄 Abriendo historial para:", { tipo, idArchivo, nombreArchivo, usuarioNotificacion });
      
      // Resetear estado
      historial.value = [];
      servicioDisponible.value = true;
      mensajeServicio.value = "";
      intentoAlternativo.value = false;
      metodoAlternativo.value = false;
      
      // Configurar datos
      tipoArchivo.value = tipo;
      idArchivoActual.value = idArchivo;
      nombreArchivoActual.value = nombreArchivo || `Archivo ${idArchivo}`;
      usuarioNotificacionActual.value = usuarioNotificacion; // NUEVO: guardar usuario de notificación
      
      // Mostrar modal y cargar
      visible.value = true;
      cargarHistorial();
    };
    
    const cerrar = () => {
      visible.value = false;
    };
    
    return {
      visible,
      cargando,
      tipoArchivo,
      idArchivoActual,
      nombreArchivoActual,
      historial,
      servicioDisponible,
      mensajeServicio,
      intentoAlternativo,
      metodoAlternativo,
      usuarioNotificacionActual,
      hayInconsistencia,
      cargarHistorial,
      verificarYRecargar,
      intentarAlternativo,
      formatearFecha,
      formatearHora,
      calcularDuracion,
      getRowClass,
      getEstadoClass,
      getEstadoIcon,
      getEstadoTexto,
      mostrar,
      cerrar
    };
  }
});
</script>

<style scoped>
/* BASE STYLES */
.historial-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  backdrop-filter: blur(3px);
}

.historial-modal-container {
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 15px 50px rgba(0, 0, 0, 0.3);
  width: 95%;
  max-width: 1200px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* HEADER */
.historial-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
  color: white;
}

.historial-modal-header h3 {
  margin: 0;
  font-size: 1.4rem;
  font-weight: 600;
}

.close-button {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  cursor: pointer;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 8px;
  transition: all 0.2s;
}

.close-button:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.05);
}

/* ARCHIVO INFO */
.archivo-info {
  margin-bottom: 1.5rem;
  padding: 1.25rem;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  border-radius: 8px;
  border-left: 4px solid #4f46e5;
}

.archivo-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.archivo-header h4 {
  margin: 0;
  color: #1e293b;
  font-size: 1.1rem;
  font-weight: 600;
}

.archivo-id {
  background-color: rgba(79, 70, 229, 0.1);
  color: #4f46e5;
  padding: 0.3rem 0.7rem;
  border-radius: 15px;
  font-size: 0.85rem;
  font-weight: 600;
}

.archivo-tipo {
  display: inline-block;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 600;
}

.archivo-tipo.preoperacion {
  background-color: rgba(59, 130, 246, 0.1);
  color: #2563eb;
  border: 1px solid rgba(59, 130, 246, 0.2);
}

.archivo-tipo.postoperacion {
  background-color: rgba(34, 197, 94, 0.1);
  color: #16a34a;
  border: 1px solid rgba(34, 197, 94, 0.2);
}

/* BODY */
.historial-modal-body {
  padding: 1.5rem;
  overflow-y: auto;
  flex: 1;
  min-height: 300px;
}

/* LOADING */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #f1f5f9;
  border-top: 4px solid #4f46e5;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1.5rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-container span {
  font-size: 1.1rem;
  color: #475569;
  margin-bottom: 0.5rem;
}

.loading-container small {
  color: #94a3b8;
  font-size: 0.9rem;
}

/* SERVICE UNAVAILABLE */
.service-unavailable {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
}

.service-unavailable i {
  font-size: 4rem;
  color: #f59e0b;
  margin-bottom: 1.5rem;
}

.unavailable-content h4 {
  margin: 0 0 1rem;
  font-size: 1.3rem;
  color: #1e293b;
}

.unavailable-content p {
  margin: 0 0 2rem;
  color: #64748b;
  line-height: 1.6;
  max-width: 400px;
}

.unavailable-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.btn-check, .btn-close {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.7rem 1.3rem;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-check {
  background-color: #4f46e5;
  color: white;
}

.btn-check:hover {
  background-color: #3730a3;
  transform: translateY(-1px);
}

.btn-close {
  background-color: #6b7280;
  color: white;
}

.btn-close:hover {
  background-color: #4b5563;
}

/* EMPTY STATE */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
}

.empty-state i {
  font-size: 4rem;
  color: #94a3b8;
  margin-bottom: 1.5rem;
}

.empty-content h4 {
  margin: 0 0 1rem;
  font-size: 1.3rem;
  color: #1e293b;
}

.empty-content p {
  margin: 0 0 1.5rem;
  color: #64748b;
  line-height: 1.6;
}

.empty-suggestions {
  text-align: left;
  background-color: #f8fafc;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  border-left: 3px solid #3b82f6;
}

.empty-suggestions small {
  color: #475569;
  font-weight: 600;
}

.empty-suggestions ul {
  margin: 0.5rem 0 0 1rem;
  color: #64748b;
  font-size: 0.9rem;
}

.btn-alternative {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.7rem 1.3rem;
  background-color: #0ea5e9;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-alternative:hover {
  background-color: #0284c7;
  transform: translateY(-1px);
}

/* ALERTA DE INCONSISTENCIA */
.inconsistencia-alert {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1rem;
  margin-bottom: 1.5rem;
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  border: 2px solid #f59e0b;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.2);
}

.inconsistencia-alert i {
  font-size: 2rem;
  color: #d97706;
  margin-top: 0.25rem;
}

.alert-content h4 {
  margin: 0 0 0.5rem;
  color: #92400e;
  font-size: 1rem;
}

.alert-content p {
  margin: 0 0 0.5rem;
  color: #78350f;
  line-height: 1.4;
}

.alert-content small {
  color: #a16207;
  font-style: italic;
}

/* HISTORIAL CONTAINER */
.historial-summary {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding: 1rem;
  background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
  border-left: 4px solid #10b981;
  border-radius: 6px;
}

.summary-text {
  color: #047857;
  font-weight: 600;
  font-size: 1rem;
}

.metodo-badge {
  background-color: rgba(59, 130, 246, 0.1);
  color: #2563eb;
  padding: 0.3rem 0.7rem;
  border-radius: 15px;
  font-size: 0.8rem;
  font-weight: 500;
}

/* TABLE */
.table-wrapper {
  overflow-x: auto;
  border-radius: 8px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.historial-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 800px;
  background-color: white;
}

.historial-table th,
.historial-table td {
  padding: 1rem 0.75rem;
  text-align: left;
  border-bottom: 1px solid #e2e8f0;
  vertical-align: top;
}

.historial-table th {
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  font-weight: 700;
  color: #374151;
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  position: sticky;
  top: 0;
  z-index: 1;
}

.historial-table tr:hover {
  background-color: #f8fafc;
}

.historial-table tr.propietario-actual {
  background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
  border-left: 4px solid #10b981;
}

.historial-table tr.propietario-actual:hover {
  background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
}

/* PROPIETARIOS */
.propietario {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  font-weight: 500;
  padding: 0.5rem 0.7rem;
  border-radius: 8px;
  position: relative;
}

.propietario.anterior {
  background-color: #f8fafc;
  color: #64748b;
  border: 1px solid #e2e8f0;
}

.propietario.actual {
  background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
  color: #1d4ed8;
  font-weight: 600;
  border: 1px solid #93c5fd;
}

.actual-badge {
  position: absolute;
  top: -6px;
  right: -6px;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  font-size: 0.6rem;
  padding: 0.2rem 0.4rem;
  border-radius: 8px;
  font-weight: 700;
  letter-spacing: 0.3px;
  box-shadow: 0 2px 6px rgba(16, 185, 129, 0.4);
}

.no-data {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #94a3b8;
  font-style: italic;
  padding: 0.5rem 0.7rem;
}

/* FECHAS */
.fecha-info {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.fecha-info .fecha {
  font-weight: 600;
  color: #374151;
  font-size: 0.9rem;
}

.fecha-info .hora {
  font-size: 0.8rem;
  color: #6b7280;
  font-family: 'Courier New', monospace;
}

.estado-actual {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
  color: #047857;
  padding: 0.5rem 0.7rem;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.85rem;
  border: 1px solid #a7f3d0;
}

/* DURACIÓN */
.duracion-valor {
  display: inline-block;
  padding: 0.4rem 0.7rem;
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  color: #92400e;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.85rem;
  border: 1px solid #f9cc33;
}

/* ESTADOS */
.estado-badge {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.5rem 0.8rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.estado-activo {
  background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%);
  color: #166534;
  border: 1px solid #86efac;
}

.estado-finalizado {
  background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
  color: #475569;
  border: 1px solid #cbd5e1;
}

/* FOOTER */
.historial-modal-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.25rem 1.5rem;
  border-top: 1px solid #e2e8f0;
  background-color: #f8fafc;
}

.footer-info small {
  color: #64748b;
  font-style: italic;
}

.btn-secondary {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.7rem 1.3rem;
  background-color: #6b7280;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-secondary:hover {
  background-color: #4b5563;
  transform: translateY(-1px);
}

/* RESPONSIVE */
@media (max-width: 768px) {
  .historial-modal-container {
    width: 98%;
    margin: 1rem;
  }
  
  .archivo-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .historial-summary {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .unavailable-actions {
    flex-direction: column;
    width: 100%;
  }
  
  .btn-check, .btn-close, .btn-alternative {
    width: 100%;
    justify-content: center;
  }
}
</style>