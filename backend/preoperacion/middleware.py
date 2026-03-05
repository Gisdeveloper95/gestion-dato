# En preoperacion/middleware.py
from django.core.cache import cache
from django.http import HttpResponseTooManyRequests
import time

class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Solo aplicar a endpoints de detalles
        if '/preoperacion/detalles-insumo/' in request.path:
            client_ip = self.get_client_ip(request)
            cache_key = f"rate_limit_{client_ip}"
            
            # Permitir máximo 60 requests por minuto por IP
            requests = cache.get(cache_key, [])
            now = time.time()
            
            # Limpiar requests antiguos (más de 1 minuto)
            requests = [req_time for req_time in requests if now - req_time < 60]
            
            if len(requests) >= 60:
                return HttpResponseTooManyRequests(
                    "Demasiadas peticiones. Límite: 60 por minuto."
                )
            
            requests.append(now)
            cache.set(cache_key, requests, 60)
        
        return self.get_response(request)
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
class MunicipioPermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Agregar información de municipios permitidos al request
        if request.user.is_authenticated:
            if request.user.groups.filter(name='Administradores').exists():
                request.municipios_permitidos = 'todos'
            elif request.user.groups.filter(name='Profesionales_Seguimiento').exists():
                try:
                    profesional = request.user.profesional_seguimiento
                    municipios_ids = ProfesionalMunicipio.objects.filter(
                        cod_profesional=profesional
                    ).values_list('cod_municipio', flat=True)
                    request.municipios_permitidos = list(municipios_ids)
                except:
                    request.municipios_permitidos = []
            else:
                request.municipios_permitidos = []
        
        response = self.get_response(request)
        return response