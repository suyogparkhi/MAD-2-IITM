from flask_caching import Cache
import os   

cache = Cache(
    config = {
        'CACHE_TYPE': 'redis',
        'CACHE_REDIS_URL': os.getenv('REDIS_URL', 'redis://localhost:6379/1'),
        'CACHE_DEFAULT_TIMEOUT': 300
    }
)

SERVICE_CACHE_KEY = 'all_services'
SERVICE_DETAIL_CACHE_KEY = 'service_{}'
PROFESSIONAL_LIST_CACHE_KEY = 'proffesionals_{}'
DASHBOARD_STATS_CACHE_KEY = 'dashboard_stats_{}'

def init_cache(app):
    cache.init_app(app)
    return cache

def clear_service_cache(service_id = None):
    if service_id:
        cache.delete(SERVICE_DETAIL_CACHE_KEY.format(service_id))
        cache.delete(PROFESSIONAL_LIST_CACHE_KEY.format(f'service_{service_id}'))

    cache.delete(SERVICE_CACHE_KEY)

def clear_professional_cache(professional_id=None, service_id=None):
    """Clear professional-related caches"""
    if professional_id:
        cache.delete(f'professional_{professional_id}')
    
    if service_id:
        cache.delete(PROFESSIONAL_LIST_CACHE_KEY.format(f'service_{service_id}'))
    
    cache.delete(PROFESSIONAL_LIST_CACHE_KEY.format('all'))

def clear_dashboard_cache(user_role, user_id=None):
    """Clear dashboard stats cache"""
    if user_id:
        cache.delete(DASHBOARD_STATS_CACHE_KEY.format(f'{user_role}_{user_id}'))
    else:
        cache.delete(DASHBOARD_STATS_CACHE_KEY.format(user_role))
