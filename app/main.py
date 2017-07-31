import logging
import os
import sys

from sdc.rabbit import AsyncConsumer
from sdc.rabbit import MessageConsumer
from sdc.rabbit import QueuePublisher
import tornado.ioloop
import tornado.web

from response_processor import ResponseProcessor


def logger_initial_config(service_name=None,
                          log_level=None,
                          logger_format=None,
                          logger_date_format=None):
    '''Set initial logging configurations.
    :param service_name: Name of the service
    :type logger: String
    :param log_level: A string or integer corresponding to a Python logging level
    :type log_level: String
    :param logger_format: A string defining the format of the logs
    :type log_level: String
    :param logger_date_format: A string defining the format of the date/time in the logs
    :type log_level: String
    :rtype: None
    '''
    if not log_level:
        log_level = os.getenv('LOGGING_LEVEL', 'DEBUG')
    if not logger_format:
        logger_format = (
            "%(asctime)s.%(msecs)06dZ|"
            "%(levelname)s: {}: %(message)s"
        ).format(service_name)
    if not logger_date_format:
        logger_date_format = os.getenv('LOGGING_DATE_FORMAT', "%Y-%m-%dT%H:%M:%S")

    logging.basicConfig(level=log_level,
                        format=logger_format,
                        datefmt=logger_date_format)

logging.getLogger('pika').setLevel('ERROR')
logger_initial_config()
logger = logging.getLogger(__name__)


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.set_status(200)
        self.write("ok")


def make_app():
    return tornado.web.Application([
        (r"/healthcheck", MainHandler),
    ])


def main():
    # Create the API service
    app = make_app()
    app.listen('8089')

    async_consumer = AsyncConsumer(
        durable_queue=True,
        exchange=os.getenv('RABBIT_EXCHANGE', 'test'),
        exchange_type=os.getenv('EXCHANGE_TYPE', 'topic'),
        rabbit_queue=os.getenv('RABBIT_QUEUE', 'test'),
        rabbit_urls=os.getenv('RABBIT_URLS', ['amqp://guest:guest@0.0.0.0:5672/%2f']),
    )

    quarantine_publisher = QueuePublisher(os.getenv('RABBIT_URL',
                                                    ['amqp://guest:guest@0.0.0.0:5672/%2f']),
                                          os.getenv('RABBIT_QUARANTINE_QUEUE',
                                                    'QUARANTINE_TEST'),
                                          )

    rp = ResponseProcessor(logger=logger)

    message_consumer = MessageConsumer(
        async_consumer,
        quarantine_publisher,
        process=rp.process,
    )

    message_consumer._consumer.run()
    return 0

if __name__ == "__main__":
    rv = main()
    sys.exit(rv)
