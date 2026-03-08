from decouple import config
from typing import Any

# API Configuration
API_LOGIN_REQUIRED = config('API_LOGIN_REQUIRED', default=False, cast=bool)
API_ADVANCED_MODE = config('API_ADVANCED_MODE', default=False, cast=bool)

# Django REST Framework
DEBUG_MODE = config('DEBUG', default=False, cast=bool)

if DEBUG_MODE:
    REST_FRAMEWORK: dict[str, Any] = {
        'DEFAULT_PERMISSION_CLASSES': [
            'rest_framework.permissions.IsAuthenticated'
            if API_LOGIN_REQUIRED
            else 'rest_framework.permissions.AllowAny'
        ],
        'DEFAULT_RENDERER_CLASSES': [
            'rest_framework.renderers.JSONRenderer',
            'rest_framework.renderers.BrowsableAPIRenderer',
        ],
    }

    if API_ADVANCED_MODE:
        REST_FRAMEWORK['DEFAULT_PAGINATION_CLASS'] = 'rest_framework.pagination.PageNumberPagination'
        REST_FRAMEWORK['PAGE_SIZE'] = config('API_PAGE_SIZE', default=100, cast=int)
else:
    REST_FRAMEWORK: dict[str, Any] = {
        'DEFAULT_PERMISSION_CLASSES': [
            'rest_framework.permissions.AllowAny'
        ],
        'DEFAULT_RENDERER_CLASSES': [
            'rest_framework.renderers.JSONRenderer',
        ],
    }
