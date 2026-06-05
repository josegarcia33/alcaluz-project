from django.utils.cache import patch_cache_control

class NoCacheMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Si el usuario no está autenticad vamo y evitamos la caché en el navegador
        if not request.user.is_authenticated:
            patch_cache_control(
                response, 
                no_cache=True, 
                must_revalidate=True, 
                no_store=True
            )
        return response