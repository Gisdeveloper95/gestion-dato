#!/usr/bin/env python3
"""
Módulo de Índice Vectorial para Búsqueda Semántica
Usa sentence-transformers + ChromaDB para búsqueda inteligente de archivos
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional
import json
from datetime import datetime

# Importar dependencias
try:
    from sentence_transformers import SentenceTransformer
    import chromadb
    from chromadb.config import Settings
    from tqdm import tqdm
except ImportError as e:
    print(f"⚠️ Error importando dependencias: {e}")
    print("Ejecuta: pip3 install sentence-transformers chromadb tqdm")
    sys.exit(1)

# Importar utilidades locales
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.common import Config, DatabaseManager


class VectorIndex:
    """
    Sistema de búsqueda semántica con embeddings vectoriales.
    Indexa archivos de la BD y permite búsquedas por similitud.
    """

    def __init__(self, config_path: Optional[str] = None):
        """Inicializa el índice vectorial"""
        print("🚀 Inicializando sistema de búsqueda semántica...")

        self.config = Config(config_path)
        self.db = DatabaseManager(self.config)

        # Directorio para almacenar el índice vectorial
        self.vector_db_path = Path(__file__).parent.parent / "vector_db"
        self.vector_db_path.mkdir(exist_ok=True)

        # Inicializar modelo de embeddings (multilingual)
        print("📥 Cargando modelo de embeddings (puede tardar la primera vez)...")
        self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

        # Obtener dimensiones del modelo
        try:
            dim = self.model.get_sentence_embedding_dimension()
        except:
            # Para versiones nuevas de sentence-transformers
            dim = self.model.encode(["test"], show_progress_bar=False).shape[1]

        print(f"✅ Modelo cargado: {dim} dimensiones")

        # Inicializar ChromaDB
        self.client = chromadb.PersistentClient(
            path=str(self.vector_db_path),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )

        # Colecciones por fase operacional
        self.collections = {
            'preo': self._get_or_create_collection('archivos_preoperacion'),
            'post': self._get_or_create_collection('archivos_postoperacion'),
            'opera': self._get_or_create_collection('archivos_operacion'),
            'transv': self._get_or_create_collection('archivos_transversal')
        }

        print(f"✅ ChromaDB inicializado en: {self.vector_db_path}")
        self._mostrar_estadisticas()

    def _get_or_create_collection(self, name: str):
        """Obtiene o crea una colección en ChromaDB"""
        try:
            return self.client.get_collection(name=name)
        except:
            return self.client.create_collection(
                name=name,
                metadata={"hnsw:space": "cosine"}  # Similitud coseno
            )

    def _mostrar_estadisticas(self):
        """Muestra estadísticas del índice"""
        print("\n📊 Estadísticas del índice vectorial:")
        for fase, collection in self.collections.items():
            count = collection.count()
            print(f"   {fase.upper()}: {count:,} archivos indexados")
        print()

    # ==================== INDEXACIÓN ====================

    def indexar_archivo(self, archivo: Dict, fase: str = 'preo'):
        """
        Indexa un archivo individual

        Args:
            archivo: Diccionario con información del archivo
            fase: Fase operacional (preo, post, opera, transv)
        """
        if fase not in self.collections:
            raise ValueError(f"Fase inválida: {fase}. Debe ser: preo, post, opera, transv")

        # Construir descripción semántica del archivo
        descripcion = self._construir_descripcion(archivo, fase)

        # Generar embedding
        embedding = self.model.encode(descripcion, convert_to_numpy=True)

        # ID único
        file_id = f"{fase}_{archivo.get('id', archivo.get('path', '').replace('/', '_'))}"

        # Guardar en ChromaDB
        try:
            self.collections[fase].add(
                embeddings=[embedding.tolist()],
                documents=[descripcion],
                metadatas=[{
                    'id': str(archivo.get('id', '')),
                    'path': archivo.get('path', ''),
                    'nombre': archivo.get('nombre', ''),
                    'cod_mpio': archivo.get('cod_mpio', ''),
                    'fase': fase,
                    'extension': archivo.get('extension', ''),
                    'size_mb': str(archivo.get('size_mb', 0)),
                    'fecha': archivo.get('fecha', ''),
                    'categoria': archivo.get('categoria', ''),
                    'indexed_at': datetime.now().isoformat()
                }],
                ids=[file_id]
            )
        except Exception as e:
            # Si ya existe, actualizar
            try:
                self.collections[fase].update(
                    embeddings=[embedding.tolist()],
                    documents=[descripcion],
                    metadatas=[{
                        'id': str(archivo.get('id', '')),
                        'path': archivo.get('path', ''),
                        'nombre': archivo.get('nombre', ''),
                        'cod_mpio': archivo.get('cod_mpio', ''),
                        'fase': fase,
                        'extension': archivo.get('extension', ''),
                        'size_mb': str(archivo.get('size_mb', 0)),
                        'fecha': archivo.get('fecha', ''),
                        'categoria': archivo.get('categoria', ''),
                        'indexed_at': datetime.now().isoformat()
                    }],
                    ids=[file_id]
                )
            except Exception as e2:
                print(f"⚠️ Error indexando {file_id}: {e2}")

    def _construir_descripcion(self, archivo: Dict, fase: str) -> str:
        """Construye descripción semántica del archivo"""
        parts = []

        # Nombre del archivo (más importante)
        if archivo.get('nombre'):
            nombre = archivo['nombre'].replace('_', ' ').replace('-', ' ')
            parts.append(nombre)

        # Código de municipio
        if archivo.get('cod_mpio'):
            parts.append(f"municipio {archivo['cod_mpio']}")

        # Categoría/tipo
        if archivo.get('categoria'):
            parts.append(archivo['categoria'])

        # Fase operacional
        parts.append(f"fase {fase}")

        # Extensión (útil para búsquedas tipo "busca shapefiles")
        if archivo.get('extension'):
            ext = archivo['extension'].replace('.', '')
            parts.append(f"archivo {ext}")

        # Partes del path (para contexto)
        if archivo.get('path'):
            path_parts = Path(archivo['path']).parts
            # Tomar solo partes relevantes (no todo el path)
            relevant_parts = [p for p in path_parts if len(p) > 3 and not p.startswith('.')]
            parts.extend(relevant_parts[-5:])  # Últimas 5 partes

        return ' '.join(parts).lower()

    def indexar_lote(self, archivos: List[Dict], fase: str = 'preo', batch_size: int = 100):
        """
        Indexa múltiples archivos en lotes

        Args:
            archivos: Lista de diccionarios con información de archivos
            fase: Fase operacional
            batch_size: Tamaño del lote para procesamiento
        """
        total = len(archivos)
        print(f"📦 Indexando {total:,} archivos de {fase.upper()} en lotes de {batch_size}...")

        for i in tqdm(range(0, total, batch_size), desc=f"Indexando {fase}"):
            batch = archivos[i:i+batch_size]

            # Construir descripciones
            descripciones = [self._construir_descripcion(a, fase) for a in batch]

            # Generar embeddings en lote (más rápido)
            embeddings = self.model.encode(descripciones, convert_to_numpy=True, show_progress_bar=False)

            # IDs y metadatos
            ids = [f"{fase}_{a.get('id', i+idx)}" for idx, a in enumerate(batch)]
            metadatas = [{
                'id': str(a.get('id', '')),
                'path': a.get('path', ''),
                'nombre': a.get('nombre', ''),
                'cod_mpio': a.get('cod_mpio', ''),
                'fase': fase,
                'extension': a.get('extension', ''),
                'size_mb': str(a.get('size_mb', 0)),
                'fecha': a.get('fecha', ''),
                'categoria': a.get('categoria', ''),
                'indexed_at': datetime.now().isoformat()
            } for a in batch]

            # Agregar a ChromaDB
            try:
                self.collections[fase].upsert(
                    embeddings=embeddings.tolist(),
                    documents=descripciones,
                    metadatas=metadatas,
                    ids=ids
                )
            except Exception as e:
                print(f"⚠️ Error en lote {i}-{i+batch_size}: {e}")

        print(f"✅ Indexación completada: {fase.upper()}")

    # ==================== BÚSQUEDA ====================

    def buscar(self, query: str, fase: Optional[str] = None, n_results: int = 10,
               cod_mpio: Optional[str] = None) -> List[Dict]:
        """
        Busca archivos por similitud semántica

        Args:
            query: Consulta en lenguaje natural
            fase: Fase específica (preo, post, opera, transv) o None para todas
            n_results: Número de resultados
            cod_mpio: Filtrar por código de municipio

        Returns:
            Lista de archivos ordenados por relevancia
        """
        # Generar embedding de la consulta
        query_embedding = self.model.encode(query, convert_to_numpy=True)

        # Buscar en colecciones
        if fase:
            colecciones = {fase: self.collections[fase]}
        else:
            colecciones = self.collections

        resultados = []

        for fase_name, collection in colecciones.items():
            # Filtro por municipio si se especifica
            where_filter = None
            if cod_mpio:
                where_filter = {"cod_mpio": cod_mpio}

            try:
                results = collection.query(
                    query_embeddings=[query_embedding.tolist()],
                    n_results=n_results,
                    where=where_filter
                )

                # Formatear resultados
                if results['ids'] and results['ids'][0]:
                    for i in range(len(results['ids'][0])):
                        metadata = results['metadatas'][0][i]
                        distance = results['distances'][0][i] if 'distances' in results else 0

                        resultados.append({
                            'fase': fase_name,
                            'id': metadata.get('id'),
                            'path': metadata.get('path'),
                            'nombre': metadata.get('nombre'),
                            'cod_mpio': metadata.get('cod_mpio'),
                            'extension': metadata.get('extension'),
                            'size_mb': float(metadata.get('size_mb', 0)),
                            'fecha': metadata.get('fecha'),
                            'categoria': metadata.get('categoria'),
                            'similitud': 1 - distance,  # Convertir distancia a similitud
                            'score': int((1 - distance) * 100)  # Score en porcentaje
                        })
            except Exception as e:
                print(f"⚠️ Error buscando en {fase_name}: {e}")

        # Ordenar por similitud
        resultados.sort(key=lambda x: x['similitud'], reverse=True)

        return resultados[:n_results]

    def buscar_municipio(self, nombre_mpio: str, query: str, n_results: int = 10) -> List[Dict]:
        """
        Busca archivos de un municipio específico

        Args:
            nombre_mpio: Nombre del municipio (ej: "Ibagué", "Neiva")
            query: Consulta adicional (ej: "acta comité", "shapefile")
            n_results: Número de resultados
        """
        # Construir consulta combinada
        query_completa = f"{nombre_mpio} {query}"

        return self.buscar(query_completa, n_results=n_results)

    # ==================== MANTENIMIENTO ====================

    def limpiar_indice(self, fase: Optional[str] = None):
        """Limpia el índice (elimina todos los documentos)"""
        if fase:
            print(f"🗑️ Limpiando índice de {fase.upper()}...")
            self.collections[fase].delete(where={})
        else:
            print("🗑️ Limpiando todos los índices...")
            for fase_name, collection in self.collections.items():
                collection.delete(where={})

        print("✅ Índice limpiado")

    def exportar_estadisticas(self) -> Dict:
        """Exporta estadísticas del índice"""
        # Obtener dimensiones del modelo
        try:
            dim = self.model.get_sentence_embedding_dimension()
        except:
            dim = self.model.encode(["test"], show_progress_bar=False).shape[1]

        stats = {
            'timestamp': datetime.now().isoformat(),
            'vector_db_path': str(self.vector_db_path),
            'modelo': 'paraphrase-multilingual-MiniLM-L12-v2',
            'dimensiones': dim,
            'fases': {}
        }

        for fase, collection in self.collections.items():
            stats['fases'][fase] = {
                'total_archivos': collection.count(),
                'coleccion': collection.name
            }

        return stats


def test_basico():
    """Test básico del sistema"""
    print("\n" + "="*60)
    print("TEST BÁSICO DE BÚSQUEDA SEMÁNTICA")
    print("="*60 + "\n")

    # Inicializar
    idx = VectorIndex()

    # Test de búsqueda
    print("\n🔍 Test 1: Búsqueda general")
    resultados = idx.buscar("acta de comité", n_results=5)

    if resultados:
        print(f"\n✅ Encontrados {len(resultados)} resultados:")
        for i, r in enumerate(resultados, 1):
            print(f"\n{i}. {r['nombre']}")
            print(f"   Fase: {r['fase'].upper()} | Municipio: {r['cod_mpio']}")
            print(f"   Similitud: {r['score']}% | Tamaño: {r['size_mb']:.2f} MB")
            print(f"   Path: {r['path'][:80]}...")
    else:
        print("⚠️ No hay archivos indexados. Ejecuta el script de indexación.")

    # Estadísticas
    print("\n" + "="*60)
    try:
        stats = idx.exportar_estadisticas()
        print(f"\n📊 Estadísticas:")
        print(json.dumps(stats, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"⚠️ Error obteniendo estadísticas: {e}")


if __name__ == '__main__':
    test_basico()
