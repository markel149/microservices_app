#!/bin/bash

payload="{\"payment\":\"$1\",\"id_client\":\"$2\"}"

curl -X POST -H 'Content-Type: application/json' --data $payload http://localhost:8002/payment


