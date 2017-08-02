import logging
import os

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.exceptions import MaxRetryError
from requests.packages.urllib3.util.retry import Retry
from sdc.rabbit.exceptions import BadMessageError, RetryableError
from structlog import wrap_logger

from .decrypt import decrypt, DecryptionError
from .secrets import load_secrets

# Configure the number of retries attempted before failing call
session = requests.Session()
retries = Retry(total=5, backoff_factor=0.1)
session.mount('http://', HTTPAdapter(max_retries=retries))
session.mount('https://', HTTPAdapter(max_retries=retries))


class ResponseProcessor:

    def __init__(self,
                 key_purpose_submission,
                 expected_secrets=[],
                 logger=None):

        self.key_purpose_submission = key_purpose_submission
        self.secret_store = load_secrets(key_purpose_submission,
                                         expected_secrets)
        self.logger = logger or wrap_logger(logging.getLogger(__name__))

    def process(self, msg):
        try:
            data = decrypt(msg, self.secret_store, self.key_purpose_submission)
        except DecryptionError:
            self.logger.error("Decryption error. Quarantining msg")
            raise BadMessageError
        except Exception:
            self.logger.error("Unknown exception occurred. Quarantining message.")
            raise BadMessageError

        filename = data.get('filename')
        file = data.get('file')

        ras_ci_url = os.getenv('RAS_CI_UPLOAD_URL')

        files = {'file':
                 (filename,
                     open(file, 'rb'),
                     'application/octet-stream',
                     {'Expires': '0'}),
                 }

        try:
            logger.info('Posting files to ras')
            res = session.post(ras_ci_url,
                               files=files)
        except MaxRetryError:
            self.logger.error("Max retries exceeded (5)",
                              request_url=res.url)
        self.response_ok(res)

    def response_ok(self, res):

        if res.status_code == 200 or res.status_code == 201:
            logger.info("Returned from service",
                        response="ok",
                        service=service)
            return

        elif res.status_code == 400:
            logger.info("Returned from service",
                        response="client error",
                        service=service)
            raise BadMessageError

        else:
            logger.error("Returned from service",
                         response="service error",
                         service=service)
            raise RetryableError
