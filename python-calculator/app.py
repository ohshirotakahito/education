import tkinter as tk
from tkinter import ttk

from calculator import calculate, format_number


class CalculatorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Python Calculator")
        self.geometry("390x610")
        self.minsize(350, 540)
        self.configure(bg="#171816")
        self.expression = tk.StringVar()
        self.result = tk.StringVar(value="0")
        self.history = []
        self.scientific_visible = False
        self.angle_mode = "DEG"
        self.orientation = "portrait"
        self._build_ui()
        self.bind_all("<Key>", self._handle_key)

    def _build_ui(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Calc.TButton", font=("Segoe UI", 16), padding=13, background="#292a27", foreground="white", borderwidth=0)
        style.map("Calc.TButton", background=[("active", "#3a3b37")])
        style.configure("Op.TButton", font=("Segoe UI", 17, "bold"), padding=13, background="#e95a3f", foreground="white", borderwidth=0)
        style.map("Op.TButton", background=[("active", "#ff7257")])
        style.configure("Sub.TButton", font=("Segoe UI", 14), padding=13, background="#deddd7", foreground="#171816", borderwidth=0)

        header = tk.Frame(self, bg="#171816")
        header.pack(fill="x", padx=22, pady=(22, 0))
        tk.Label(header, text="PY / CALC", bg="#171816", fg="#e95a3f", font=("Consolas", 11, "bold")).pack(side="left")
        tk.Button(header, text="履歴", command=self._show_history, bg="#171816", fg="#aaa", activebackground="#171816", activeforeground="white", border=0, font=("Segoe UI", 10), cursor="hand2").pack(side="right")
        self.mode_button = tk.Button(header, text="関数電卓", command=self._toggle_scientific, bg="#e95a3f", fg="white", activebackground="#ff7257", activeforeground="white", border=0, padx=12, pady=5, font=("Segoe UI", 10, "bold"), cursor="hand2")
        self.mode_button.pack(side="right", padx=(0, 10))
        self.orientation_button = tk.Button(header, text="横型にする", command=self._toggle_orientation, bg="#292a27", fg="white", activebackground="#3a3b37", activeforeground="white", border=0, padx=12, pady=5, font=("Segoe UI", 10, "bold"), cursor="hand2")
        self.orientation_button.pack(side="right", padx=(0, 10))

        self.workspace = tk.Frame(self, bg="#171816")
        self.workspace.pack(fill="both", expand=True)
        self.display_frame = tk.Frame(self.workspace, bg="#171816", height=130)
        self.display_frame.grid_propagate(False)
        tk.Label(self.display_frame, textvariable=self.expression, anchor="e", bg="#171816", fg="#8f918b", font=("Consolas", 15)).pack(fill="x", padx=22, pady=(28, 4))
        tk.Label(self.display_frame, textvariable=self.result, anchor="e", bg="#171816", fg="white", font=("Segoe UI", 36, "bold"), wraplength=330).pack(fill="x", padx=22)

        self.controls_frame = tk.Frame(self.workspace, bg="#171816")

        self.scientific_frame = tk.Frame(self.controls_frame, bg="#171816")
        scientific_layout = [
            [("sin", "sin("), ("cos", "cos("), ("tan", "tan("), ("√", "sqrt(")],
            [("log", "log("), ("ln", "ln("), ("π", "pi"), ("e", "e")],
            [("x²", "^2"), ("xʸ", "^"), ("(", "("), (")", ")")],
            [("n!", "fact("), ("DEG", "angle"), ("AC", "clear"), ("⌫", "backspace")],
        ]
        for row in range(4):
            self.scientific_frame.rowconfigure(row, weight=1)
        for column in range(4):
            self.scientific_frame.columnconfigure(column, weight=1)
        for row, items in enumerate(scientific_layout):
            for column, (label, action) in enumerate(items):
                button = ttk.Button(self.scientific_frame, text=label, style="Calc.TButton", command=lambda value=action: self._press(value))
                button.grid(row=row, column=column, sticky="nsew", padx=4, pady=3)
                if action == "angle":
                    self.angle_button = button

        self.buttons_frame = tk.Frame(self.controls_frame, bg="#171816")
        self.buttons_frame.pack(fill="both", expand=True, padx=18, pady=(0, 18))
        for row in range(5):
            self.buttons_frame.rowconfigure(row, weight=1)
        for column in range(4):
            self.buttons_frame.columnconfigure(column, weight=1)

        layout = [
            [("C", "clear", "Sub.TButton"), ("⌫", "backspace", "Sub.TButton"), ("%", "%", "Sub.TButton"), ("÷", "÷", "Op.TButton")],
            [("7", "7", "Calc.TButton"), ("8", "8", "Calc.TButton"), ("9", "9", "Calc.TButton"), ("×", "×", "Op.TButton")],
            [("4", "4", "Calc.TButton"), ("5", "5", "Calc.TButton"), ("6", "6", "Calc.TButton"), ("−", "-", "Op.TButton")],
            [("1", "1", "Calc.TButton"), ("2", "2", "Calc.TButton"), ("3", "3", "Calc.TButton"), ("+", "+", "Op.TButton")],
            [("±", "negate", "Calc.TButton"), ("0", "0", "Calc.TButton"), (".", ".", "Calc.TButton"), ("=", "equals", "Op.TButton")],
        ]
        for row, items in enumerate(layout):
            for column, (label, action, style_name) in enumerate(items):
                ttk.Button(self.buttons_frame, text=label, style=style_name, command=lambda value=action: self._press(value)).grid(row=row, column=column, sticky="nsew", padx=4, pady=4)
        self._apply_orientation()

    def _press(self, value):
        if value == "clear":
            self.expression.set("")
            self.result.set("0")
        elif value == "backspace":
            self.expression.set(self.expression.get()[:-1])
        elif value == "equals":
            self._calculate()
        elif value == "negate":
            current = self.expression.get()
            self.expression.set(f"-({current})" if current else "-")
        elif value == "angle":
            self.angle_mode = "RAD" if self.angle_mode == "DEG" else "DEG"
            self.angle_button.configure(text=self.angle_mode)
        else:
            self.expression.set(self.expression.get() + value)

    def _calculate(self):
        expression = self.expression.get()
        try:
            answer = format_number(calculate(expression, self.angle_mode))
            self.result.set(answer)
            self.history.insert(0, (expression, answer))
            self.history = self.history[:20]
        except ValueError as error:
            self.result.set(str(error))

    def _toggle_scientific(self):
        self.scientific_visible = not self.scientific_visible
        if self.scientific_visible:
            self.mode_button.configure(text="通常電卓")
        else:
            self.mode_button.configure(text="関数電卓")
        self._apply_orientation()

    def _toggle_orientation(self):
        self.orientation = "landscape" if self.orientation == "portrait" else "portrait"
        self._apply_orientation()

    def _apply_orientation(self):
        self.display_frame.grid_forget()
        self.controls_frame.grid_forget()
        self.scientific_frame.pack_forget()
        self.buttons_frame.pack_forget()
        for index in range(2):
            self.workspace.rowconfigure(index, weight=0)
            self.workspace.columnconfigure(index, weight=0)
        if self.orientation == "portrait":
            self.geometry("390x820" if self.scientific_visible else "390x610")
            self.minsize(350, 700 if self.scientific_visible else 540)
            self.workspace.columnconfigure(0, weight=1)
            self.workspace.rowconfigure(1, weight=1)
            self.display_frame.grid(row=0, column=0, sticky="ew", pady=(10, 0))
            self.controls_frame.grid(row=1, column=0, sticky="nsew")
            if self.scientific_visible:
                self.scientific_frame.pack(fill="x", padx=18, pady=(0, 6))
            self.buttons_frame.pack(fill="both", expand=True, padx=18, pady=(0, 18))
            self.orientation_button.configure(text="横型にする")
        else:
            self.geometry("1050x560" if self.scientific_visible else "760x460")
            self.minsize(680, 420)
            self.workspace.columnconfigure(0, weight=2)
            self.workspace.columnconfigure(1, weight=3)
            self.workspace.rowconfigure(0, weight=1)
            self.display_frame.grid(row=0, column=0, sticky="nsew", padx=(14, 0), pady=10)
            self.controls_frame.grid(row=0, column=1, sticky="nsew")
            if self.scientific_visible:
                self.scientific_frame.pack(side="left", fill="both", expand=True, padx=(12, 4), pady=(8, 18))
                self.buttons_frame.pack(side="left", fill="both", expand=True, padx=(4, 18), pady=(8, 18))
            else:
                self.buttons_frame.pack(fill="both", expand=True, padx=18, pady=(8, 18))
            self.orientation_button.configure(text="縦型にする")

    def _handle_key(self, event):
        if event.keysym in {"Return", "KP_Enter"}:
            self._press("equals")
        elif event.keysym == "BackSpace":
            self._press("backspace")
        elif event.keysym == "Escape":
            self._press("clear")
        elif event.char in "0123456789.+-*/%()":
            self._press(event.char)

    def _show_history(self):
        window = tk.Toplevel(self)
        window.title("計算履歴")
        window.geometry("340x420")
        window.configure(bg="#171816")
        tk.Label(window, text="計算履歴", bg="#171816", fg="white", font=("Segoe UI", 20, "bold")).pack(anchor="w", padx=20, pady=20)
        if not self.history:
            tk.Label(window, text="まだ履歴はありません", bg="#171816", fg="#888").pack(pady=60)
        for expression, answer in self.history:
            row = tk.Frame(window, bg="#252622")
            row.pack(fill="x", padx=20, pady=3)
            tk.Label(row, text=expression, bg="#252622", fg="#999", font=("Consolas", 10)).pack(anchor="e", padx=12, pady=(8, 0))
            tk.Label(row, text=f"= {answer}", bg="#252622", fg="white", font=("Segoe UI", 15, "bold")).pack(anchor="e", padx=12, pady=(0, 8))


if __name__ == "__main__":
    CalculatorApp().mainloop()
