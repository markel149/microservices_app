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
    def consume_payment_accepted(ch, method, properties, body):
        message = json.loads(body)
        print('Payment status changes for order' + str(message['order_id']) + ': ACCEPTED')

        session = Session()
        order = session.query(Order).filter(Order.order_id == message['order_id']).one()
        if not order:
            abort(NotFound.code)
        order.status = 'PAID'
        session.commit()
        session.close()

    @staticmethod
    def consume_payment_rejected(ch, method, properties, body):
        message = json.loads(body)
        print('Payment status changes for order' + str(message['order_id']) + ': REJECTED')

        session = Session()
        order = session.query(Order).filter(Order.order_id == message['order_id']).one()
        if not order:
            abort(NotFound.code)
        order.status = 'REJECTED'
        session.commit()
        session.close()

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
        session = session()
        session.close()
    
    