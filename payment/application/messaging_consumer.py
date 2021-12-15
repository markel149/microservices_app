import pika
import json
import threading
from . import Session
from .models import Deposit
from flask import request, jsonify, abort
from werkzeug.exceptions import NotFound, InternalServerError, BadRequest, UnsupportedMediaType
from .messaging_producer import send_message
import json
import ssl

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
        context.load_cert_chain("/app/application/certs/client_certificate.pem","/app/application/certs/client_key.pem")
        ssl_options = pika.SSLOptions(context, "rabbitmq")
        #conn_params = pika.ConnectionParameters(port=5671,ssl_options=ssl_options)
    

        connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq', ssl_options=ssl_options, port=5672))
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
    def consume_check_balance(ch, method, properties, body):
        message = json.loads(body)
        print('Requested to check the balance of client' + str(message['client_id']))

        session = Session()
        deposit = session.query(Deposit).filter(Deposit.client_id == message['client_id']).one()
        if not deposit:
            abort(NotFound.code)
        print('Checking the balance of the ' + str(deposit.client_id) + ': ' + str(deposit.balance))

        # Imagine a piece's price is 5
        routing_key = ''
        cost = int(message['number_of_pieces']) * 5
        if cost > deposit.balance:
            routing_key = 'payment.insufficient_money'
            print('Not enough money')
        else:
            routing_key = 'payment.sufficient_money'
            print('Sufficient money')
            deposit.balance = deposit.balance - cost
        session.commit()
        message_body = {
            'order_id': message['order_id'],
            'client_id': message['client_id'],
            'number_of_pieces': message['number_of_pieces']
        }
        send_message(exchange_name='response_exchange', routing_key=routing_key, message=json.dumps(message_body))
        session.close()

    @staticmethod
    def consume_new_client(ch, method, properties, body):
        message = json.loads(body)
        print('Creating deposit for client  ' + str(message['client_id']))

        session = Session()
        new_deposit = Deposit(
            client_id=message['client_id'],
            balance=0
        )
        session.add(new_deposit)
        session.commit()
        session.close()

    @staticmethod
    def consume_pub_key(ch, method, properties, body):
        message = json.loads(body)
        global auth_public_key
        auth_public_key = message['public_key']
        