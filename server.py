import socket
import select
import threading
import random
from protocol import encode_message, decode_message
from email_sender import send_email

server = None  # Global server socket
shutdown_flag = False  # Flag to stop server loop
HOST = '127.0.0.1'
PORT = 65432

target_number = random.randint(1, 100)
clients = []
player_names = {}
turn_index = 0
winner_declared = False
print(f"[SERVER] Target number is {target_number}")

def handle_client(conn, addr):
    global turn_index, winner_declared
    print(f"[NEW CONNECTION] {addr} connected.")
    
    while True:
        name_msg = conn.recv(1024).decode()
        _, name, _ = decode_message(name_msg)

        if name in player_names.values():
            # Kirim pesan bahwa nama sudah dipakai
            conn.send(encode_message("NAMEERROR", "server", "Gmail sudah dipakai, masukkan prefix gmail lain:").encode())
        else:
            break  # Nama valid

    player_names[conn] = name
    clients.append(conn)


    # Kirim konfirmasi join
    conn.send(encode_message("RESP", "server", f"Halo {name}, tunggu giliranmu...").encode())

    # Kalau dia pemain pertama, langsung kasih giliran
    if len(clients) == 1:
        conn.send(encode_message("RESP", "server", "Giliranmu! Tebak angka 1-100").encode())

    while True:
        if winner_declared:
            break
        try:
            data = conn.recv(1024).decode()
            if not data:
                break
            msg_type, sender, msg = decode_message(data)

            if msg_type == "CHAT":
                # Kirim ke semua klien yang bukan pengirim & bukan yang sedang nebak
                for c in clients:
                    if c != conn:
                        try:
                            c.send(encode_message("CHAT", sender, msg).encode())
                        except:
                            pass
                continue  # lanjut ke loop berikutnya, tidak hitung giliran


            if msg_type == "GUESS" and clients[turn_index] == conn:
                try:
                    guess = int(msg)
                except ValueError:
                     # Kirim pesan error jika input bukan angka
                    conn.send(encode_message("RESP", "server", "Bukan Integer, masukkan angka!").encode())
                    
                    turn_index = (turn_index + 1) % len(clients)
                    next_conn = clients[turn_index]
                    next_conn.send(encode_message("RESP", "server", "Giliranmu! Tebak angka 1-100").encode())
                    continue 
                if guess < target_number:
                    conn.send(encode_message("RESP", "server", "Terlalu kecil").encode())
                elif guess > target_number:
                    conn.send(encode_message("RESP", "server", "Terlalu besar").encode())
                else:
                    broadcast(encode_message("WINNER", "server", f"{sender}"))
                    send_email(sender)
                    winner_declared = True
                    shutdown_server()
                    break

                print(f"processing next turn. lenclients:{len(clients)}")
                # Next turn
                turn_index = (turn_index + 1) % len(clients)
                next_conn = clients[turn_index]
                next_conn.send(encode_message("RESP", "server", "Giliranmu! Tebak angka 1-100").encode())

        except Exception as e:
            print(f"[ERROR] {e}")
            break
    conn.close()
    print(f"[DISCONNECTED] {addr} disconnected.")


def broadcast(message):
    for client in clients:
        try:
            client.send(message.encode())
        except:
            pass

def shutdown_server():
    global shutdown_flag, server
    shutdown_flag = True

    # Inform all clients
    broadcast(encode_message("END", "server", "Game selesai. Server dimatikan."))

    # Close all client connections
    for client in clients:
        try:
            client.shutdown(socket.SHUT_RDWR)
            client.close()
        except:
            pass

    # Close the server socket
    if server:
        try:
            server.close()
        except:
            pass

    print("[SERVER SHUTDOWN] Server has been shut down.")


def start():
    global server, shutdown_flag
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"[LISTENING] Server is listening on {HOST}:{PORT}")

    while not shutdown_flag:
        try:
            server.settimeout(1.0)  # Timeout to allow shutdown_flag checking
            conn, addr = server.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()
        except socket.timeout:
            continue
        except OSError:
            break 

if __name__ == "__main__":
    start()