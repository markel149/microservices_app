#!/bin/bash

<<<<<<< HEAD:curl_client.sh
payload="{\"username\":\"$1\",\"password\":\"$2\",\"role\":\"$3\"}"
=======
payload="{\"name\":\"$1\",\"surname\":\"$2\",\"username\":\"$3\"}"
>>>>>>> ba2686b1ef16a094943a67b59b3819141dba7513:scripts/curl_client.sh

curl -X POST -H 'Content-Type: application/json' --data $payload http://localhost:8001/client



