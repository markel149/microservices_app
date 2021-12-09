from application import create_app
from application.messaging_consumer import Consumer


app = create_app()

sufficient_money_consumer = Consumer(
                                'response_exchange',
                                'queue_of_order_for_payment',
                                'payment.sufficient_money',
                                Consumer.consume_sufficient_money)

insufficient_money_consumer = Consumer(
                                'response_exchange',
                                'queue_of_order_for_payment_rejected',
                                'payment.insufficient_money',
                                Consumer.consume_insufficient_money)

outside_BAC_consumer = Consumer(
                                'response_exchange',
                                'queue_of_order_for_payment',
                                'delivery.outside_BAC',
                                Consumer.consume_outside_BAC)

inside_BAC_consumer = Consumer(
                                'response_exchange',
                                'queue_of_order_for_payment_rejected',
                                'delivery.inside_BAC',
                                Consumer.consume_inside_BAC)

piece_created_consumer = Consumer(
                                'event_exchange',
                                'queue_of_order_for_machine',
                                'machine.piece_from_order_created',
                                Consumer.consume_piece_created)
#pub_key_changed = Consumer('event_exchange', 'queue_of_pub_key2', 'auth.pub_key2', Consumer.consume_pub_key)
pub_key_changed = Consumer('event_exchange', 'queue_of_pub_key2', 'auth.pub_key2', Consumer.consume_pub_key)


app.app_context().push()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
