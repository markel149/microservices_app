import pika
import json
import threading
from . import Session
from .models import Piece
from flask import request, jsonify, abort
from werkzeug.exceptions import NotFound, InternalServerError, BadRequest, UnsupportedMediaType
from .messaging_producer import send_message


class Consumer:
    def __init__(self, exchange_name, routing_key, callback):
        self.exchange_name = exchange_name
        self.routing_key = routing_key
        self.callback = callback
        self.declare_connection()

    def declare_connection(self):
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='rabbitmq'))
        channel = connection.channel()
        channel.exchange_declare(exchange=self.exchange_name, exchange_type='topic')

        result = channel.queue_declare('', exclusive=True)
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
        deposito = session.query(Deposit).filter(Deposit.id_cliente == message['client_id']).one()
        if not deposito:
            abort(NotFound.code)
        print("GET Deposit {}: {}".format(deposito.id_deposito, deposito.saldo))

        # Imagine a piece's price is 5
        status=''
        cost = int(message['number_of_pieces']) * 5
        if cost > deposito.saldo:
            status = 'REJECTED'
        else:
            status = 'PAID'
            deposito.saldo = deposito.saldo - cost
        session.commit()
        message_body = {
            'id_order': message['id_order'],
            'id_cliente': message['id_cliente'],
            'number_of_pieces': message['number_of_pieces'],
            'payment_status': status
        }
        send_message(exchange_name='payment_exchange', routing_key='payment.payment_status_changed', message=json.dumps(message_body))
        session.close()
