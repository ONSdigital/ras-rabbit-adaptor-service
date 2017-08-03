import os
import sys

from sdc.rabbit import MessageConsumer, QueuePublisher
import tornado.ioloop
import tornado.web

from app.response_processor import ResponseProcessor


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.set_status(200)
        self.write("ok")


def make_app():
    return tornado.web.Application([
        (r"/healthcheck", MainHandler),
    ])


def main():

    # Set tornado to listen to healthcheck endpoint
    app = make_app()
    app.listen(os.getenv('PORT', '8080'))

    rp = ResponseProcessor("ci_uploads")
    default_amqp_url = 'amqp://guest:guest@0.0.0.0:5672/%2f'
    quarantine_publisher = QueuePublisher(os.getenv('RABBIT_URL',
                                                    [default_amqp_url]),
                                          os.getenv('RABBIT_QUARANTINE_QUEUE',
                                                    'QUARANTINE_TEST'),
                                          )

    message_consumer = MessageConsumer(
        durable_queue=True,
        exchange=os.getenv('RABBIT_EXCHANGE', 'test'),
        exchange_type=os.getenv('EXCHANGE_TYPE', 'topic'),
        rabbit_queue=os.getenv('RABBIT_QUEUE', 'test'),
        rabbit_urls=os.getenv('RABBIT_URLS', [default_amqp_url]),
        quarantine_publisher=quarantine_publisher,
        process=rp.process,
    )

    message_consumer.run()
    return 0


if __name__ == "__main__":
    rv = main()
    sys.exit(rv)
