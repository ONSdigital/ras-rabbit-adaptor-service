import os
import unittest


class TestMain(unittest.TestCase):

    def setUp():
        url = 'http://localhost:8080/1.0.2/upload/{}/upload.txt'
        os.environ['RAS_CI_UPLOAD_URL'] = url
        os.environ['']
