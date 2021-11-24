import pika
import ssl

def send_message(exchange_name, routing_key, message):
    # Define ssl context 
    context = ssl.create_default_context(cafile="/app/application/certs/ca_certificate.pem")
    context.load_cert_chain("/app/application/certs/client_certificate.pem","/app/application/certs/client_key.pem", password="bunnies")
    ssl_options = pika.SSLOptions(context, "rabbitmq")
    #conn_params = pika.ConnectionParameters(port=5671,ssl_options=ssl_options)
    

    connection = pika.BlockingConnection(pika.ConnectionParameters(host='10.0.2.115', ssl_options=ssl_options, port=5672))
    channel = connection.channel()

    channel.exchange_declare(exchange=exchange_name, exchange_type='topic')

    channel.basic_publish(exchange=exchange_name, routing_key=routing_key, body=message)
    print("Sent: " + message)
    connection.close()
