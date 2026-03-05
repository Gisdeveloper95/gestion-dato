<template>
  <div class="concepto-form-container">
    <h2 class="form-title">{{ isEditing ? 'Editar Concepto' : 'Crear Nuevo Concepto' }}</h2>
    
    <!-- Filtros jerárquicos -->
    <div class="filtros-section">
      <div class="row">
        <div class="col-md-6">
          <div class="form-group">
            <label for="departamento" class="required">Departamento:</label>
            <select
              id="departamento"
              v-model="filtros.departamento"
              @change="cargarMunicipios"
              class="form-control"
              required
            >
              <option value="">Seleccione un departamento</option>
              <option
                v-for="depto in departamentos"
                :key="depto.cod_depto"
                :value="String(depto.cod_depto)"
              >
                {{ depto.nom_depto }}
              </option>
            </select>
          </div>
        </div>
        
        <div class="col-md-6">
          <div class="form-group">
            <label for="municipio" class="required">Municipio:</label>
            <select
              id="municipio"
              v-model="filtros.municipio"
              @change="cargarInsumos"
              class="form-control"
              :disabled="!filtros.departamento || municipiosCargando"
              required
            >
              <option value="">Seleccione un municipio</option>
              <option
                v-for="municipio in municipios"
                :key="municipio.cod_municipio"
                :value="String(municipio.cod_municipio)"
              >
                {{ municipio.nom_municipio }}
              </option>
            </select>
            <div v-if="municipiosCargando" class="mt-2 text-info">
              <small>Cargando municipios...</small>
            </div>
          </div>
        </div>
      </div>
      
      <div class="row">
        <div class="col-md-6">
          <div class="form-group">
            <label for="insumo" class="required">Insumo:</label>
            <select
              id="insumo"
              v-model="filtros.insumo"
              @change="cargarClasificaciones"
              class="form-control"
              :disabled="!filtros.municipio || insumosCargando"
              required
            >
              <option value="">Seleccione un insumo</option>
              <option
                v-for="insumo in insumosConCategoria"
                :key="insumo.cod_insumo"
                :value="String(insumo.cod_insumo)"
              >
                {{ insumo.cod_insumo }} - {{ insumo.tipo_insumo }} ({{ insumo.categoria_nombre }})
              </option>
            </select>
            <div v-if="insumosCargando" class="mt-2 text-info">
              <small>Cargando insumos...</small>
            </div>
          </div>
        </div>
        
        <div class="col-md-6">
          <div class="form-group">
            <label for="clasificacion" class="required">Clasificación:</label>
            <select
              id="clasificacion"
              v-model="filtros.clasificacion"
              @change="cargarDetalles"
              class="form-control"
              :disabled="!filtros.insumo || clasificacionesCargando"
              required
            >
              <option value="">Seleccione una clasificación</option>
              <option
                v-for="clasificacion in clasificaciones"
                :key="clasificacion.cod_clasificacion"
                :value="String(clasificacion.cod_clasificacion)"
              >
                {{ clasificacion.nombre }}
              </option>
            </select>
            <div v-if="clasificacionesCargando" class="mt-2 text-info">
              <small>Cargando clasificaciones...</small>
            </div>
          </div>
        </div>
      </div>
      
      <div class="row">
        <div class="col-md-12">
          <div class="form-group">
            <label for="detalle" class="required">Detalle:</label>
            <select
              id="detalle"
              v-model="formData.cod_detalle"
              class="form-control"
              :disabled="!filtros.clasificacion || detallesCargando"
              required
            >
              <option value="">Seleccione un detalle</option>
              <!-- MODIFICADO: Agregar información de zona en el dropdown y convertir value a String -->
              <option
                v-for="detalle in detalles"
                :key="detalle.cod_detalle"
                :value="String(detalle.cod_detalle)"
              >
                {{ detalle.cod_detalle }} - {{ detalle.estado }} - {{ formatFecha(detalle.fecha_entrega) }} - {{ detalle.formato_tipo }}{{ detalle.zona ? ' - ' + detalle.zona : '' }}{{ detalle.nombre_centro_poblado ? ' - ' + detalle.nombre_centro_poblado : '' }}
              </option>
            </select>
            <div v-if="detallesCargando" class="mt-2 text-info">
              <small>Cargando detalles...</small>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Formulario principal -->
    <form @submit.prevent="guardarConcepto" class="form-main">
      <!-- Campo oculto para cod_concepto -->
      <input type="hidden" v-model="formData.cod_concepto" />
      
      <div class="row">
        <div class="col-md-12">
          <div class="form-group">
            <label for="concepto" class="required">Concepto:</label>
            <input 
              type="text" 
              id="concepto" 
              v-model="formData.concepto" 
              class="form-control" 
              placeholder="Descripción del concepto"
              required
            />
          </div>
        </div>
      </div>
      
      <div class="row">
        <div class="col-md-6">
          <div class="form-group">
            <label for="fecha" class="required">Fecha:</label>
            <input 
              type="date" 
              id="fecha" 
              v-model="formData.fecha" 
              :max="fechaMaxima"
              class="form-control"
              required
            />
          </div>
        </div>
        
        <div class="col-md-6">
          <div class="form-group">
            <label for="evaluacion">Evaluación:</label>
            <input 
              type="text" 
              id="evaluacion" 
              v-model="formData.evaluacion" 
              class="form-control" 
              placeholder="Ingrese la evaluación"
            />
          </div>
        </div>
      </div>
      
      <div class="row">
        <div class="col-md-12">
          <div class="form-group">
            <label for="detalle_concepto" class="required">Detalle del Concepto:</label>
            <textarea 
              id="detalle_concepto" 
              v-model="formData.detalle_concepto" 
              class="form-control" 
              rows="5"
              placeholder="Detalle completo del concepto..."
              required
            ></textarea>
          </div>
        </div>
      </div>
      
      <!-- Nuevo campo PDF -->
      <div class="row">
        <div class="col-md-12">
          <div class="form-group">
            <label for="pdf">Información de PDF:</label>
            <textarea 
              id="pdf" 
              v-model="formData.pdf" 
              class="form-control" 
              rows="3"
              placeholder="Ingrese información sobre el PDF relacionado..."
              maxlength="500"
            ></textarea>
            <small class="form-text text-muted">
              Máximo 500 caracteres. Caracteres restantes: {{ 500 - (formData.pdf?.length || 0) }}
            </small>
          </div>
        </div>
      </div>
      
      <div class="row">
        <div class="col-md-12">
          <div class="form-group">
            <label for="observacion">Observaciones:</label>
            <textarea 
              id="observacion" 
              v-model="formData.observacion" 
              class="form-control" 
              rows="3"
              placeholder="Observaciones adicionales..."
            ></textarea>
          </div>
        </div>
      </div>
      
      <div class="form-buttons">
        <button type="button" class="btn btn-secondary" @click="cancelar">Cancelar</button>
        <button type="submit" class="btn btn-primary" :disabled="!isFormValid">Guardar Concepto</button>
      </div>
    </form>
    
    <!-- Mensajes de error/éxito -->
    <div v-if="mensaje.texto" class="alert" :class="{ 'alert-success': mensaje.tipo === 'success', 'alert-danger': mensaje.tipo === 'error' }">
      {{ mensaje.texto }}
    </div>
    
    <!-- Leyenda para campos requeridos -->
    <div class="required-fields-legend">
      <span class="required-indicator">*</span> Campos obligatorios
    </div>
  </div>
</template>

<script lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '@/store/auth';
import axios from 'axios';

// URL base para las API
import api, { API_URL } from '@/api/config';

export default {
  name: 'ConceptoForm',
  
  setup() {
    const router = useRouter();
    const route = useRoute();
    const authStore = useAuthStore();
    
    // Estado de carga y error
    const cargando = ref(false);
    const error = ref(null);
    
    // Estado para los selectores dependientes
    const municipiosCargando = ref(false);
    const insumosCargando = ref(false);
    const clasificacionesCargando = ref(false);
    const detallesCargando = ref(false);
    
    // Verificar si estamos editando o creando
    const isEditing = computed(() => !!route.params.id);
    
    // Filtros jerárquicos
    const filtros = ref({
      departamento: '',
      municipio: '',
      insumo: '',
      clasificacion: ''
    });
    
    // Catálogos y listas
    const departamentos = ref([]);
    const municipios = ref([]);
    const insumos = ref([]);
    const clasificaciones = ref([]);
    const detalles = ref([]);
    
    // Datos del formulario
    const formData = ref({
      cod_concepto: '', 
      concepto: '',
      fecha: '',
      evaluacion: '',
      detalle_concepto: '',
      observacion: '',
      pdf: '', // Nuevo campo para PDF
      cod_detalle: '' // Referencia al detalle seleccionado
    });
    
    // Mensajes de error/éxito
    const mensaje = ref({
      texto: '',
      tipo: ''
    });
    
    // Función para cargar TODOS los datos sin importar la paginación
    const cargarTodosLosDatos = async (url, params = {}) => {
      try {
        // Array para almacenar todos los resultados
        let todosLosResultados = [];
        // URL inicial
        let urlActual = url;
        
        // Añadir parámetros iniciales a la URL
        if (Object.keys(params).length > 0) {
          const queryParams = new URLSearchParams(params).toString();
          urlActual = `${url}?${queryParams}`;
        }
        
        // Primera llamada para obtener el total de elementos
        const primeraRespuesta = await axios.get(urlActual);
        
        // Verificar si la respuesta ya es un array simple (sin paginación)
        if (Array.isArray(primeraRespuesta.data)) {
          console.log(`Recibidos ${primeraRespuesta.data.length} elementos (sin paginación)`);
          return primeraRespuesta.data;
        }
        
        // Si hay resultados paginados, obtener la primera página
        if (primeraRespuesta.data.results) {
          todosLosResultados = [...primeraRespuesta.data.results];
          
          // Calcular el número total de elementos
          const count = primeraRespuesta.data.count || 0;
          console.log(`Total de elementos a cargar: ${count}`);
          
          // Si ya tenemos todos los elementos, terminar
          if (todosLosResultados.length >= count) {
            return todosLosResultados;
          }
          
          // Calcular cuántas páginas necesitamos cargar
          const pageSize = primeraRespuesta.data.results.length;
          const totalPages = Math.ceil(count / pageSize);
          
          // Preparar todas las peticiones para las páginas restantes
          const promesas = [];
          for (let pagina = 2; pagina <= totalPages; pagina++) {
            // Construir URL con parámetro de página
            let urlPagina = `${url}?page=${pagina}`;
            
            // Añadir otros parámetros si existen
            if (Object.keys(params).length > 0) {
              const otrosParams = new URLSearchParams(params).toString();
              urlPagina = `${url}?${otrosParams}&page=${pagina}`;
            }
            
            promesas.push(axios.get(urlPagina));
          }
          
          // Ejecutar todas las peticiones en paralelo
          const respuestas = await Promise.all(promesas);
          
          // Procesar todas las respuestas y añadir los resultados
          respuestas.forEach(respuesta => {
            if (respuesta.data && respuesta.data.results) {
              todosLosResultados = [...todosLosResultados, ...respuesta.data.results];
            }
          });
          
          return todosLosResultados;
        } else {
          return [];
        }
      } catch (error) {
        console.error(`Error cargando datos de ${url}:`, error);
        throw error;
      }
    };
    
    // Formatear fecha para mostrar
    const formatFecha = (fecha) => {
      if (!fecha) return 'Sin fecha';
      
      try {
        const fechaObj = new Date(fecha);
        return fechaObj.toLocaleDateString('es-CO', {
          day: '2-digit',
          month: '2-digit',
          year: 'numeric'
        });
      } catch (error) {
        return fecha;
      }
    };
    
    // Obtener último código de concepto
    const obtenerUltimoCodigoConcepto = async () => {
      try {
        const todosConceptos = await cargarTodosLosDatos(`${API_URL}/preoperacion/conceptos/`);
        
        if (!todosConceptos.length) {
          formData.value.cod_concepto = 1;
          return;
        }
        
        const maxCodigo = Math.max(...todosConceptos.map(c => Number(c.cod_concepto)));
        formData.value.cod_concepto = maxCodigo + 1;
      } catch (error) {
        console.error('Error al obtener último código de concepto:', error);
        formData.value.cod_concepto = Math.floor(Date.now() / 1000) % 100000; // Fallback
      }
    };
    
    // Cargar departamentos
    const cargarDepartamentos = async () => {
      try {
        console.log('Cargando departamentos...');
        const resultado = await cargarTodosLosDatos(`${API_URL}/preoperacion/departamentos/`);
        departamentos.value = resultado;
        console.log(`Cargados ${departamentos.value.length} departamentos`);
        return resultado;
      } catch (error) {
        console.error('Error al cargar departamentos:', error);
        mensaje.value = {
          texto: 'Error al cargar departamentos',
          tipo: 'error'
        };
        return [];
      }
    };
    
    // Cargar municipios
    const cargarMunicipios = async () => {
      // Limpiar datos dependientes si no hay departamento seleccionado
      if (!filtros.value.departamento) {
        municipios.value = [];
        filtros.value.municipio = '';
        filtros.value.insumo = '';
        filtros.value.clasificacion = '';
        formData.value.cod_detalle = '';
        return [];
      }
      
      try {
        municipiosCargando.value = true;
        const idDepartamento = filtros.value.departamento;
        console.log(`Cargando municipios del departamento ${idDepartamento}...`);
        
        const params = { cod_depto: idDepartamento };
        const resultado = await cargarTodosLosDatos(`${API_URL}/preoperacion/municipios/`, params);
        
        municipios.value = resultado;
        console.log(`Cargados ${municipios.value.length} municipios`);
        
        // Limpiar selecciones dependientes
        filtros.value.municipio = '';
        filtros.value.insumo = '';
        filtros.value.clasificacion = '';
        formData.value.cod_detalle = '';
        
        return resultado;
      } catch (error) {
        console.error('Error al cargar municipios:', error);
        mensaje.value = {
          texto: 'Error al cargar municipios',
          tipo: 'error'
        };
        return [];
      } finally {
        municipiosCargando.value = false;
      }
    };
    
    // Cargar insumos
    const cargarInsumos = async () => {
      // Limpiar datos dependientes si no hay municipio seleccionado
      if (!filtros.value.municipio) {
        insumos.value = [];
        filtros.value.insumo = '';
        filtros.value.clasificacion = '';
        formData.value.cod_detalle = '';
        return [];
      }
      
      try {
        insumosCargando.value = true;
        const idMunicipio = filtros.value.municipio;
        console.log(`Cargando insumos del municipio ${idMunicipio}...`);
        
        const insumosData = await cargarTodosLosDatos(
          `${API_URL}/preoperacion/municipios/${idMunicipio}/insumos/`
        );
        
        const insumosConCategorias = await Promise.all(insumosData.map(async (insumo) => {
          try {
            if (insumo.categoria && insumo.categoria.nom_categoria) {
              return {
                ...insumo,
                categoria_nombre: insumo.categoria.nom_categoria
              };
            }
            
            const categoriaResponse = await axios.get(
              `${API_URL}/preoperacion/categorias/${insumo.cod_categoria}/`
            );
            return {
              ...insumo,
              categoria_nombre: categoriaResponse.data.nom_categoria
            };
          } catch (error) {
            console.error(`Error al obtener categoría para insumo ${insumo.cod_insumo}:`, error);
            return {
              ...insumo,
              categoria_nombre: 'Categoría no disponible'
            };
          }
        }));
        
        insumos.value = insumosConCategorias;
        console.log(`Cargados ${insumos.value.length} insumos`);
        
        // Limpiar selecciones dependientes
        filtros.value.insumo = '';
        filtros.value.clasificacion = '';
        formData.value.cod_detalle = '';
        
        return insumosConCategorias;
      } catch (error) {
        console.error('Error al cargar insumos:', error);
        mensaje.value = {
          texto: 'Error al cargar insumos',
          tipo: 'error'
        };
        return [];
      } finally {
        insumosCargando.value = false;
      }
    };
    
    // Cargar clasificaciones
    const cargarClasificaciones = async () => {
      // Limpiar datos dependientes si no hay insumo seleccionado
      if (!filtros.value.insumo) {
        clasificaciones.value = [];
        filtros.value.clasificacion = '';
        formData.value.cod_detalle = '';
        return [];
      }
      
      try {
        clasificacionesCargando.value = true;
        const idInsumo = filtros.value.insumo;
        console.log(`Cargando clasificaciones del insumo ${idInsumo}...`);
        
        const resultado = await cargarTodosLosDatos(
          `${API_URL}/preoperacion/insumos/${idInsumo}/clasificaciones/`
        );
        
        clasificaciones.value = resultado;
        console.log(`Cargadas ${clasificaciones.value.length} clasificaciones`);
        
        // Limpiar selecciones dependientes
        filtros.value.clasificacion = '';
        formData.value.cod_detalle = '';
        
        return resultado;
      } catch (error) {
        console.error('Error al cargar clasificaciones:', error);
        mensaje.value = {
          texto: 'Error al cargar clasificaciones',
          tipo: 'error'
        };
        return [];
      } finally {
        clasificacionesCargando.value = false;
      }
    };
    
    // ✅ MODIFICADO: Cargar detalles por clasificación con información de zona
    const cargarDetalles = async () => {
      // Limpiar datos dependientes si no hay clasificación seleccionada
      if (!filtros.value.clasificacion) {
        detalles.value = [];
        formData.value.cod_detalle = '';
        return [];
      }
      
      try {
        detallesCargando.value = true;
        const idClasificacion = filtros.value.clasificacion;
        console.log(`Cargando detalles de la clasificación ${idClasificacion}...`);
        
        const params = { cod_clasificacion: idClasificacion };
        const resultado = await cargarTodosLosDatos(`${API_URL}/preoperacion/detalles-insumo/`, params);
        
        // ✅ MODIFICADO: Enriquecer detalles con nombres de centros poblados Y zona
        const detallesEnriquecidos = await Promise.all(resultado.map(async (detalle) => {
          let detalleEnriquecido = { ...detalle };
          
          // Agregar información del centro poblado si existe
          if (detalle.cod_centro_poblado) {
            try {
              const response = await axios.get(
                `${API_URL}/preoperacion/centros-poblados/${detalle.cod_centro_poblado}/`
              );
              
              detalleEnriquecido.nombre_centro_poblado = response.data.nom_centro_poblado || '';
            } catch (error) {
              console.error(`Error al obtener centro poblado ${detalle.cod_centro_poblado}:`, error);
            }
          }
          
          // ✅ NUEVO: La zona ya viene en el detalle desde la API
          // No necesitamos hacer una llamada adicional, solo asegurarnos de que esté presente
          console.log(`Detalle ${detalle.cod_detalle} - Zona: ${detalle.zona || 'Sin zona'}`);
          
          return detalleEnriquecido;
        }));
        
        detalles.value = detallesEnriquecidos;
        console.log(`Cargados ${detalles.value.length} detalles con información de zona`);
        
        // Limpiar selección dependiente
        formData.value.cod_detalle = '';
        
        return detallesEnriquecidos;
      } catch (error) {
        console.error('Error al cargar detalles:', error);
        mensaje.value = {
          texto: 'Error al cargar detalles',
          tipo: 'error'
        };
        return [];
      } finally {
        detallesCargando.value = false;
      }
    };
    
    // Verificar si el formulario es válido
    const isFormValid = computed(() => {
      return (
        formData.value.concepto && 
        formData.value.cod_detalle
      );
    });

    const fechaMaxima = computed(() => {
      const hoy = new Date();
      const año = hoy.getFullYear();
      const mes = String(hoy.getMonth() + 1).padStart(2, '0');
      const dia = String(hoy.getDate()).padStart(2, '0');
      return `${año}-${mes}-${dia}`;
    });
    
    // Cargar concepto existente para edición
    const cargarConceptoExistente = async (id) => {
      try {
        cargando.value = true;
        
        mensaje.value = {
          texto: 'Cargando datos del concepto...',
          tipo: 'info'
        };
        
        // Asegurarse de que id sea un número válido
        const conceptoId = parseInt(id);
        if (isNaN(conceptoId)) {
          throw new Error('ID del concepto inválido');
        }
        
        console.log(`Cargando concepto existente con ID: ${conceptoId}`);
        
        // 1. Primero obtener datos del concepto
        const response = await axios.get(`${API_URL}/preoperacion/conceptos/${conceptoId}/`);
        
        if (!response.data) {
          throw new Error('No se encontraron datos para el concepto solicitado');
        }
        
        const concepto = response.data;
        console.log('Datos del concepto obtenidos:', concepto);
        
        // 2. Almacenar datos básicos del concepto
        formData.value = {
          cod_concepto: concepto.cod_concepto,
          concepto: concepto.concepto || '',
          fecha: concepto.fecha || '',
          evaluacion: concepto.evaluacion || '',
          detalle_concepto: concepto.detalle_concepto || '',
          observacion: concepto.observacion || '',
          pdf: concepto.pdf || '', // Nuevo campo PDF
          cod_detalle: ''  // Se establecerá después
        };
        
        // 3. Buscar el detalle asociado a este concepto
        const detallesConcepto = await cargarTodosLosDatos(`${API_URL}/preoperacion/detalles-insumo/`, {
          cod_concepto: conceptoId
        });
        
        if (!detallesConcepto || detallesConcepto.length === 0) {
          console.warn('No se encontraron detalles asociados a este concepto');
          mensaje.value = {
            texto: 'No se encontraron detalles asociados a este concepto. Esto puede causar problemas al guardarlo.',
            tipo: 'error'
          };
          cargando.value = false;
          return;
        }
        
        // Tomar el primer detalle encontrado
        const detalle = detallesConcepto[0];
        console.log('Detalle encontrado:', detalle);
        
        // 4. Cargar todos los catálogos necesarios para la jerarquía
        // Primero cargar todos los departamentos
        await cargarDepartamentos();
        
        if (!detalle.cod_clasificacion) {
          console.warn('El detalle no tiene clasificación asociada');
          mensaje.value = {
            texto: 'El detalle no tiene clasificación asociada. Esto puede causar problemas al guardarlo.',
            tipo: 'error'
          };
          cargando.value = false;
          return;
        }
        
        // 5. Obtener la clasificación
        const clasificacionResponse = await axios.get(
          `${API_URL}/preoperacion/clasificaciones/${detalle.cod_clasificacion}/`
        );
        
        if (!clasificacionResponse.data) {
          console.warn('No se pudo obtener la clasificación asociada');
          mensaje.value = {
            texto: 'No se pudo obtener la clasificación asociada.',
            tipo: 'error'
          };
          cargando.value = false;
          return;
        }
        
        const clasificacion = clasificacionResponse.data;
        console.log('Clasificación encontrada:', clasificacion);
        
        // 6. Obtener el insumo
        if (!clasificacion.cod_insumo) {
          console.warn('La clasificación no tiene insumo asociado');
          mensaje.value = {
            texto: 'La clasificación no tiene insumo asociado.',
            tipo: 'error'
          };
          cargando.value = false;
          return;
        }
        
        const insumoResponse = await axios.get(
          `${API_URL}/preoperacion/insumos/${clasificacion.cod_insumo}/`
        );
        
        if (!insumoResponse.data) {
          console.warn('No se pudo obtener el insumo asociado');
          mensaje.value = {
            texto: 'No se pudo obtener el insumo asociado.',
            tipo: 'error'
          };
          cargando.value = false;
          return;
        }
        
        const insumo = insumoResponse.data;
        console.log('Insumo encontrado:', insumo);
        
        // 7. Obtener el municipio
        if (!insumo.cod_municipio) {
          console.warn('El insumo no tiene municipio asociado');
          mensaje.value = {
            texto: 'El insumo no tiene municipio asociado.',
            tipo: 'error'
          };
          cargando.value = false;
          return;
        }
        
        // El municipio puede venir como número o como objeto
        const municipioId = typeof insumo.cod_municipio === 'object' ? 
          insumo.cod_municipio.cod_municipio : insumo.cod_municipio;
        
        const municipioResponse = await axios.get(
          `${API_URL}/preoperacion/municipios/${municipioId}/`
        );
        
        if (!municipioResponse.data) {
          console.warn('No se pudo obtener el municipio asociado');
          mensaje.value = {
            texto: 'No se pudo obtener el municipio asociado.',
            tipo: 'error'
          };
          cargando.value = false;
          return;
        }
        
        const municipio = municipioResponse.data;
        console.log('Municipio encontrado:', municipio);
        
        // 8. Obtener departamento
        let departamentoId;
        if (typeof municipio.cod_depto === 'object') {
          departamentoId = municipio.cod_depto.cod_depto;
        } else {
          departamentoId = municipio.cod_depto;
        }

        if (!departamentoId) {
          console.warn('El municipio no tiene departamento asociado');
          mensaje.value = {
            texto: 'El municipio no tiene departamento asociado.',
            tipo: 'error'
          };
          cargando.value = false;
          return;
        }

        console.log('Departamento ID encontrado:', departamentoId);

        // 9. Cargar todos los datos relacionados en orden
        // IMPORTANTE: Convertir todos los IDs a string para asegurar comparación correcta en los selects
        const deptoIdStr = String(departamentoId);
        const municipioIdStr = String(municipioId);
        const insumoIdStr = String(insumo.cod_insumo);
        const clasificacionIdStr = String(clasificacion.cod_clasificacion);
        const detalleIdStr = String(detalle.cod_detalle);

        console.log('IDs convertidos a string:', { deptoIdStr, municipioIdStr, insumoIdStr, clasificacionIdStr, detalleIdStr });

        // Establecer departamento y cargar municipios
        filtros.value.departamento = deptoIdStr;

        // Cargar municipios sin limpiar la selección posterior
        try {
          const params = { cod_depto: deptoIdStr };
          const resultadoMunicipios = await cargarTodosLosDatos(`${API_URL}/preoperacion/municipios/`, params);
          municipios.value = resultadoMunicipios;
          console.log(`Cargados ${municipios.value.length} municipios para edición`);
        } catch (err) {
          console.error('Error cargando municipios para edición:', err);
        }

        // Establecer municipio y cargar insumos
        filtros.value.municipio = municipioIdStr;

        try {
          const insumosData = await cargarTodosLosDatos(
            `${API_URL}/preoperacion/municipios/${municipioIdStr}/insumos/`
          );

          const insumosConCategorias = await Promise.all(insumosData.map(async (ins) => {
            try {
              if (ins.categoria && ins.categoria.nom_categoria) {
                return { ...ins, categoria_nombre: ins.categoria.nom_categoria };
              }
              const categoriaResponse = await axios.get(
                `${API_URL}/preoperacion/categorias/${ins.cod_categoria}/`
              );
              return { ...ins, categoria_nombre: categoriaResponse.data.nom_categoria };
            } catch (error) {
              return { ...ins, categoria_nombre: 'Categoría no disponible' };
            }
          }));

          insumos.value = insumosConCategorias;
          console.log(`Cargados ${insumos.value.length} insumos para edición`);
        } catch (err) {
          console.error('Error cargando insumos para edición:', err);
        }

        // Establecer insumo y cargar clasificaciones
        filtros.value.insumo = insumoIdStr;

        try {
          const resultadoClasificaciones = await cargarTodosLosDatos(
            `${API_URL}/preoperacion/insumos/${insumoIdStr}/clasificaciones/`
          );
          clasificaciones.value = resultadoClasificaciones;
          console.log(`Cargadas ${clasificaciones.value.length} clasificaciones para edición`);
        } catch (err) {
          console.error('Error cargando clasificaciones para edición:', err);
        }

        // Establecer clasificación y cargar detalles
        filtros.value.clasificacion = clasificacionIdStr;

        try {
          const params = { cod_clasificacion: clasificacionIdStr };
          const resultadoDetalles = await cargarTodosLosDatos(`${API_URL}/preoperacion/detalles-insumo/`, params);

          // Enriquecer detalles con nombres de centros poblados
          const detallesEnriquecidos = await Promise.all(resultadoDetalles.map(async (det) => {
            let detalleEnriquecido = { ...det };
            if (det.cod_centro_poblado) {
              try {
                const response = await axios.get(
                  `${API_URL}/preoperacion/centros-poblados/${det.cod_centro_poblado}/`
                );
                detalleEnriquecido.nombre_centro_poblado = response.data.nom_centro_poblado || '';
              } catch (error) {
                console.error(`Error al obtener centro poblado ${det.cod_centro_poblado}:`, error);
              }
            }
            return detalleEnriquecido;
          }));

          detalles.value = detallesEnriquecidos;
          console.log(`Cargados ${detalles.value.length} detalles para edición`);
        } catch (err) {
          console.error('Error cargando detalles para edición:', err);
        }

        // Finalmente, establecemos el detalle
        formData.value.cod_detalle = detalleIdStr;
        
        console.log('Todos los datos relacionados han sido cargados correctamente');
        console.log('Estado final de filtros:', filtros.value);
        console.log('Formulario:', formData.value);
        
        mensaje.value = {
          texto: 'Datos del concepto cargados correctamente',
          tipo: 'success'
        };
      } catch (err) {
        console.error('Error al cargar concepto:', err);
        mensaje.value = {
          texto: 'Error al cargar los datos del concepto: ' + (err.message || 'Error desconocido'),
          tipo: 'error'
        };
      } finally {
        cargando.value = false;
      }
    };
    
    // Guardar concepto
    const guardarConcepto = async () => {
      if (!isFormValid.value) {
        mensaje.value = {
          texto: 'Por favor complete todos los campos requeridos',
          tipo: 'error'
        };
        return;
      }
      
      try {
        // Obtener el token de autenticación
        const token = localStorage.getItem('token');
        if (!token) {
          mensaje.value = {
            texto: 'No se encontró token de autenticación. Por favor, inicie sesión nuevamente.',
            tipo: 'error'
          };
          setTimeout(() => {
            router.push('/login');
          }, 2000);
          return;
        }
        
        // Configurar headers con el token
        const config = {
          headers: {
            'Authorization': `Token ${token}`,
            'Content-Type': 'application/json'
          }
        };
        
        // Determinar si es creación o edición
        const isEdit = !!route.params.id;
        let conceptoId = null;
        
        if (isEdit) {
          conceptoId = parseInt(route.params.id);
          if (isNaN(conceptoId)) {
            mensaje.value = {
              texto: 'ID de concepto inválido',
              tipo: 'error'
            };
            return;
          }
        }
        
        // Asegurar que los códigos estén como números
        const datosAEnviar = {
          ...formData.value,
          cod_concepto: isEdit ? conceptoId : parseInt(formData.value.cod_concepto)
        };
        
        // Log para depuración
        console.log(`Operación: ${isEdit ? 'Actualización' : 'Creación'}`);
        console.log('ID del concepto:', isEdit ? conceptoId : datosAEnviar.cod_concepto);
        console.log('Datos a enviar:', datosAEnviar);
        
        let response;
        
        if (isEdit) {
          // Actualizar concepto existente
          response = await axios.put(
            `${API_URL}/preoperacion/conceptos/${conceptoId}/`, 
            datosAEnviar, 
            config
          );
          mensaje.value = {
            texto: 'Concepto actualizado exitosamente',
            tipo: 'success'
          };
        } else {
          // Crear nuevo concepto
          response = await axios.post(
            `${API_URL}/preoperacion/conceptos/`, 
            datosAEnviar, 
            config
          );
          mensaje.value = {
            texto: 'Concepto guardado exitosamente',
            tipo: 'success'
          };
        }
        
        console.log('Respuesta exitosa:', response.data);
        
        // También necesitamos actualizar el detalle con la referencia al concepto
        try {
          // Obtener el detalle actual
          const detalleResponse = await axios.get(
            `${API_URL}/preoperacion/detalles-insumo/${formData.value.cod_detalle}/`
          );
          
          const detalle = detalleResponse.data;
          
          // Actualizar la referencia al concepto en el detalle
          const detalleActualizado = {
            ...detalle,
            cod_concepto: isEdit ? conceptoId : parseInt(formData.value.cod_concepto)
          };
          
          // Actualizar el detalle
          await axios.put(
            `${API_URL}/preoperacion/detalles-insumo/${formData.value.cod_detalle}/`,
            detalleActualizado,
            config
          );
          
          console.log('Detalle actualizado con referencia al concepto');
        } catch (err) {
          console.error('Error al actualizar detalle con referencia al concepto:', err);
          // No bloqueamos el proceso, solo registramos el error
        }
        
        // Esperar un momento y redirigir
        setTimeout(() => {
          router.push('/gestion-informacion/conceptos');
        }, 1500);
      } catch (error) {
        console.error('Error al guardar concepto:', error);
        
        // Mostrar error de forma segura
        let mensajeError = (route.params.id) ? 
          'Error al actualizar el concepto' :
          'Error al guardar el concepto';
        
        if (error.response) {
          if (error.response.status === 500) {
            mensajeError = 'Error en el servidor: Hay un problema con la configuración del backend.';
          } else if (error.response.status === 404) {
            mensajeError = 'Error: No se encontró el recurso solicitado. Verifique que el ID del concepto sea válido.';
          } else if (error.response.data && typeof error.response.data === 'object') {
            const errores = [];
            Object.keys(error.response.data).forEach(campo => {
              errores.push(`${campo}: ${error.response.data[campo]}`);
            });
            
            if (errores.length > 0) {
              mensajeError = `Errores en el formulario: ${errores.join(', ')}`;
            }
          } else if (error.response.data && typeof error.response.data === 'string') {
            mensajeError = `Error: ${error.response.data}`;
          }
        }
        
        mensaje.value = {
          texto: mensajeError,
          tipo: 'error'
        };
      }
    };
    
    // Cancelar edición
    const cancelar = () => {
      router.push('/gestion-informacion/conceptos');
    };
    
    // Insumos con categoría
    const insumosConCategoria = computed(() => {
      return insumos.value.map(insumo => {
        if (insumo.categoria_nombre) {
          return insumo;
        }
        
        if (insumo.categoria && insumo.categoria.nom_categoria) {
          return {
            ...insumo,
            categoria_nombre: insumo.categoria.nom_categoria
          };
        }
        
        return {
          ...insumo,
          categoria_nombre: 'Categoría no disponible'
        };
      });
    });
    
    // Inicialización del componente
    onMounted(async () => {
      // Verificar autenticación
      if (!authStore.isAuthenticated) {
        console.warn('Usuario no autenticado, redirigiendo a login...');
        router.push('/login?redirect=' + encodeURIComponent(route.fullPath));
        return;
      }
      
      try {
        // Cargar catálogos y dominios primero
        await Promise.all([
          cargarDepartamentos()
        ]);
        
        // Si hay un ID en la ruta, cargar los datos para edición
        if (route.params.id) {
          await cargarConceptoExistente(route.params.id);
        } else {
          // Si es nuevo, obtener nuevo código
          await obtenerUltimoCodigoConcepto();
        }
      } catch (err) {
        console.error('Error al inicializar formulario:', err);
        mensaje.value = {
          texto: 'Error al cargar los datos iniciales: ' + (err.message || 'Error desconocido'),
          tipo: 'error'
        };
      }
    });
    
    // Observar cambios en el detalle seleccionado
    watch(() => formData.value.cod_detalle, async (newValue) => {
      if (newValue) {
        // Si se selecciona un detalle y estamos creando un concepto nuevo,
        // verificar si ya tiene conceptos asociados
        if (!route.params.id) {
          try {
            const detalleResponse = await axios.get(
              `${API_URL}/preoperacion/detalles-insumo/${newValue}/`
            );
            
            const detalle = detalleResponse.data;
            
            if (detalle.cod_concepto && detalle.cod_concepto !== 0) {
              mensaje.value = {
                texto: `Advertencia: Este detalle ya tiene un concepto asociado (Código: ${detalle.cod_concepto})`,
                tipo: 'error'
              };
            } else {
              mensaje.value = {
                texto: '',
                tipo: ''
              };
            }
          } catch (err) {
            console.error('Error al verificar el detalle:', err);
          }
        }
      }
    });
    
    return {
      // Estado
      cargando,
      error,
      isEditing,
      municipiosCargando,
      insumosCargando,
      clasificacionesCargando,
      detallesCargando,
      
      // Filtros
      filtros,
      
      // Catálogos
      departamentos,
      municipios,
      insumos,
      insumosConCategoria,
      clasificaciones,
      detalles,
      
      // Datos del formulario
      formData,
      mensaje,
      isFormValid,
      fechaMaxima,
      
      // Métodos y funciones
      cargarDepartamentos,
      cargarMunicipios,
      cargarInsumos,
      cargarClasificaciones,
      cargarDetalles,
      formatFecha,
      guardarConcepto,
      cancelar
    };
  }
};
</script>
<style scoped>
.concepto-form-container {
background-color: #ffffff;
border-radius: 8px;
box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
padding: 2rem;
margin-bottom: 2rem;
}

.form-title {
color: #343a40;
margin-bottom: 1.5rem;
font-size: 1.6rem;
font-weight: 600;
}

.filtros-section {
background-color: #f8f9fa;
border-radius: 6px;
padding: 1.5rem;
margin-bottom: 2rem;
border: 1px solid #e9ecef;
}

.row {
display: flex;
flex-wrap: wrap;
margin-right: -15px;
margin-left: -15px;
margin-bottom: 1rem;
}

.col-md-6 {
position: relative;
width: 100%;
padding-right: 15px;
padding-left: 15px;
flex: 0 0 50%;
max-width: 50%;
}

.col-md-12 {
position: relative;
width: 100%;
padding-right: 15px;
padding-left: 15px;
flex: 0 0 100%;
max-width: 100%;
}

.form-group {
margin-bottom: 1.5rem;
}

.form-group label {
display: block;
font-weight: 500;
margin-bottom: 0.5rem;
color: #495057;
}

.form-control {
display: block;
width: 100%;
padding: 0.5rem 0.75rem;
font-size: 1rem;
line-height: 1.5;
color: #495057;
background-color: #fff;
background-clip: padding-box;
border: 1px solid #ced4da;
border-radius: 4px;
transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
}

.form-control:focus {
border-color: #80bdff;
outline: 0;
box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
}

.form-control:disabled {
background-color: #e9ecef;
opacity: 1;
}

.form-buttons {
display: flex;
justify-content: flex-end;
gap: 1rem;
margin-top: 2rem;
}

.btn {
display: inline-block;
font-weight: 500;
text-align: center;
white-space: nowrap;
vertical-align: middle;
user-select: none;
border: 1px solid transparent;
padding: 0.5rem 1rem;
font-size: 1rem;
line-height: 1.5;
border-radius: 4px;
transition: color 0.15s ease-in-out, background-color 0.15s ease-in-out, border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
cursor: pointer;
}

.btn-primary {
color: #fff;
background-color: #007bff;
border-color: #007bff;
}

.btn-primary:hover {
color: #fff;
background-color: #0069d9;
border-color: #0062cc;
}

.btn-primary:disabled {
color: #fff;
background-color: #007bff;
border-color: #007bff;
opacity: 0.65;
cursor: not-allowed;
}

.btn-secondary {
color: #fff;
background-color: #6c757d;
border-color: #6c757d;
}

.btn-secondary:hover {
color: #fff;
background-color: #5a6268;
border-color: #545b62;
}

.alert {
position: relative;
padding: 1rem;
margin-top: 1.5rem;
border: 1px solid transparent;
border-radius: 4px;
}

.alert-success {
color: #155724;
background-color: #d4edda;
border-color: #c3e6cb;
}

.alert-danger {
color: #721c24;
background-color: #f8d7da;
border-color: #f5c6cb;
}

/* Responsive styles */
@media (max-width: 768px) {
.col-md-6 {
  flex: 0 0 100%;
  max-width: 100%;
}

.form-buttons {
  flex-direction: column;
  gap: 0.5rem;
}

.btn {
  width: 100%;
}
}

.concepto-form-container {
  padding: 20px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.form-title {
  margin-bottom: 20px;
  color: #333;
  border-bottom: 2px solid #007bff;
  padding-bottom: 10px;
}

.filtros-section {
  background-color: #f8f9fa;
  padding: 15px;
  border-radius: 5px;
  margin-bottom: 20px;
  border-left: 4px solid #007bff;
}

.form-main {
  margin-top: 20px;
}

.form-group {
  margin-bottom: 15px;
}

.form-buttons {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.btn-primary {
  background-color: #007bff;
  border-color: #007bff;
}

.btn-secondary {
  background-color: #6c757d;
  border-color: #6c757d;
}

.alert {
  margin-top: 15px;
}

/* Estilos para campos requeridos */
label.required:after {
  content: " *";
  color: #dc3545;
  font-weight: bold;
}

.required-fields-legend {
  margin-top: 20px;
  font-size: 0.9rem;
  color: #6c757d;
}

.required-indicator {
  color: #dc3545;
  font-weight: bold;
}

/* Resaltar campos con error de validación */
.form-control:invalid {
  border-color: #dc3545;
}

.text-info small {
  color: #17a2b8;
}

/* Estilos responsivos */
@media (max-width: 768px) {
  .row {
    margin-right: -5px;
    margin-left: -5px;
  }
  
  .col-md-6, .col-md-12 {
    padding-right: 5px;
    padding-left: 5px;
  }
  
  .form-buttons {
    flex-direction: column;
  }
  
  .btn {
    width: 100%;
    margin-bottom: 10px;
  }
}
</style>