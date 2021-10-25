import pika
import json
import threading
from . import Session
from application.models import PiecesOrdered, Piece
from application.machine import Machine
from flask import request, jsonify, abort
from werkzeug.exceptions import NotFound, InternalServerError, BadRequest, UnsupportedMediaType
from .messaging_producer import send_message

my_machine = Machine()

class Consumer:
    def __init__(self, exchange_name, queue_name, routing_key, callback):
        self.exchange_name = exchange_name
        self.queue_name = queue_name
        self.routing_key = routing_key
        self.callback = callback
        self.declare_connection()

    def declare_connection(self):
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='rabbitmq'))
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
    def consume_new_order(ch, method, properties, body):
        message = json.loads(body)
        print('New order created:  ' + str(message['order_id']))

        session = Session()
        new_order = PiecesOrdered(
            order_id=message['order_id'],
            number_of_pieces=message['number_of_pieces']
        )
        session.add(new_order)
        session.commit()
        session.close()

    @staticmethod
    def consume_order_paid(ch, method, properties, body):
        message = json.loads(body)
        print('New order paid:  ' + str(message['order_id']))

        session = Session()
        pieces_ordered = session.query(PiecesOrdered).filter(PiecesOrdered.order_id == message['order_id']).one()
        if str(message['payment_status']) == 'REJECTED':
            pieces_ordered.status = 'REJECTED'
        else:
            for i in range(pieces_ordered.number_of_pieces):
                piece = Piece()
                piece.order = pieces_ordered
                session.add(piece)
            session.commit()
            my_machine.add_pieces_to_queue(pieces_ordered.pieces)
            session.commit()
        session.close()
