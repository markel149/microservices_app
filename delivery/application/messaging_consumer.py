import pika
import json
import threading
from flask import request, jsonify, abort
from werkzeug.exceptions import NotFound, InternalServerError, BadRequest, UnsupportedMediaType
from . import Session
from .models import Delivery
import ssl
from .messaging_producer import send_message

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
    def consume_check_inside_BAC(ch, method, properties, body):
        message = json.loads(body)
        print('Order requested to check if it is inside BAC:  ' + str(message['order_id']))

        #if message['client_address'][0:2] == '01' or message['client_address'][0:2] == '20' or message['client_address'][0:2] == '48'
        session = Session()
        if message['client_address'] == '20500':
            new_delivery = Delivery(
                order_id=int(message['order_id']),
                status='CORRECT_ADDRESS'
            )
            session.add(new_delivery)
            session.commit()
            session.close()
            message_body = {
                'order_id': message['order_id'],
                'number_of_pieces': message['number_of_pieces']
            }
            send_message('response_exchange', 'delivery.inside_BAC', json.dumps(message_body))
        else:
            new_delivery = Delivery(
                order_id=int(message['order_id']),
                status='OUTSIDE_BAC'
            )
            session.add(new_delivery)
            session.commit()
            session.close()
            message_body = {
                'order_id': message['order_id']
            }
            send_message('response_exchange', 'delivery.outside_BAC', json.dumps(message_body))

    @staticmethod
    def consume_cancel_delivery(ch, method, properties, body):
        message = json.loads(body)
        print('Requested delivery cancel for order' + str(message['order_id']))

        session = Session()
        delivery = session.query(Delivery).filter(Delivery.order_id == message['order_id']).one()
        if not delivery:
            abort(NotFound.code)
        delivery.status = 'CANCELLED_BY_INSUFFICIENT_MONEY'
        session.commit()
        session.close()

    @staticmethod
    def consume_order_completed(ch, method, properties, body):
        message = json.loads(body)
        print('Pieces ready for order' + str(message['order_id']))

        session = Session()
        delivery = session.query(Delivery).filter(Delivery.order_id == message['order_id']).one()
        if not delivery:
            abort(NotFound.code)
        delivery.status = 'READY_FOR_SHIPMENT'
        session.commit()
        session.close()
