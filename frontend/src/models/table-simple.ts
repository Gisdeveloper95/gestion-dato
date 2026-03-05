// Tipos para el TableManager

export interface TableColumn {
  key: string
  label: string
  type: 'text' | 'number' | 'date' | 'boolean' | 'email'
  sortable?: boolean
  editable?: boolean
  required?: boolean
  placeholder?: string
  minWidth?: string
  format?: (value: any) => string
}

export interface TableFilter {
  key: string
  label: string
  type: 'text' | 'select' | 'date' | 'number'
  placeholder?: string
  options?: Array<{ value: any; label: string }>
}

export interface TableConfig {
  title: string
  singularName: string
  pluralName: string
  apiEndpoint: string
  idField: string
  itemsPerPage?: number
  columns: TableColumn[]
  searchFields?: string[]
  filters?: TableFilter[]
}

export interface TablePermissions {
  canCreate: boolean
  canEdit: boolean
  canDelete: boolean
  canExport: boolean
}

// Tipos para datos de la API
export interface ApiResponse<T> {
  results?: T[]
  count?: number
  next?: string | null
  previous?: string | null
}

export interface PaginationParams {
  page?: number
  page_size?: number
  search?: string
  ordering?: string
}

// Tipos específicos para dominios
export interface DominioBase {
  [key: string]: any
}

export interface Categoria extends DominioBase {
  cod_categoria: number
  nom_categoria: string
}

export interface TipoInsumo extends DominioBase {
  tipo_insumo: string
}

export interface Entidad extends DominioBase {
  cod_entidad: string
  nom_entidad: string
}

export interface EstadoInsumo extends DominioBase {
  estado: string
}

// Tipos para componentes
export interface NotificacionToast {
  show: boolean
  type: 'success' | 'error' | 'warning' | 'info'
  title: string
  message: string
  icon: string
}

export interface SortState {
  campo: string
  direccion: 'asc' | 'desc'
}

// Utilidades de validación
export interface ValidationRule {
  required?: boolean
  minLength?: number
  maxLength?: number
  pattern?: RegExp
  message?: string
}

export interface FormField {
  key: string
  label: string
  type: string
  value: any
  rules?: ValidationRule[]
  placeholder?: string
  options?: Array<{ value: any; label: string }>
}

// Estados de carga
export interface LoadingState {
  loading: boolean
  error: string | null
  success: boolean
}

// Configuración de tabla extendida
export interface ExtendedTableConfig extends TableConfig {
  allowInlineEdit?: boolean
  allowBulkActions?: boolean
  refreshInterval?: number
  cacheData?: boolean
  virtualScroll?: boolean
}

export default {
  TableColumn,
  TableFilter,
  TableConfig,
  TablePermissions,
  ApiResponse,
  PaginationParams,
  DominioBase,
  Categoria,
  TipoInsumo,
  Entidad,
  EstadoInsumo,
  NotificacionToast,
  SortState,
  ValidationRule,
  FormField,
  LoadingState,
  ExtendedTableConfig
}