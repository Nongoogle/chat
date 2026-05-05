import socket
import threading
import os
import tkinter as tk
from tkinter import filedialog

HOST = "100.87.71.106"
PORT = 50505

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))
username = input("Enter your name: ")
def receive():
    buffer = b""
    while True:
        try:
            data = client.recv(4096)
            if not data:
                break

            buffer += data

            while b"<END>" in buffer:
                full_msg, buffer = buffer.split(b"<END>", 1)

                try:
                    header, body = full_msg.split(b"\n", 1)
                except:
                    continue

                info = header.decode().split("|")

                if info[0] == "MSG":
                    sender = info[1]  
                    chat.insert(tk.END, f"{sender}: {body.decode()}\n")
                    chat.yview(tk.END)

                elif info[0] == "FILE":
                    sender = info[1]          
                    filename = "received_" + info[2]  
                    with open(filename, "wb") as f:
                        f.write(body)

                    chat.insert(tk.END, f"{sender} sent file: {filename}\n")
                    chat.yview(tk.END)

        except:
            break

def send_msg():
    msg = entry.get()
    if msg.strip() == "":
        return

    packet = f"MSG|{username}\n{msg}".encode()
    client.sendall(packet + b"<END>")

    chat.insert(tk.END, "Me: " + msg + "\n")
    entry.delete(0, tk.END)
    chat.yview(tk.END)

def send_file():
    path = filedialog.askopenfilename()
    if not path:
        return
    filename = os.path.basename(path)
    with open(path, "rb") as f:
        data = f.read()

    header = f"FILE|{username}|{filename}\n".encode()
    client.sendall(header + data + b"<END>")

    chat.insert(tk.END, f"Sent: {path}\n")
    chat.yview(tk.END)
    

# UI
root = tk.Tk()
root.title("Chat")
root.config(bg="#1e1e1e")

chat = tk.Text(
    root, 
    height=20, width=50,
    bg="#2b2b2b",
    fg="white",
    insertbackground="white",
    state=tk.DISABLED)
chat.pack(padx=10, pady=10)

entry = tk.Entry(
    root, 
    width=40,
     bg="#3a3a3a",
    fg="white",
    insertbackground="white")
entry.pack(padx=10, pady=(0, 10))

btn_frame = tk.Frame(root, bg="#1e1e1e")
btn_frame.pack()

btn_send = tk.Button(
    btn_frame,
    text="Send Text",
    command=send_msg,
     bg="#4CAF50",
    fg="white",
    width=15)
btn_send.pack(side=tk.LEFT, padx=5)

btn_file = tk.Button(
    btn_frame,
    text="Send File",
    command=send_file,
    bg="#2196F3",
    fg="white",
    width=15)
btn_file.pack(side=tk.LEFT, padx=5)

threading.Thread(target=receive, daemon=True).start()

root.mainloop()