from fastapi import FastAPI

from . import auth, validation


def add_exception_handlers(app: FastAPI) -> None:
    validation.add_exception_handlers(app)
    auth.add_exception_handlers(app)
