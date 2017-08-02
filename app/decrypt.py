import binascii
import logging

from cryptography import exceptions
from sdc.crypto.decrypter import decrypt as sdc_decrypt
from sdc.crypto.invalid_token_exception import InvalidTokenException
from structlog import wrap_logger

logger = logging.getLogger(name=__name__)
logger = wrap_logger(logger)


class DecryptionError(Exception):
    """Raised when a decryption attempt is unsuccessful"""


def decrypt(data, secret_store, key_purpose_submission):

    try:
        logger.info("Received some data")
        data_bytes = data.decode('UTF8')
        decrypted_json = sdc_decrypt(data_bytes,
                                     secret_store,
                                     key_purpose_submission)
    except (
        exceptions.UnsupportedAlgorithm,
        exceptions.InvalidKey,
        exceptions.AlreadyFinalized,
        exceptions.InvalidSignature,
        exceptions.NotYetFinalized,
        exceptions.AlreadyUpdated,
    ) as e:
        logger.exception(e)
        raise DecryptionError("Decryption failure")
    except binascii.Error as e:
        logger.exception(e)
        raise DecryptionError("Data was not base64 encoded")
    except InvalidTokenException as e:
        logger.exception(e)
        raise DecryptionError("Invalid token")
    except ValueError as e:
        logger.exception(e)
        raise DecryptionError("Value error")
    except Exception as e:
        logger.exception(e)
        raise e
    else:
        bound_logger = logger.bind(tx_id=decrypted_json.get("tx_id"))
        bound_logger.info("Received data succesfully decrypted")
        return decrypted_json
