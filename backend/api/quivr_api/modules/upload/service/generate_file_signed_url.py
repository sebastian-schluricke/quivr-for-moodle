import os
from multiprocessing import get_logger

from quivr_api.modules.dependencies import get_supabase_client
from supabase.client import Client

logger = get_logger()

SIGNED_URL_EXPIRATION_PERIOD_IN_SECONDS = 3600
EXTERNAL_SUPABASE_URL = os.getenv("EXTERNAL_SUPABASE_URL", None)
SUPABASE_URL = os.getenv("SUPABASE_URL", None)


class SignedUrlGenerationError(Exception):
    """Raised when signed URL generation fails."""

    pass


def generate_file_signed_url(path):
    supabase_client: Client = get_supabase_client()

    try:
        response = supabase_client.storage.from_("quivr").create_signed_url(
            path,
            SIGNED_URL_EXPIRATION_PERIOD_IN_SECONDS,
            options={
                "download": True,
                "transform": None,
            },
        )
        logger.info("RESPONSE SIGNED URL", response)

        # Check if response contains signedURL
        if response is None or "signedURL" not in response or response["signedURL"] is None:
            logger.error(f"Failed to generate signed URL for path: {path}, response: {response}")
            raise SignedUrlGenerationError(f"Could not generate signed URL for file: {path}")

        # Replace in the response the supabase url by the external supabase url in the object signedURL
        if EXTERNAL_SUPABASE_URL and SUPABASE_URL:
            response["signedURL"] = response["signedURL"].replace(
                SUPABASE_URL, EXTERNAL_SUPABASE_URL
            )
        return response
    except SignedUrlGenerationError:
        raise
    except Exception as e:
        logger.error(f"Error generating signed URL for path {path}: {e}")
        raise SignedUrlGenerationError(f"Error generating signed URL: {e}")
