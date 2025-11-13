import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os, csv, tempfile
from julia_models.JuliaExecutor import SimpleJuliaExecutor


class GymBlockchainGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🏋️ Gym Ledger – Attendance & Forecast")
        self.root.geometry("1000x700")
        self.root.configure(bg="#f7f7f7")

        self.julia = SimpleJuliaExecutor()
        self.data_path = os.path.join(os.getcwd(), "data", "attendance.csv")

        self.create_inputs()
        self.create_buttons()
        self.create_output_box()
        self.create_chart_area()

    # ------------------------ GUI BUILD ------------------------
    def create_inputs(self):
        frm = ttk.LabelFrame(self.root, text="Add New Entry", padding=10)
        frm.pack(fill="x", padx=10, pady=10)

        labels = ["Gym Location", "Time (hour)", "Attendance", "Cleanliness (1–10)", "Date (YYYY-MM-DD)"]
        defaults = ["Brickell", "18", "50", "8", str(date.today())]
        self.entries = []

        for i, (label, default) in enumerate(zip(labels, defaults)):
            ttk.Label(frm, text=label + ":").grid(row=0, column=i * 2, padx=5, pady=5, sticky="e")
            var = tk.StringVar(value=default)
            entry = ttk.Entry(frm, textvariable=var, width=15)
            entry.grid(row=0, column=i * 2 + 1, padx=5, pady=5, sticky="w")
            self.entries.append(var)

    def create_buttons(self):
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(fill="x", padx=10, pady=10)

        ttk.Button(btn_frame, text="➕ Add Entry", command=self.add_entry).pack(side="left", padx=10)
        ttk.Button(btn_frame, text="📈 Run Forecast", command=self.run_forecast).pack(side="left", padx=10)
        ttk.Button(btn_frame, text="📊 View Chart", command=self.plot_data).pack(side="left", padx=10)

    def create_output_box(self):
        self.output = tk.Text(self.root, height=12, wrap="word", font=("Consolas", 10))
        self.output.pack(fill="both", expand=False, padx=10, pady=10)

    def create_chart_area(self):
        self.fig, self.ax = plt.subplots(figsize=(7, 4))
        self.fig.subplots_adjust(bottom=0.35)
        self.ax.set_title("Attendance vs. Cleanliness")
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=(0, 10), ipady=80)


    # ------------------------ CORE LOGIC ------------------------
    def add_entry(self):
        os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
        row = [v.get() for v in self.entries]

        with open(self.data_path, "a", newline="") as f:
            writer = csv.writer(f)
            if f.tell() == 0:  # new file
                writer.writerow(["Location", "Time", "Attendance", "Cleanliness", "Date"])
            writer.writerow(row)

        output_text = result.get("output", "").strip()
        if output_text:
            self.output.insert("end", "\n📊 Forecast Results\n" + "="*80 + "\n" + output_text + "\n" + "="*80 + "\n")
        else:
            self.output.insert("end", "\n⚠️ No forecast output returned.\n")
        self.output.see("end")


    def run_forecast(self):
        print("🧩 Running forecast...")
        julia_setup_path = os.path.abspath(os.path.join(os.getcwd(), "julia_models", "Julia.jl"))
        model_path = os.path.abspath(os.path.join(os.getcwd(), "julia_models", "model.jl"))
        print("Julia setup:", julia_setup_path)
        print("Model path:", model_path)
        print("Data path:", self.data_path)
    
        code = f"""
        include(raw"{julia_setup_path}")
        include(raw"{model_path}")
        result = predict_peak_hours(raw"{self.data_path}")
        println(result)
        result
        """

        with tempfile.NamedTemporaryFile(delete=False, suffix=".jl", mode="w") as tf:
            tf.write(code)
            temp_path = tf.name

        result = self.julia.execute_file(temp_path, timeout=120)
        os.unlink(temp_path)

        print("Forecast result:", result)  # 👈 Add this one too
        self.output.insert("end", f"\n— Forecast Results —\n{result.get('output', '')}\n")
        self.output.see("end")


    def plot_data(self):
        if not os.path.exists(self.data_path):
            messagebox.showerror("No Data", "No attendance data found yet.")
            return

    # Load CSV
        times, attendance, cleanliness = [], [], []
        with open(self.data_path, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                times.append(int(row["Time"]))
                attendance.append(float(row["Attendance"]))
                cleanliness.append(float(row["Cleanliness"]))

    # Convert 24h times → readable AM/PM strings
        def format_hour(hour):
            if hour == 0:
                return "12 AM"
            elif hour < 12:
                return f"{hour} AM"
            elif hour == 12:
                return "12 PM"
            else:
                return f"{hour-12} PM"

        formatted_times = [format_hour(t) for t in times]

    # Clear old plot
        self.ax.clear()

    # Draw bars and line
        self.ax.bar(formatted_times, attendance, color="#4e79a7", alpha=0.8, label="Attendance")
        self.ax.plot(formatted_times, cleanliness, color="#f28e2b", linewidth=2, marker="o", label="Cleanliness")

    # Beautify chart
        self.ax.set_xlabel("Time of Day", fontsize=11)
        self.ax.set_ylabel("Value", fontsize=11)
        self.ax.set_title("Attendance vs Cleanliness", fontsize=13, pad=12)
        self.ax.legend()
        self.ax.grid(True, linestyle="--", alpha=0.4)
        self.ax.tick_params(axis="x", rotation=30, labelsize=8)

        self.canvas.draw()


        # Clear old plot
        self.ax.clear()

        # Create bar chart
        self.ax.bar(times, attendance, color="#4e79a7", alpha=0.8, label="Attendance")
        self.ax.plot(times, cleanliness, color="#f28e2b", linewidth=2, marker="o", label="Cleanliness")

        self.ax.set_xlabel("Time (Hour of Day)")
        self.ax.set_ylabel("Value")
        self.ax.set_title(f"Attendance vs Cleanliness — {locations[0] if locations else ''}")
        self.ax.legend()
        self.ax.grid(True, linestyle="--", alpha=0.4)

        self.canvas.draw()

    # ------------------------ EXIT ------------------------
    def on_close(self):
        self.julia.cleanup()
        self.root.destroy()


if __name__ == "__main__":
    GymBlockchainGUI().root.mainloop()
