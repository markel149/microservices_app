#!/bin/bash

create_client() {
  read -p "Username: " username
  read -p "Password: " password
  read -p "Role: " role
  payload="{\"username\":\"$username\",\"password\":\"$password\",\"role\":\"$role\"}"
  curl -X POST -H 'Content-Type: application/json' --data $payload http://localhost:8080/client | jq
}

create_order() {
  read -p "Number of pieces: " pieces
  read -p "Description: " description
  read -p "Client ID: " cid
  payload="{\"description\":\"$description\",\"number_of_pieces\":\"$pieces\",\"client_id\":\"$cid\"}"
  curl -X POST -H 'Content-Type: application/json' --data $payload http://localhost:8080/order | jq
}

get_jwt() {
  read -p "Username: " username
  read -p "Password: " password
  read -p  "Cliend ID: " cid
  payload="{\"username\":\"$username\",\"password\":\"$password\", \"id\":\"$cid\"}"
  curl -X GET -H 'Content-Type: application/json' --data $payload http://localhost:8080/client/get_jwt | jq
}

pay(){
  read -p "Client ID: " cid
  read -p "Amount: " amount
  payload="{\"client_id\":\"$cid\",\"amount\":$amount}"
  curl -X POST -H 'Content-Type: application/json' --data $payload http://localhost:8080/payment | jq
}

get_delivery() {
  read -p "Delivery ID: " did
  curl -H 'Content-Type: application/json' http://localhost:8080/delivery/$did | jq
}

get_logs() {
  curl -H 'Content-Type: application/json' http://localhost:8080/logger | jq
}

get_order(){
  read -p "Order ID: " oid
  curl -H 'Content-Type: application/json' http://localhost:8080/order/$oid
}

get_payment(){
  read -p "Payment ID: " pid
  curl -H 'Content-Type: application/json' http://localhost:8080/payment/$pid
}

while [ true ]
do
  clear
  echo "Choose option:"
  echo ""
  echo "1) Create client"
  echo "2) Create order"
  echo "3) Get client"
  echo "4) Get order"
  echo "5) Get delivery"
  echo "6) Get jwt token"
  echo "7) Pay"
  echo "8) Get logs"
  echo "9) Get payment"
  echo "0) Exit"
  
  read option
  
  case $option in
    1)
      clear
      create_client
      read -p "Press key to continue."
      ;;
    2)
      clear
      create_order
      read -p "Press key to continue."
      ;;
    3)
      clear
      create_order
      read -p "Press key to continue."
      ;;
    4)
      clear
      get_order
      read -p "Press key to continue."
      ;;
    5)
      clear
      create_order
      read -p "Press key to continue."
      ;;
    6)
      clear
      get_jwt
      read -p "Press key to continue."
      ;;
    7)
      clear
      pay
      read -p "Press key to continue."
      ;;
    8)
      clear
      get_logs
      read -p "Press key to continue."
      ;;
    9)
      clear
      get_payment
      read -p "Press key to continue."
      ;;
    0)
      clear
      exit 0
      ;;
  esac

done
