from application import create_app
from application.messaging_consumer import Consumer


app = create_app()

order_created_consumer = Consumer('event_exchange', 'queue_of_delivery_for_order', 'order.order_created', Consumer.consume_order_created)
payment_changed_consumer = Consumer('event_exchange', 'queue_of_delivery_for_payment', 'payment.payment_status_changed', Consumer.consume_order_paid)
pieces_ready_consumer = Consumer('event_exchange', 'queue_of_delivery_for_machine', 'machine.pieces_from_order_created', Consumer.consume_pieces_ready)

app.app_context().push()


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
