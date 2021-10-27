from application import create_app
from application.messaging_producer import send_message
import json

app = create_app()

app.app_context().push()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
