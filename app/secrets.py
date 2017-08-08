import json
import logging
import os

from sdc.crypto.secrets import SecretStore, validate_required_secrets

logger = logging.getLogger(name=__name__)


def load_secrets(key_purpose_submission, expected_secrets=[]):
    """Load secrets from a local yaml file."""

    logger.info("Loading keys from environment")
    with open(os.getenv('CI_SECRETS')) as fp:
        secrets = json.load(fp)
    logger.info("Loaded keys from environment")

    validate_required_secrets(secrets,
                              expected_secrets,
                              key_purpose_submission)

    secrets = SecretStore(secrets)
    return secrets
