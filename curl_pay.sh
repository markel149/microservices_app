

#!/bin/bash

payload="{\"client_id\":\"$1\",\"amount\":$2}"

curl -X POST -H 'Content-Type: application/json' --data $payload http://localhost:8080/payment



