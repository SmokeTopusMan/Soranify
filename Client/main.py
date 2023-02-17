import os
import tkinter as tk
import pygame
import socket
import threading
import time
import UserScreen
import StartScreen
import sys

# Initializing pygame
pygame.mixer.init()

# True if the client is connected
CONNECTED = False
PARTY_INV = False
WAITING = False
NAME = ""

global user_screen
# The first tk window for the username
root = tk.Tk()
start_screen = StartScreen.StartScreen(root)


def log_tcp(command):
    if len(command) == 2:
        if command == "01":
            print(f"SENDING command:USERNAME from CLIENT")
        elif command == "02":
            print(f"SENDING command:GET_SONG from CLIENT")
        elif command == "03":
            print(f"SENDING command:ADD_NAME from CLIENT")
        elif command == "04":
            print(f"SENDING command:REMOVE_PARTICIPANT from CLIENT")
    else:
        if command == "0001":
            print(f"RECEIVING command:TRANSFERRING_SONG from SERVER")
        elif command == "0002":
            print(f"RECEIVING command:NAME_INVITE from SERVER")
        elif command == "0003":
            print(f"RECEIVING command:NAME_ACCEPTED from SERVER")
        elif command == "0004":
            print(f"RECEIVING command:KICKED from SERVER")


def recv_from_server(sock, u_screen):
    global CONNECTED, PARTY_INV
    while CONNECTED:
        try:
            data = sock.recv(4)
            handle_protocol(data.decode(), sock, u_screen)
            if PARTY_INV:
                handle_protocol("0002", sock, u_screen)
                PARTY_INV = False
        except socket.error:
            print("server died! very sad")
            CONNECTED = False
        except Exception as e:
            print(e)
            continue


def remove_participant(sock, u_screen):
    name_length = sock.recv(3)
    name = sock.recv(int(name_length))
    u_screen.remove_participant(name.decode())


def recv_inv(sock, u_screen):
    names_length = int(sock.recv(3))
    names = sock.recv(names_length).decode().split('~')
    u_screen.party_req(names[0])
    for _ in range(0, 10):
        if u_screen.In_Party:
            sock.send("OK".encode())
            break
        time.sleep(1)
    if not u_screen.In_Party:
        pass
        sock.send("NO".encode())


def recv_inv_ans(sock, u_screen):
    data = sock.recv(2)
    if data.decode() == "OK":
        data = int(sock.recv(3))
        name = sock.recv(data).decode()
        u_screen.add_name(name)
        u_screen.ser_ans("Listener Has Been Added!")
    else:
        data = sock.recv(7)
        if data.decode() == "TIMEOUT":
            u_screen.ser_ans("Listener Took Too Long\nTo Respond. Try Again!")
        elif data.decode() == "DECLINED":
            u_screen.ser_ans("Listener Didn't Want To\nJoin. What A Party Pooper...")
        else:
            u_screen.ser_ans("Seems Like Listener Does\n Not Exist...\n Check The Name Again!?!?")


def recv_song(sock, u_screen):
    global PARTY_INV
    tries = 2  # this is the amount of the attempts the func will try to get the song
    ans = sock.recv(2)
    song_name_length = int(sock.recv(3))
    song = sock.recv(song_name_length).decode()  # the name of the song
    if ans.decode() == "OK":
        song_file = open(f"{song}.mp3", "wb")
        u_screen.ser_ans("Loading Song...")
        sock.settimeout(4)
        while tries > 0:
            try:
                data = sock.recv(1024)
                if len(data) != 1024:
                    try:
                        if len(data) > 3:
                            if data[len(data) - 7:].decode() == "0001END":
                                tries -= 2
                            elif data[len(data) - 4:].decode() == "0004":
                                PARTY_INV = True
                                tries -= 2
                    except UnicodeDecodeError:
                        pass
                song_file.write(data)
            except sock.timeout:
                tries -= 1
                if tries == 0:
                    u_screen.ser_ans("Server Took To Long\n To Respond Try Again!")
                    break
            except Exception as exe:  # ToDo: change to the right exception
                print(exe)
                time.sleep(1.5)
                tries -= 1
                if tries == 0:
                    u_screen.ser_ans("Server Took To Long\n To Respond Try Again!")
        if song_file:
            u_screen.add_song(song)
            u_screen.ser_ans("Successfully Loaded!")
        sock.settimeout(None)
        song_file.close()
    else:
        u_screen.ser_ans(f"Couldn't Find:  '{song}'\nTry Again <3!")


def handle_protocol(message, sock, u_screen=None, func_num=""):
    """
    the function gets a message and a command num
    and building the message according to protocol.
    it also receives a message and determine whether
    the server got the message or not.
    :param sock
    :param u_screen
    :param message
    :param func_num
    :returns XXX if the server declined and "" if the nickname has been approved
    """
    if len(func_num) == 2:
        message = message.replace("\n", "").replace("\r", "")
        if func_num == "01":
            message = f"{func_num}{(str(len(message))).zfill(3)}{message}"
            log_tcp(func_num)
        elif func_num == "02":
            if message in u_screen.get_songs():
                u_screen.ser_ans("Cant Duplicate Songs!")
                return None
            else:
                message = f"{func_num}{(str(len(message))).zfill(3)}{message}"
                log_tcp(func_num)
        elif func_num == "03":
            if message in u_screen.get_names():
                u_screen.ser_ans("Cant Duplicate Names!")
                return None
            else:
                message = f"{func_num}{(str(len(message))).zfill(3)}{message}"
                log_tcp(func_num)
        elif func_num == "04":
            message = f"04{str((len(message))).zfill(3)}{message}"
            log_tcp(func_num)
        return message.encode()
    if len(message) == 4:
        if message == "0001":
            log_tcp(message)
            recv_song(sock, u_screen)
        elif message == "0002":
            sock.send("OK".encode())
            recv_inv(sock, u_screen)
        elif message == "0003":
            log_tcp(message)
            recv_inv_ans(sock, u_screen)
        elif message == "0004":
            remove_participant(sock, u_screen)
        elif message == "0005":
            u_screen.In_Party = False
            u_screen.ser_ans("You Were Kicked From \r\n The Party")
            log_tcp(message)

    if message == "NO":
        ans = sock.recv(2)
        if ans == b"01":
            # clears the text and point the pointer to the first line
            u_screen.change_screen_username()
        elif ans == b"02":
            u_screen.change_screen_invalid()
        return "XXX"
    return ""


def first_entry(sock, s_screen, u_root) -> None:  # ToDO: If there is time, add this func to the recv_from_server func
    """
    checks if the user first entered the username
    :param u_root:
    :param s_screen:
    :param sock
    """
    global CONNECTED, NAME
    last_name = ""
    while True:
        try:
            username = s_screen.Username
            if username == last_name or username == '':
                continue
            last_name = username
            username = handle_protocol(username, sock, func_num="01")
            sock.send(username)
            answer = sock.recv(2)
            answer = answer.decode()
            if handle_protocol(answer, sock, s_screen) == "":
                print("The server has accepted your username")
                CONNECTED = True
                u_root.quit()
                NAME = last_name
                break
            else:
                username = ""
        except socket.error as err:
            print(f'Got socket error: {err}')
            try:
                u_root.destroy()
            except RuntimeError:
                pass
            break
        except Exception as err:
            print(f'General error: {err}')
            try:
                u_root.destroy()
            except RuntimeError:
                pass
            break


def handle_client(sock, u_screen, u_root):
    """
    this function handles the client,
    it sends the wanted message to the server and
    receiving from the server
    :param: sock
    :return: None
    """
    global CONNECTED
    recv_thread = threading.Thread(target=recv_from_server, args=(sock, u_screen))
    recv_thread.start()
    while CONNECTED:
        try:
            if u_screen.Song == "" and u_screen.wanted_username == "" and u_screen.Kick_name == "":
                time.sleep(0.1)
                continue
            else:
                if u_screen.In_Party:
                    u_screen.ser_ans("Cannot do that \r\n While In Party!")
                elif u_screen.Song != "":
                    data = handle_protocol(u_screen.Song, sock, u_screen, "02")
                    if len(data) != 5:
                        sock.send(data)
                elif u_screen.wanted_username != "":
                    data = handle_protocol(u_screen.wanted_username, sock, u_screen, "03")
                    if len(data) != 5:
                        sock.send(data)
                elif u_screen.Kick_name != "":
                    data = handle_protocol(u_screen.Kick_name, sock, u_screen, "04")
                    sock.send(data)
                u_screen.Song = ""
                u_screen.wanted_username = ""
                u_screen.Kick_name = ""

        except socket.error as err:
            print(f'Got socket error: {err}')
            break
        except Exception as err:
            print(f'General error: {err}')
            break
    try:
        u_root.destroy()
    except RuntimeError:
        pass


def main(ip, s_screen, u_root):
    global user_screen, CONNECTED, NAME
    sock = socket.socket()
    port = 13389
    try:
        sock.connect((ip, port))
        print(f'Connection succeeded {ip}:{port}')
        # check if the server accepted the username
        username_thread = threading.Thread(target=first_entry, args=(sock, s_screen, u_root))
        username_thread.start()
        u_root.mainloop()
    except Exception as exe:
        print(f'Error while trying to connect.  Check ip or port -- {ip}:{port}')
        print(exe)

    # The second tk window for the app
    if CONNECTED:
        user_screen = UserScreen.User_Screen(u_root, NAME)
        user_thread = threading.Thread(target=handle_client, args=(sock, user_screen, u_root))
        user_thread.start()
        u_root.mainloop()
    CONNECTED = False
    try:
        pygame.mixer.music.stop()
        pygame.mixer.stop()  # Turning off the mixer if it activated
        pygame.mixer.quit()
    except pygame.error:
        pass
    print('Bye')
    sock.close()


if __name__ == '__main__':
    time.sleep(0.3)
    files = os.listdir(fr"{sys.argv[0]}\..")
    for file in files:  # Deleting every mp3 files remaining in the client directory
        if ".mp3" in file:
            os.remove(file)
    if len(sys.argv) > 1:
        main(sys.argv[1], start_screen, root)
    else:
        clt_ip = input("Enter The Wanted IP (if its on this computer enter -1): ")
        if clt_ip != "-1":
            main(clt_ip, start_screen, root)
        else:
            main('127.0.0.1', start_screen, root)
