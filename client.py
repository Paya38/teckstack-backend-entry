
# client.py
import socket
import json
import sys

HOST = '127.0.0.1'  # Server IP
PORT = 65432        # Server port


def send_command(sock, action, key, value=None):
    message = {'action': action, 'key': key, 'value': value}
    sock.sendall(json.dumps(message).encode())
    response = sock.recv(4096)
    print('Server response:', response.decode())


def main():
    if len(sys.argv) < 2:
        print("Usage: python client.py <username>")
        return
    username = sys.argv[1]
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        # Authentication
        s.sendall(username.encode())
        auth_resp = s.recv(1024).decode()
        if auth_resp != 'AUTH_OK':
            print('Authentication failed')
            return
        print('Authenticated successfully')

        # Interactive loop
        try:
            while True:
                cmd = input("Enter command (CREATE/READ/UPDATE/DELETE) and key [and value]: ")
                parts = cmd.split()
                if not parts:
                    continue
                action = parts[0].upper()
                if action not in ('CREATE', 'READ', 'UPDATE', 'DELETE'):
                    print('Invalid action')
                    continue
                key = parts[1] if len(parts) > 1 else None
                value = None
                if action in ('CREATE', 'UPDATE'):
                    value = input("Enter value: ")
                send_command(s, action, key, value)
        except KeyboardInterrupt:
            print('\nExiting client.')

if __name__ == '__main__':
    main()
