from application import create_app
from application.messaging_consumer import Consumer

app = create_app()

payment_status_changed_consumer = Consumer('event_exchange', 'queue_of_order', 'payment.payment_status_changed', Consumer.consume_payment_status)

app.app_context().push()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=13000)
