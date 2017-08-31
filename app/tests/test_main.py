import base64
import json
import logging
import os
import unittest

from sdc.crypto.encrypter import encrypt
from sdc.crypto.secrets import SecretStore
from sdc.rabbit.exceptions import BadMessageError, RetryableError
from requests.models import Response
from structlog import wrap_logger

from ..response_processor import ResponseProcessor


def to_bytes(bytes_or_str):
    if isinstance(bytes_or_str, str):
        value = bytes_or_str.encode()
    else:
        value = bytes_or_str
    return value


def encrpyter(data,
              secrets_file='app/tests/encrypter_secrets.json',
              key_purpose='ci_uploads'):
    with open(secrets_file) as fp:
        secrets = json.loads(fp.read())

    secret_store = SecretStore(secrets)
    print(secret_store.__dict__)
    return encrypt(data, secret_store=secret_store, key_purpose=key_purpose)


class TestMain(unittest.TestCase):

    def setUp(self):
        url = 'http://localhost:9999'
        ResponseProcessor.RAS_CI_UPLOAD_URL = url
        with open('app/tests/secrets.json') as fp:
            secrets = fp.read()

        os.environ['CI_SECRETS'] = secrets
        print(os.getenv('CI_SECRETS'))
        self.logger = wrap_logger(logging.getLogger(__name__))
        self.response_processor = ResponseProcessor('ci_uploads',
                                                    logger=self.logger)

    def test_response_processor_init(self):
        self.assertEqual(self.response_processor.key_purpose_submission,
                         'ci_uploads')
        self.assertEqual(self.response_processor.logger, self.logger)

    def test_process_unknown_exception(self):
        binary_data = b'\x00\xFF\x00\xFF'

        with self.assertRaises(BadMessageError):
            with self.assertLogs(level='ERROR') as cm:
                self.response_processor.process(binary_data)

        self.assertIn("Decryption error occurred. Quarantining message.",
                      cm[0][0].message)

    def test_process_max_retry_error(self):
        binary_data = b'\x00\xFF\x00\xFF'
        file = base64.standard_b64encode(binary_data).decode("ascii")
        data = {'filename': 'somefile',
                'file': file,
                }

        encrypted_message = encrpyter(data)

        with self.assertRaises(RetryableError):
            self.response_processor.process(encrypted_message)

    def test_response_ok_200(self):

        res = Response()
        res.status_code = 200

        returned_response = self.response_processor.response_ok(res)
        self.assertEqual(returned_response, None)

    def test_response_ok_201(self):
        res = Response()
        res.status_code = 201

        returned_response = self.response_processor.response_ok(res)
        self.assertEqual(returned_response, None)

    def test_response_ok_400(self):
        res = Response()
        res.status_code = 400

        with self.assertRaises(BadMessageError):
            self.response_processor.response_ok(res)

    def test_response_ok_500(self):
        res = Response()
        res.status_code = 500

        with self.assertRaises(RetryableError):
            self.response_processor.response_ok(res)
