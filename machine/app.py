from application import create_app
from application.messaging_consumer import Consumer


app = create_app()

new_order_consumer = Consumer('event_exchange', 'queue_of_machine_for_order', 'order.order_created', Consumer.consume_new_order)
order_paid_consumer = Consumer('event_exchange', 'queue_of_machine_for_payment', 'payment.payment_status_changed', Consumer.consume_order_paid)

app.app_context().push()


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=13003)
