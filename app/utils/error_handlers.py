import traceback
import falcon
import uuid
from app.config.config import ENVIRONMENT
from app.utils.logger import logger


def generic_error_handler(req, resp, ex, params):
    """Catch-all error handler for unexpected exceptions."""

    # If the error is an HTTPError, just re-raise it
    if isinstance(ex, falcon.HTTPError):
        raise ex

    # Generate unique error ID
    error_id = str(uuid.uuid4())

    # Always log full error details
    logger.error(f"[{error_id}] Unhandled exception", exc_info=ex)

    # For LOCAL (developer mode)
    if ENVIRONMENT == "develop":
        tb_list = traceback.format_exception(type(ex), ex, ex.__traceback__)
        traceback_clean = [line.rstrip("\n") for line in tb_list]

        # OPTIONAL: log traceback separately (lebih mudah dibaca)
        logger.error(f"[{error_id}] Traceback:\n" + "".join(tb_list))

        raise falcon.HTTPInternalServerError(
            title="Internal Server Error",
            description={
                "message": str(ex),
                "error_id": error_id,
                "traceback": traceback_clean,
            },
        )

    # For DEVELOPMENT / GK-STAGE / PRODUCTION
    raise falcon.HTTPInternalServerError(
        title="Internal Server Error",
        description=(
            "An unexpected error occurred. "
            f"Please provide error ID: {error_id}."
        ),
    )

def handle_404(req, resp, ex, params):
    """Standard 404 handler for non-existing endpoints."""
    raise falcon.HTTPNotFound(description="The requested API endpoint does not exist.")


def register_error_handlers(app):
    app.add_error_handler(falcon.HTTPNotFound, handle_404)
    app.add_error_handler(Exception, generic_error_handler)