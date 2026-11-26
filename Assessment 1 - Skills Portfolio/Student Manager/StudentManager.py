import ctypes
import os
from pathlib import Path
import tkinter as tk
from PIL import ImageTk, Image
from tkinter import ttk, messagebox, simpledialog

BASEDIR = os.path.dirname(os.path.abspath(__file__))
FILEPATH = os.path.join(BASEDIR, "studentMarks.txt")
ICONPATH = os.path.join(BASEDIR, "hap.ico")
GIFPATH = os.path.join(BASEDIR, "bgg.gif")

ttfpath = Path(BASEDIR) / "Emirates-Bold.ttf"
if ttfpath.exists():
    try:
        ctypes.windll.gdi32.AddFontResourceExW(str(ttfpath), 0x10, 0)
    except Exception: #0x10 tells windows gdi to register the font privately for this available
        pass #if font unavailable, this prevents a crash of the gui and falls back to system font

FONTFAMILY = "Emirates"

DEFAULTMARKSDATA = ( #exists to replace studentmarks.txt if it goes missing
    "10\n"
    "1345,John Curry,8,15,7,45\n"
    "2345,Sam Sturtivant,14,15,14,77\n"
    "9876,Lee Scott,17,11,16,99\n"
    "3724,Matt Thompson,19,11,15,81\n"
    "1212,Ron Herrema,14,17,18,66\n"
    "8439,Jake Hobbs,10,11,10,43\n"
    "2344,Jo Hyde,6,15,10,55\n"
    "9384,Gareth Southgate,5,6,8,33\n"
    "8327,Alan Shearer,20,20,20,100\n"
    "2983,Les Ferdinand,15,17,18,92\n"
)


class StudentManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hap™")
        self.root.geometry("980x620")
        self.root.configure(bg="#FAF7F2")

        if os.path.exists(ICONPATH):
            try:
                self.root.iconbitmap(ICONPATH)
            except tk.TclError:
                pass

        self.students = []
        self.ensuredatafile() #checks if the studentmarks.txt file exists, if not it takes data from the defaultmarksdata dictionary
        self.loadsdata()

        self.gifframes = [] #initializes gif animation
        self.gifphoto = None #keeps a python reference to the currently displayed photoimage
        self.gifindex = 0 #current frame index
        self.gifjob = None #stores the id stored by selfrootafter so stopgifanimation can cancel it later

        self.setupstyles()
        self.showstartscreen()

    def stopgifanimation(self): #cancels pending scheduled animation frames when reentering showstartscreen or transitioning to openmainapp
        if self.gifjob is not None:
            try:
                self.root.after_cancel(self.gifjob) #resets selfgifjob to none to prevent stale cancellations or overlapping roots
            except Exception:
                pass
            self.gifjob = None

    def loadgifframes(self, width, height): #clears any previously loaded frames first so memory doesnt pile up on resizing
        self.gifframes.clear()
        if not os.path.exists(GIFPATH):
            return False
        try:
            with Image.open(GIFPATH) as gif: #opens the gif
                framecount = getattr(gif, "n_frames", 1) #finds total frames
                for idx in range(framecount):
                    gif.seek(idx) #seeks to each frame
                    resized = gif.convert("RGBA").resize( #converts to rgba
                        (max(width, 1), max(height, 1)), #resizes to match the canvas' dimensions
                        Image.Resampling.LANCZOS,
                    )
                    self.gifframes.append(ImageTk.PhotoImage(resized)) #saves each frame as a tkinter photoimage
            return len(self.gifframes) > 0
        except Exception:
            self.gifframes.clear() #if the file is missing or unreadable, returning false lets the start screen render cleanly on its colored canvas
            return False

    def animatebg(self, canvas, bgimageid, delay=60):
        if not self.gifframes or not canvas.winfo_exists(): #checks if the canvas hasnt been destroyed
            return
        self.gifindex = (self.gifindex + 1) % len(self.gifframes) #wraps smoothly from the last frame back to the initial frame
        self.gifphoto = self.gifframes[self.gifindex]
        canvas.itemconfig(bgimageid, image=self.gifphoto) #updates the existing canvas image rather than creating new ones for every frame 
        self.gifjob = self.root.after(delay, lambda: self.animatebg(canvas, bgimageid, delay)) #schedules next frame after delay of 60 milliseconds

    def showstartscreen(self): #destroys previous widgets in selfroot
        self.stopgifanimation()
        for widget in self.root.winfo_children(): 
            widget.destroy()

        self.root.update_idletasks()
        winw = self.root.winfo_width() if self.root.winfo_width() > 1 else 980 
        winh = self.root.winfo_height() if self.root.winfo_height() > 1 else 620

        startcanvas = tk.Canvas(
            self.root,
            width=winw,
            height=winh,
            bg="#FAF7F2",
            highlightthickness=0,
        )
        startcanvas.pack(fill=tk.BOTH, expand=True)

        hasgif = self.loadgifframes(winw, winh)
        bgimageid = None
        if hasgif:
            self.gifindex = 0
            self.gifphoto = self.gifframes[0]
            bgimageid = startcanvas.create_image(0, 0, anchor="nw", image=self.gifphoto)
            self.animatebg(startcanvas, bgimageid)

        def onresize(event):
            if event.widget is startcanvas and (event.width > 1 and event.height > 1):
                if self.loadgifframes(event.width, event.height) and bgimageid is not None:
                    self.gifindex = 0 #checks width and height, loads gif frames, places centered overlaycard, connects enter button to openmainapp
                    self.gifphoto = self.gifframes[0]
                    startcanvas.itemconfig(bgimageid, image=self.gifphoto)

        startcanvas.bind("<Configure>", onresize)

        overlaycard = tk.Frame(
            startcanvas,
            bg="#FFFDF9",
            padx=36,
            pady=30,
            highlightbackground="#E3DAC9",
            highlightthickness=1,
        )
        startcanvas.create_window(winw // 2, winh // 2, window=overlaycard, anchor="center")

        tk.Label(
            overlaycard,
            text="Hap™",
            font=(FONTFAMILY, 28, "bold"),
            fg="#D71A21",
            bg="#FFFDF9",
        ).pack()

        tk.Label(
            overlaycard,
            text="Student Manager",
            font=(FONTFAMILY, 14),
            fg="#1F1B24",
            bg="#FFFDF9",
        ).pack(pady=(2, 10))

        tk.Label(
            overlaycard,
            text="Analyze Better.",
            font=(FONTFAMILY, 10, "bold"),
            fg="#D71A21",
            bg="#FFFDF9",
        ).pack(pady=(0, 20))

        enterbtn = tk.Button(
            overlaycard,
            text="Enter",
            command=self.openmainapp,
            font=(FONTFAMILY, 11, "bold"),
            bg="#D71A21",
            fg="#FFFDF9",
            activebackground="#D2343A",
            activeforeground="#FFFDF9",
            bd=0,
            padx=24,
            pady=10,
            cursor="hand2",
        )
        enterbtn.pack()
        enterbtn.bind("<Enter>", lambda e: enterbtn.configure(bg="#D2343A"))
        enterbtn.bind("<Leave>", lambda e: enterbtn.configure(bg="#D71A21"))

    def openmainapp(self): #when main app opens stop the gif at the homepage and destroy all widgets in the homepage
        self.stopgifanimation()
        for widget in self.root.winfo_children():
            widget.destroy()
        self.setupui()
        self.viewallrecords()

    def ensuredatafile(self): #creates studentMarks.txt in the same folder using the dataset in case it is missing
        if not os.path.exists(FILEPATH):
            with open(FILEPATH, "w", encoding="utf-8") as f:
                f.write(DEFAULTMARKSDATA)

    def loadsdata(self): #loads student records from studentMarks.txt
        self.students.clear() #resets the list before loading so reloading doesnt duplicate entries
        try:
            with open(FILEPATH, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f if line.strip()] #strips whitespaces and new lines and filters out blank lines

            if not lines: #prevents indexerror if the file is completely empty
                return

            for line in lines[1:]: #skips the first line which is the student count header
                parts = [p.strip() for p in line.split(",")] #splits the data at the commas
                if len(parts) == 6: #reflects the actual number of valid records
                    code = int(parts[0])
                    name = parts[1]
                    c1, c2, c3 = int(parts[2]), int(parts[3]), int(parts[4])
                    exam = int(parts[5])
                    self.students.append(self.buildstudentdict(code, name, c1, c2, c3, exam)) #if file reading fails fall back to dictionary
        except Exception as e:
            messagebox.showerror("File Error", f"Could not load studentMarks.txt:\n{e}") #catches error and displays error message

    def savedata(self): #saves updated count and student records back to studentMarks.txt
        try:
            with open(FILEPATH, "w", encoding="utf-8") as f:
                f.write(f"{len(self.students)}\n")
                for s in self.students:
                    f.write(f"{s['code']},{s['name']},{s['c1']},{s['c2']},{s['c3']},{s['exam']}\n")
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save studentMarks.txt:\n{e}")

    @staticmethod #because it foes not need self or class state, it is a pure calculation and dictionary builder
    def buildstudentdict(code, name, c1, c2, c3, exam): #calculates coursework total (/60), overall score (/160), percentage, and grade
        cwtotal = c1 + c2 + c3
        overallscore = cwtotal + exam
        percentage = (overallscore / 160.0) * 100.0

        if percentage >= 70:
            grade = "A"
        elif percentage >= 60:
            grade = "B"
        elif percentage >= 50:
            grade = "C"
        elif percentage >= 40:
            grade = "D"
        else:
            grade = "F"

        return {
            "code": code,
            "name": name,
            "c1": c1,
            "c2": c2,
            "c3": c3,
            "cwtotal": cwtotal,
            "exam": exam,
            "overallscore": overallscore,
            "percentage": percentage,
            "grade": grade,
        }

    def setupstyles(self):
        style = ttk.Style(self.root)
        style.theme_use("clam")

        style.configure(
            "Hap.Treeview",
            background="#FFFDF9",
            foreground="#1F1B24",
            fieldbackground="#FFFDF9",
            bordercolor="#E3DAC9",
            rowheight=28,
            font=(FONTFAMILY, 10),
        )

        style.configure(
            "Hap.Treeview.Heading",
            background="#D71A21",
            foreground="#FFFDF9",
            relief="flat",
            font=(FONTFAMILY, 10, "bold"),
        )

        style.map(
            "Hap.Treeview",
            background=[("selected", "#D71A21")],
            foreground=[("selected", "#FFFDF9")],
        )

        style.map(
            "Hap.Treeview.Heading",
            background=[("active", "#D71A21")],
        )

    def setupui(self):
        header = tk.Frame(self.root, bg="#F3EDE2", padx=18, pady=12)
        header.pack(fill=tk.X)

        setlbl = tk.Label(
            header,
            text="Hap™ | Student Manager",
            font=(FONTFAMILY, 15, "bold"),
            fg="#D71A21",
            bg="#F3EDE2",
        )
        setlbl.pack(side=tk.LEFT)

        setlbl1 = tk.Label(
            header,
            text="Student Marks (Out of 160)",
            font=(FONTFAMILY, 10),
            fg="#D71A21",
            bg="#F3EDE2",
        )
        setlbl1.pack(side=tk.RIGHT)

        body = tk.Frame(self.root, bg="#FAF7F2", padx=15, pady=15)
        body.pack(fill=tk.BOTH, expand=True)

        menuframe = tk.LabelFrame(
            body,
            text=" Menu ",
            font=(FONTFAMILY, 10, "bold"),
            fg="#D71A21",
            bg="#F3EDE2",
            padx=10,
            pady=10,
        )
        menuframe.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))

        menuitems = [
            ("View All Student Records", self.viewallrecords),
            ("View Individual Student Record", self.viewindividualrecord),
            ("Show Highest Total Score", self.showhighestscore),
            ("Show Lowest Total Score", self.showlowestscore),
            ("Sort Student Records", self.sortrecordsdialog),
            ("Add a Student Record", self.addstudentdialog),
            ("Delete a Student Record", self.deletestudentdialog),
            ("Update a Student's Record", self.updatestudentdialog),
            ("Exit", self.showstartscreen),
        ]

        for label, action in menuitems:
            btn = tk.Button(
                menuframe,
                text=label,
                command=action,
                width=28,
                anchor="w",
                font=(FONTFAMILY, 10),
                bg="#FFFDF9",
                fg="#1F1B24",
                activebackground="#D71A21",
                activeforeground="#FFFDF9",
                bd=0,
                padx=10,
                pady=7,
                cursor="hand2",
            )
            btn.pack(pady=4)
            btn.bind("<Enter>", lambda e, b=btn: b.configure(bg="#D71A21", fg="#FFFDF9"))
            btn.bind("<Leave>", lambda e, b=btn: b.configure(bg="#FFFDF9", fg="#1F1B24"))

        rightpanel = tk.Frame(body, bg="#FAF7F2")
        rightpanel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.sectiontitle = tk.StringVar(value="View All Student Records")
        sst = tk.Label(
            rightpanel,
            textvariable=self.sectiontitle,
            font=(FONTFAMILY, 12, "bold"),
            fg="#1F1B24",
            bg="#FAF7F2",
            anchor="w",
        )
        sst.pack(fill=tk.X, pady=(0, 8))

        columns = ("name", "code", "cw", "exam", "pct", "grade")
        self.tree = ttk.Treeview(
            rightpanel,
            columns=columns,
            show="headings",
            style="Hap.Treeview",
            height=15,
        )

        self.tree.heading("name", text="Student Name")
        self.tree.heading("code", text="Student Number")
        self.tree.heading("cw", text="Total Coursework (/60)")
        self.tree.heading("exam", text="Exam Mark (/100)")
        self.tree.heading("pct", text="Overall %")
        self.tree.heading("grade", text="Grade")

        self.tree.column("name", width=185, anchor="w")
        self.tree.column("code", width=115, anchor="center")
        self.tree.column("cw", width=145, anchor="center")
        self.tree.column("exam", width=120, anchor="center")
        self.tree.column("pct", width=100, anchor="center")
        self.tree.column("grade", width=70, anchor="center")

        scrollbar = ttk.Scrollbar(rightpanel, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        scrollbar.place(in_=self.tree, relx=1.0, rely=0, relheight=1.0, anchor="ne")

        summarybox = tk.LabelFrame(
            rightpanel,
            text=" Summary ",
            font=(FONTFAMILY, 10, "bold"),
            fg="#D71A21",
            bg="#F3EDE2",
            padx=12,
            pady=10,
        )
        summarybox.pack(fill=tk.X, pady=(12, 0))

        self.summaryvar = tk.StringVar(value="")
        sumlbl = tk.Label(
            summarybox,
            textvariable=self.summaryvar,
            font=(FONTFAMILY, 10),
            fg="#D71A21",
            bg="#F3EDE2",
            anchor="w",
            justify=tk.LEFT,
        )
        sumlbl.pack(fill=tk.X)

    def populatetable(self, records, includeclasssummary=False):
        for item in self.tree.get_children():
            self.tree.delete(item)
#clears existing rows in selftree before inserting records so every view mode reuses the same table widget
        for s in records:
            self.tree.insert(
                "",
                tk.END,
                values=(
                    s["name"],
                    s["code"],
                    f"{s['cwtotal']} / 60",
                    f"{s['exam']} / 100",
                    f"{s['percentage']:.2f}%", #percentage to 2 decimal places
                    s["grade"],
                ),
            )

        if includeclasssummary: #overall summary for all students
            count = len(records)
            avgpct = sum(s["percentage"] for s in records) / count if count else 0.0
            self.summaryvar.set(
                f"Students in Class: {count}    |    Average Percentage Mark: {avgpct:.2f}%"
            )
        elif len(records) == 1: #summary for individual student record
            s = records[0]
            self.summaryvar.set(
                f"{s['name']} (#{s['code']}) - "
                f"Coursework Breakdown: {s['c1']}/20, {s['c2']}/20, {s['c3']}/20  |  "
                f"Total Score: {s['overallscore']}/160 ({s['percentage']:.2f}%)"
            )
        else: #when no student is selected
            self.summaryvar.set("No matching student records.")

    def findstudent(self, query):
        q = query.strip() #strips whietrspace
        if not q:
            return None

        for s in self.students:
            if str(s["code"]) == q or s["name"].lower() == q.lower(): #case insensitive full name
                return s

        partial = [s for s in self.students if q.lower() in s["name"].lower()]
        return partial[0] if len(partial) == 1 else None

    def viewallrecords(self):
        self.sectiontitle.set("All Student Records")
        self.populatetable(self.students, includeclasssummary=True)

    def viewindividualrecord(self):
        if not self.students:
            messagebox.showinfo("No Data", "There are no student records.")
            return

        query = simpledialog.askstring(
            "Individual Record",
            "Enter Student Name or Student Number (1000-9999):",
            parent=self.root,
        )
        if query is None: #if cancel is selected or prompt is closed exit the method
            return

        student = self.findstudent(query)
        if student:
            self.sectiontitle.set(f"Record for {student['name']}")
            self.populatetable([student], includeclasssummary=False)
        else:
            messagebox.showwarning("Not Found", f"No unique student found for '{query}'.")

    def showhighestscore(self):
        if not self.students:
            messagebox.showinfo("No Data", "There are no student records.")
            return

        topstudent = max(self.students, key=lambda s: s["overallscore"])
        self.sectiontitle.set("Highest Total Score")
        self.populatetable([topstudent], includeclasssummary=False)

    def showlowestscore(self):
        if not self.students:
            messagebox.showinfo("No Data", "There are no student records.")
            return

        lowstudent = min(self.students, key=lambda s: s["overallscore"])
        self.sectiontitle.set("Lowest Total Score")
        self.populatetable([lowstudent], includeclasssummary=False)

    def sortrecordsdialog(self):
        if not self.students:
            messagebox.showinfo("No Data", "There are no student records.")
            return

        win = tk.Toplevel(self.root)
        win.title("Sort Student Records")
        win.geometry("320x210")
        win.configure(bg="#FAF7F2")
        win.resizable(False, False)
        win.grab_set() #blocks interaction with main window until this dialog is closed

        tk.Label(
            win,
            text="Sort Field:",
            bg="#FAF7F2",
            fg="#1F1B24",
            font=(FONTFAMILY, 10, "bold"),
        ).pack(pady=(14, 4))
        fieldvar = tk.StringVar(value="percentage")
        ttk.Combobox(
            win,
            textvariable=fieldvar,
            values=["percentage", "name", "code"],
            state="readonly",
        ).pack()

        tk.Label(
            win,
            text="Direction:",
            bg="#FAF7F2",
            fg="#1F1B24",
            font=(FONTFAMILY, 10, "bold"),
        ).pack(pady=(12, 4))
        ordervar = tk.StringVar(value="Descending")
        ttk.Combobox(
            win,
            textvariable=ordervar,
            values=["Ascending", "Descending"],
            state="readonly",
        ).pack()

        def applysort():
            reverse = ordervar.get() == "Descending"
            keyname = fieldvar.get()
            sortedrecords = sorted(
                self.students,
                key=lambda s: s[keyname].lower() if isinstance(s[keyname], str) else s[keyname],
                reverse=reverse,
            )
            self.sectiontitle.set(f"Sorted Student Records ({keyname.capitalize()} - {ordervar.get()})")
            self.populatetable(sortedrecords, includeclasssummary=True)
            win.destroy()

        tk.Button(
            win,
            text="Sort Records",
            command=applysort,
            bg="#D71A21",
            fg="#FFFDF9",
            font=(FONTFAMILY, 10),
            bd=0,
            padx=16,
            pady=6,
            cursor="hand2",
        ).pack(pady=18)

    def addstudentdialog(self): #form to add a new studnet
        win = tk.Toplevel(self.root)
        win.title("Add a Student Record")
        win.geometry("350x330")
        win.configure(bg="#FAF7F2")
        win.resizable(False, False)
        win.grab_set()

        prompts = [
            "Student Code (1000-9999):",
            "Student Name:",
            "Coursework 1 (0-20):",
            "Coursework 2 (0-20):",
            "Coursework 3 (0-20):",
            "Exam Mark (0-100):",
        ]
        inputs = {}

        for idx, text in enumerate(prompts):
            tk.Label(
                win,
                text=text,
                bg="#FAF7F2",
                fg="#1F1B24",
                font=(FONTFAMILY, 10),
            ).grid(row=idx, column=0, padx=12, pady=7, sticky="w")
            ent = tk.Entry(
                win,
                width=18,
                bg="#FFFDF9",
                fg="#1F1B24",
                insertbackground="#1F1B24",
                font=(FONTFAMILY, 10),
            )
            ent.grid(row=idx, column=1, padx=12, pady=7)
            inputs[text] = ent

        def submitstudent():
            try:
                code = int(inputs["Student Code (1000-9999):"].get().strip())
                name = inputs["Student Name:"].get().strip()
                c1 = int(inputs["Coursework 1 (0-20):"].get().strip())
                c2 = int(inputs["Coursework 2 (0-20):"].get().strip())
                c3 = int(inputs["Coursework 3 (0-20):"].get().strip())
                exam = int(inputs["Exam Mark (0-100):"].get().strip())

                if not (1000 <= code <= 9999):
                    raise ValueError("Student code must be between 1000 and 9999.")
                if any(s["code"] == code for s in self.students):
                    raise ValueError(f"Student code {code} already exists.")
                if not name or "," in name:
                    raise ValueError("Enter a valid name without commas.")
                if not (0 <= c1 <= 20 and 0 <= c2 <= 20 and 0 <= c3 <= 20):
                    raise ValueError("Coursework marks must be between 0 and 20.")
                if not (0 <= exam <= 100):
                    raise ValueError("Exam mark must be between 0 and 100.")

                self.students.append(self.buildstudentdict(code, name, c1, c2, c3, exam))
                self.savedata()
                self.viewallrecords()
                messagebox.showinfo("Saved", f"Added {name} (#{code}) to studentMarks.txt.")
                win.destroy()
            except ValueError as err:
                messagebox.showerror("Invalid Input", str(err), parent=win)

        tk.Button(
            win,
            text="Save Record",
            command=submitstudent,
            bg="#D71A21",
            fg="#FFFDF9",
            font=(FONTFAMILY, 10),
            bd=0,
            padx=16,
            pady=6,
            cursor="hand2",
        ).grid(row=6, column=0, columnspan=2, pady=14)

    def deletestudentdialog(self):
        if not self.students:
            messagebox.showinfo("No Data", "There are no student records to delete.")
            return

        query = simpledialog.askstring(
            "Delete a Student Record",
            "Enter Student Name or Student Code to delete:",
            parent=self.root,
        )
        if query is None:
            return

        student = self.findstudent(query)
        if not student:
            messagebox.showwarning("Not Found", f"No unique student found for '{query}'.")
            return

        if messagebox.askyesno(
            "Confirm Delete",
            f"Delete record for {student['name']} (#{student['code']})?",
        ):
            self.students.remove(student)
            self.savedata()
            self.viewallrecords()
            messagebox.showinfo("Deleted", f"Removed {student['name']} from studentMarks.txt.")

    def updatestudentdialog(self):
        if not self.students:
            messagebox.showinfo("No Data", "There are no student records to update.")
            return

        query = simpledialog.askstring(
            "Update a Student's Record",
            "Enter Student Name or Student Code to update:",
            parent=self.root,
        )
        if query is None:
            return

        student = self.findstudent(query)
        if not student:
            messagebox.showwarning("Not Found", f"No unique student found for '{query}'.")
            return

        win = tk.Toplevel(self.root)
        win.title(f"Update {student['name']}")
        win.geometry("350x310")
        win.configure(bg="#FAF7F2")
        win.resizable(False, False)
        win.grab_set()

        tk.Label(
            win,
            text=f"Editing #{student['code']}",
            bg="#FAF7F2",
            fg="#D71A21",
            font=(FONTFAMILY, 10, "bold"),
        ).grid(row=0, column=0, columnspan=2, pady=(12, 6))

        fields = [
            ("Student Name:", str(student["name"])),
            ("Coursework 1 (0-20):", str(student["c1"])),
            ("Coursework 2 (0-20):", str(student["c2"])),
            ("Coursework 3 (0-20):", str(student["c3"])),
            ("Exam Mark (0-100):", str(student["exam"])),
        ]
        inputs = {}

        for idx, (label, val) in enumerate(fields, start=1):
            tk.Label(
                win,
                text=label,
                bg="#FAF7F2",
                fg="#1F1B24",
                font=(FONTFAMILY, 10),
            ).grid(row=idx, column=0, padx=12, pady=6, sticky="w")
            ent = tk.Entry(
                win,
                width=18,
                bg="#FFFDF9",
                fg="#1F1B24",
                insertbackground="#1F1B24",
                font=(FONTFAMILY, 10),
            )
            ent.insert(0, val)
            ent.grid(row=idx, column=1, padx=12, pady=6)
            inputs[label] = ent

        def savechanges():
            try:
                name = inputs["Student Name:"].get().strip()
                c1 = int(inputs["Coursework 1 (0-20):"].get().strip())
                c2 = int(inputs["Coursework 2 (0-20):"].get().strip())
                c3 = int(inputs["Coursework 3 (0-20):"].get().strip())
                exam = int(inputs["Exam Mark (0-100):"].get().strip())

                if not name or "," in name:
                    raise ValueError("Enter a valid name without commas.")
                if not (0 <= c1 <= 20 and 0 <= c2 <= 20 and 0 <= c3 <= 20):
                    raise ValueError("Coursework marks must be between 0 and 20.")
                if not (0 <= exam <= 100):
                    raise ValueError("Exam mark must be between 0 and 100.")

                updated = self.buildstudentdict(student["code"], name, c1, c2, c3, exam)
                idx = self.students.index(student)
                self.students[idx] = updated

                self.savedata()
                self.viewallrecords()
                messagebox.showinfo("Updated", f"Updated {name} in studentMarks.txt.")
                win.destroy()
            except ValueError as err:
                messagebox.showerror("Invalid Input", str(err), parent=win)

        tk.Button(
            win,
            text="Update Record",
            command=savechanges,
            bg="#D71A21",
            fg="#FFFDF9",
            font=(FONTFAMILY, 10),
            bd=0,
            padx=16,
            pady=6,
            cursor="hand2",
        ).grid(row=6, column=0, columnspan=2, pady=14)


if __name__ == "__main__": #only runs when executed directly as the main script and not if import by another script
    root = tk.Tk()
    app = StudentManagerApp(root)
    root.mainloop()