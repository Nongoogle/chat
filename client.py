import socket
import threading
import tkinter as tk
from tkinter import filedialog

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('chat.up.railway.app', 50505))

def receive():
    buffer = b""
    while True:
        try:
            data = client.recv(4096)
            if not data:
                break

            buffer += data

            if b"<END>" in buffer:
                full_msg, buffer = buffer.split(b"<END>", 1)

                header, body = full_msg.split(b"\n", 1)
                info = header.decode().split("|")

                if info[0] == "MSG":
                    chat.insert(tk.END, "Other: " + body.decode() + "\n")

                else:
                    filename = "received_" + info[1].split("/")[-1]
                    with open(filename, "wb") as f:
                        f.write(body)
                    chat.insert(tk.END, f"Received file: {filename}\n")

        except:
            break

def send_msg():
    msg = entry.get()
    if msg == "":
        return

    packet = f"MSG|text\n{msg}".encode()
    client.sendall(packet + b"<END>")

    chat.insert(tk.END, "Me: " + msg + "\n")
    entry.delete(0, tk.END)

def send_file():
    path = filedialog.askopenfilename()
    if not path:
        return

    with open(path, "rb") as f:
        data = f.read()

    header = f"FILE|{path}\n".encode()
    client.sendall(header + data + b"<END>")

    chat.insert(tk.END, f"Sent: {path}\n")


root = tk.Tk()
root.title("Chat")

chat = tk.Text(root, height=20, width=50)
chat.pack()

entry = tk.Entry(root, width=40)
entry.pack()

btn_send = tk.Button(root, text="Send Text", command=send_msg)
btn_send.pack()

btn_file = tk.Button(root, text="Send File / Image / Video", command=send_file)
btn_file.pack()

threading.Thread(target=receive, daemon=True).start()

root.mainloop()