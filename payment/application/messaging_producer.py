import pika


def send_message(exchange_name, routing_key, message):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='rabbitmq'))
    channel = connection.channel()

    channel.exchange_declare(exchange=exchange_name, exchange_type='topic')

    channel.basic_publish(exchange=exchange_name, routing_key=routing_key, body=message)
    print("Sent: " + message)
    connection.close()
