from tkinter import *
from tkinter import filedialog
from mutagen.mp3 import MP3
import tkinter.ttk as ttk


class StartScreen:

    def __init__(self, master):
        # Define the screen size and its background
        self.master = master
        self.master.title('SoraniFy')
        self.master.iconbitmap('Pics For The App/icon - 256.ico')
        self.master.geometry("650x450")
        self.bg = PhotoImage(file='Pics For The App/entry screen - 650x450.png')
        background_label = Label(self.master, image=self.bg)
        background_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Make The Main Arguments
        self.Username = ""

        username_frame = Frame(self.master, bg="Grey", pady=5, padx=5)
        username_frame.place(x=130, y=235)

        # Define the button and the text box and griding them to the frame
        self.text = Text(username_frame, width=30, height=1.1, bg="white", fg="Green", font=("Comic Sans MS", 12))
        self.text.bind("<Return>", lambda event: self.username_button())
        self.text["wrap"] = "none"
        self.submit_button = Button(username_frame, text="Enter", bg="#5FBD88", fg="#9B49D1", font=("Comic Sans MS",), activebackground="#53A677", activeforeground="#B957FA", command=lambda: self.username_button())
        self.text.grid(row=0, column=0)
        self.submit_button.grid(row=0, column=1, padx=15)

    # the function sets the global var USERNAME to the text in the tk text widget
    def username_button(self):
        self.Username = self.text.get(1.0, END)
        self.text.delete(1.0, END)

    # Change The Screen To Error Screen

    def change_screen_username(self):
        self.text.destroy()
        self.submit_button.destroy()
        self.bg = PhotoImage(file='Pics For The App/entry screen2 - 650x450.png')
        bg_label = Label(self.master, image=self.bg)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        username_frame = Frame(self.master, bg="Grey", pady=5, padx=5)
        username_frame.place(x=130, y=235)

        # Define the button and the text box and griding them to the frame
        self.text = Text(username_frame, width=30, height=1.1, bg="white", fg="Green", font=("Comic Sans MS", 12))
        self.text.bind("<Return>", lambda event: self.username_button())
        self.text["wrap"] = "none"
        self.submit_button = Button(username_frame, text="Enter", bg="#5FBD88", fg="#9B49D1", font=("Comic Sans MS",), activebackground="#53A677", activeforeground="#B957FA", command=lambda: self.username_button())
        self.text.grid(row=0, column=0)
        self.submit_button.grid(row=0, column=1, padx=15)

    def change_screen_invalid(self):
        self.text.destroy()
        self.submit_button.destroy()
        self.bg = PhotoImage(file='Pics For The App/entry screen3 - 650x450.png')
        bg_label = Label(self.master, image=self.bg)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        username_frame = Frame(self.master, bg="Grey", pady=5, padx=5)
        username_frame.place(x=130, y=235)

        # Define the button and the text box and griding them to the frame
        self.text = Text(username_frame, width=30, height=1.1, bg="white", fg="Green", font=("Comic Sans MS", 12))
        self.text.bind("<Return>", lambda event: self.username_button())
        self.text["wrap"] = "none"
        self.submit_button = Button(username_frame, text="Enter", bg="#5FBD88", fg="#9B49D1", font=("Comic Sans MS",), activebackground="#53A677", activeforeground="#B957FA", command=lambda: self.username_button())
        self.text.grid(row=0, column=0)
        self.submit_button.grid(row=0, column=1, padx=15)


