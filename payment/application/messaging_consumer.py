import pika
import json
import threading
from . import Session
from .models import Deposit
from flask import request, jsonify, abort
from werkzeug.exceptions import NotFound, InternalServerError, BadRequest, UnsupportedMediaType
from .messaging_producer import send_message


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
        #queue_name = result.method.queue

        channel.queue_bind(exchange=self.exchange_name, queue=self.queue_name, routing_key=self.routing_key)

        channel.basic_consume(queue=self.queue_name, on_message_callback=self.callback, auto_ack=True)
        print(' [*] Waiting for messages. To exit press CTRL+C')
        thread = threading.Thread(target=channel.start_consuming)
        thread.start()

    @staticmethod
    def consume_new_order(ch, method, properties, body):
        message = json.loads(body)
        print('New order created:  ' + str(message['order_id']))

        session = Session()
        deposit = session.query(Deposit).filter(Deposit.client_id == message['client_id']).one()
        if not deposit:
            abort(NotFound.code)
        print("GET Deposit {}: {}".format(deposit.deposit_id, deposit.balance))

        # Imagine a piece's price is 5
        status = ''
        cost = int(message['number_of_pieces']) * 5
        if cost > deposit.balance:
            status = 'REJECTED'
        else:
            status = 'PAID'
            deposit.balance = deposit.balance - cost
        session.commit()
        message_body = {
            'order_id': message['order_id'],
            'client_id': message['client_id'],
            'number_of_pieces': message['number_of_pieces'],
            'payment_status': status
        }
        send_message(exchange_name='event_exchange', routing_key='payment.payment_status_changed', message=json.dumps(message_body))
        session.close()

    @staticmethod
    def consume_new_client(ch, method, properties, body):
        message = json.loads(body)
        print('New client created:  ' + str(message['client_id']))

        session = Session()
        new_deposit = Deposit(
            client_id=message['client_id'],
            balance=0
        )
        session.add(new_deposit)
        session.commit()
        session.close()