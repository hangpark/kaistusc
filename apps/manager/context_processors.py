from django.conf import settings

def development_ip(request):
    return {
        'development_ip': settings.DEVELOPMENT_IP
    }