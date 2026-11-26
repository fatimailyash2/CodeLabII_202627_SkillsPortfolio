import ctypes
from pathlib import Path
import tkinter as tk
import random
from PIL import ImageTk, Image
import pygame

BASE_DIR = Path(__file__).resolve().parent #gets the exact directory containing the main python script so relative assets work even if the script is launched from a different directory
ttf_path = BASE_DIR / "Graffiti City.otf"

ctypes.windll.gdi32.AddFontResourceExW(str(ttf_path), 0x10, 0)

root = tk.Tk()
root.geometry("500x500")
root.configure(bg="#f2ede1") #green #afd014 orange #fd6d03
root.title("The Hardest Quiz Ever™")
root.iconbitmap('maths.ico')

bgpil = Image.open(BASE_DIR / "bgimg.png") #sets the background image using Pillow
bg = ImageTk.PhotoImage(bgpil)

bglbl = tk.Label(root, image=bg)
bglbl.place(x=0, y=0, relwidth=1, relheight=1) #since theres no way to add an image as a background using Tkinter, a label containing the image inside it is used
bglbl.image = bg #keeps an explicit python reference on the widget so garbage collection doesnt drop the image and leave a blank label

FONTFAMILY = "Graffiti City"

DIFFICULTYLEVELS = {
    "easy": (1,9),
    "moderate":(10,99),
    "advanced":(1000,9999)
}

TOTALQUESTIONS = 10 #storing number bounds in difficulty levels and round length in totalquestions avoids magic numbers scattered across functions and makes tuning difficulty or round length easy 

state = { #instead of separate global variables for every piece of game data, state groups the currenr round's variables into one dictionary
    "difficulty": "easy",
    "questionnum": 0,
    "score": 0,
    "attempt": 1,
    "num1": 0,
    "num2": 0,
    "op":"+",
    "answer": 0,
    "advancing": False
}

def playsound(): #play background music on a loop
    pygame.mixer.init()
    pygame.mixer.music.load(str(BASE_DIR / "bgmsc.mp3"))
    pygame.mixer.music.set_volume(0.2)
    pygame.mixer.music.play(loops=-1)

playsound()

def switchframe(frame):
    frame.tkraise() #lifts that frame to the top of the stacking order in root without destroyiong or recreating widgets

FRAME_W = 430
FRAME_H = 410

def placecentered(frame): #positions every framer at the center of root
    frame.place(relx=0.5, rely=0.5, anchor="center", width=FRAME_W, height=FRAME_H)

def randomint(difficulty):
    low, high = DIFFICULTYLEVELS[difficulty] #unpacks "(low, high)" from DIFFICULTYLEVELS and returns a random integer inclusive of both ends via "random.randint(low,high)"
    return random.randint(low, high)

def decideoperation(): #chooses an operator
    operations = ["+", "-"]
    return random.choice(operations)

def getrank(score):
    if score >= 90:
        return "Genius"
    elif score >= 70:
        return "Smart"
    elif score >= 50:
        return "Average"
    else:
        return "Idiot"

def displaymenu():
    state["advancing"] = False
    switchframe(menuframe)

def startquiz(level): #resets questionnum and score to 0, sets difficulty=level, and advancing=false, raises gameplayframe, and calls nextquestion()
    state["difficulty"] = level
    state["questionnum"] = 0
    state["score"] = 0
    state["advancing"] = False
    switchframe(gameplayframe)
    nextquestion()

def nextquestion():
    state["advancing"] = False
    state["questionnum"] += 1

    if state["questionnum"] > TOTALQUESTIONS: 
        displayresults(state["score"])
        return

    state["attempt"] = 1
    state["num1"] = randomint(state["difficulty"])
    state["num2"] = randomint(state["difficulty"])
    state["op"] = decideoperation()
    state["answer"] = (
        state["num1"] + state["num2"]
        if state["op"] == "+"
        else state["num1"] - state["num2"]
        if state["op"] == "-"
        else 0
    )
    displayproblem()

def displayproblem():
    lblqcount.config(text=f"Question {state['questionnum']} / {TOTALQUESTIONS}")
    lblscore.config(text=f"Score: {state['score']}")
    lblproblem.config(text=f"{state['num1']} {state['op']} {state['num2']} = ")
    lblfeedback.config(text="Attempt 1 of 2 (+10 points)", fg="#222222")
    entryanswer.config(state="normal")
    entryanswer.delete(0, tk.END)
    entryanswer.focus_set()

def iscorrect(userans, correctans, attempt):
    if userans == correctans:
        points = 10 if attempt == 1 else 5
        state["score"] += points
        lblscore.config(text=f"Score: {state['score']}")
        lblfeedback.config(text=f"Correct! (+{points} points)", fg="#afd014")
        state["advancing"] = True
        entryanswer.config(state="disabled")
        root.after(800, nextquestion)
        return True

    if attempt == 1:
        state["attempt"] = 2
        lblfeedback.config(text="Incorrect! Try again. (+5 points)", fg="#fd6d03")
        entryanswer.delete(0, tk.END)
    else:
        lblfeedback.config(text=f"Incorrect! The correct answer was {correctans}.", fg="#fd6d03")
        state["advancing"] = True
        entryanswer.config(state="disabled")
        root.after(1100, nextquestion)

    return False

def submitans(event=None): #event=none allows the same function to be triggered both by clicking the check button and by pressing enter
    if state["advancing"]: #blocks extra submissions while waiting to move to the next question
        return

    raw = entryanswer.get().strip() #reads the entry box and removes leading or trailing spaces
    try:
        userans = int(raw) #converts it to an integer, if the input is empty or non number, valueerror is caught
    except ValueError:
        lblfeedback.config(text="Please enter a valid integer.", fg="#fd6d03")
        entryanswer.focus_set()
        return

    iscorrect(userans, state["answer"], state["attempt"])

def displayresults(score):
    rank = getrank(score)
    lblresult.config(text=f"Your Score: {score} / {TOTALQUESTIONS * 10}")
    lblrank.config(text=f"Rank: {rank}")
    lblreplayprompt.config(text="Wanna play again?")
    switchframe(resultsframe)

menuframe = tk.Frame(root, bg="#f2ede1")

lbl1 = tk.Label(
    menuframe,
    text="The Hardest Quiz Ever",
    font=(FONTFAMILY, 40),
    bg="#f2ede1",
    fg="#afd014",
    wraplength=390,
)
lbl1.pack(pady=(16, 10))

btn1 = tk.Button(
    menuframe,
    text="Start Quiz",
    font=(FONTFAMILY, 25),
    bg="#afd014",
    fg="#f2ede1",
    width=14,
    command=lambda: switchframe(quizframe),
)
btn1.pack(pady=7)

btn2 = tk.Button(
    menuframe,
    text="Instructions",
    font=(FONTFAMILY, 25),
    bg="#afd014",
    fg="#f2ede1",
    width=14,
    command=lambda: switchframe(instructionsframe),
)
btn2.pack(pady=7)

btn3 = tk.Button(
    menuframe,
    text="Credits",
    font=(FONTFAMILY, 25),
    bg="#afd014",
    fg="#f2ede1",
    width=14,
    command=lambda: switchframe(creditsframe)
)
btn3.pack(pady=7)

lblfooter = tk.Label(
    menuframe,
    text="2026 Fatima Ilyas",
    font=(FONTFAMILY, 14),
    bg="#f2ede1",
    fg="#fd6d03",
)
lblfooter.pack(side="bottom", pady=8)

quizframe = tk.Frame(root, bg="#f2ede1")

lbl2 = tk.Label(
    quizframe,
    text="Select Difficulty",
    font=(FONTFAMILY, 40),
    bg="#f2ede1",
    fg="#afd014",
)
lbl2.pack(pady=(20, 15))

for label, level in [("Easy", "easy"), ("Moderate", "moderate"), ("Advanced", "advanced")]:
    btn4 = tk.Button(
        quizframe,
        text=label,
        font=(FONTFAMILY, 20),
        bg="#afd014",
        fg="#f2ede1",
        width=14,
        command=lambda lvl=level: startquiz(lvl)
    )
    btn4.pack(pady=6)

btn5 = tk.Button(
    quizframe,
    text="Back to Menu",
    font=(FONTFAMILY, 16),
    bg="#fd6d03",
    fg="#f2ede1",
    width=14,
    command=lambda: switchframe(menuframe)
)
btn5.pack(pady=15)

gameplayframe = tk.Frame(root, bg="#fd6d03")

topbar = tk.Frame(gameplayframe, bg="#afd014")
topbar.pack(fill="x", padx=20, pady=(16,6))

lblqcount = tk.Label(
    topbar,
    text="Question 1 / 10",
    font=(FONTFAMILY, 16),
    bg="#fd6d03",
    fg="#f2ede1"
)
lblqcount.pack(side="left")

lblscore = tk.Label(
    topbar,
    text="Score 0",
    font=(FONTFAMILY, 16),
    bg="#fd6d03",
    fg="#afd014"
)
lblscore.pack(side="right")

lblproblem = tk.Label(
    gameplayframe,
    text="0 + 0 =",
    font=(FONTFAMILY, 22),
    bg="#ffffff",
    fg="#222222"
)
lblproblem.pack(pady=(14, 10))

entryanswer = tk.Entry(
    gameplayframe,
    font=(FONTFAMILY, 22),
    bg="#ffffff",
    fg="#222222",
    justify="center",
    width=12
)
entryanswer.pack(pady=6)
entryanswer.bind("<Return>", submitans)

btnsubmit = tk.Button(
    gameplayframe,
    text="Check",
    font=(FONTFAMILY, 20),
    bg="#afd014",
    fg="#f2ede1",
    width=12,
    command=submitans
)
btnsubmit.pack(pady=10)

lblfeedback = tk.Label(
    gameplayframe,
    text="",
    font=(FONTFAMILY, 15),
    bg="#f2ede1",
    fg="#fd6d03",
    wraplength=390,
    justify="center"
)
lblfeedback.pack(pady=4)

btnquitround = tk.Button(
    gameplayframe,
    text="Quit to Menu",
    font=(FONTFAMILY, 14),
    bg="#fd6d03",
    fg="#f2ede1",
    width=14,
    command=displaymenu
)
btnquitround.pack(side="bottom", pady=14)

resultsframe = tk.Frame(root, bg="#f2ede1")

lblcomplete = tk.Label(
    resultsframe,
    text="Quiz Complete!",
    font=(FONTFAMILY, 34),
    bg="#f2ede1",
    fg="#afd014"
)
lblcomplete.pack(pady=(22,8))

lblresult = tk.Label(
    resultsframe,
    text="Your Score: 0 / 100",
    font=(FONTFAMILY, 26),
    bg="#f2ede1",
    fg="#fd6d03"
)
lblresult.pack(pady=4)

lblrank = tk.Label(
    resultsframe,
    text="Rank: Idiot",
    font=(FONTFAMILY, 22),
    bg="#f2ede1",
    fg="#222222"
)
lblrank.pack(pady=4)

lblreplayprompt = tk.Label(
    resultsframe,
    text="Wanna Play Again?",
    font=(FONTFAMILY, 18),
    bg="#f2ede1",
    fg="#222222"
)
lblreplayprompt.pack(pady=(10,8))

btnplayagain = tk.Button(
    resultsframe,
    text="Play Again",
    font=(FONTFAMILY, 20),
    bg="#afd014",
    fg="#f2ede1",
    width=14,
    command=lambda: switchframe(quizframe)
)
btnplayagain.pack(pady=5)

btnmainmenu = tk.Button(
    resultsframe,
    text="Main Menu",
    font=(FONTFAMILY, 16),
    bg="#fd6d03",
    fg="#f2ede1",
    width=12,
    command=displaymenu
)
btnmainmenu.pack(pady=5)

instructionsframe = tk.Frame(root, bg="#f2ede1")

lbl3 = tk.Label(
    instructionsframe,
    text="Instructions",
    font=(FONTFAMILY, 28),
    bg="#f2ede1",
    fg="#afd014",
)
lbl3.pack(pady=(20, 10))

lbl4 = tk.Label(
    instructionsframe,
    text=(
        "10 Arithmethic Questions per Round. \n"
        "1st Try Right: +10 points\n"
        "2nd Try Right: +5 points\n"
        "Max Score: 100 points\n"
    ),
    font=(FONTFAMILY, 20),
    bg="#f2ede1",
    fg="#222222",
    justify="center",
)
lbl4.pack(pady=10)

btn6 = tk.Button(
    instructionsframe,
    text="Back to Menu",
    font=(FONTFAMILY, 16),
    bg="#fd6d03",
    fg="#f2ede1",
    command=lambda: switchframe(menuframe)
)
btn6.pack(pady=15)

creditsframe = tk.Frame(root, bg="#f2ede1")

lbl5 = tk.Label(
    creditsframe,
    text="Credits",
    font=(FONTFAMILY, 28),
    bg="#f2ede1",
    fg="#afd014",
)
lbl5.pack(pady=(30, 15))

lbl6 = tk.Label(
    creditsframe,
    text="The Hardest Quiz Ever™\nBuilt with Python and Tkinter\nby Fatima Ilyas",
    font=(FONTFAMILY, 20),
    bg="#f2ede1",
    fg="#222222",
    justify="center",
)
lbl6.pack(pady=10)

btn7 = tk.Button(
    creditsframe,
    text="Back to Menu",
    font=(FONTFAMILY, 16),
    bg="#fd6d03",
    fg="#f2ede1",
    command=lambda: switchframe(menuframe)
)
btn7.pack(pady=20)

placecentered(menuframe)
placecentered(quizframe)
placecentered(instructionsframe)
placecentered(creditsframe)
placecentered(gameplayframe)
placecentered(resultsframe)
switchframe(menuframe)

root.mainloop()