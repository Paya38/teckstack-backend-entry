#!/bin/bash

echo alice > users.txt
echo bob >> users.txt

python3 server.py &

sleep 2

python3 client.py alice
python3 client.py bob
