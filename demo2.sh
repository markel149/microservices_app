docker-compose down -v
docker-compose up -d rabbitmq
docker-compose up -d
sleep 5
docker-compose restart haproxy