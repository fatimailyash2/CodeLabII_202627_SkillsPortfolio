import ctypes
import os
from pathlib import Path
import tkinter as tk
from PIL import ImageTk, Image
from tkinter import ttk, messagebox, simpledialog
import pygame


BASEDIR = os.path.dirname(os.path.abspath(__file__))
FILEPATH = os.path.join(BASEDIR, "studentMarks.txt")
ICONPATH = os.path.join(BASEDIR, "hap.ico")
GIFPATH = os.path.join(BASEDIR, "bgg.gif")

ttfpath = Path(BASEDIR) / "MeganCloudyPersonalUseOnly.ttf"
if ttfpath.exists():
    try:
        ctypes.windll.gdi32.AddFontResourceExW(str(ttfpath), 0x10, 0)
    except Exception:
        pass

FONTFAMILY = "Megan Cloudy"


def playsound():
    """Play background music on a loop."""
    pygame.mixer.init()
    pygame.mixer.music.load(str(Path(BASEDIR) / "bgms.mp3"))
    pygame.mixer.music.set_volume(0.09)
    pygame.mixer.music.play(loops=-1)


playsound()

DEFAULTMARKSDATA = (
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
        self.ensuredatafile()
        self.loadsdata()

        self.gifframes = []
        self.gifphoto = None
        self.gifindex = 0
        self.gifjob = None

        self.setupstyles()
        self.showstartscreen()

    def stopgifanimation(self):
        if self.gifjob is not None:
            try:
                self.root.after_cancel(self.gifjob)
            except Exception:
                pass
            self.gifjob = None

    def loadgifframes(self, width, height):
        self.gifframes.clear()
        if not os.path.exists(GIFPATH):
            return False
        try:
            with Image.open(GIFPATH) as gif:
                framecount = getattr(gif, "n_frames", 1)
                for idx in range(framecount):
                    gif.seek(idx)
                    resized = gif.convert("RGBA").resize(
                        (max(width, 1), max(height, 1)),
                        Image.Resampling.LANCZOS,
                    )
                    self.gifframes.append(ImageTk.PhotoImage(resized))
            return len(self.gifframes) > 0
        except Exception:
            self.gifframes.clear()
            return False

    def animatebg(self, canvas, bgimageid, delay=60):
        if not self.gifframes or not canvas.winfo_exists():
            return
        self.gifindex = (self.gifindex + 1) % len(self.gifframes)
        self.gifphoto = self.gifframes[self.gifindex]
        canvas.itemconfig(bgimageid, image=self.gifphoto)
        self.gifjob = self.root.after(delay, lambda: self.animatebg(canvas, bgimageid, delay))

    def showstartscreen(self):
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
                    self.gifindex = 0
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
            fg="#9f6cf3",
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
            text="Analyze marks, grades, rankings, and student records",
            font=(FONTFAMILY, 10),
            fg="#5A5265",
            bg="#FFFDF9",
        ).pack(pady=(0, 20))

        enterbtn = tk.Button(
            overlaycard,
            text="Enter Student Manager",
            command=self.openmainapp,
            font=(FONTFAMILY, 11, "bold"),
            bg="#9f6cf3",
            fg="#FFFDF9",
            activebackground="#8752e3",
            activeforeground="#FFFDF9",
            bd=0,
            padx=24,
            pady=10,
            cursor="hand2",
        )
        enterbtn.pack()
        enterbtn.bind("<Enter>", lambda e: enterbtn.configure(bg="#8752e3"))
        enterbtn.bind("<Leave>", lambda e: enterbtn.configure(bg="#9f6cf3"))

    def openmainapp(self):
        self.stopgifanimation()
        for widget in self.root.winfo_children():
            widget.destroy()
        self.setupui()
        self.viewallrecords()

    def ensuredatafile(self):
        """Creates studentMarks.txt in the same folder using the dataset in case it is missing."""
        if not os.path.exists(FILEPATH):
            with open(FILEPATH, "w", encoding="utf-8") as f:
                f.write(DEFAULTMARKSDATA)

    def loadsdata(self):
        """Loads student records from studentMarks.txt."""
        self.students.clear()
        try:
            with open(FILEPATH, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f if line.strip()]

            if not lines:
                return

            for line in lines[1:]:
                parts = [p.strip() for p in line.split(",")]
                if len(parts) == 6:
                    code = int(parts[0])
                    name = parts[1]
                    c1, c2, c3 = int(parts[2]), int(parts[3]), int(parts[4])
                    exam = int(parts[5])
                    self.students.append(self.buildstudentdict(code, name, c1, c2, c3, exam))
        except Exception as e:
            messagebox.showerror("File Error", f"Could not load studentMarks.txt:\n{e}")

    def savedata(self):
        """Saves updated count and student records back to studentMarks.txt."""
        try:
            with open(FILEPATH, "w", encoding="utf-8") as f:
                f.write(f"{len(self.students)}\n")
                for s in self.students:
                    f.write(f"{s['code']},{s['name']},{s['c1']},{s['c2']},{s['c3']},{s['exam']}\n")
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save studentMarks.txt:\n{e}")

    @staticmethod
    def buildstudentdict(code, name, c1, c2, c3, exam):
        """Calculates coursework total (/60), overall score (/160), percentage, and grade."""
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
            background="#9f6cf3",
            foreground="#FFFDF9",
            relief="flat",
            font=(FONTFAMILY, 10, "bold"),
        )

        style.map(
            "Hap.Treeview",
            background=[("selected", "#9f6cf3")],
            foreground=[("selected", "#FFFDF9")],
        )

        style.map(
            "Hap.Treeview.Heading",
            background=[("active", "#8752e3")],
        )

    def setupui(self):
        header = tk.Frame(self.root, bg="#F3EDE2", padx=18, pady=12)
        header.pack(fill=tk.X)

        setlbl = tk.Label(
            header,
            text="Hap™ | Student Manager",
            font=(FONTFAMILY, 15, "bold"),
            fg="#9f6cf3",
            bg="#F3EDE2",
        )
        setlbl.pack(side=tk.LEFT)

        setlbl1 = tk.Label(
            header,
            text="studentMarks.txt (Out of 160)",
            font=(FONTFAMILY, 10),
            fg="#5A5265",
            bg="#F3EDE2",
        )
        setlbl1.pack(side=tk.RIGHT)

        body = tk.Frame(self.root, bg="#FAF7F2", padx=15, pady=15)
        body.pack(fill=tk.BOTH, expand=True)

        menuframe = tk.LabelFrame(
            body,
            text=" Menu ",
            font=(FONTFAMILY, 10, "bold"),
            fg="#9f6cf3",
            bg="#F3EDE2",
            padx=10,
            pady=10,
        )
        menuframe.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))

        menuitems = [
            ("1. View All Student Records", self.viewallrecords),
            ("2. View Individual Student Record", self.viewindividualrecord),
            ("3. Show Highest Total Score", self.showhighestscore),
            ("4. Show Lowest Total Score", self.showlowestscore),
            ("5. Sort Student Records", self.sortrecordsdialog),
            ("6. Add a Student Record", self.addstudentdialog),
            ("7. Delete a Student Record", self.deletestudentdialog),
            ("8. Update a Student's Record", self.updatestudentdialog),
            ("Home Screen", self.showstartscreen),
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
                activebackground="#9f6cf3",
                activeforeground="#FFFDF9",
                bd=0,
                padx=10,
                pady=7,
                cursor="hand2",
            )
            btn.pack(pady=4)
            btn.bind("<Enter>", lambda e, b=btn: b.configure(bg="#9f6cf3", fg="#FFFDF9"))
            btn.bind("<Leave>", lambda e, b=btn: b.configure(bg="#FFFDF9", fg="#1F1B24"))

        rightpanel = tk.Frame(body, bg="#FAF7F2")
        rightpanel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.sectiontitle = tk.StringVar(value="1. View All Student Records")
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
            fg="#9f6cf3",
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
            fg="#1F1B24",
            bg="#F3EDE2",
            anchor="w",
            justify=tk.LEFT,
        )
        sumlbl.pack(fill=tk.X)

    def populatetable(self, records, includeclasssummary=False):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for s in records:
            self.tree.insert(
                "",
                tk.END,
                values=(
                    s["name"],
                    s["code"],
                    f"{s['cwtotal']} / 60",
                    f"{s['exam']} / 100",
                    f"{s['percentage']:.2f}%",
                    s["grade"],
                ),
            )

        if includeclasssummary:
            count = len(records)
            avgpct = sum(s["percentage"] for s in records) / count if count else 0.0
            self.summaryvar.set(
                f"Students in Class: {count}    |    Average Percentage Mark: {avgpct:.2f}%"
            )
        elif len(records) == 1:
            s = records[0]
            self.summaryvar.set(
                f"{s['name']} (#{s['code']})  —  "
                f"Coursework Breakdown: {s['c1']}/20, {s['c2']}/20, {s['c3']}/20  |  "
                f"Total Score: {s['overallscore']}/160 ({s['percentage']:.2f}%)"
            )
        else:
            self.summaryvar.set("No matching student records.")

    def findstudent(self, query):
        q = query.strip()
        if not q:
            return None

        for s in self.students:
            if str(s["code"]) == q or s["name"].lower() == q.lower():
                return s

        partial = [s for s in self.students if q.lower() in s["name"].lower()]
        return partial[0] if len(partial) == 1 else None

    def viewallrecords(self):
        self.sectiontitle.set("1. View All Student Records")
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
        if query is None:
            return

        student = self.findstudent(query)
        if student:
            self.sectiontitle.set(f"2. Individual Record — {student['name']}")
            self.populatetable([student], includeclasssummary=False)
        else:
            messagebox.showwarning("Not Found", f"No unique student found for '{query}'.")

    def showhighestscore(self):
        if not self.students:
            messagebox.showinfo("No Data", "There are no student records.")
            return

        topstudent = max(self.students, key=lambda s: s["overallscore"])
        self.sectiontitle.set("3. Show Highest Total Score")
        self.populatetable([topstudent], includeclasssummary=False)

    def showlowestscore(self):
        if not self.students:
            messagebox.showinfo("No Data", "There are no student records.")
            return

        lowstudent = min(self.students, key=lambda s: s["overallscore"])
        self.sectiontitle.set("4. Show Lowest Total Score")
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
        win.grab_set()

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
            self.sectiontitle.set(f"5. Sort Student Records ({keyname.capitalize()} - {ordervar.get()})")
            self.populatetable(sortedrecords, includeclasssummary=True)
            win.destroy()

        tk.Button(
            win,
            text="Sort Records",
            command=applysort,
            bg="#9f6cf3",
            fg="#FFFDF9",
            font=(FONTFAMILY, 10),
            bd=0,
            padx=16,
            pady=6,
            cursor="hand2",
        ).pack(pady=18)

    def addstudentdialog(self):
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
            bg="#9f6cf3",
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
            fg="#9f6cf3",
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
            bg="#9f6cf3",
            fg="#FFFDF9",
            font=(FONTFAMILY, 10),
            bd=0,
            padx=16,
            pady=6,
            cursor="hand2",
        ).grid(row=6, column=0, columnspan=2, pady=14)


if __name__ == "__main__":
    root = tk.Tk()
    app = StudentManagerApp(root)
    root.mainloop()