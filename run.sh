echo alice > users.txt
echo bob >> users.txt

python3 server.py

python3 client.py alice
python3 client.py bob
