import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk, font as tkfont
import os


class Chat:
    def __init__(self, client):
        if not client:
            raise ValueError("Client must be provided.")
        self.client = client
        self.root = tk.Tk()
        self.root.title("Semantic Document Search Engine")

        # set styles and build UI
        self._set_styles()
        self._build_ui()

    def _set_styles(self):
        # some other colors
        self.bg_color = "#2C2F33"
        self.user_bg = "#7289DA"
        self.bot_bg = "#99AAB5"
        self.text_color = "#FFFFFF"
        self.text_input_bg = "#40444B"
        self.text_input_fg = "#FFFFFF"
        self.text_input_cursor = "#FFFFFF"
        self.chat_font = tkfont.Font(family="Firago", size=12)

        style = ttk.Style()
        style.theme_use("clam")  # better customization support

        # Overall chat container
        style.configure("ChatContainer.TFrame", background=self.bg_color)

        # Modern button
        style.configure("Modern.TButton",
            background="#3A3F44",
            foreground="#FFFFFF",
            padding=8,
            relief="flat",
            borderwidth=0,
            focusthickness=0,
            font=self.chat_font
        )
        style.map("Modern.TButton",
            background=[("active", "#4E545B")],
            foreground=[("disabled", "#888888")]
        )


    def _build_ui(self):
        # apply colors
        self.root.configure(bg=self.bg_color)
        # Fixed window size
        self.root.geometry("1080x600")
        self.root.resizable(False, False)
        self.root.option_add("*Font", self.chat_font)
        # on close event
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        container = ttk.Frame(self.root, style="ChatContainer.TFrame")
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 0))

        self.canvas = tk.Canvas(container, bg=self.bg_color, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.chat_body = tk.Frame(self.canvas, bg=self.bg_color)
        self.chat_window = self.canvas.create_window((0, 0), window=self.chat_body, anchor='nw')
        self.canvas.bind('<Configure>', lambda e: self.canvas.itemconfig(self.chat_window, width=e.width))
        self.chat_body.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox('all')))

        # Controls frame — using pack with side=LEFT, then fixed width for send_btn
        controls = ttk.Frame(self.root)
        controls.pack(fill=tk.X, padx=10, pady=10)

        upload_btn = ttk.Button(controls, text="📁", command=self.upload_file, style="Modern.TButton")
        upload_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.query_input = tk.Text(controls, height=1, wrap="word", font=self.chat_font)
        self.query_input.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.query_input.bind("<KeyRelease>", self._resize_textbox)
        self.query_input.bind("<Shift-Return>", self._allow_newline)
        self.query_input.bind("<Return>", self._on_enter_pressed)
        self.query_input.configure(
            bg=self.text_input_bg,
            fg=self.text_input_fg,
            insertbackground=self.text_input_cursor,
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground="#555555",
            padx=10,
            pady=6
        )

        # Submit (Send) button with fixed width
        send_btn = ttk.Button(controls, text="➤", command=self.submit_query, style="Modern.TButton")
        send_btn.pack(side=tk.RIGHT, padx=(5, 0))

    def _on_close(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.root.destroy()
        self.client.close(False)

    def _resize_textbox(self, event=None):
        lines = int(self.query_input.index('end-1c').split('.')[0])
        self.query_input.configure(height=min(max(1, lines), 6))

    def _allow_newline(self, event):
        self.query_input.insert(tk.INSERT, "\n")
        return "break"

    def _on_enter_pressed(self, event):
        self.submit_query()
        return "break"

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


    def upload_file(self):
        file_path = filedialog.askopenfilename(
            title="Select files",
            filetypes=[
                ("All Supported", "*.pdf *.txt *.csv"),
                ("PDF", "*.pdf"),
                ("Text", "*.txt"),
                ("CSV", "*.csv"),
                ("All", "*.*")
            ]
        )
        if not file_path: return
        self.client.upload_file(file_path)
        self._add_message(f"Successfully uploaded {os.path.basename(file_path)}", sender="bot")

    def submit_query(self):
        query = self.query_input.get("1.0", tk.END).strip()
        if not self.client.files:
            messagebox.showerror("Error", "Please upload a file first.")
            return
        if not query:
            return

        self.query_input.delete("1.0", tk.END)
        self._add_message(query, sender="user")
        self._resize_textbox()
        # display the answer
        answer = self.client.ask(query)
        self._add_message(answer, sender="bot")


    def _add_message(self, message, sender="bot"):
        anchor = 'w' if sender=="bot" else 'e'
        # Bubble label with increased width to fill space
        bubble = tk.Label(
            self.chat_body,
            text=message,
            wraplength=520,
            justify=tk.LEFT,
            font=self.chat_font,
            fg=self.text_color,
            bg=self.bot_bg if sender=="bot" else self.user_bg,
            padx=10,
            pady=5,
            bd=0
        )
        bubble.pack(anchor=anchor, pady=5, padx=5)
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1.0)

    def run(self): self.root.mainloop()


