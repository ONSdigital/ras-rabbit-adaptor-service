from json import dumps
import logging
import os

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.exceptions import MaxRetryError
from requests.packages.urllib3.util.retry import Retry
from sdc.rabbit.exceptions import BadMessageError, RetryableError
from structlog import wrap_logger

# Configure the number of retries attempted before failing call
session = requests.Session()
retries = Retry(total=5, backoff_factor=0.1)
session.mount('http://', HTTPAdapter(max_retries=retries))
session.mount('https://', HTTPAdapter(max_retries=retries))


class ResponseProcessor:

    def __init__(self, logger=None):
        self.logger = logger or wrap_logger(logging.getLogger(__name__))

    def process(self, msg):
        self.logger.ERROR("Processing")
        # decrypted_json = self.decrypt_message(msg)
        filename = msg.body['FILENAME']
        ras_ci_url = os.getenv('RAS_CI_UPLOAD_URL')
        files = {'file':
                 (filename,
                     open(filename, 'rb'),
                     'application/vnd.ms-excel',
                     {'Expires': '0'}),
                 }

        try:
            res = session.post(ras_ci_url,
                               files=files)
        except MaxRetryError:
            self.logger.error("Max retries exceeded (5)",
                              request_url=request_url)
        response_ok(res)

    def response_ok(self, res):
        request_url = res.url

        if res.status_code == 200 or res.status_code == 201:
            res_logger.info("Returned from service", response="ok", service=service)
            return

        elif res.status_code == 400:
            res_logger.info("Returned from service", response="client error", service=service)
            raise BadMessageError

        else:
            res_logger.error("Returned from service", response="service error", service=service)
            raise RetryableError
