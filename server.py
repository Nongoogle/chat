import socket
import threading
import os
PORT = int(os.environ.get("PORT", 50505))
clients = []

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('0.0.0.0', PORT))
server.listen()

print("Server running...")

def broadcast(data, sender):
    for client in clients:
        if client != sender:
            try:
                client.sendall(data)
            except:
                clients.remove(client)

def handle_client(conn, addr):
    print("Connected:", addr)
    clients.append(conn)

    buffer = b""

    while True:
        try:
            data = conn.recv(4096)
            if not data:
                break

            buffer += data

            while b"<END>" in buffer:
              full_msg, buffer = buffer.split(b"<END>", 1)
              broadcast(full_msg + b"<END>", conn)

        except:
            break

    clients.remove(conn)
    conn.close()
    print("Disconnected:", addr)

while True:
    conn, addr = server.accept()
    threading.Thread(target=handle_client, args=(conn, addr)).start()