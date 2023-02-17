from tkinter import *
from tkinter import font
import pygame
import os
import random
import time

# Initialize Pygame Mixer
pygame.mixer.init()


class User_Screen:

    def __init__(self, master, name):
        self.master = master
        self.master.title("SoraniFy")
        self.master.iconbitmap('Pics For The App/icon - 256.ico')
        self.master.geometry("1450x630")
        bg = Label(self.master, bg='#54545C')
        bg.place(x=0, y=0, width=1450, height=630)

        # Make The Main Arguments
        self.Name = name
        self.Kick_name = ""
        self.Random = False
        self.Paused = False
        self.Song_Num = 0
        self.In_Party = False
        self.Leave = False
        self.Song = ""
        self.wanted_username = ""

        # Create Playlist Box
        self.song_box = Listbox(self.master, bg='Black', fg='White', highlightbackground='Black', highlightcolor='Blue', selectbackground='Black', selectforeground='Green', width=60, height=19, font=font.Font(family='Helvetica', size=16, weight='bold'))
        self.song_box.place(x=350)

        # Create Participants Frame
        self.participants_frame = Frame(self.master, bg='#54545C', highlightbackground='Black', highlightcolor='Blue')
        self.participants_frame.place(x=1100)
        self.participant_box = Listbox(self.participants_frame, bg='#595959', fg='White', highlightbackground='Black', highlightcolor='Blue', selectbackground='Black', selectforeground='Green', width=20, height=19, font=font.Font(family='Malgun Gothic', size=14, weight='bold'))
        self.participant_box.grid(row=0, column=1, padx=5, pady=10)
        self.participant_box.insert(END, (self.Name + "  --->  HOST"))

        # Create Participant Name Box
        self.participant_pop_frame = Frame(self.master, bg="Grey", pady=20, padx=20)
        self.participant_text = Text(self.participant_pop_frame, width=25, height=1.1, bg="white", fg="Green", font=("Times New Roman", 14))
        self.participant_text.bind("<Return>", lambda event: self.get_username())
        self.participant_text["wrap"] = "none"
        self.submit_button = Button(self.participant_pop_frame, text="Enter", bg="#5FBD88", fg="#9B49D1", font=("Comic Sans MS",), activebackground="#53A677", activeforeground="#B957FA", command=lambda: self.get_username())
        self.participant_text.grid(row=0, column=0)
        self.submit_button.grid(row=0, column=1, padx=15)

        # Create Accept Button When is Asked for Party:
        self.party_req_frame = Frame(self.master, bg="Grey", pady=20, padx=20)
        self.accept_button = Button(self.party_req_frame, text="accept", bg="#5FBD88", fg="#9B49D1", font=("Comic Sans MS",), activebackground="#53A677", activeforeground="#B957FA", command=lambda: self.party_accept())
        self.decline_button = Button(self.party_req_frame, text="decline", bg="#5FBD88", fg="#9B49D1", font=("Comic Sans MS",), activebackground="#53A677", activeforeground="#B957FA", command=lambda: self.party_decline())
        self.invite_text = Label(self.party_req_frame, text="", bg='#54545C', fg='Red', width=50, height=3, font=("Microsoft JhengHei", 14))
        self.invite_text.grid(row=1, column=0)
        self.accept_button.grid(row=2, column=0)
        self.decline_button.grid(row=0, column=0)

        # Create New Songs Box
        self.new_songs_frame = Frame(self.master, bg='#54545C', highlightbackground='Black', highlightcolor='Blue', width=290, height=724)
        self.new_songs_frame.place(x=2)

        # Create Server Answer Box
        self.server_ans = Label(self.master, text="Enter Your Desired", bg='#54545C', fg='Red', highlightbackground='Black', highlightcolor='Blue', width=25, height=3, font="Stencil")

        # Create Text Box For Searching Song
        self.text_box = Text(self.new_songs_frame, width=20, height=1.1, bg="white", fg="Green", font=("Times New Roman", 14))
        self.text_box.bind("<Return>", lambda event: self.get_song())
        self.text_box["wrap"] = "none"

        # Define Player Control Button Images
        self.back_btn_img = PhotoImage(file=r'Pics For The App\left button 50.png')
        self.forward_btn_img = PhotoImage(file=r'Pics For The App\right button 50.png')
        self.play_btn_img = PhotoImage(file=r'Pics For The App\play button 50.png')
        self.pause_btn_img = PhotoImage(file=r'Pics For The App\unpause button 50.png')
        self.stop_btn_img = PhotoImage(file=r'Pics For The App\stop button 50.png')
        self.add_song_btn_img = PhotoImage(file=r'Pics For The App\add song button 80.png')
        self.remove_song_img = PhotoImage(file=r'Pics For The App\remove song button 35.png')
        self.random_btn_img = PhotoImage(file=r'Pics For The App\not random 50.png')
        self.loop_btn_img = PhotoImage(file=r'Pics For The App\not repeat 50.png')
        self.add_participant_img = PhotoImage(file=r'Pics For The App\add client button 35.png')

        # Create Player Control Frame
        controls_frame = Frame(self.master, bg='#54545C')
        controls_frame.place(x=490, y=520)

        # Create Player Control Buttons
        self.back_button = Button(controls_frame, image=self.back_btn_img, borderwidth=0, bg='Black', activebackground='Black', command=lambda: self.previous_song())
        self.forward_button = Button(controls_frame, image=self.forward_btn_img, borderwidth=0, bg='Black', activebackground='Black', command=lambda: self.next_song())
        self.play_button = Button(controls_frame, image=self.play_btn_img, borderwidth=0, bg='Black', activebackground='Black', command=lambda: self.play())
        self.pause_button = Button(controls_frame, image=self.pause_btn_img, borderwidth=0, bg='Black', activebackground='Black', command=lambda: self.pause())
        self.stop_button = Button(controls_frame, image=self.stop_btn_img, borderwidth=0, bg='Black', activebackground='Black', command=lambda: self.stop())

        # Add song to the playlist
        self.add_song_button = Button(self.new_songs_frame, image=self.add_song_btn_img, borderwidth=0, bg='Black', activebackground='Black', command=lambda: self.get_song())
        self.remove_song_button = Button(self.new_songs_frame, image=self.remove_song_img, borderwidth=0, bg='Black', activebackground='Black', command=lambda: self.delete_song())

        # Those are special buttons, their image is changing according to their status
        self.random_button = Button(controls_frame, image=self.random_btn_img, borderwidth=0, bg='Black', activebackground='Black', command=lambda: self.random())

        # add/remove participants to the list:
        self.add_participant_button = Button(self.participants_frame, image=self.add_participant_img, borderwidth=0, bg='Black', activebackground='Black', command=lambda: self.get_participant_name())
        self.remove_participant_button = Button(self.participants_frame, image=self.remove_song_img, borderwidth=0, bg='Black', activebackground='Black', command=lambda: self.remove_participant_click())

        # Add the Buttons To The Frame
        self.back_button.grid(row=0, column=0, padx=10)
        self.play_button.grid(row=0, column=1, padx=10)
        self.pause_button.grid(row=0, column=2, padx=10)
        self.stop_button.grid(row=0, column=3, padx=10)
        self.random_button.grid(row=0, column=4, padx=10)
        self.forward_button.grid(row=0, column=6, padx=10)

        self.add_song_button.grid(row=0, column=0, padx=10, pady=20)
        self.remove_song_button.grid(row=0, column=2, padx=2, pady=20)

        self.add_participant_button.grid(row=0, column=0, padx=5, pady=10)
        self.remove_participant_button.grid(row=0, column=2, padx=5, pady=10)

        self.server_ans.place(x=20, y=200)

    # Delete the current song
    def delete_song(self):
        if self.song_box.size() != 0:
            try:
                song_name = f"{self.song_box.get(self.song_box.curselection())}"
                if self.Song_Num == self.song_box.curselection()[0]:
                    if self.Song_Num > 0:
                        self.Song_Num -= 1
                    self.song_box.delete(self.song_box.curselection())
                    if self.song_box.size() != 0:
                        self.next_song()
                    else:
                        pygame.mixer.music.stop()
                        pygame.mixer.quit()
                        pygame.mixer.init()
                        self.clear_pause_button()

                elif self.Song_Num > self.song_box.curselection()[0]:
                    self.Song_Num -= 1
                    self.song_box.delete(ANCHOR)
                else:
                    self.stop()
                    self.song_box.delete(ANCHOR)
            except Exception:
                song_name = f"{self.song_box.get(0)}"
                if self.Song_Num == 0:  # if the song is not selected but the first song is being played
                    self.Song_Num -= 1
                    self.song_box.delete(0)
                    self.next_song()
                else:
                    self.song_box.delete(0)
                    self.Song_Num -= 1
                pygame.mixer.music.stop()
                pygame.mixer.quit()
                pygame.mixer.init()
            os.remove(f"{song_name}.mp3")

    # Play selected song
    def play(self):
        self.clear_pause_button()
        song = self.song_box.get(ACTIVE)
        try:
            self.Song_Num = self.song_box.curselection()[0]
        except IndexError:
            self.Song_Num = 0
        if song != '':
            song = f"{song}.mp3"
            # Clear active bar in playlist listbox
            self.song_box.selection_clear(0, END)
            # Activate new bar
            self.song_box.activate(self.Song_Num)
            # Set Active bar to the current song
            self.song_box.selection_set(self.Song_Num, last=None)
            pygame.mixer.music.load(song)
            pygame.mixer.music.play(loops=0)

    # Stop playing the current song
    def stop(self):
        pygame.mixer.music.stop()
        self.song_box.selection_clear(ACTIVE)
        self.clear_pause_button()

    # Add a song if it exist
    def get_song(self):
        self.server_ans.config(text="Enter Your Desired")
        if self.text_box.grid_info():
            self.text_box.grid_remove()
            self.server_ans.place(x=20, y=200)
            self.Song = self.text_box.get(1.0, END)
            self.text_box.delete(1.0, END)
            self.Song = self.Song.replace("\n", "").replace("\r", "")
        else:
            self.text_box.grid(row=0, column=1, padx=10, pady=20)
            self.server_ans.place_forget()

    def get_songs(self):
        return self.song_box.get(0, END)

    def add_song(self, song):
        self.song_box.insert(END, song)

    def ser_ans(self, ans):
        self.server_ans.config(text=ans)
        self.server_ans.place_forget()
        self.server_ans.place(x=20, y=200)

    # Changing the status of the button according to the press
    def change_random_button(self):
        if self.Random:
            not_random_pic = PhotoImage(file=r'Pics For The App\not random 50.png')
            self.random_button.photo = not_random_pic
            self.random_button.config(image=not_random_pic)
            self.random_button.grid(row=0, column=4, padx=10)
        else:
            random_pic = PhotoImage(file=r'Pics For The App\random 50.png')
            self.random_button.photo = random_pic
            self.random_button.config(image=random_pic)
            self.random_button.grid(row=0, column=4, padx=10)

    # Activate and deactivate the Random button
    def random(self):
        self.change_random_button()
        self.Random = not self.Random

    # Reset the pause button
    def clear_pause_button(self):
        unpause_pic = PhotoImage(file=r'Pics For The App\unpause button 50.png')
        self.pause_button.photo = unpause_pic
        self.pause_button.config(image=unpause_pic)
        self.pause_button.grid(row=0, column=2, padx=10)
        self.Paused = False

    # Changing the pause button
    def change_pause_button(self):
        if self.Paused:
            unpause_pic = PhotoImage(file=r'Pics For The App\unpause button 50.png')
            self.pause_button.photo = unpause_pic
            self.pause_button.config(image=unpause_pic)
            self.pause_button.grid(row=0, column=2, padx=10)
        else:
            pause_pic = PhotoImage(file=r'Pics For The App\pause button 50.png')
            self.pause_button.photo = pause_pic
            self.pause_button.config(image=pause_pic)
            self.pause_button.grid(row=0, column=2, padx=10)

    # pause and unpause the current song
    def pause(self):
        if self.Paused:
            pygame.mixer.music.unpause()
        else:
            pygame.mixer.music.pause()
        self.change_pause_button()
        self.Paused = not self.Paused

    # Play the previous song
    def previous_song(self):
        if self.song_box.size() != 0:
            cur_song = self.Song_Num
            if self.Random:
                while True:
                    self.Song_Num = random.randint(0, self.song_box.size() - 1)
                    try:
                        if self.Song_Num != self.song_box.curselection()[0]:
                            break
                    except IndexError:
                        if self.Song_Num != cur_song:
                            break
                # Grab song title from playlist
                song = self.song_box.get(self.Song_Num)
            else:
                # Get the current song tuple number
                try:
                    self.Song_Num = self.song_box.curselection()[0]
                except IndexError:
                    pass
                self.Song_Num -= 1
                if self.Song_Num == -1:
                    self.Song_Num = self.song_box.size() - 1
                song = self.song_box.get(self.Song_Num)
            self.clear_pause_button()
            song = f"{song}.mp3"
            pygame.mixer.music.load(song)
            pygame.mixer.music.play(loops=0)

            # Clear active bar in playlist listbox
            self.song_box.selection_clear(0, END)
            # Activate new bar
            self.song_box.activate(self.Song_Num)
            # Set Active bar to the current song
            self.song_box.selection_set(self.Song_Num, last=None)

    # Play the next song in the playlist
    def next_song(self):
        if self.song_box.size() != 0:
            cur_song = self.Song_Num
            if self.Random:
                while True:
                    self.Song_Num = random.randint(0, self.song_box.size() - 1)
                    try:
                        if self.Song_Num != self.song_box.curselection()[0]:
                            break
                    except IndexError:
                        if self.Song_Num != cur_song:
                            break
                # Grab song title from playlist
                song = self.song_box.get(self.Song_Num)
            else:
                # Get the current song tuple number
                try:
                    self.Song_Num = self.song_box.curselection()[0]
                except IndexError:
                    pass
                self.Song_Num += 1
                if self.Song_Num == self.song_box.size():
                    self.Song_Num = 0
                song = self.song_box.get(self.Song_Num)
            self.clear_pause_button()
            song = f"{song}.mp3"
            pygame.mixer.music.load(song)
            pygame.mixer.music.play(loops=0)

            # Clear active bar in playlist listbox
            self.song_box.selection_clear(0, END)
            # Activate new bar
            self.song_box.activate(self.Song_Num)
            # Set Active bar to the current song
            self.song_box.selection_set(self.Song_Num, last=None)

    # Get the name that he want's in his party
    def get_participant_name(self):
        if not self.participant_pop_frame.place_info():
            self.participant_pop_frame.place(x=550, y=320)

    def get_username(self):
        self.wanted_username = self.participant_text.get(1.0, END)
        self.participant_text.delete(1.0, END)
        self.participant_pop_frame.place_forget()

    def get_names(self):
        return self.participant_box.get(0, END)

    def add_name(self, name):
        self.participant_box.insert(END, name)

    def party_decline(self):
        self.party_req_frame.place_forget()

    def party_accept(self):
        self.In_Party = True
        self.party_req_frame.place_forget()

    def party_req(self, src_name):
        self.party_req_frame.place(x=550, y=320)
        self.invite_text.config(text=f"YOUR Presence Has Been Requested\n     By:  '({src_name})'")

    def remove_participant_click(self):
        if not self.In_Party:
            if self.participant_box.curselection():
                if self.participant_box.curselection()[0] != 0:
                    self.Kick_name = self.participant_box.get(self.participant_box.curselection()[0])

    def remove_participant(self, name):
        for i in range(1, self.participant_box.size()):
            if self.participant_box.get(i) == name:
                self.participant_box.delete(i)
                break
