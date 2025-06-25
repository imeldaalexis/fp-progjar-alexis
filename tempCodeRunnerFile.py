import socket
from protocol import encode_message, decode_message

HOST = '127.0.0.1'
PORT = 65432

name = input("Masukkan nama Anda: ")
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))
client.send(encode_message("JOIN", name, "").encode())

while True:
    data = client.recv(1024).decode()
    msg_type, sender, msg = decode_message(data)
    print(f"[{sender}] {msg}")

    if msg_type == "WINNER":
        print("Kamu pemenangnya!")
        break

    if msg_type == "RESP" and msg == "Bukan giliranmu":
        continue

    if msg_type == "RESP" and msg == "Giliranmu! Tebak angka 1-100":
        guess = input("Tebakan Anda: ")
        client.send(encode_message("GUESS", name, guess).encode())

