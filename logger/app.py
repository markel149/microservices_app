from application import create_app
from application.messaging_consumer import Consumer

from application.BLConsul import BLConsul

app = create_app()

logger_consumer = Consumer('event_exchange', 'queue_of_logger', '*.*', Consumer.logger)

app.app_context().push()

bl_consul = BLConsul.get_instance()
bl_consul.init_and_register(app)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
