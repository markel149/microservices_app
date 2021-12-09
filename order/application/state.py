from flask import request, jsonify, abort
from werkzeug.exceptions import NotFound
from .messaging_producer import send_message
import json
from . import Session
from .models import Order


class OrderProcess(object):
    def __init__(self, order_id, client_id, client_address, number_of_pieces):
        self.order_id = order_id
        self.client_id = client_id
        self.client_address = client_address
        self.number_of_pieces = number_of_pieces
        self.state = CheckingAddressState()

        message_body = {
            'order_id': self.order_id,
            'client_address': self.client_address,
            'number_of_pieces': self.number_of_pieces
        }
        send_message(exchange_name='command_exchange',
                     routing_key='delivery.check_BAC',
                     message=json.dumps(message_body))

    def on_event(self, event, values):
        self.state = self.state.on_event(event, values)


class State(object):

    def on_event(self, event, values):
        pass

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return self.__class__.__name__


class CheckingAddressState(State):

    def on_event(self, event, values):
        if event == 'address_inside_BAC':
            message_body = {
                'order_id': values['order_id'],
                'number_of_pieces': values['number_of_pieces']
            }
            send_message(exchange_name='command_exchange',
                         routing_key='payment.check_balance',
                         message=json.dumps(message_body))
            return CheckingBalanceState()

        if event == 'address_outside_BAC':
            message_body = {
                'order_id': values['order_id'],
                'number_of_pieces': values['number_of_pieces']
            }
            send_message(exchange_name='command_exchange',
                         routing_key='payment.check_balance',
                         message=json.dumps(message_body))
            return OrderCancelledState(values['order_id'], 'ADDRESS_OUTSIDE_BAC')

        return self


class CheckingBalanceState(State):

    def on_event(self, event, values):
        if event == 'sufficient_money':

            return OrderRequirementsCompletedState(values['order_id'], values['number_of_pieces'])

        if event == 'insufficient_money':
            message_body = {
                'order_id': values.order_id,
            }
            send_message(exchange_name='command_exchange',
                         routing_key='delivery.cancel_delivery',
                         message=json.dumps(message_body))
            return OrderCancelledState(values['order_id'], 'INSUFFICIENT_MONEY')

        return self


class OrderRequirementsCompletedState(State):

    def __init__(self, order_id, number_of_pieces):
        message_body = {
            'order_id': order_id,
            'number_of_pieces': number_of_pieces,
        }

        send_message(exchange_name='event_exchange',
                     routing_key='order.order_request_completed',
                     message=json.dumps(message_body))

        session = Session()
        order = session.query(Order).filter(Order.order_id == order_id).one()
        if not order:
            abort(NotFound.code)
        order.status = 'PROCESSED'
        session.commit()
        session.close()


class OrderCancelledState(State):

    def __init__(self, order_id, cause):
        session = Session()
        order = session.query(Order).filter(Order.order_id == order_id).one()
        if not order:
            abort(NotFound.code)
        order.status = cause
        session.commit()
        session.close()

