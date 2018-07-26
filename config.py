import os


class Config:

    HOST = os.getenv('HOST', 'localhost')
    CI_SECRETS = os.getenv('CI_SECRETS')
    COLLEX_ID = os.getenv('COLLEX_ID')
    RAS_CI_UPLOAD_URL = os.getenv('RAS_CI_UPLOAD_URL',
                                  'http://{}:8002/'
                                  'collection-instrument-api'
                                  '/1.0.2/upload/{}/{}')
    SECURITY_USER_NAME = os.getenv('SECURITY_USER_NAME')
    SECURITY_USER_PASSWORD = os.getenv('SECURITY_USER_PASSWORD')
    BASIC_AUTH = (SECURITY_USER_NAME, SECURITY_USER_PASSWORD)

    # Rabbitmq details

    RABBITMQ_DEFAULT_USER = os.getenv('RABBITMQ_DEFAULT_USER', 'guest')
    RABBITMQ_DEFAULT_PASS = os.getenv('RABBITMQ_DEFAULT_PASS', 'guest')
    RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')
    RABBITMQ_PORT = os.getenv('RABBITMQ_PORT', 5672)
    RABBITMQ_DEFAULT_VHOST = os.getenv('RABBITMQ_DEFAULT_VHOST', '%2f')
    RABBIT_URL = 'amqp://{}:{}@{}:{}/{}'.format(
        RABBITMQ_DEFAULT_USER, RABBITMQ_DEFAULT_PASS,
        RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_DEFAULT_VHOST)
