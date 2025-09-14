from django.conf import settings


def analytics(request):
    return {
        'GTM_CONTAINER_ID': getattr(settings, 'GTM_CONTAINER_ID', ''),
        'GA_MEASUREMENT_ID': getattr(settings, 'GA_MEASUREMENT_ID', ''),
        'RECAPTCHA_SITE_KEY': getattr(settings, 'RECAPTCHA_SITE_KEY', ''),
        'RECAPTCHA_ENABLED': getattr(settings, 'RECAPTCHA_ENABLED', False),
    }
