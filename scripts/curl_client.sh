#!/bin/bash

payload="{\"name\":\"$1\",\"surname\":\"$2\",\"username\":\"$3\"}"

curl -X POST -H 'Content-Type: application/json' --data $payload http://localhost:8080/client



