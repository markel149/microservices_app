from application import create_app
from application.messaging_consumer import Consumer


app = create_app()

new_order_consumer = Consumer('event_exchange', 'queue_of_payment_for_order', 'order.order_created', Consumer.consume_new_order)

app.app_context().push()


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
