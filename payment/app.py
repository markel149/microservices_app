from application import create_app
from application.messaging_consumer import Consumer
from application.BLConsul import BLConsul

app = create_app()

check_balance_consumer = Consumer('command_exchange',
                                  'queue_of_payment_for_order',
                                  'payment.check_balance',
                                  Consumer.consume_check_balance)

new_client_consumer = Consumer('event_exchange',
                               'queue_of_payment_for_client',
                               'client.client_created',
                               Consumer.consume_new_client)
pub_key_changed = Consumer('event_exchange', 'queue_of_pub_key', 'auth.pub_key', Consumer.consume_pub_key)


app.app_context().push()

bl_consul = BLConsul.get_instance()
bl_consul.init_and_register(app)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
