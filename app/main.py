import os
import sys

from sdc.rabbit import MessageConsumer, QueuePublisher
import tornado.ioloop
import tornado.web

from .logger_config import logger_initial_config
from .response_processor import ResponseProcessor

logger_initial_config(service_name='ras-rabbit-adapter')


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.set_status(200)
        self.write("ok")


def make_app():
    return tornado.web.Application([
        (r"/info", MainHandler),
    ])


def main():

    # Set tornado to listen to healthcheck endpoint
    app = make_app()
    server = tornado.httpserver.HTTPServer(app)
    server.bind(os.getenv('PORT', '8080'))
    server.start(1)

    rp = ResponseProcessor("outbound")
    default_amqp_url = 'amqp://guest:guest@0.0.0.0:5672/%2f'
    quarantine_publisher = QueuePublisher([os.getenv('RABBIT_URL',
                                                     default_amqp_url)],
                                          os.getenv('RABBIT_QUARANTINE_QUEUE',
                                                    'QUARANTINE_TEST'),
                                          )

    message_consumer = MessageConsumer(
        durable_queue=True,
        exchange=os.getenv('RABBIT_EXCHANGE', 'test'),
        exchange_type=os.getenv('EXCHANGE_TYPE', 'topic'),
        rabbit_queue=os.getenv('RABBIT_QUEUE', 'test'),
        rabbit_urls=[os.getenv('RABBIT_URLS', default_amqp_url)],
        quarantine_publisher=quarantine_publisher,
        process=rp.process,
        check_tx_id=False,
    )

    message_consumer.run()
    return 0


if __name__ == "__main__":
    rv = main()
    sys.exit(rv)
