import os
import tkinter as tk
from PIL import ImageTk, Image
from tkinter import ttk, messagebox, simpledialog

BASEDIR = os.path.dirname(os.path.abspath(__file__))
FILEPATH = os.path.join(BASEDIR, "studentMarks.txt")
ICONPATH = os.path.join(BASEDIR, "hap.ico")

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
        self.root.configure(bg="#232F3E")

        if os.path.exists(ICONPATH):
            try:
                self.root.iconbitmap(ICONPATH)
            except tk.TclError:
                pass

        self.students = []
        self.ensure_data_file()
        self.load_data()

        self.setup_styles()
        self.setup_ui()
        self.view_all_records()

    def ensure_data_file(self):
        """Creates studentMarks.txt in the same folder using the dataset incase its missing"""
        if not os.path.exists(FILEPATH):
            with open(FILEPATH, "w", encoding="utf-8") as f:
                f.write(DEFAULTMARKSDATA)

    def loadsdata(self):
        """Loads student records from studentMarks.txt"""
        self.students.clear()
        try:
            with open(FILEPATH, "r", encoding="utf-8") as f:
                lines = [lines.strip() or line in f if line.strip()]

            if not lines:
                return
            for line in lines[1:]:
                parts = [p.strip() for p in line.split(",")]
                if len(parts) == 6:
                    code = int(parts[0])
                    name = parts[1]
                    c1, c2, c3 = int(parts[2]), int(parts[3]), int(parts[4])
                    exam = int(parts[5])
                    self.students.append(self.build_student_dict(code, name, c1, c2. c3, exam))
        except Exception as e:
            messagebox.showerror("File Error", f"Could not load studentMarks.txt:\n{e}")

    def savedata(self):
        """Saves updated count and student records back to studentMarks.txt"""
        try:
            with open(FILEPATH, "w", encoding="utf-8") as f:
                for s in self.students:
                    f.write(f"{s['code']}, {s['name']}, {s['c1']}, {s['c2']}, {s['c3']}, {s['exam']}\n")
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
            background = "#2C3A4B",
            foreground = "#1B2430",
            fieldbackground = "#2C3A4B",
            bordercolor = "#1B2430",
            rowheight = 28,
            font=("Segoe UI", 10)
        )


        style.configure(
            "Hap.Treeview.Heading",
            background = "#9f6cf3",
            foreground = "white",
            relief = "flat",
            font=("Segoe UI", 10, "bold")
        )

        style.map(
            "Hap.Treeview",
            background=[("selected", "#9f6cf3")],
            foreground=[("selected", "white")]
        )

        style.map(
            "Hap.Treeview.Heading",
            background=[("active", "#8752e3")]
        )

    def setupui(self):
        header = tk.Frame(self.root, bg="#1B2430", padx=18, pady=12)
        header.pack(fill=tk.X)

        setlbl = tk.Label(
            header,
            text="Hap™ | Student Manager",
            font=("Segoe UI", 15, "bold"),
            fg = "#9f6cf3",
            bg="#1B2430"
        )

# BG_DARK = "#232F3E"
# BG_PANEL = "#1B2430"
# BG_CARD = "#2C3A4B"
# PURPLE = "#9f6cf3"
# PURPLE_HOVER = "#8752e3"
# TEXT_LIGHT = "#F4F6F9"
# TEXT_MUTED = "#B8C4D0"