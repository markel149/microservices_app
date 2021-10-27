from application import create_app
from application.messaging_producer import send_message
import json

app = create_app()

message_body = {
    "update": 1
}
#send_message(exchange_name='event_exchange', routing_key='auth.pub_key', message=json.dumps(message_body))

app.app_context().push()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
