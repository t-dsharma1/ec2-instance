from fastapi import FastAPI, Request, Response, status
from jose import JWTError
from jose.exceptions import JWTClaimsError
from jwt import ExpiredSignatureError


def add_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(ExpiredSignatureError)
    def expired_signature_handler(request: Request, exc: ExpiredSignatureError) -> Response:
        return Response(status_code=status.HTTP_401_UNAUTHORIZED)

    @app.exception_handler(JWTError)
    def jwt_error_handler(request: Request, exc: ExpiredSignatureError) -> Response:
        return Response(status_code=status.HTTP_401_UNAUTHORIZED)

    @app.exception_handler(JWTClaimsError)
    def jwt_claims_error_handler(request: Request, exc: ExpiredSignatureError) -> Response:
        return Response(status_code=status.HTTP_403_FORBIDDEN)
