import os
import socket
import threading
import time
import sys

WAITING_LIST = []  # containing the tuple of the invite name (src,dst)
MEMBER_DICT = {}  # organizing the members by their thread number
PARTY_DICT = {}  # organizing the usernames' party by their names
SONGS_DICT = {}


def log_tcp(tid, func_num):
    if func_num == "01":
        print(f"Client number {tid} SENT command:USERNAME")
    elif func_num == "02":
        print(f"Client number {tid} SENT command:GET_SONG")
    elif func_num == "03":
        print(f"Client number {tid} SENT command:ADD_NAME")


def remove_participant(leader_tid, current_name):
    global MEMBER_DICT, PARTY_DICT
    i = PARTY_DICT[MEMBER_DICT[leader_tid]].index(current_name)
    PARTY_DICT[MEMBER_DICT[leader_tid]][i] += "-LEFT"


def in_party(sock, leader_tid, tid):
    global PARTY_DICT, MEMBER_DICT, SONGS_DICT
    sock.settimeout(3)
    try:
        while MEMBER_DICT[tid] in PARTY_DICT[MEMBER_DICT[leader_tid]]:
            try:
                sock.recv(2)
                remove_participant(leader_tid, MEMBER_DICT[tid])
                time.sleep(0.3)
                sock.send("OK")
            except socket.timeout:
                if SONGS_DICT[MEMBER_DICT[tid]]:
                    sock.send(SONGS_DICT[MEMBER_DICT[tid]])
                    SONGS_DICT[MEMBER_DICT[tid]] = b""
            except socket.error:
                remove_participant(leader_tid, MEMBER_DICT[tid])
    except Exception as exp:
        print(exp)
    sock.send("0005".encode())
    SONGS_DICT[MEMBER_DICT[tid]] = b""
    sock.settimeout(0.1)

        
def song_exist(sock, length):
    song = sock.recv(length)
    song = song.decode()
    if len(sys.argv) > 1:
        if os.path.exists(fr"{sys.argv[1]}\{song}.mp3"):
            return True, song
    else:
        if os.path.exists(fr"{song}.mp3"):
            return True, song
    return False, song


def send_song(sock, length, tid):
    global PARTY_DICT, MEMBER_DICT, SONGS_DICT
    song = song_exist(sock, length)
    if song[0]:
        if len(sys.argv) > 1:
            song_file = open(fr"{sys.argv[1]}\{song[1]}.mp3", 'rb')
        else:
            song_file = open(fr"{song[1]}.mp3", 'rb')
        data = song_file.read()
        data = (f"0001OK{str(len(song[1])).zfill(3)}{song[1]}".encode() + data + "0001END".encode())
        participant_list = PARTY_DICT[MEMBER_DICT[tid]]
        for username in participant_list:
            SONGS_DICT[username] = data
            time.sleep(1.5)
        sock.send(data)
        song_file.close()
    else:
        data = f"0001NO{str(len(song[1])).zfill(3)}{song[1]}"
        sock.send(data.encode())


def client_answer(sock, tid):
    global WAITING_LIST, PARTY_DICT, MEMBER_DICT
    for pair in WAITING_LIST:
        if pair[1] == MEMBER_DICT[tid]:
            temp = MEMBER_DICT
            sock.send("0002".encode())
            sock.settimeout(10)
            try:
                data = sock.recv(2)
                if data.decode() == "OK":
                    sock.send(f"{str(len(pair[0]) + len(pair[1]) + 1).zfill(3)}{pair[0]}~{pair[1]}".encode())
                    data = sock.recv(2)
                    if data.decode() == "NO":
                        PARTY_DICT[pair[0]].append(f"{pair[1]}-DECLINED")
                    else:
                        print(MEMBER_DICT)
                        print(temp)
                        PARTY_DICT[pair[0]].append(f"{pair[1]}")
                        print(MEMBER_DICT)
                        print(temp)
                        host_tid = (list(temp.keys())[list(temp.values()).index(pair[0])])
                        print(MEMBER_DICT)
                        print(temp)
                        in_party(sock, host_tid, tid)
                        break
            except socket.timeout:
                PARTY_DICT[pair[0]].append(f"{pair[1]}-DECLINED")
            sock.settimeout(0.1)


def ask_member(sock, length_name_dst, name_src):
    global WAITING_LIST, PARTY_DICT
    name_dst = sock.recv(length_name_dst)
    name_dst = name_dst.decode()
    if name_dst in list(PARTY_DICT.keys()):
        if name_dst not in WAITING_LIST and name_dst != name_src:
            WAITING_LIST.append((name_src, name_dst))
            for _ in range(0, 25):
                if name_dst in PARTY_DICT[name_src]:
                    WAITING_LIST.remove((name_src, name_dst))
                    return True, name_dst
                elif f"{name_dst}-DECLINED" in PARTY_DICT[name_src]:
                    PARTY_DICT[name_src].remove(f"{name_dst}-DECLINED")
                    WAITING_LIST.remove((name_src, name_dst))
                    return False, "TIMEOUT"
                time.sleep(0.5)
            WAITING_LIST.remove((name_src, name_dst))
        return False, "DECLINED"
    return False, "EXIST"


def add_new_username(username, tid):
    global MEMBER_DICT, PARTY_DICT, SONGS_DICT
    if not ('~' in username):
        if username not in list(MEMBER_DICT.values()):
            MEMBER_DICT[tid] = username
            PARTY_DICT[username] = []
            SONGS_DICT[username] = b""
            return True,
        return False, b"02"
    return False, b"01"


def handle_protocol(clt_sock, tid, func_num):
    global PARTY_DICT, MEMBER_DICT
    try:
        if func_num == "01":
            log_tcp(tid, func_num)
            username_length = int(clt_sock.recv(3).decode())  # the length of the message
            answer = add_new_username(clt_sock.recv(username_length).decode(), tid)
            if answer[0]:
                clt_sock.send("OK".encode())
            else:
                clt_sock.send("NO".encode() + answer[1])

        elif func_num == "02":
            log_tcp(tid, func_num)
            song_length = int(clt_sock.recv(3).decode())  # the length of the song
            send_song(clt_sock, song_length, tid)

        elif func_num == "03":
            log_tcp(tid, func_num)
            name_length = int(clt_sock.recv(3))  # the length of the name
            is_accepted = ask_member(clt_sock, name_length, MEMBER_DICT[tid])
            if is_accepted[0]:
                clt_sock.send(f"0003OK{str(len(is_accepted[1])).zfill(3)}{is_accepted[1]}".encode())
            else:
                clt_sock.send(f"0003NO{is_accepted[1]}".encode())
        elif func_num == "04":
            name_length = int(clt_sock.recv(3))
            name = clt_sock.recv(name_length).decode()
            remove_participant(tid, name)
        return False
    except socket.error:
        return True


def handle_client(clt_sock, tid, addr):
    global MEMBER_DICT, WAITING_LIST, PARTY_DICT, SONGS_DICT
    finish = False
    print(f"client '({tid})' has joined from {addr}")
    clt_sock.settimeout(0.1)
    while not finish:
        try:
            try:
                if PARTY_DICT[MEMBER_DICT[tid]]:
                    for name in PARTY_DICT[MEMBER_DICT[tid]]:  # Checks if one of the members has left
                        if "-LEFT" in name:
                            clt_sock.send(f"0004{str(len(name) - 5).zfill(3)}{name[:len(name) - 5]}".encode())
                            PARTY_DICT[MEMBER_DICT[tid]].remove(name)

            except KeyError:
                pass
            client_answer(clt_sock, tid)
            byte_data = clt_sock.recv(2)  # first two bytes refers to the function number
            if byte_data == b'':
                print(f"Seems client '({tid})' disconnected")
                break
            clt_sock.settimeout(None)
            finish = handle_protocol(clt_sock, tid, byte_data.decode())
            clt_sock.settimeout(0.5)
            if finish:
                time.sleep(1)
                break
        except socket.timeout:
            continue
        except socket.error as err:
            print(f'Socket Error exit client loop: err:  {err}')
            break
        except Exception as err:
            print(f'General Error %s exit client loop: {err}')
            break
    print(f"Client '({tid})' Exit\r\n {MEMBER_DICT}")
    try:
        PARTY_DICT.pop(MEMBER_DICT[tid])
        SONGS_DICT.pop(MEMBER_DICT[tid])
        MEMBER_DICT.pop(tid)  # deleting the client's username from the dictionary
    except KeyError:
        print(f"Seems like client '({tid})' disconnected before he picked a nickname")
    clt_sock.close()


def main():
    threads = []
    srv_sock = socket.socket()

    srv_sock.bind(('0.0.0.0', 13389))
    srv_sock.listen(20)  # setting up the server socket
    # next line release the port
    srv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    i = 1
    while True:
        cli_sock, addr = srv_sock.accept()
        t = threading.Thread(target=handle_client, args=(cli_sock, str(i), addr))
        t.start()
        threads.append(t)  # appending the client's thread to the thread list
        i += 1
        if i > 100000000:
            break

    srv_sock.close()
    print('Bye...')


if __name__ == '__main__':
    main()
