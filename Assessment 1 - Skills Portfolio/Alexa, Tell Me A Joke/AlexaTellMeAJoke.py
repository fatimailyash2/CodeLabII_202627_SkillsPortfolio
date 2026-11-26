import ctypes #lets python call windows c/win32 APi functions directly, used here to register custom fonts with windows at runtime
from pathlib import Path #safely builds file paths across operating systems
import random #generates random jokes
import threading #runs the joke function in a separate thread so it doesn't freeze the GUI
import tkinter as tk
from PIL import Image, ImageSequence, ImageTk
import pygame #used for audio playback
import pyttsx3 #used for text to speech

BASEDIR = Path(__file__).resolve().parent #finds the folder where the main python file exists, so relative asset paths still work even if the script is run from a different directory
ttf_path = BASEDIR / "fonts" / "AmazonEmber_Bd.ttf"

ctypes.windll.gdi32.AddFontResourceExW(str(ttf_path), 0x10, 0) #load the bundles font just for this running app on windows

root = tk.Tk()
root.geometry("500x600")
root.configure(bg="#00CAFF") #black #232F3E #FFFFFF other blue #88ced8 other blue #c0f9ec
root.title("Amazon Alexa™")
root.iconbitmap('alexa.ico')

def playsound(): #play background music on a loop
    pygame.mixer.init() #loads music file
    pygame.mixer.music.load(str(BASEDIR / "bgmusic.mp3"))
    pygame.mixer.music.set_volume(0.2)
    pygame.mixer.music.play(loops=-1)

playsound()

#main label
label1 = tk.Label(
    root, 
    text="Alexa™", 
    font=("Amazon Ember", 20), 
    bg="#00CAFF", 
    fg="white"
)
label1.pack(pady=20)

jokelabel = tk.Label(
    root,
    text="Click on Alexa to Hear a Joke!",
    font=("Amazon Ember", 16),
    bg="#00CAFF",
    fg="white",
    wraplength=400
)
jokelabel.pack(pady=15)

gifpath = BASEDIR / "detroit.gif" 
gifimage = Image.open(gifpath) #open image with Pillow

frames = [] #if Python garbage-collects PhotoImage objects, images disappear or fail to render. storing them in a frames list keeps them accessible
for frame in ImageSequence.Iterator(gifimage): #iterates through every frame of the gif
    framergba = frame.convert("RGBA") #converts to RGBA (red green blue alpha) and wraps each frame in ImageTk.PhotoImage which converts Pillow images into a format tkinter labels and buttons can display
    frames.append(ImageTk.PhotoImage(framergba))

currentframe = 0 #initial frame
currentsetup = ""
currentpunchline = ""
punchlineshown = False

def splitjokeonquestion(jokeline: str):
    """Splits joke into (setup, punchline).
    Supports '?' (eg, 'Why did the chicken cross the road?To get to the other side!')"""

    if "?" in jokeline:
        setup, punchline = jokeline.split("?", 1)
        return (setup.strip() + "?"), punchline.strip()
    return jokeline.strip(), ""

def telljoke():
    global currentsetup, currentpunchline, punchlineshown
    if not jokes:
        jokelabel.config(text="No jokes available.") #guards against an emptry file
        punchlinebutton.config(state="disabled", text="What?")
        return

    chosenjoke = random.choice(jokes) #picks a random joke
    setup, punchline = splitjokeonquestion(chosenjoke)

    currentsetup = setup
    currentpunchline = punchline
    punchlineshown = False

    jokelabel.config(text=currentsetup)
    speakjokes(currentsetup) #speaks the joke through text to speech

    if currentpunchline:
        punchlinebutton.config(text="View Punchline!", state="normal")
    else:
        punchlinebutton.config(text="No Punchline :(", state="disabled")

def revealpunchline():
    global punchlineshown
    if not currentpunchline or punchlineshown:
        return

    punchlineshown = True
    jokelabel.config(text=f"{currentsetup}\n\n{currentpunchline}")
    speakjokes(currentpunchline)
    punchlinebutton.config(text="Haha!", state="disabled")

gifbutton = tk.Button( #a button that makes the gif clickable and functional
    root,
    image=frames[0],
    command=telljoke,
    bg="#00CAFF",
    activebackground="#00CAFF",
    bd=0,
    highlightthickness=0,
    cursor="hand2"
)
gifbutton.pack(pady=10)

punchlinebutton = tk.Button(
    root,
    text="What?",
    command=revealpunchline,
    font=("Amazon Ember", 13),
    bg="#232F3E",
    fg="white",
    activebackground="#37475A",
    activeforeground="white",
    disabledforeground="#B8DCE8",
    relief="flat",
    bd=0,
    padx=22,
    pady=10,
    cursor="hand2",
    state="disabled"
)
punchlinebutton.pack(pady=12)

def animategif():
    global currentframe #tkinter's standard tk.PhotoImage does not automatically cycle through multi-frame GIFs on its own. thus, the GIF is split into individual frame images using Pillow
    currentframe = (currentframe + 1) % len(frames) #loops smoothly back to 0 after the last frame
    gifbutton.config(image=frames[currentframe])
    root.after(100, animategif) #used to step through the individual frames one by one after 100 milliseconds so the GUI stays responsive 

if len(frames) > 1:
    root.after(100, animategif)

jokesfile = BASEDIR / "randomJokes.txt"

with open(jokesfile, "r", encoding="utf-8") as file: #reads randomJokes.txt using UTF-8 encoding, strips trailing newslines and whitespace
    jokes = [line.strip() for line in file if line.strip()] #"if linestrip()" ignores blank lines

def speakjokes(joketext):
    def _run_tts():
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        for voice in voices:
            if "zira" in voice.name.lower() or "female" in voice.name.lower(): #loops through installed system voices and looks for either "zira" or "female"
                engine.setProperty('voice', voice.id)
                break
        engine.say(joketext)
        engine.runAndWait() #a blocking call, meaning it waits until the entire joke has been spoken before returning. if ran on the main tkinter thread, the GUI would freeze while Alexa is talking, which is why ->
        engine.stop()

    threading.Thread(target=_run_tts, daemon=True).start() #keeps the UI responsive and "daemon=True" lets Python close cleanly if the window is closed

root.mainloop()