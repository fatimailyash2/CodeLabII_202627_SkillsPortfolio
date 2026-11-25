import ctypes
from pathlib import Path
import random #generates random jokes
import threading #runs the joke function in a separate thread so it doesn't freeze the GUI
import tkinter as tk
from PIL import Image, ImageSequence, ImageTk
import pygame
import pyttsx3

BASE_DIR = Path(__file__).resolve().parent #finds the folder where the main python file exists, so relative asset paths still work even if the script is run from a different directory
ttf_path = BASE_DIR / "fonts" / "AmazonEmber_Bd.ttf"

ctypes.windll.gdi32.AddFontResourceExW(str(ttf_path), 0x10, 0) #load the bundles font just for this running app on windows

root = tk.Tk()
root.geometry("500x600")
root.configure(bg="#00CAFF") #black #232F3E #FFFFFF other blue #88ced8 other blue #c0f9ec
root.title("Amazon Alexa™")
root.iconbitmap('alexa.ico')

def playsound(): #play background music on a loop
    pygame.mixer.init() #loads music file
    pygame.mixer.music.load(str(BASE_DIR / "bgmusic.mp3"))
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

gif_path = BASE_DIR / "detroit.gif" 
gif_image = Image.open(gif_path) #open image with Pillow

frames = [] #if Python garbage-collects PhotoImage objects, images disappear or fail to render. storing them in a frames list keeps them accessible
for frame in ImageSequence.Iterator(gif_image): #iterates through every frame of the gif
    frame_rgba = frame.convert("RGBA") #converts to RGBA (red green blue alpha) and wraps each frame in ImageTk.PhotoImage which converts Pillow images into a format tkinter labels and buttons can display
    frames.append(ImageTk.PhotoImage(frame_rgba))

current_frame = 0 #initial frame

def telljoke():
    if not jokes:
        jokelabel.config(text="No jokes available.") #guards against an emptry file
        return

    chosenjoke = random.choice(jokes) #picks a random joke
    jokelabel.config(text=chosenjoke)
    speakjokes(chosenjoke) #speaks the joke through text to speech


gif_button = tk.Button( #a button that makes the gif clickable and functional
    root,
    image=frames[0],
    command=telljoke,
    bg="#00CAFF",
    activebackground="#00CAFF",
    bd=0,
    highlightthickness=0,
    cursor="hand2"
)
gif_button.pack(pady=10)

def animategif():
    global current_frame #tkinter's standard tk.PhotoImage does not automatically cycle through multi-frame GIFs on its own. thus, the GIF is split into individual frame images using Pillow
    current_frame = (current_frame + 1) % len(frames) #loops smoothly back to 0 after the last frame
    gif_button.config(image=frames[current_frame])
    root.after(100, animategif) #used to step through the individual frames one by one after 100 milliseconds so the GUI stays responsive 

if len(frames) > 1:
    root.after(100, animategif)

jokesfile = BASE_DIR / "randomJokes.txt"

with open(jokesfile, "r", encoding="utf-8") as file: #
    jokes = [line.strip() for line in file if line.strip()]

def speakjokes(joketext):
    def _run_tts():
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        for voice in voices:
            if "zira" in voice.name.lower() or "female" in voice.name.lower():
                engine.setProperty('voice', voice.id)
                break
        engine.say(joketext)
        engine.runAndWait()
        engine.stop()

    threading.Thread(target=_run_tts, daemon=True).start()

root.mainloop()