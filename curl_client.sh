#!/bin/bash

payload="{\"name\":\"$1\",\"last_name\":\"$2\"}"

curl -X POST -H 'Content-Type: application/json' --data $payload http://localhost:8001/client


