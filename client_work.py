import socket
from protocol import encode_message, decode_message

HOST = '127.0.0.1'
PORT = 65432

name = input("Masukkan prefix email Anda: ")
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))
client.send(encode_message("JOIN", name, "").encode())

while True:
    data = client.recv(1024).decode()

    # untuk handling []
    if not data:
        print("Server disconnected.")
        break

    msg_type, sender, msg = decode_message(data)

    print(f"[{sender}] {msg}")

    if msg_type == "NAMEERROR":
        name = input("Masukkan prefix email lagi: ")
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((HOST, PORT))
        client.send(encode_message("JOIN", name, "").encode())

    if msg_type == "WINNER":
        if msg == name:
            print("Kamu pemenangnya!")
        else:
            print(f"[server] {msg} pemenangnya!")
        continue  # Wait for END

    if msg_type == "END":
        print("Server menutup koneksi. Program berhenti.")
        break

    if msg_type == "RESP" and msg == "Giliranmu! Tebak angka 1-100":
        guess = input("Tebakan Anda: ")
        client.send(encode_message("GUESS", name, guess).encode())

client.close()