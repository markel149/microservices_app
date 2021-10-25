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

  read -p "Username: "
  read -p "Password: "
  
  payload="{\"username\":\"$description\",\"password\":\"$pieces\"}"
  curl 'Content-Type: application/json' --data $payload http://localhost:8080/get_jwt | jq

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
      create_order
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
    0)
      exit 0
      ;;
  esac

done
