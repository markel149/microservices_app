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
    def consume_payment_status(ch, method, properties, body):
        message = json.loads(body)
        print('Payment status changes for:  ' + str(message['order_id']) + ",Now: " + str(message['payment_status']))

        session = Session()
        order = session.query(Order).filter(Order.order_id == message['order_id']).one()
        if not order:
            abort(NotFound.code)
        print("GET Order {}: {}".format(order.order_id, order.client_id))
        order.status = str(message['payment_status'])
        session.commit()
        session.close()




    @staticmethod
    def consume_pieces_ready(ch, method, properties, body):
        message = json.loads(body)
        print(message)
        #CAMBIOS
        session = Session()
        order = session.query(Order).filter(Order.order_id == message['order_id']).one()
        if not order:
            abort(NotFound.code)
        print("GET Order {}: {}".format(order.order_id, order.client_id))
        order.status = 'MANUFACTURED'
        session.commit()
        session.close()
    

    @staticmethod
    def consume_pub_key(ch, method, properties, body):
        message = json.loads(body)
        global auth_public_key    
        auth_public_key = message['public_key']
        session = session()
        session.close()
    
    