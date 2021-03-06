import json
import logging
import os

from sdc.crypto.key_store import KeyStore

logger = logging.getLogger(name=__name__)


def load_secrets(key_purpose_submission, expected_secrets=[]):
    """Load secrets from a local yaml file."""

    logger.info("Loading keys from environment")
    json_string = os.getenv('CI_SECRETS')
    secrets = json.loads(json_string)
    logger.info("Loaded keys from environment")

    secrets = KeyStore(secrets)

    return secrets
