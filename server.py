import socket
import threading
import json
import os
import tempfile
from colorama import init, Fore


init(autoreset=True)

HOST = '127.0.0.1'  # Server address
PORT = 65432       # Fixed port

USERS_FILE = 'users.txt'
ENTITIES_FILE = 'entities.json'


with open(USERS_FILE, 'r') as f:
    AUTH_USERS = [line.strip() for line in f if line.strip()]


def load_entities():
    if os.path.exists(ENTITIES_FILE):
        with open(ENTITIES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

entities = load_entities()
lock = threading.Lock()  # Ensure thread-safe access


# def save_entities():
#     """Persist entities dictionary to JSON file."""
#     with lock:
#         try:
#             # Write to a temporary file first
#             dir_name = os.path.dirname(os.path.abspath(ENTITIES_FILE))
#             fd, temp_path = tempfile.mkstemp(dir=dir_name, prefix='entities_', suffix='.json')
#             with os.fdopen(fd, 'w', encoding='utf-8') as tmp_file:
#                 json.dump(entities, tmp_file, ensure_ascii=False, indent=2)
#                 tmp_file.flush()
#                 os.fsync(tmp_file.fileno())
#             # Atomically replace the old file
#             os.replace(temp_path, ENTITIES_FILE)
#         except Exception as e:
#             print(Fore.RED + f"[ERROR] Failed to save entities: {e}")

def save_entities():
    with open(ENTITIES_FILE, 'w') as f:
        json.dump(entities, f)


def handle_client(conn, addr):
    print(Fore.CYAN + f"[NEW CONNECTION] {addr} connected.")
    try:
        # Authenticate user
        username = conn.recv(1024).decode().strip()
        if username not in AUTH_USERS:
            conn.sendall("AUTH_FAIL".encode())
            print(Fore.RED + f"[AUTH FAILED] {addr} with username '{username}'")
            return
        conn.sendall("AUTH_OK".encode())
        print(Fore.GREEN + f"[AUTH SUCCESS] '{username}' from {addr}")

        while True:
            data = conn.recv(4096)
            if not data:
                break
            message = data.decode().strip()
            print(Fore.YELLOW + f"[{username}@{addr}] -> {message}")
            response = process_command(message)
            conn.sendall(response.encode())

    except Exception as e:
        print(Fore.RED + f"[ERROR] {e}")
    finally:
        conn.close()
        print(Fore.MAGENTA + f"[DISCONNECT] {addr} disconnected.")


def process_command(message: str) -> str:
    parts = message.split(maxsplit=2)
    if not parts:
        return "ERROR: Empty command"
    cmd = parts[0].upper()

    # ADD entity
    if cmd == 'ADD' and len(parts) == 3:
        name, data = parts[1], parts[2]
        with lock:
            if name in entities:
                return f"ERROR: Entity '{name}' already exists"
            entities[name] = data
            save_entities()
        return f"[OK] '{name}' added"

    # EDIT entity
    if cmd == 'EDIT' and len(parts) == 3:
        name, data = parts[1], parts[2]
        with lock:
            if name not in entities:
                return f"ERROR: Entity '{name}' not found"
            entities[name] = data
            save_entities()
        return f"[OK] '{name}' updated"

    # GET entity
    if cmd == 'GET' and len(parts) == 2:
        name = parts[1]
        with lock:
            if name not in entities:
                return f"ERROR: Entity '{name}' not found"
            return f"{name}: {entities[name]}"

    # DELETE entity
    if cmd == 'DELETE' and len(parts) == 2:
        name = parts[1]
        with lock:
            if name not in entities:
                return f"ERROR: Entity '{name}' not found"
            del entities[name]
            save_entities()
        return f"[OK] '{name}' deleted"

    # LIST all entities
    if cmd == 'LIST':
        with lock:
            if not entities:
                return "No entities found"
            return json.dumps(entities, ensure_ascii=False)

    return "ERROR: Invalid command or wrong parameters"


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((HOST, PORT))
        server.listen()
        print(Fore.BLUE + f"[STARTED] Server listening on {HOST}:{PORT}...")
        while True:
            conn, addr = server.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            thread.start()


if __name__ == '__main__':
    main()
