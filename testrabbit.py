import pika

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', port=5672, blocked_connection_timeout=10))
channel = connection.channel()
channel.queue_declare(queue='hello')
channel.basic_publish(exchange='',
                      routing_key='hello',
                      body='Hello World!')
print(" [x] Sent 'Hello World!'")
connection.close()
