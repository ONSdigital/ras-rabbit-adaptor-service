from base64 import standard_b64decode
import logging
import os

import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectionError
from urllib3.util.retry import Retry
from sdc.rabbit.exceptions import BadMessageError, RetryableError
from sdc.crypto.decrypter import decrypt as sdc_decrypt
from structlog import wrap_logger

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

    def process(self, msg, tx_id=None):

        try:
            self.logger.info("Received some data")
            decrypted_json = sdc_decrypt(msg,
                                         self.secret_store,
                                         self.key_purpose_submission)

        except Exception as e:
            self.logger.error("Decryption error occurred. "
                              "Quarantining message.",
                              e=str(e))
            raise BadMessageError

        filename = decrypted_json.get('filename')
        file = standard_b64decode(decrypted_json.get('file').encode('UTF8'))

        ras_ci_url = os.getenv('RAS_CI_UPLOAD_URL')

        files = {'file':
                 (filename,
                  file,
                  'application/vnd.' +
                  'openxmlformats-officedocument.spreadsheetml.sheet',
                  ),
                 }

        try:
            self.logger.info('Posting files to ras')
            res = session.post(ras_ci_url.format(filename),
                               files=files)
        except ConnectionError:
            self.logger.error("Max retries exceeded (5)")

            raise RetryableError

        self.response_ok(res)

    def response_ok(self, res):

        if res.status_code == 200 or res.status_code == 201:
            self.logger.info("Returned from service",
                             response="ok")
            return

        elif res.status_code == 400:
            self.logger.info("Returned from service",
                             response="client error")
            raise BadMessageError

        else:
            self.logger.error("Returned from service",
                              response="service error")
            raise RetryableError
