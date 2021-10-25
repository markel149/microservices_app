import pika
import json
import threading
from flask import request, jsonify, abort
from werkzeug.exceptions import NotFound, InternalServerError, BadRequest, UnsupportedMediaType
from . import Session
from .models import Delivery


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

    # CAMBIOS
    @staticmethod
    def consume_order_created(ch, method, properties, body):
        message = json.loads(body)
        print('New order created:  ' + str(message['order_id']))

        session = Session()
        new_delivery = Delivery(
            order_id=int(message['order_id'])
        )
        session.add(new_delivery)
        session.commit()
        session.close()

    @staticmethod
    def consume_order_paid(ch, method, properties, body):
        message = json.loads(body)
        print('Payment status changes for:  ' + str(message['order_id']) + ",Now: " + str(message['payment_status']))

        session = Session()
        delivery = session.query(Delivery).filter(Delivery.order_id == message['order_id']).one()
        if not delivery:
            abort(NotFound.code)
        print("GET Delivery {}".format(delivery.order_id))
        status = ''
        if str(message['payment_status']) == 'PAID':
            delivery.status = 'MANUFACTURING'
        else:
            delivery.status = 'REJECTED'
        session.commit()
        session.close()

    @staticmethod
    def consume_pieces_ready(ch, method, properties, body):
        message = json.loads(body)
        print('Pieces ready for:  ' + str(message['order_id']))

        session = Session()
        delivery = session.query(Delivery).filter(Delivery.order_id == message['order_id']).one()
        if not delivery:
            abort(NotFound.code)
        print("GET Delivery {}".format(delivery.order_id))
        delivery.status = 'READY_FOR_SHIPMENT'
        session.commit()
        session.close()
