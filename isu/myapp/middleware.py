import logging
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger('django')

class LoggingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        ip = self.get_client_ip(request)
        # Передаем дополнительные поля через extra
        logger.info(
            "Request received",
            extra={'ip': ip if ip else 'unknown', 'path': request.path if request.path else 'unknown'}
        )
        return None

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip