from application import create_app
from application.messaging_producer import send_message
import json
from application.BLConsul import BLConsul

app = create_app()

app.app_context().push()
bl_consul = BLConsul.get_instance()
bl_consul.init_and_register(app)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
