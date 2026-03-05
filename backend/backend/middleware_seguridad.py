# backend/middleware_seguridad.py
"""
Middlewares de seguridad para protección contra:
- Host Header Injection
- HTTP Parameter Pollution
"""

from django.http import HttpResponseBadRequest, JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class SecurityHeaderValidationMiddleware(MiddlewareMixin):
    """Protección contra Host Header Injection"""

    def process_request(self, request):
        host_header = request.META.get('HTTP_HOST', '')

        if not host_header:
            logger.warning("⚠️ Request sin header Host")
            return HttpResponseBadRequest("Invalid or missing Host header")

        if ',' in host_header:
            logger.warning(f"⚠️ Múltiples headers Host detectados: {host_header}")
            return HttpResponseBadRequest("Multiple Host headers not allowed")

        caracteres_sospechosos = ['<', '>', '"', "'", '\\', '\n', '\r', '\t']
        if any(char in host_header for char in caracteres_sospechosos):
            logger.warning(f"⚠️ Caracteres sospechosos en Host header: {host_header}")
            return HttpResponseBadRequest("Invalid characters in Host header")

        return None


class ParameterPollutionProtectionMiddleware(MiddlewareMixin):
    """Protección contra HTTP Parameter Pollution"""

    ACTION = getattr(settings, 'PARAMETER_POLLUTION_ACTION', 'log_only')
    ALLOWED_DUPLICATES = getattr(settings, 'ALLOWED_DUPLICATE_PARAMS', ['filter', 'tag', 'category'])

    def process_request(self, request):
        """Validar parámetros GET"""
        duplicates = self._find_duplicates(request.GET)

        if duplicates:
            real_duplicates = [param for param in duplicates if param not in self.ALLOWED_DUPLICATES]

            if real_duplicates:
                logger.warning(
                    f"⚠️ Parameter Pollution detectado en GET: {real_duplicates} | "
                    f"URL: {request.path} | Usuario: {request.user.username if request.user.is_authenticated else 'Anónimo'}"
                )

                if self.ACTION == 'reject':
                    return JsonResponse({
                        'error': 'Invalid request: duplicate parameters not allowed',
                        'duplicate_parameters': real_duplicates
                    }, status=400)

        return None

    def process_view(self, request, view_func, view_args, view_kwargs):
        """Validar parámetros POST/PUT/PATCH"""
        if request.method in ['POST', 'PUT', 'PATCH']:
            duplicates = self._find_duplicates(request.POST)

            if duplicates:
                real_duplicates = [param for param in duplicates if param not in self.ALLOWED_DUPLICATES]

                if real_duplicates:
                    logger.warning(
                        f"⚠️ Parameter Pollution detectado en {request.method}: {real_duplicates} | "
                        f"URL: {request.path}"
                    )

                    if self.ACTION == 'reject':
                        return JsonResponse({
                            'error': f'Invalid request: duplicate parameters in {request.method} body',
                            'duplicate_parameters': real_duplicates
                        }, status=400)

        return None

    def _find_duplicates(self, query_dict):
        """Encuentra parámetros que tienen múltiples valores"""
        duplicates = []
        for key in query_dict.keys():
            values = query_dict.getlist(key)
            if len(values) > 1:
                duplicates.append(key)
        return duplicates
