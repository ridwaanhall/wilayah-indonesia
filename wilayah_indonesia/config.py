from decouple import config

# API Configuration
API_LOGIN_REQUIRED = config('API_LOGIN_REQUIRED', default=False, cast=bool)
API_ADVANCED_MODE = config('API_ADVANCED_MODE', default=False, cast=bool)

# Django REST Framework
REST_FRAMEWORK = {
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
    REST_FRAMEWORK['PAGE_SIZE'] = 100
