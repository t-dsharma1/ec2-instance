from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from genie_core.utils import logging

logger = logging.get_or_create_logger(logger_name=__name__)


def add_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        # Retrieve the client's IP address
        client_host = request.client.host
        # Retrieve the request body asynchronously
        body = await request.body()
        body_str = body.decode("utf-8")  # Assuming the body is in UTF-8
        # Format the exception string
        exc_str = f"{exc}".replace("\n", " ").replace("   ", " ")
        # Log the IP and the exception with the request body
        logger.error(f"Source IP: {client_host}, Request Body: {body_str}, Error: {exc_str}")
        # Prepare the JSON response
        content = {"status_code": 10422, "message": exc_str, "data": None}
        return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
