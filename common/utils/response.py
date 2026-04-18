from rest_framework.response import Response

def api_response(success=True, message="", data=None, erros=None, status=200):
    Return Response({
        "success": success,
        "message": message,
        "data": data,
        "erros": erros
    }, status=status)