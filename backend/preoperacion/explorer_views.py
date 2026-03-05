import os
import datetime
import stat
from pathlib import Path, PureWindowsPath
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny

class DirectoryExplorerView(APIView):
    """
    Vista para explorar estructuras de directorios en rutas de red compartidas.
    """
    # permission_classes = [IsAuthenticated]  # Requerir autenticación para acceder
    permission_classes = [AllowAny] 
    # Ruta base que se explorará
    BASE_PATH = r"\\repositorio\DirGesCat\2510SP\H_Informacion_Consulta\Sub_Proy"
    
    def get(self, request, format=None):
        """
        Explorar directorios a partir de un path relativo a la ruta base.
        
        Parámetros de consulta:
        - path: Ruta relativa para explorar (opcional)
        """
        relative_path = request.query_params.get('path', '')
        
        # Sanitizar el path para evitar navegación a directorios superiores
        relative_path = self._sanitize_path(relative_path)
        
        # Construir ruta completa
        full_path = os.path.join(self.BASE_PATH, relative_path)
        
        try:
            # Si no existe el directorio, devolver error
            if not os.path.exists(full_path):
                return Response(
                    {"error": f"La ruta especificada no existe: {relative_path}"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Si es un archivo, devolver info del archivo
            if os.path.isfile(full_path):
                return Response(self._get_file_info(full_path, relative_path))
            
            # Si es un directorio, explorar su contenido
            items = []
            try:
                for item in os.listdir(full_path):
                    item_path = os.path.join(full_path, item)
                    item_relative_path = os.path.join(relative_path, item) if relative_path else item
                    
                    # Recopilar información base
                    item_info = {
                        "name": item,
                        "path": item_relative_path.replace('\\', '/'),  # Para URLs más consistentes
                        "type": "directory" if os.path.isdir(item_path) else "file",
                    }
                    
                    # Añadir información adicional según el tipo
                    if os.path.isfile(item_path):
                        self._add_file_info(item_info, item_path)
                    else:  # es directorio
                        item_info["child_count"] = self._count_children(item_path)
                    
                    items.append(item_info)
                
                # Ordenar: primero directorios, luego archivos, ambos alfabéticamente
                items.sort(key=lambda x: (0 if x["type"] == "directory" else 1, x["name"].lower()))
                
                # Construir respuesta
                response_data = {
                    "path": relative_path,
                    "full_path": full_path,
                    "parent_path": os.path.dirname(relative_path) if relative_path else None,
                    "items": items
                }
                
                return Response(response_data)
            
            except PermissionError:
                return Response(
                    {"error": f"Acceso denegado a la ruta: {relative_path}"},
                    status=status.HTTP_403_FORBIDDEN
                )
                
        except Exception as e:
            return Response(
                {"error": f"Error al explorar directorio: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _sanitize_path(self, path):
        """Sanitizar la ruta para evitar navegación a directorios superiores"""
        # Eliminar caracteres peligrosos y convertir a ruta normalizada
        path = path.replace('..', '').replace('~', '')
        # Eliminar cualquier barra inicial para garantizar que sea relativa
        while path.startswith('/') or path.startswith('\\'):
            path = path[1:]
        return path
    
    def _count_children(self, dir_path):
        """Contar elementos dentro de un directorio"""
        try:
            return len(os.listdir(dir_path))
        except:
            return 0
    
    def _get_file_info(self, file_path, relative_path):
        """Obtener información detallada de un archivo"""
        file_info = {
            "name": os.path.basename(file_path),
            "path": relative_path.replace('\\', '/'),
            "type": "file",
        }
        self._add_file_info(file_info, file_path)
        return file_info
    
    def _add_file_info(self, file_info, file_path):
        """Añadir información adicional sobre un archivo"""
        try:
            stat_info = os.stat(file_path)
            file_info.update({
                "size": stat_info.st_size,
                "size_human": self._human_readable_size(stat_info.st_size),
                "modified": datetime.datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
                "created": datetime.datetime.fromtimestamp(stat_info.st_ctime).isoformat(),
                "extension": os.path.splitext(file_path)[1].lower()[1:] or None,
            })
        except:
            # En caso de error al obtener estadísticas, añadir valores predeterminados
            file_info.update({
                "size": 0,
                "size_human": "0 B",
                "modified": None,
                "created": None,
                "extension": os.path.splitext(file_path)[1].lower()[1:] or None,
            })
    
    def _human_readable_size(self, size, decimal_places=2):
        """Convertir tamaño en bytes a formato legible por humanos"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB', 'PB']:
            if size < 1024.0 or unit == 'PB':
                break
            size /= 1024.0
        return f"{size:.{decimal_places}f} {unit}"