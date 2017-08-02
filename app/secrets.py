import logging
import os

from sdc.crypto.secrets import SecretStore, validate_required_secrets
import yaml

logger = logging.getLogger(name=__name__)


def load_secrets(key_purpose_submission, expected_secrets=[]):
    """Load secrets from a local yaml file."""

    with open(os.getenv('CI_SECRETS_FILE'), 'r') as file:
        secrets = yaml.safe_load(file)

    validate_required_secrets(secrets,
                              expected_secrets,
                              key_purpose_submission)

    secrets = SecretStore(secrets)
    return secrets
