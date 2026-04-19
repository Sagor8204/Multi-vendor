from rest_framework.views import exception_handler
from .utils import api_response

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        return api_response(
            success=False,
            message=str(exc.detail) if hasattr(exc, 'detail') else "Something went wrong",
            data=response.data,
            status=response.status_code
        )

    return response