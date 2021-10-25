
#!/bin/bash

payload="{\"description\":\"aaaa\",\"number_of_pieces\":\"$1\",\"client_id\":\"$2\"}"

curl -X POST -H 'Content-Type: application/json' --data $payload http://localhost:8080/order



