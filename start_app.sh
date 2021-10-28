bash deletedb.sh

docker-compose down -v
docker-compose up -d rabbitmq
docker-compose up -d --build
sleep 10
docker-compose restart haproxy
echo ""
echo "APP STARTED !"
echo ""
read
clear

echo "==============="
echo "CLIENT DATABASE"
echo "==============="
echo ""
sqlite3 -column -header auth/client.db "SELECT * FROM Client"  

read
clear

echo "====================================="
echo "CLIENT DATABASE AFTER CREATING CLIENT"
echo "====================================="
echo ""
sqlite3 -column -header auth/client.db "SELECT * FROM Client"  

read
clear

echo "====================================================="
echo "CLIENT DATABASE AFTER CREATING CLIENT AND GETTING 403"
echo "====================================================="
echo ""
sqlite3 -column -header auth/client.db "SELECT * FROM Client"

read
clear

echo "========================================="
echo "PAYMENT DATABASE BEFORE CREATING A DEPOSIT"
echo "========================================="
echo ""
sqlite3 -column -header payment/payment.db "SELECT * FROM Deposit"

read
clear

echo "========================================="
echo "PAYMENT DATABASE AFTER CREATING A DEPOSIT"
echo "========================================="
echo ""
sqlite3 -column -header payment/payment.db "SELECT * FROM Deposit"

read
clear

echo "========================================="
echo "           MACHINE DATABASE              "
echo "========================================="
echo ""
sqlite3 -column -header machine/machine.db "SELECT * FROM Piece"

read
clear

echo "========================================="
echo "           ORDERS DATABASE               "
echo "========================================="
echo ""
sqlite3 -column -header order/order.db "SELECT * FROM manufacturing_order"

read
clear

echo "========================================="
echo "           MACHINE DATABASE              "
echo "========================================="
echo ""
sqlite3 -column -header machine/machine.db "SELECT * FROM Piece"

read
clear

echo "================================================================"
echo "           MACHINE DATABASE AFTER REJECTED OREDER               "
echo "================================================================"
echo ""
sqlite3 -column -header machine/machine.db "SELECT * FROM Piece"

read
clear

echo "========================================="
echo "               DELIVERY                  "
echo "========================================="
echo ""
sqlite3 -column -header delivery/delivery.db "SELECT * FROM Delivery"