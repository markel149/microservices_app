#!/bin/bash

payload="{\"username\":\"$1\",\"password\":\"$2\",\"role\":\"$3\"}"

curl -X POST -H 'Content-Type: application/json' --data $payload http://localhost:8001/client



