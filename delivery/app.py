from application import create_app
from application.messaging_consumer import Consumer


app = create_app()

order_ready_consumer = Consumer('event_exchange', 'queue_of_delivery', 'order.order_ready', Consumer.consume_order_paid)

app.app_context().push()


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=13002)
