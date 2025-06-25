import socket
import threading
from protocol import encode_message, decode_message

HOST = '127.0.0.1'
PORT = 65432

name = input("Masukkan prefix email Anda: ")
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))
client.send(encode_message("JOIN", name, "").encode())

turn_active = False
running = True

def receive_messages():
    global turn_active, running, name
    while running:
        try:
            data = client.recv(1024).decode()
            if not data:
                print("Server disconnected.")
                running = False
                break

            msg_type, sender, msg = decode_message(data)

            if msg_type == "NAMEERROR":
                print(f"[SERVER] {msg}")
                name = input("Masukkan prefix email lagi: ")
                client.send(encode_message("JOIN", name, "").encode())

            elif msg_type == "WINNER":
                if msg == name:
                    print("Kamu pemenangnya!")
                else:
                    print(f"[SERVER] {msg} pemenangnya!")

            elif msg_type == "END":
                print("[SERVER] Game selesai.")
                running = False
                break

            elif msg_type == "RESP":
                print(f"[SERVER] {msg}")
                if msg == "Giliranmu! Tebak angka 1-100":
                    turn_active = True
                else:
                    turn_active = False

            elif msg_type == "CHAT":
                print(f"[{sender} (chat)] {msg}")

        except Exception as e:
            print(f"[ERROR] {e}")
            break

def send_messages():
    global turn_active, running, name
    while running:
        try:
            if turn_active:
                guess = input("[Giliranmu] Tebakan Anda: ")
                client.send(encode_message("GUESS", name, guess).encode())
                turn_active = False
            else:
                msg = input()
                if msg.strip() != "":
                    client.send(encode_message("CHAT", name, msg).encode())
        except Exception as e:
            print(f"[ERROR] {e}")
            break

recv_thread = threading.Thread(target=receive_messages)
send_thread = threading.Thread(target=send_messages)
recv_thread.start()
send_thread.start()
recv_thread.join()
send_thread.join()
client.close()
