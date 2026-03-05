# Crear archivo: preoperacion/management/commands/diagnostico_notificaciones.py

from django.core.management.base import BaseCommand
from datetime import datetime, timedelta
from django.db import connection

class Command(BaseCommand):
    help = 'Diagnóstico completo del sistema de notificaciones'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔍 DIAGNÓSTICO DEL SISTEMA DE NOTIFICACIONES'))
        self.stdout.write('=' * 60)
        
        # 1. Verificar existencia de tablas
        self.verificar_tablas()
        
        # 2. Contar registros por tabla
        self.contar_registros()
        
        # 3. Verificar índices
        self.verificar_indices()
        
        # 4. Probar consultas problemáticas
        self.probar_consultas()
        
        # 5. Verificar notificaciones de hoy
        self.verificar_notificaciones_hoy()
        
        self.stdout.write(self.style.SUCCESS('\n✅ Diagnóstico completado'))
    
    def verificar_tablas(self):
        self.stdout.write('\n📋 VERIFICANDO TABLAS:')
        
        with connection.cursor() as cursor:
            # Verificar tabla preoperación
            try:
                cursor.execute("SELECT COUNT(*) FROM notificaciones")
                count_pre = cursor.fetchone()[0]
                self.stdout.write(f"  ✅ Tabla 'notificaciones' existe: {count_pre} registros")
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  ❌ Error tabla 'notificaciones': {e}"))
            
            # Verificar tabla postoperación
            try:
                cursor.execute("SELECT COUNT(*) FROM notificaciones_post")
                count_post = cursor.fetchone()[0]
                self.stdout.write(f"  ✅ Tabla 'notificaciones_post' existe: {count_post} registros")
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  ❌ Error tabla 'notificaciones_post': {e}"))
    
    def contar_registros(self):
        self.stdout.write('\n📊 CONTANDO REGISTROS:')
        
        try:
            from preoperacion.models import Notificaciones
            total_pre = Notificaciones.objects.count()
            no_leidas_pre = Notificaciones.objects.filter(leido=False).count()
            hoy_pre = Notificaciones.objects.filter(
                fecha_cambio__date=datetime.now().date()
            ).count()
            
            self.stdout.write(f"  📈 Preoperación:")
            self.stdout.write(f"    - Total: {total_pre}")
            self.stdout.write(f"    - No leídas: {no_leidas_pre}")
            self.stdout.write(f"    - Hoy: {hoy_pre}")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  ❌ Error preoperación: {e}"))
        
        try:
            from postoperacion.models import NotificacionesPost
            total_post = NotificacionesPost.objects.count()
            no_leidas_post = NotificacionesPost.objects.filter(leido=False).count()
            hoy_post = NotificacionesPost.objects.filter(
                fecha_cambio__date=datetime.now().date()
            ).count()
            
            self.stdout.write(f"  📈 Postoperación:")
            self.stdout.write(f"    - Total: {total_post}")
            self.stdout.write(f"    - No leídas: {no_leidas_post}")
            self.stdout.write(f"    - Hoy: {hoy_post}")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  ❌ Error postoperación: {e}"))
    
    def verificar_indices(self):
        self.stdout.write('\n🔍 VERIFICANDO ÍNDICES:')
        
        with connection.cursor() as cursor:
            # Verificar índices en notificaciones
            try:
                cursor.execute("""
                    SELECT indexname FROM pg_indexes 
                    WHERE tablename = 'notificaciones' 
                    AND indexname LIKE '%fecha%'
                """)
                indices_pre = cursor.fetchall()
                self.stdout.write(f"  📋 Índices de fecha en 'notificaciones': {len(indices_pre)}")
                for idx in indices_pre:
                    self.stdout.write(f"    - {idx[0]}")
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"  ⚠️ No se pudieron verificar índices preoperación: {e}"))
            
            # Verificar índices en notificaciones_post
            try:
                cursor.execute("""
                    SELECT indexname FROM pg_indexes 
                    WHERE tablename = 'notificaciones_post' 
                    AND indexname LIKE '%fecha%'
                """)
                indices_post = cursor.fetchall()
                self.stdout.write(f"  📋 Índices de fecha en 'notificaciones_post': {len(indices_post)}")
                for idx in indices_post:
                    self.stdout.write(f"    - {idx[0]}")
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"  ⚠️ No se pudieron verificar índices postoperación: {e}"))
    
    def probar_consultas(self):
        self.stdout.write('\n🧪 PROBANDO CONSULTAS PROBLEMÁTICAS:')
        
        # Probar consulta con filtro de fecha
        try:
            from preoperacion.models import Notificaciones
            hoy = datetime.now().date()
            
            # Esta es la consulta que estaba fallando
            queryset = Notificaciones.objects.exclude(accion='sincronizar')
            queryset = queryset.filter(fecha_cambio__date=hoy)
            queryset = queryset.order_by('-fecha_cambio')
            count = queryset.count()
            
            self.stdout.write(f"  ✅ Consulta fecha preoperación: {count} registros")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  ❌ Error consulta preoperación: {e}"))
        
        try:
            from postoperacion.models import NotificacionesPost
            hoy = datetime.now().date()
            
            # Esta es la consulta que estaba fallando
            queryset = NotificacionesPost.objects.exclude(accion='sincronizar')
            queryset = queryset.filter(fecha_cambio__date=hoy)
            queryset = queryset.order_by('-fecha_cambio')
            count = queryset.count()
            
            self.stdout.write(f"  ✅ Consulta fecha postoperación: {count} registros")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  ❌ Error consulta postoperación: {e}"))
    
    def verificar_notificaciones_hoy(self):
        self.stdout.write('\n📅 VERIFICANDO NOTIFICACIONES DE HOY:')
        
        try:
            from preoperacion.models import Notificaciones
            from postoperacion.models import NotificacionesPost
            from datetime import datetime
            
            hoy = datetime.now().date()
            
            # Preoperación
            notif_pre_hoy = Notificaciones.objects.filter(
                fecha_cambio__date=hoy
            ).exclude(accion='sincronizar').order_by('-fecha_cambio')[:5]
            
            self.stdout.write(f"  📋 Preoperación hoy: {notif_pre_hoy.count()} registros")
            for notif in notif_pre_hoy:
                self.stdout.write(f"    - ID: {notif.id}, Tipo: {notif.tipo_entidad}, Acción: {notif.accion}")
            
            # Postoperación
            notif_post_hoy = NotificacionesPost.objects.filter(
                fecha_cambio__date=hoy
            ).exclude(accion='sincronizar').order_by('-fecha_cambio')[:5]
            
            self.stdout.write(f"  📋 Postoperación hoy: {notif_post_hoy.count()} registros")
            for notif in notif_post_hoy:
                self.stdout.write(f"    - ID: {notif.id}, Tipo: {notif.tipo_entidad}, Acción: {notif.accion}")
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  ❌ Error verificando notificaciones de hoy: {e}"))


# TAMBIÉN crear: postoperacion/management/commands/diagnostico_notificaciones.py
# (El mismo contenido, es para tenerlo en ambas apps)