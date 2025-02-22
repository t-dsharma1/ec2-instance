import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from passlib.context import CryptContext
from prometheus_client import make_asgi_app

from connectai.handlers import exception, get_or_create_logger
from connectai.handlers.api.archive_manager import periodic_task
from connectai.handlers.api.routers import (
    chat_view,
    flow_builder,
    superset_login,
    telcoapi,
)
from connectai.handlers.api.routers.public import whatsapp
from connectai.handlers.utils.api_idp import idp
from connectai.modules.services.scheduler import scheduler
from connectai.settings import GLOBAL_SETTINGS

logger = get_or_create_logger(logger_name="FastAPI")


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Load the ML model
    scheduler.start()

    # Periodic task to archive the conversation data
    days_to_exclude = 14
    archive_task = asyncio.create_task(periodic_task(days_to_exclude))

    try:
        yield
    finally:
        # Clean up the ML models and release the resources
        scheduler.shutdown()

        # Cancel the periodic archive task
        archive_task.cancel()
        try:
            await archive_task
        except asyncio.CancelledError:
            logger.info("Periodic archive task was cancelled successfully.")


app = FastAPI(lifespan=lifespan)

# Only selective hosts are trusted for incoming requests.
# In particular, a host like connectai-api.public.* is _NOT_ trusted and blocked from
# accessing API routes meant to be internal, or at least behind an IP restricted ELB.
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=[
        # external API requests coming in through DNS, ELB and Traefik ingress:
        f"genie-api.{GLOBAL_SETTINGS.environment.value}.{GLOBAL_SETTINGS.platform_base_domain}",
        # cluster-internal API requests coming from the frontend-services, skipping DNS/ingress:
        "*.svc.cluster.local",
        *GLOBAL_SETTINGS.add_trusted_hostnames,
    ],
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

idp.add_swagger_config(app)

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Access-Control-Allow-Origin"],
)

app.include_router(telcoapi.router)
app.include_router(chat_view.router)
app.include_router(flow_builder.router)
app.include_router(superset_login.router)

app.mount("/metrics", make_asgi_app())

exception.add_exception_handlers(app)

# Add WhatsApp router
public_app = FastAPI()
public_app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=[
        f"genie-api.public.{GLOBAL_SETTINGS.platform_base_domain}.atlas-platform.io",
        *GLOBAL_SETTINGS.add_trusted_hostnames,
    ],
)
public_app.include_router(whatsapp.router)

app.mount("/public", public_app)
