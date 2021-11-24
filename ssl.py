
    # Define ssl context 
    context = ssl.create_default_context(cafile="/app/application/certs/ca_certificate.pem")
    context.load_cert_chain("/app/application/certs/client_certificate.pem","/app/application/certs/client_key.pem", password="bunnies")
    ssl_options = pika.SSLOptions(context, "rabbitmq")
    #conn_params = pika.ConnectionParameters(port=5671,ssl_options=ssl_options)
    

    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq', ssl_options=ssl_options, port=5672))
