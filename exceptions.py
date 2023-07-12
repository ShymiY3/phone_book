from fastapi import HTTPException, status, Request
from fastapi.responses import JSONResponse, RedirectResponse


class FormException(HTTPException):
    pass

async def form_exception_handler(request: Request, exc: FormException):
    if request.headers.get("accept") == "application/json":
        # Return JSON response for API clients
        return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)
    else:
        # Render the form page with error message for browser clients
        return RedirectResponse(f'?alert=danger&mess={exc.detail}', status_code=status.HTTP_302_FOUND, )
