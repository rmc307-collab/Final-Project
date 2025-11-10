import tkinter as tk
from tkinter import ttk, filedialog, messagebox 
import threading
import os
from JuliaExecutor import SimpleJuliaExecutor

class TestGUI:
    """Simple GUI for executing MLJ scripts"""
def __init__(self):
    self.root = tk.Tk()
    self.root.title("My App") 
    self.root.geometry("800x600") 
    self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    self.julia = SimpleJuliaExecutor()
    self.setup_gui()

class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("FinTech Scorer (Julia + Python)")
        self.root.geometry("520x360")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.julia = SimpleJuliaExecutor()  # starts the background Julia process

        frm = ttk.Frame(self.root, padding=14)
        frm.pack(fill="both", expand=True)

        ttk.Label(frm, text="Income ($):").grid(row=0, column=0, sticky="e", pady=6)
        ttk.Label(frm, text="Debt ($):").grid(row=1, column=0, sticky="e", pady=6)

        self.income = tk.StringVar(value="60000")
        self.debt   = tk.StringVar(value="12000")

        ttk.Entry(frm, textvariable=self.income, width=20).grid(row=0, column=1, sticky="w")
        ttk.Entry(frm, textvariable=self.debt,   width=20).grid(row=1, column=1, sticky="w")

        self.run_btn = ttk.Button(frm, text="Calculate Score", command=self.run_score)
        self.run_btn.grid(row=2, column=0, columnspan=2, pady=12, sticky="ew")

        self.out = tk.Text(frm, height=12, wrap="word")
        self.out.grid(row=3, column=0, columnspan=2, sticky="nsew", pady=6)

        frm.columnconfigure(1, weight=1)
        frm.rowconfigure(3, weight=1)

    def run_score(self):
        # validate numbers
        try:
            inc = float(self.income.get().strip())
            deb = float(self.debt.get().strip())
        except ValueError:
            messagebox.showerror("Invalid input", "Please enter numeric values.")
            return

        # make a tiny Julia runner that includes your model and prints the score
        model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "julia_models", "model.jl"))
        code = f"""
            include(raw"{model_path}")
            inc = {inc}
            deb = {deb}
            score = credit_score(inc, deb)
            println("Computed credit score: " * string(score))
            score
        """

        # write temp .jl and execute via executor
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jl", mode="w") as tf:
            tf.write(code)
            temp_path = tf.name

        try:
            result = self.julia.execute_file(temp_path, timeout=60)
        finally:
            try: os.unlink(temp_path)
            except: pass

        self.out.insert("end", "\n— Run —\n")
        if result.get("success"):
            if "output" in result and result["output"]:
                self.out.insert("end", result["output"].strip() + "\n")
            self.out.insert("end", f"Return value: {result.get('result')}\n")
        else:
            self.out.insert("end", f"Error: {result.get('error')}\n")
        self.out.see("end")

    def on_close(self):
        self.julia.cleanup()
        self.root.destroy()

if __name__ == "__main__":
    App().root.mainloop()