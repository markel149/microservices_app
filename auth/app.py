from application import create_app
from application.messaging_producer import send_message
import json

app = create_app()

message_body = {
    "update": 1
}

app.app_context().push()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
