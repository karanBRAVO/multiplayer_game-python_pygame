import socket
from _thread import *
import colorama
from colorama import Fore, Back, Style

SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
colorama.init(autoreset=True)

IP = socket.gethostbyname(socket.gethostname())
PORT = 5689
ADDR = (IP, PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "...left"
CONN_LIST = []
OBJ_LIST = []

SOCKET.bind(ADDR)


def handleClientData(conn, addr, conn_list):
    print(Fore.BLACK + Back.MAGENTA + f"[NEW CLIENT] {addr[0]} : {addr[1]}")

    while True:
        CLIENT_DATA = conn.recv(1024)
        if CLIENT_DATA:
            CLIENT_MESSAGE = CLIENT_DATA.decode(FORMAT)
            print(Fore.GREEN + f"[RECEIVED] {addr[1]}: {CLIENT_MESSAGE}")
            if CLIENT_MESSAGE != "--user joined":
                OBJ_LIST.append(CLIENT_MESSAGE)
            if len(conn_list) > 1:
                for i in range(0, len(conn_list)):
                    if conn_list[i] != conn:
                        print(Fore.BLACK + Back.BLUE + "[SENDING] sending messages ...")
                        if CLIENT_MESSAGE == DISCONNECT_MESSAGE:
                            MSG = "--user left"
                        else:
                            MSG = CLIENT_MESSAGE
                        SEND_MESSAGE = MSG.encode(FORMAT)
                        conn_list[i].send(SEND_MESSAGE)
                        print(Fore.BLACK + Back.GREEN + "--[SUCCESS] message sent successfully ...")
            if CLIENT_MESSAGE == DISCONNECT_MESSAGE:
                MSG = "[SERVER]: Bye"
                conn.send(MSG.encode(FORMAT))
                conn_list.pop(conn_list.index(conn))
                break

    print(Fore.MAGENTA + "[CLOSING] closing the connection ...")
    conn.close()
    print(Fore.BLACK + Back.CYAN + f"--closed for {addr[1]}")


def startServer():
    SOCKET.listen()
    print(Fore.YELLOW + Style.BRIGHT + f"[LISTENING] (on port {PORT}) server is listening  ...")

    while True:
        print(Fore.BLUE + "[WAITING] waiting for connections ...")
        conn, addr = SOCKET.accept()
        CONN_LIST.append(conn)
        start_new_thread(handleClientData, (conn, addr, CONN_LIST))


if __name__ == "__main__":
    print(Fore.YELLOW + Style.BRIGHT + "[STARTING] server is starting ...")
    startServer()
