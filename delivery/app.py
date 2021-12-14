from application import create_app
from application.messaging_consumer import Consumer
import json
import requests
from application.BLConsul import BLConsul

app = create_app()

order_created_consumer = Consumer(
                            'event_exchange',
                            'queue_of_delivery_for_order',
                            'order.order_created',
                            Consumer.consume_order_created)

payment_accepted_consumer = Consumer(
                            'event_exchange',
                            'queue_of_delivery_for_payment',
                            'payment.payment_accepted',
                            Consumer.consume_payment_accepted)

payment_rejected_consumer = Consumer(
                            'event_exchange',
                            'queue_of_delivery_for_payment_rejected',
                            'payment.payment_rejected',
                            Consumer.consume_payment_rejected)

order_completed_consumer = Consumer(
                            'event_exchange',
                            'queue_of_delivery_for_order_completed',
                            'order.order_completed',
                            Consumer.consume_order_completed)

app.app_context().push()

bl_consul = BLConsul.get_instance()
bl_consul.init_and_register(app)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
