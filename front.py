import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk, font as tkfont
import os
import csv
from PyPDF2 import PdfReader

class ChatStyledFileQAApp:
    def __init__(self, root):
        self.root = root
        root.title("Chat Q&A Assistant")
        # Dark mode colors
        self.bg_color = "#2C2F33"
        self.user_bg = "#7289DA"
        self.bot_bg = "#99AAB5"
        self.text_color = "#FFFFFF"
        root.configure(bg=self.bg_color)
        # Fixed window size
        root.geometry("600x700")
        root.resizable(False, False)

        # Load custom font
        self.chat_font = tkfont.Font(family="Firago", size=12)
        self.root.option_add("*Font", self.chat_font)

        # Build UI
        self.file_paths = []
        self._build_ui()

    def _build_ui(self):
        # Chat messages area (scrollable)
        container = ttk.Frame(self.root)
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10,0))
        container.configure(style="ChatContainer.TFrame")

        self.canvas = tk.Canvas(container, bg=self.bg_color, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.chat_body = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.chat_body, anchor='nw')
        self.chat_body.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox('all')))

        # Controls frame
        controls = ttk.Frame(self.root)
        controls.pack(fill=tk.X, padx=10, pady=10)

        # Upload button
        upload_btn = ttk.Button(controls, text="📁", command=self.upload_files)
        upload_btn.pack(side=tk.LEFT, padx=(0,5))

        # Text widget for multiline growing input
        self.question_text = tk.Text(controls, height=1, wrap="word", font=self.chat_font)
        self.question_text.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.question_text.bind("<KeyRelease>", self._resize_textbox)
        self.question_text.bind("<Shift-Return>", self._allow_newline)
        self.question_text.bind("<Return>", self._on_enter_pressed)

        # Send button
        send_btn = ttk.Button(controls, text="➤", command=self.submit_question)
        send_btn.pack(side=tk.RIGHT, padx=(5,0))

    def _resize_textbox(self, event=None):
        text_widget = self.question_text
        lines = int(text_widget.index('end-1c').split('.')[0])
        text_widget.configure(height=min(max(1, lines), 6))

    def _allow_newline(self, event):
        self.question_text.insert(tk.INSERT, "\n")
        return "break"

    def _on_enter_pressed(self, event):
        self.submit_question()
        return "break"

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def upload_files(self):
        paths = filedialog.askopenfilenames(
            title="Select files",
            filetypes=[
                ("All Supported", "*.pdf *.txt *.csv"),
                ("PDF", "*.pdf"),
                ("Text", "*.txt"),
                ("CSV", "*.csv"),
                ("All", "*.*")
            ]
        )
        if paths:
            self.file_paths = list(paths)
            names = [os.path.basename(p) for p in self.file_paths]
            self._add_message(f"Uploaded files: {', '.join(names)}", sender="bot")

    def submit_question(self):
        question = self.question_text.get("1.0", tk.END).strip()
        if not self.file_paths:
            messagebox.showwarning("No Files", "Upload at least one file.")
            return
        if not question:
            return

        self._add_message(question, sender="user")
        self.question_text.delete("1.0", tk.END)
        self._resize_textbox()

        text = self.extract_text_from_files(self.file_paths)
        response = f"Extracted text preview:\n{text[:300]}..."
        self._add_message(response, sender="bot")

    def _add_message(self, message, sender="bot"):
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
        bubble.pack(anchor='w' if sender=="bot" else 'e', pady=5, padx=5)
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1.0)

    @staticmethod
    def extract_text_from_files(paths):
        all_text = ""
        for fp in paths:
            try:
                ext = os.path.splitext(fp)[1].lower()
                if ext == ".pdf":
                    reader = PdfReader(fp)
                    for page in reader.pages:
                        all_text += (page.extract_text() or "") + "\n"
                elif ext == ".txt":
                    with open(fp, 'r', encoding='utf-8') as f:
                        all_text += f.read() + "\n"
                elif ext == ".csv":
                    with open(fp, 'r', encoding='utf-8') as f:
                        for row in csv.reader(f):
                            all_text += ", ".join(row) + "\n"
                else:
                    all_text += f"Unsupported file type: {fp}\n"
            except Exception as e:
                all_text += f"Error reading {fp}: {e}\n"
        return all_text

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatStyledFileQAApp(root)
    root.mainloop()