# server.py
import socket
import threading
import json
import logging
from typing import Dict, Any

# Configuration
HOST = '127.0.0.1'  # Static IP for server
PORT = 65432        # Static port for server
USER_FILE = 'users.txt'

# Initialize logger
target = logging.StreamHandler()
logging.basicConfig(level=logging.INFO, handlers=[target], format='%(asctime)s - %(levelname)s - %(message)s')

# Load authorized users
def load_users(filename: str) -> set:
    try:
        with open(filename, 'r') as f:
            return set(line.strip() for line in f if line.strip())
    except FileNotFoundError:
        logging.warning(f"User file {filename} not found, no users loaded.")
        return set()

authorized_users = load_users(USER_FILE)

# Shared entity storage and lock for thread-safety
entities: Dict[str, Any] = {}
entities_lock = threading.Lock()

# Handle a single client connection
def handle_client(conn: socket.socket, addr):
    logging.info(f"New connection from {addr}")
    try:
        # Authentication phase
        auth_data = conn.recv(1024).decode().strip()
        username = auth_data
n        if username not in authorized_users:
            conn.sendall(b"AUTH_FAIL")
            logging.info(f"Authentication failed for {addr} username={username}")
            return
        conn.sendall(b"AUTH_OK")
        logging.info(f"User authenticated: {username} from {addr}")

        # Command loop
        while True:
            data = conn.recv(4096)
            if not data:
                break
            try:
                message = json.loads(data.decode())
                action = message.get('action')
                key = message.get('key')
                value = message.get('value')
            except json.JSONDecodeError:
                conn.sendall(b"ERROR: Invalid JSON")
                continue

            response = {}
            with entities_lock:
                if action == 'CREATE':
                    entities[key] = value
                    response = {'status': 'OK', 'message': f"Created {key}"}
                elif action == 'READ':
                    if key in entities:
                        response = {'status': 'OK', 'value': entities[key]}
                    else:
                        response = {'status': 'ERROR', 'message': f"{key} not found"}
                elif action == 'UPDATE':
                    if key in entities:
                        entities[key] = value
                        response = {'status': 'OK', 'message': f"Updated {key}"}
                    else:
                        response = {'status': 'ERROR', 'message': f"{key} not found"}
                elif action == 'DELETE':
                    if key in entities:
                        del entities[key]
                        response = {'status': 'OK', 'message': f"Deleted {key}"}
                    else:
                        response = {'status': 'ERROR', 'message': f"{key} not found"}
                else:
                    response = {'status': 'ERROR', 'message': 'Unknown action'}
            conn.sendall(json.dumps(response).encode())
            logging.info(f"{username}@{addr} -> {action} {key}")
    finally:
        conn.close()
        logging.info(f"Connection closed: {addr}")

# Main server loop
def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        logging.info(f"Server listening on {HOST}:{PORT}")
        while True:
            conn, addr = s.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            thread.start()

if __name__ == '__main__':
    start_server()

