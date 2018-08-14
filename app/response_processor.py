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

from config import Config
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

        collex_id = os.getenv('COLLEX_ID')

        files = {'file':
                 (filename,
                  file,
                  'application/vnd.' +
                  'openxmlformats-officedocument.spreadsheetml.sheet',
                  ),
                 }

        try:
            url = Config.RAS_CI_UPLOAD_URL.format(os.getenv('HOST'), collex_id, filename)
            self.logger.info('Posting files to ras',
                             ex_id=collex_id,
                             filename=filename,
                             url=url)
            res = session.post(url, auth=Config.BASIC_AUTH, files=files)
            self.logger.info("Response", text=res.text)

            self.response_ok(res)

        except ConnectionError:
            self.logger.error("Connection error")
            raise RetryableError

    def response_ok(self, res):

        if res.status_code == 200 or res.status_code == 201:
            self.logger.info("Returned from service",
                             response="ok")
            return

        elif res.status_code == 400:
            self.logger.info("Returned from service",
                             response="client error")
            self.logger.info("Response details",
                             response_status=res.status_code,
                             response_content=res.content)
            raise BadMessageError

        else:
            self.logger.error("Returned from service",
                              response="service error")
            self.logger.error("Response details",
                              response_status=res.status_code,
                              response_content=res.content)
            raise RetryableError
