from application import create_app
from application.messaging_consumer import Consumer
import json
import requests

app = create_app()

check_BAC_consumer = Consumer(
                            'command_exchange',
                            'queue_of_delivery_for_order',
                            'delivery.check_BAC',
                            Consumer.consume_check_inside_BAC)

cancel_delivery_consumer = Consumer(
                            'command_exchange',
                            'queue_of_delivery_for_order2',
                            'delivery.cancel_delivery',
                            Consumer.consume_cancel_delivery)

order_completed_consumer = Consumer(
                            'event_exchange',
                            'queue_of_delivery_for_order_completed',
                            'order.order_completed',
                            Consumer.consume_order_completed)

app.app_context().push()


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
