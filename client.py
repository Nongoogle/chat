import socket
import threading
import os
import subprocess
import tkinter as tk
from tkinter import filedialog
from PIL import Image

# HOST Setup
# feras = "100.121.91.60"
HOST = "100.72.213.77"  # belal
PORT = 50505

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))
username = input("Enter your name: ")

# Define the folder where received files will be saved
SAVE_DIRECTORY = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "Received_Files"
)
os.makedirs(SAVE_DIRECTORY, exist_ok=True)


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
                    chat.config(state=tk.NORMAL)
                    chat.insert(tk.END, f"{sender}\n", "name_left")
                    chat.insert(tk.END, f"{body.decode()}\n\n", "text_left")
                    chat.yview(tk.END)
                    chat.config(state=tk.DISABLED)

                elif info[0] == "FILE":
                    sender = info[1]
                    safe_filename = os.path.basename(info[2])
                    filepath = os.path.join(SAVE_DIRECTORY, safe_filename)

                    with open(filepath, "wb") as f:
                        f.write(body)

                    chat.config(state=tk.NORMAL)
                    chat.insert(tk.END, f"{sender}\n", "name_left")
                    chat.insert(
                        tk.END,
                        f"[File Received: {safe_filename}]\nSaved to: {SAVE_DIRECTORY}\n\n",
                        "text_left",
                    )
                    chat.yview(tk.END)
                    chat.config(state=tk.DISABLED)

        except:
            break


def send_msg():
    msg = entry.get()
    if msg.strip() == "":
        return

    packet = f"MSG|{username}\n{msg}".encode()
    client.sendall(packet + b"<END>")

    chat.config(state=tk.NORMAL)
    chat.insert(tk.END, "Me\n", "name_right")
    chat.insert(tk.END, f"{msg}\n\n", "text_right")
    entry.delete(0, tk.END)
    chat.yview(tk.END)
    chat.config(state=tk.DISABLED)


def send_file():
    path = filedialog.askopenfilename()
    if not path:
        return
    filename = os.path.basename(path)
    with open(path, "rb") as f:
        data = f.read()

    header = f"FILE|{username}|{filename}\n".encode()
    client.sendall(header + data + b"<END>")

    chat.config(state=tk.NORMAL)
    chat.insert(tk.END, "Me\n", "name_right")
    chat.insert(tk.END, f"[File Sent: {filename}]\n\n", "text_right")
    chat.yview(tk.END)
    chat.config(state=tk.DISABLED)


def compress_and_send_file():
    input_path = filedialog.askopenfilename()
    if not input_path:
        return

    current_dir = os.path.dirname(os.path.abspath(__file__))
    ext = os.path.splitext(input_path)[1].lower()

    original_filename = os.path.basename(input_path)
    output_name = "compressed_" + original_filename
    output_path = os.path.join(current_dir, output_name)

    try:
        if ext in [".jpg", ".jpeg", ".png"]:
            myimage = Image.open(input_path)
            if myimage.mode != "RGB":
                myimage = myimage.convert("RGB")
            myimage.save(output_path, quality=50)

        elif ext in [".mp4", ".avi", ".mov", ".mkv"]:
            command = [
                "ffmpeg",
                "-i",
                input_path,
                "-vcodec",
                "libx264",
                "-crf",
                "28",
                "-preset",
                "fast",
                "-acodec",
                "aac",
                "-b:a",
                "128k",
                "-y",
                output_path,
            ]
            try:
                subprocess.run(command, check=True)
            except FileNotFoundError:
                chat.config(state=tk.NORMAL)
                chat.insert(tk.END, "System Error\n", "name_left")
                chat.insert(
                    tk.END,
                    "FFmpeg not found. Ensure it is installed and in your PATH.\n\n",
                    "text_left",
                )
                chat.yview(tk.END)
                chat.config(state=tk.DISABLED)
                return

        else:
            chat.config(state=tk.NORMAL)
            chat.insert(tk.END, "System\n", "name_left")
            chat.insert(
                tk.END, "Unsupported file type for compression.\n\n", "text_left"
            )
            chat.yview(tk.END)
            chat.config(state=tk.DISABLED)
            return

        with open(output_path, "rb") as f:
            data = f.read()

        header = f"FILE|{username}|{output_name}\n".encode()
        client.sendall(header + data + b"<END>")

        chat.config(state=tk.NORMAL)
        chat.insert(tk.END, "Me\n", "name_right")
        chat.insert(tk.END, f"[Compressed File Sent: {output_name}]\n\n", "text_right")
        chat.yview(tk.END)
        chat.config(state=tk.DISABLED)

    except Exception as e:
        chat.config(state=tk.NORMAL)
        chat.insert(tk.END, "System Error\n", "name_left")
        chat.insert(tk.END, f"{str(e)}\n\n", "text_left")
        chat.yview(tk.END)
        chat.config(state=tk.DISABLED)


# UI Setup

root = tk.Tk()
root.title("Secure Chat & Transfer")
root.config(bg="#1e1e1e")
root.geometry("550x650")

# Chat Display Area
chat = tk.Text(
    root,
    bg="#2b2b2b",
    fg="#e0e0e0",
    insertbackground="white",
    state=tk.DISABLED,
    wrap=tk.WORD,
)
chat.pack(padx=15, pady=15, fill=tk.BOTH, expand=True)

# Visual Tags for formatting names and text
chat.tag_configure(
    "name_left", justify="left", foreground="#4CAF50", font=("Segoe UI", 10, "bold")
)
chat.tag_configure("text_left", justify="left", foreground="#e0e0e0")

chat.tag_configure(
    "name_right", justify="right", foreground="#2196F3", font=("Segoe UI", 10, "bold")
)
chat.tag_configure("text_right", justify="right", foreground="#e0e0e0")

entry = tk.Entry(root, bg="#3a3a3a", fg="white", insertbackground="white")
entry.pack(padx=15, pady=(0, 10), fill=tk.X)
entry.bind("<Return>", lambda event: send_msg())

btn_frame = tk.Frame(root, bg="#1e1e1e")
btn_frame.pack(pady=(0, 15))

btn_send = tk.Button(
    btn_frame,
    text="Send Text",
    command=send_msg,
    bg="#4CAF50",
    fg="white",
    width=12,
)
btn_send.pack(side=tk.LEFT, padx=5)

btn_file = tk.Button(
    btn_frame,
    text="Send File",
    command=send_file,
    bg="#2196F3",
    fg="white",
    width=12,
)
btn_file.pack(side=tk.LEFT, padx=5)

btn_compress = tk.Button(
    btn_frame,
    text="Compress & Send",
    command=compress_and_send_file,
    bg="#9C27B0",
    fg="white",
    width=16,
)
btn_compress.pack(side=tk.LEFT, padx=5)

threading.Thread(target=receive, daemon=True).start()

root.mainloop()
