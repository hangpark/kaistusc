from django.conf import settings

def development_ip(request):
    return {
        'development_ip': getattr(settings, 'DEVELOPMENT_IP', False)
    }
