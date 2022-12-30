import pygame
import socket
from _thread import *
import colorama
from colorama import Fore, Back, Style

pygame.init()
colorama.init(autoreset=True)
clock = pygame.time.Clock()
CLIENT_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

IP = socket.gethostbyname(socket.gethostname())
PORT = 5689
ADDR = (IP, PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "...left"
windowWidth = 300
windowHeight = windowWidth
FPS = 60
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
AVAILABLE_COLORS = ["GREEN", "RED", "BLUE"]
BREAK_MSG = False
PLAYER_WIDTH = 20
PLAYER_HEIGHT = PLAYER_WIDTH

window = pygame.display.set_mode((windowWidth, windowHeight))
pygame.display.set_caption("MULTIPLAYER-GAME")


class Player:
    def __init__(self, win, x, y, width, height, color, border_radius):
        self.window = win
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.vel = 3
        self.borderRadius = border_radius

    def drawRect(self):
        pygame.draw.rect(self.window, self.color, (self.x, self.y, self.width, self.height), border_radius=self.borderRadius)

    def moveRect(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            self.x -= self.vel
            try:
                sendData(self.x, self.y, self.color)
            except socket.error:
                print(Fore.RED + "(!)Not connected to any server")
        if keys[pygame.K_RIGHT]:
            self.x += self.vel
            try:
                sendData(self.x, self.y, self.color)
            except socket.error:
                print(Fore.RED + "(!)Not connected to any server")
        if keys[pygame.K_UP]:
            self.y -= self.vel
            try:
                sendData(self.x, self.y, self.color)
            except socket.error:
                print(Fore.RED + "(!)Not connected to any server")
        if keys[pygame.K_DOWN]:
            self.y += self.vel
            try:
                sendData(self.x, self.y, self.color)
            except socket.error:
                print(Fore.RED + "(!)Not connected to any server")

        self.drawRect()


other_player = Player(window, -50, -50, PLAYER_WIDTH, PLAYER_HEIGHT, BLACK, 100)


def sendData(x, y, color):
    MESSAGE = f"x_pos: {x}, y_pos: {y}, color: {color}"
    DATA = MESSAGE.encode(FORMAT)
    CLIENT_SOCKET.send(DATA)


def recvData():
    global other_player
    while True:
        DATA = CLIENT_SOCKET.recv(1024)
        if DATA:
            MESSAGE = DATA.decode(FORMAT)
            print(Fore.GREEN + f"[RECEIVED]: {MESSAGE}")
            try:
                other_player_x_pos = int(MESSAGE[MESSAGE.index("x_pos: ") + 7: MESSAGE.index(",")])
                other_player_y_pos = int(MESSAGE[MESSAGE.index("y_pos: ") + 7: MESSAGE.index(", c")])
                other_player_color = MESSAGE[MESSAGE.index("color: ") + 7:]
                other_player = Player(window, other_player_x_pos, other_player_y_pos, PLAYER_WIDTH, PLAYER_HEIGHT, other_player_color, 100)
            except ValueError:
                pass
            if BREAK_MSG:
                break


def connectTOserver(address):
    print(Fore.YELLOW + Style.BRIGHT + "[CONNECTING] trying to connect ...")
    try:
        CLIENT_SOCKET.connect(address)
        print(Fore.BLACK + Back.GREEN + "[CONNECTED] connected to server :)")
        MESSAGE = "--user joined"
        CLIENT_SOCKET.send(MESSAGE.encode(FORMAT))
        start_new_thread(recvData, ())
    except socket.error:
        print(Fore.BLACK + Back.RED + "[!NOT FOUND] cannot connect :(")


def mainLoop():
    global BREAK_MSG
    print(Fore.BLACK + Back.CYAN + "[AVAILABLE COLORS]: GREEN, RED, BLUE")
    IS_COLOR = False
    COLOR = None
    while not IS_COLOR:
        print(Fore.BLUE + "Enter Color: ")
        COLOR = input()
        for i in range(0, len(AVAILABLE_COLORS)):
            if COLOR.upper() == str(AVAILABLE_COLORS[i]):
                print(Fore.BLACK + Back.GREEN + "--game started")
                IS_COLOR = True
                break
        if not IS_COLOR:
            print(Fore.BLACK + Back.RED + "(!)Not a Color")
    run = True
    main_player = Player(window, 50, 10, PLAYER_WIDTH, PLAYER_HEIGHT, COLOR.upper(), 100)
    sendData(main_player.x, main_player.y, main_player.color)
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run = False
        window.fill(WHITE)
        main_player.moveRect()
        other_player.drawRect()
        pygame.display.update()
        clock.tick(FPS)
    pygame.quit()
    print(DISCONNECT_MESSAGE)
    try:
        CLIENT_SOCKET.send(DISCONNECT_MESSAGE.encode(FORMAT))
        BREAK_MSG = True
        CLIENT_SOCKET.close()
        print(Fore.MAGENTA + " --closed the socket")
    except socket.error:
        print(Fore.RED + "no connection is running")


if __name__ == "__main__":
    print(Fore.YELLOW + Style.BRIGHT + "[STARTING] game is starting ...")
    connectTOserver(ADDR)
    mainLoop()
