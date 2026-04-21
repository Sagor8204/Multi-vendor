from rest_framework.views import exception_handler
from rest_framework.exceptions import ValidationError
from .response import api_response

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        # For validation errors, extract the first message to make it cleaner
        message = "Something went wrong"
        if isinstance(exc, ValidationError):
            message = "Validation failed"
            # Try to get the first error message from the detail dictionary/list
            if isinstance(exc.detail, dict):
                # Get the first key's first error message
                first_key = next(iter(exc.detail))
                first_error = exc.detail[first_key]
                if isinstance(first_error, list) and len(first_error) > 0:
                    message = str(first_error[0])
                else:
                    message = str(first_error)
            elif isinstance(exc.detail, list) and len(exc.detail) > 0:
                message = str(exc.detail[0])
        elif hasattr(exc, 'detail'):
            # For other exceptions like AuthenticationFailed, etc.
            if isinstance(exc.detail, dict):
                 message = str(next(iter(exc.detail.values())))
            else:
                 message = str(exc.detail)

        return api_response(
            success=False,
            message=message,
            errors=response.data,
            status=response.status_code
        )

    return response