import ctypes
from pathlib import Path
import random #generates random jokes
import threading #runs the joke function in a separate thread so it doesn't freeze the GUI
import tkinter as tk
from PIL import Image, ImageSequence, ImageTk
import pygame
import pyttsx3

BASE_DIR = Path(__file__).resolve().parent
ttf_path = BASE_DIR / "fonts" / "AmazonEmber_Bd.ttf"

ctypes.windll.gdi32.AddFontResourceExW(str(ttf_path), 0x10, 0) #load the bundles font just for this running app on windows

def play_sound(): #play background music on a loop
    pygame.mixer.init()
    pygame.mixer.music.load(str(BASE_DIR / "bgmusic.mp3"))
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(loops=-1)

play_sound()

root = tk.Tk()
root.geometry("500x600")
root.configure(bg="#000000") #black #232F3E #FFFFFF other blue #88ced8 other blue #c0f9ec
root.title("Say 'Alexa, Tell Me A Joke!'")
root.iconbitmap('alexa.ico')

#main label
label1 = tk.Label(
    root, 
    text="Say 'Hey Alexa, Tell Me A Joke!'", 
    font=("Amazon Ember", 20), 
    bg="#000000", 
    fg="white"
)
label1.pack(pady=20)

jokelabel = tk.Label(
    root,
    text="Click on Alexa to Hear a Joke!",
    font=("Amazon Ember", 16),
    bg="#000000",
    fg="white",
    wraplength=400
)
jokelabel.pack(pady=15)

gif_path = BASE_DIR / "giphy.gif"
gif_image = Image.open(gif_path)

frames = []
for frame in ImageSequence.Iterator(gif_image):
    frame_rgba = frame.convert("RGBA")
    frames.append(ImageTk.PhotoImage(frame_rgba))

current_frame = 0

def telljoke():
    if not jokes:
        jokelabel.config(text="No jokes available.")
        return

    chosenjoke = random.choice(jokes)
    jokelabel.config(text=chosenjoke)
    speakjokes(chosenjoke)


gif_button = tk.Button(
    root,
    image=frames[0],
    command=telljoke,
    bg="#000000",
    activebackground="#000000",
    bd=0,
    highlightthickness=0,
    cursor="hand2"
)
gif_button.pack(pady=10)

def animategif():
    global current_frame
    current_frame = (current_frame + 1) % len(frames)
    gif_button.config(image=frames[current_frame])
    root.after(100, animategif)

if len(frames) > 1:
    root.after(100, animategif)

jokesfile = BASE_DIR / "randomJokes.txt"

with open(jokesfile, "r", encoding="utf-8") as file:
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