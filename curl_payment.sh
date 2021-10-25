
#!/bin/bash

payload="{\"client_id\":\"$1\"}"

curl -X POST -H 'Content-Type: application/json' --data $payload http://localhost:8080/create_deposit



