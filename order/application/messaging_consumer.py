import pika
import sys
import json
import threading
from . import Session
from flask import request, jsonify, abort
from werkzeug.exceptions import NotFound, InternalServerError, BadRequest, UnsupportedMediaType
from .models import Order
from .messaging_producer import send_message
import requests
import time
import logging
import ssl
from .messaging_producer import send_message
from .sagas_orchestrator import get_orchestrator


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
        #queue_name = result.method.queue

        channel.queue_bind(exchange=self.exchange_name, queue=self.queue_name, routing_key=self.routing_key)

        channel.basic_consume(queue=self.queue_name, on_message_callback=self.callback, auto_ack=True)
        print(' [*] Waiting for messages. To exit press CTRL+C')
        thread = threading.Thread(target=channel.start_consuming)
        thread.start()

    @staticmethod
    def consume_inside_BAC(ch, method, properties, body):
        message = json.loads(body)
        print('Client address checked for order' + str(message['order_id']) + ': ACCEPTED')
        orchestrator = get_orchestrator()
        orchestrator.manage_message('address_inside_BAC', message)

    @staticmethod
    def consume_outside_BAC(ch, method, properties, body):
        message = json.loads(body)
        print('Client address checked for order' + str(message['order_id']) + ': REJECTED')
        orchestrator = get_orchestrator()
        orchestrator.manage_message('address_outside_BAC', message)

    @staticmethod
    def consume_sufficient_money(ch, method, properties, body):
        message = json.loads(body)
        print('Payment checked for order' + str(message['order_id']) + ': ACCEPTED')
        orchestrator = get_orchestrator()
        orchestrator.manage_message('sufficient_money', message)

    @staticmethod
    def consume_insufficient_money(ch, method, properties, body):
        message = json.loads(body)
        print('Payment checked for order' + str(message['order_id']) + ': REJECTED')
        orchestrator = get_orchestrator()
        orchestrator.manage_message('insufficient_money', message)

    @staticmethod
    def consume_piece_created(ch, method, properties, body):
        message = json.loads(body)
        print('Piece for order' + str(message['order_id']) + ' created')
        session = Session()
        order = session.query(Order).filter(Order.order_id == message['order_id']).one()
        if not order:
            abort(NotFound.code)
        order.number_of_pieces_created = order.number_of_pieces_created + 1
        print('Pieces created: ' + str(order.number_of_pieces_created) + ', Pieces ordered: ' + str(
            order.number_of_pieces))
        if order.number_of_pieces_created == order.number_of_pieces:
            order.status = 'MANUFACTURED'
            print("All pieces created for order" + str(order.order_id))
            message_body = {
                'order_id': order.order_id
            }
            send_message(exchange_name='event_exchange', routing_key='order.order_completed',
                         message=json.dumps(message_body))

        session.commit()
        session.close()


    @staticmethod
    def consume_pub_key(ch, method, properties, body):
        message = json.loads(body)
        global auth_public_key    
        auth_public_key = message['public_key']
        session = Session()
        session.close()
    
    