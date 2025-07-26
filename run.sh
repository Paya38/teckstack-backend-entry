echo alice > users.txt
echo bob >> users.txt

python server.py

python client.py alice
python client.py bob