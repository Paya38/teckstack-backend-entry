import socket

HOST = '127.0.0.1'
PORT = 65432

def main():
    username = input("Enter username: ").strip()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(username.encode())
        auth = s.recv(1024).decode()
        if auth != 'AUTH_OK':
            print(" Authentication failed.")
            return
        print(" Authentication successful.")

        print("Available commands:")
        print("  ADD <name> <data>")
        print("  EDIT <name> <data>")
        print("  GET <name>")
        print("  DELETE <name>")
        print("  LIST")
        print("  QUIT")

        while True:
            cmd = input(f"{username}> ").strip()
            if not cmd:
                continue
            s.sendall(cmd.encode())
            if cmd.upper() == 'QUIT':
                print("👋 Connection closed.")
                break
            response = s.recv(4096).decode()
            print(response)

if __name__ == '__main__':
    main()
