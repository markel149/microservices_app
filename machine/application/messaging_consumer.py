import pika
import json
import threading
from . import Session
from application.models import Piece
from application.machine import Machine
from flask import request, jsonify, abort
from werkzeug.exceptions import NotFound, InternalServerError, BadRequest, UnsupportedMediaType
from .messaging_producer import send_message
import ssl
my_machine = Machine()

class Consumer:
    def __init__(self, exchange_name, queue_name, routing_key, callback):
        self.exchange_name = exchange_name
        self.queue_name = queue_name
        self.routing_key = routing_key
        self.callback = callback
        self.declare_connection()

    def declare_connection(self):
                # Define ssl context 
        context = ssl.create_default_context(cafile="/app/application/certs/ca_certificate.pem")
        context.load_cert_chain("/app/application/certs/client_certificate.pem","/app/application/certs/client_key.pem", password="bunnies")
        ssl_options = pika.SSLOptions(context, "rabbitmq")
        #conn_params = pika.ConnectionParameters(port=5671,ssl_options=ssl_options)
    

        connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq', ssl_options=ssl_options, port=5672))
        channel = connection.channel()
        channel.exchange_declare(exchange=self.exchange_name, exchange_type='topic')

        result = channel.queue_declare(self.queue_name, exclusive=True)
        queue_name = result.method.queue

        channel.queue_bind(exchange=self.exchange_name, queue=queue_name, routing_key=self.routing_key)

        channel.basic_consume(queue=queue_name, on_message_callback=self.callback, auto_ack=True)
        print(' [*] Waiting for messages. To exit press CTRL+C')
        thread = threading.Thread(target=channel.start_consuming)
        thread.start()

    @staticmethod
    def consume_order_ready(ch, method, properties, body):
        message = json.loads(body)
        print('New order paid:  ' + str(message['order_id']))

        session = Session()
        num_pieces_ordered = message['number_of_pieces']
        for i in range(num_pieces_ordered):
            piece = Piece(order_id=message['order_id'])
            session.add(piece)
            session.commit()
            my_machine.add_piece_to_queue(piece)
        session.commit()
        session.close()

