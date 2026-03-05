# Crear: preoperacion/management/commands/diagnostico_real.py

from django.core.management.base import BaseCommand
from django.db import connection
import traceback

class Command(BaseCommand):
    help = 'Diagnóstico REAL del problema de notificaciones'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔥 DIAGNÓSTICO REAL - SIN PENDEJADAS'))
        self.stdout.write('=' * 80)
        
        # 1. Verificar que las tablas existen
        self.verificar_tablas_existen()
        
        # 2. Probar imports básicos
        self.probar_imports()
        
        # 3. Probar consultas SQL directas
        self.probar_consultas_directas()
        
        # 4. Probar consultas Django ORM más básicas
        self.probar_orm_basico()
        
        # 5. Probar ViewSets paso a paso
        self.probar_viewsets()
    
    def verificar_tablas_existen(self):
        self.stdout.write('\n🗃️ VERIFICANDO QUE LAS TABLAS EXISTAN:')
        
        with connection.cursor() as cursor:
            try:
                # Verificar notificaciones
                cursor.execute("SELECT COUNT(*) FROM notificaciones LIMIT 1")
                count = cursor.fetchone()[0]
                self.stdout.write(f"  ✅ Tabla 'notificaciones': {count} registros")
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  ❌ Error tabla 'notificaciones': {e}"))
            
            try:
                # Verificar notificaciones_post
                cursor.execute("SELECT COUNT(*) FROM notificaciones_post LIMIT 1")
                count = cursor.fetchone()[0]
                self.stdout.write(f"  ✅ Tabla 'notificaciones_post': {count} registros")
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  ❌ Error tabla 'notificaciones_post': {e}"))
    
    def probar_imports(self):
        self.stdout.write('\n📦 PROBANDO IMPORTS:')
        
        try:
            from preoperacion.models import Notificaciones
            self.stdout.write("  ✅ Import Notificaciones OK")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  ❌ Error import Notificaciones: {e}"))
            traceback.print_exc()
        
        try:
            from postoperacion.models import NotificacionesPost
            self.stdout.write("  ✅ Import NotificacionesPost OK")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  ❌ Error import NotificacionesPost: {e}"))
            traceback.print_exc()
        
        try:
            from preoperacion.serializers import NotificacionesSerializer
            self.stdout.write("  ✅ Import NotificacionesSerializer OK")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  ❌ Error import NotificacionesSerializer: {e}"))
            traceback.print_exc()
        
        try:
            from postoperacion.serializers import NotificacionesPostSerializer
            self.stdout.write("  ✅ Import NotificacionesPostSerializer OK")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  ❌ Error import NotificacionesPostSerializer: {e}"))
            traceback.print_exc()
    
    def probar_consultas_directas(self):
        self.stdout.write('\n💾 PROBANDO CONSULTAS SQL DIRECTAS:')
        
        with connection.cursor() as cursor:
            try:
                cursor.execute("SELECT id, tipo_entidad, accion FROM notificaciones LIMIT 3")
                resultados = cursor.fetchall()
                self.stdout.write(f"  ✅ SQL directo notificaciones: {len(resultados)} registros")
                for r in resultados:
                    self.stdout.write(f"    - ID: {r[0]}, Tipo: {r[1]}, Acción: {r[2]}")
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  ❌ Error SQL notificaciones: {e}"))
                
            try:
                cursor.execute("SELECT id, tipo_entidad, accion FROM notificaciones_post LIMIT 3")
                resultados = cursor.fetchall()
                self.stdout.write(f"  ✅ SQL directo notificaciones_post: {len(resultados)} registros")
                for r in resultados:
                    self.stdout.write(f"    - ID: {r[0]}, Tipo: {r[1]}, Acción: {r[2]}")
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  ❌ Error SQL notificaciones_post: {e}"))
    
    def probar_orm_basico(self):
        self.stdout.write('\n🔧 PROBANDO ORM BÁSICO:')
        
        try:
            from preoperacion.models import Notificaciones
            
            # Consulta más básica posible
            count = Notificaciones.objects.count()
            self.stdout.write(f"  ✅ Notificaciones.objects.count(): {count}")
            
            # Consulta con limit
            primeras = Notificaciones.objects.all()[:3]
            self.stdout.write(f"  ✅ Notificaciones.objects.all()[:3]: {len(list(primeras))} registros")
            
            # Consulta con exclude
            sin_sincronizar = Notificaciones.objects.exclude(accion='sincronizar').count()
            self.stdout.write(f"  ✅ Sin sincronizar: {sin_sincronizar}")
            
            # Consulta con order_by
            ordenadas = Notificaciones.objects.order_by('-fecha_cambio')[:3]
            self.stdout.write(f"  ✅ Order by fecha: {len(list(ordenadas))} registros")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  ❌ Error ORM preoperación: {e}"))
            traceback.print_exc()
        
        try:
            from postoperacion.models import NotificacionesPost
            
            # Consulta más básica posible
            count = NotificacionesPost.objects.count()
            self.stdout.write(f"  ✅ NotificacionesPost.objects.count(): {count}")
            
            # Consulta con limit
            primeras = NotificacionesPost.objects.all()[:3]
            self.stdout.write(f"  ✅ NotificacionesPost.objects.all()[:3]: {len(list(primeras))} registros")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  ❌ Error ORM postoperación: {e}"))
            traceback.print_exc()
    
    def probar_viewsets(self):
        self.stdout.write('\n🎯 PROBANDO VIEWSETS:')
        
        try:
            from preoperacion.views import NotificacionesViewSet
            from django.test import RequestFactory
            
            # Crear request falso
            factory = RequestFactory()
            request = factory.get('/preoperacion/notificaciones/')
            
            # Crear viewset
            viewset = NotificacionesViewSet()
            viewset.request = request
            
            # Probar get_queryset
            self.stdout.write("  🔍 Probando NotificacionesViewSet.get_queryset()...")
            queryset = viewset.get_queryset()
            count = queryset.count()
            self.stdout.write(f"  ✅ NotificacionesViewSet queryset: {count} registros")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  ❌ Error ViewSet preoperación: {e}"))
            traceback.print_exc()
        
        try:
            from postoperacion.views import NotificacionesPostViewSet
            from django.test import RequestFactory
            
            # Crear request falso
            factory = RequestFactory()
            request = factory.get('/postoperacion/notificaciones/')
            
            # Crear viewset
            viewset = NotificacionesPostViewSet()
            viewset.request = request
            
            # Probar get_queryset
            self.stdout.write("  🔍 Probando NotificacionesPostViewSet.get_queryset()...")
            queryset = viewset.get_queryset()
            count = queryset.count()
            self.stdout.write(f"  ✅ NotificacionesPostViewSet queryset: {count} registros")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  ❌ Error ViewSet postoperación: {e}"))
            traceback.print_exc()
        
        self.stdout.write('\n' + '=' * 80)
        self.stdout.write(self.style.SUCCESS('🎉 DIAGNÓSTICO COMPLETADO'))
        self.stdout.write('Si alguna parte falló, ahí está el problema. Si todo está verde, el problema es otro.')