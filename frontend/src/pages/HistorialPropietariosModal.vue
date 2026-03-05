<template>
  <div class="modal fade" id="historialPropietariosModal" tabindex="-1" role="dialog" aria-labelledby="historialModalLabel" aria-hidden="true">
    <div class="modal-dialog modal-lg" role="document">
      <div class="modal-content">
        <div class="modal-header bg-primary text-white">
          <h5 class="modal-title" id="historialModalLabel">
            <i class="fas fa-history"></i> Historial de Propietarios
          </h5>
          <button type="button" class="close text-white" data-dismiss="modal" aria-label="Close">
            <span aria-hidden="true">&times;</span>
          </button>
        </div>
        <div class="modal-body">
          <div v-if="cargando" class="text-center p-4">
            <div class="spinner-border text-primary" role="status">
              <span class="sr-only">Cargando...</span>
            </div>
            <p class="mt-2">Cargando historial...</p>
          </div>
          
          <div v-else-if="error" class="alert alert-danger">
            <i class="fas fa-exclamation-circle"></i> {{ error }}
          </div>
          
          <div v-else-if="historialPropietarios.length === 0" class="alert alert-info">
            <i class="fas fa-info-circle"></i> No hay historial de propietarios para este archivo.
          </div>
          
          <div v-else>
            <div class="mb-3">
              <strong>Archivo:</strong> {{ nombreArchivo }}
            </div>
            
            <div class="table-responsive">
              <table class="table table-striped table-bordered">
                <thead class="thead-light">
                  <tr>
                    <th>Propietario</th>
                    <th>Desde</th>
                    <th>Hasta</th>
                    <th>Duración</th>
                    <th>Estado</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(item, index) in historialPropietarios" :key="index" :class="{'table-success': item.estado === 'Propietario actual'}">
                    <td>
                      <i class="fas fa-user"></i> {{ item.propietario_nuevo }}
                      <span v-if="item.estado === 'Propietario actual'" class="badge badge-success ml-1">Actual</span>
                    </td>
                    <td>{{ formatearFecha(item.fecha_inicio) }}</td>
                    <td>{{ item.fecha_fin ? formatearFecha(item.fecha_fin) : 'Presente' }}</td>
                    <td>{{ item.duracion }}</td>
                    <td>
                      <span :class="getEstadoClass(item.estado)">
                        {{ item.estado }}
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-dismiss="modal">Cerrar</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import moment from 'moment';

export default {
  name: 'HistorialPropietariosModal',
  props: {
    tipoArchivo: {
      type: String,
      required: true
    },
    idArchivo: {
      type: [Number, String],
      required: true
    },
    nombreArchivo: {
      type: String,
      default: 'Sin nombre'
    }
  },
  data() {
    return {
      historialPropietarios: [],
      cargando: false,
      error: null
    };
  },
  methods: {
    async cargarHistorial() {
      this.cargando = true;
      this.error = null;
      
      try {
        const response = await axios.get('/api/postoperacion/historial-propietarios/por-archivo/', {
          params: {
            tipo: this.tipoArchivo,
            id_archivo: this.idArchivo
          }
        });
        
        this.historialPropietarios = response.data;
      } catch (error) {
        console.error('Error al cargar historial:', error);
        this.error = 'No se pudo cargar el historial de propietarios. Intente nuevamente.';
      } finally {
        this.cargando = false;
      }
    },
    formatearFecha(fecha) {
      return moment(fecha).format('DD/MM/YYYY HH:mm:ss');
    },
    getEstadoClass(estado) {
      return {
        'badge badge-success': estado === 'Propietario actual',
        'badge badge-secondary': estado === 'Propietario anterior'
      };
    },
    mostrar() {
      this.cargarHistorial();
      $('#historialPropietariosModal').modal('show');
    },
    ocultar() {
      $('#historialPropietariosModal').modal('hide');
    }
  }
};
</script>

<style scoped>
.badge {
  font-size: 85%;
}
</style>