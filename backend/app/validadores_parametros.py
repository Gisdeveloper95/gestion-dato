# app/validadores_parametros.py
"""
✅ ARCHIVO NUEVO - Copiar a backend/app/validadores_parametros.py

Validadores de parámetros seguros - Protección contra HTTP Parameter Pollution
"""

from rest_framework.exceptions import ValidationError
import re
import logging

logger = logging.getLogger(__name__)

class ParameterValidator:
    """Validación segura de parámetros para prevenir Parameter Pollution"""

    @staticmethod
    def get_single_param(request, param_name: str, required: bool = False, default=None):
        """Obtiene un parámetro asegurando que sea único (no múltiple)"""
        all_values = request.query_params.getlist(param_name)

        if not all_values:
            if required:
                raise ValidationError({param_name: f"El parámetro '{param_name}' es requerido"})
            return default

        if len(all_values) > 1:
            logger.warning(f"⚠️ Parameter Pollution detectado: '{param_name}' tiene {len(all_values)} valores: {all_values}")
            raise ValidationError({param_name: f"El parámetro '{param_name}' no puede tener múltiples valores"})

        return all_values[0]


class IntegerParameterValidator(ParameterValidator):
    """Valida parámetros enteros"""

    @staticmethod
    def get_integer_param(request, param_name: str, required: bool = False, default=None, min_value=None, max_value=None):
        """Obtiene y valida un parámetro entero"""
        value_str = ParameterValidator.get_single_param(request, param_name, required, default=None)

        if value_str is None:
            return default

        try:
            value = int(value_str)
        except (ValueError, TypeError):
            raise ValidationError({param_name: f"'{param_name}' debe ser un número entero"})

        if min_value is not None and value < min_value:
            raise ValidationError({param_name: f"'{param_name}' debe ser mayor o igual a {min_value}"})

        if max_value is not None and value > max_value:
            raise ValidationError({param_name: f"'{param_name}' debe ser menor o igual a {max_value}"})

        return value


class StringParameterValidator(ParameterValidator):
    """Valida parámetros string"""

    @staticmethod
    def get_string_param(request, param_name: str, required: bool = False, default=None, max_length: int = 255, allowed_values=None):
        """Obtiene y valida un parámetro string"""
        value = ParameterValidator.get_single_param(request, param_name, required, default)

        if value is None:
            return default

        if len(value) > max_length:
            raise ValidationError({param_name: f"'{param_name}' excede la longitud máxima de {max_length} caracteres"})

        if allowed_values and value not in allowed_values:
            raise ValidationError({param_name: f"'{param_name}' debe ser uno de: {allowed_values}"})

        return value


class BooleanParameterValidator(ParameterValidator):
    """Valida parámetros booleanos"""

    TRUTHY_VALUES = ['true', '1', 'yes', 'on']
    FALSY_VALUES = ['false', '0', 'no', 'off']

    @staticmethod
    def get_boolean_param(request, param_name: str, required: bool = False, default=None):
        """Obtiene y valida un parámetro booleano"""
        value_str = ParameterValidator.get_single_param(request, param_name, required, default=None)

        if value_str is None:
            return default

        value_lower = value_str.lower()

        if value_lower in BooleanParameterValidator.TRUTHY_VALUES:
            return True
        elif value_lower in BooleanParameterValidator.FALSY_VALUES:
            return False
        else:
            raise ValidationError({param_name: f"'{param_name}' debe ser true/false"})


class PathParameterValidator(ParameterValidator):
    """Valida parámetros de ruta (previene Path Traversal)"""

    DANGEROUS_PATTERNS = ['..', '~', '/etc/', '/proc/', 'C:', '\\\\']

    @staticmethod
    def get_safe_path_param(request, param_name: str, required: bool = False, default=None):
        """Obtiene y valida un parámetro de ruta de forma segura"""
        value = ParameterValidator.get_single_param(request, param_name, required, default)

        if value is None:
            return default

        value_lower = value.lower()
        for pattern in PathParameterValidator.DANGEROUS_PATTERNS:
            if pattern.lower() in value_lower:
                logger.warning(f"⚠️ Path Traversal attempt detectado en '{param_name}': {value}")
                raise ValidationError({param_name: f"Ruta inválida detectada en '{param_name}'"})

        return value
