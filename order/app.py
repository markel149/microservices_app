from application import create_app
from application.messaging_consumer import Consumer


app = create_app()

payment_accepted_consumer = Consumer(
                                'event_exchange',
                                'queue_of_order_for_payment',
                                'payment.payment_accepted',
                                Consumer.consume_payment_accepted)

payment_rejected_consumer = Consumer(
                                'event_exchange',
                                'queue_of_order_for_payment_rejected',
                                'payment.payment_rejected',
                                Consumer.consume_payment_rejected)

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
