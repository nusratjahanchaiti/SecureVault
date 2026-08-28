# pip install customtkinter
# pip install cryptography
# pip install pyperclip

import os
import customtkinter as ctk
import pyperclip
import tkinter.filedialog
import tkinter.messagebox as messagebox
import logging
from cryptography.fernet import Fernet


log_file = 'encryption_logs.log'
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='[%m/%d/%Y %I:%M:%S %p]'
)


ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

COLOR_BG = "#f3f3f3"         
COLOR_SIDEBAR = "#ffffff"     
COLOR_CARD = "#ffffff"       
COLOR_BORDER = "#d9d9d9"    
COLOR_TEXT = "#1a1a1a"
COLOR_SUBTEXT = "#6e6e6e"
COLOR_ACCENT = "#2563eb"     
COLOR_ACCENT_HOVER = "#1d4ed8"
COLOR_GREEN = "#16a34a"
COLOR_GREEN_HOVER = "#15803d"
COLOR_RED = "#dc2626"
COLOR_RED_HOVER = "#b91c1c"
COLOR_NAV_ACTIVE = "#e8f0fe"
COLOR_NAV_HOVER = "#f0f0f0"

FONT_FAMILY = "Segoe UI"


class FileEncryptorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("SecureVault")
        self.geometry("820x620")
        self.minsize(720, 560)
        self.configure(fg_color=COLOR_BG)

        # Layout: sidebar (left) + content (right)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = Sidebar(self, controller=self)
        self.sidebar.grid(row=0, column=0, sticky="nsw")

        self.content_container = ctk.CTkFrame(self, fg_color=COLOR_BG)
        self.content_container.grid(row=0, column=1, sticky="nsew")
        self.content_container.grid_rowconfigure(0, weight=1)
        self.content_container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for PageClass in (HomePage, EncryptPage, DecryptPage):
            page_name = PageClass.__name__
            frame = PageClass(parent=self.content_container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("HomePage")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()
        if hasattr(frame, "on_show"):
            frame.on_show()
        self.sidebar.set_active(page_name)


class Sidebar(ctk.CTkFrame):
    """Left-hand navigation rail, like a typical desktop utility app."""

    def __init__(self, parent, controller):
        super().__init__(parent, width=200, fg_color=COLOR_SIDEBAR,
                          corner_radius=0, border_width=1, border_color=COLOR_BORDER)
        self.controller = controller
        self.grid_propagate(False)

        # App name
        name_label = ctk.CTkLabel(
            self, text="SecureVault",
            font=(FONT_FAMILY, 16, "bold"),
            text_color=COLOR_TEXT,
            anchor="w"
        )
        name_label.pack(fill="x", padx=20, pady=(24, 2))

        tagline = ctk.CTkLabel(
            self, text="File encryption utility",
            font=(FONT_FAMILY, 11),
            text_color=COLOR_SUBTEXT,
            anchor="w"
        )
        tagline.pack(fill="x", padx=20, pady=(0, 24))

        # Nav buttons
        self.nav_buttons = {}
        self.nav_buttons["HomePage"] = self._make_nav_button("Home", "HomePage")
        self.nav_buttons["EncryptPage"] = self._make_nav_button("Encrypt", "EncryptPage")
        self.nav_buttons["DecryptPage"] = self._make_nav_button("Decrypt", "DecryptPage")

        # Spacer
        spacer = ctk.CTkFrame(self, fg_color="transparent")
        spacer.pack(fill="both", expand=True)

        # Bottom utility buttons
        divider = ctk.CTkFrame(self, height=1, fg_color=COLOR_BORDER)
        divider.pack(fill="x", padx=20, pady=(0, 12))

        logs_button = ctk.CTkButton(
            self, text="View logs",
            command=self.show_logs,
            font=(FONT_FAMILY, 12),
            fg_color="transparent",
            text_color=COLOR_TEXT,
            hover_color=COLOR_NAV_HOVER,
            anchor="w",
            corner_radius=4,
            height=32
        )
        logs_button.pack(fill="x", padx=12, pady=2)

        clear_button = ctk.CTkButton(
            self, text="Clear logs",
            command=self.delete_logs,
            font=(FONT_FAMILY, 12),
            fg_color="transparent",
            text_color=COLOR_TEXT,
            hover_color=COLOR_NAV_HOVER,
            anchor="w",
            corner_radius=4,
            height=32
        )
        clear_button.pack(fill="x", padx=12, pady=2)

        exit_button = ctk.CTkButton(
            self, text="Exit",
            command=self.exit_app,
            font=(FONT_FAMILY, 12),
            fg_color="transparent",
            text_color=COLOR_RED,
            hover_color=COLOR_NAV_HOVER,
            anchor="w",
            corner_radius=4,
            height=32
        )
        exit_button.pack(fill="x", padx=12, pady=(2, 16))

    def _make_nav_button(self, text, page_name):
        btn = ctk.CTkButton(
            self, text=text,
            command=lambda: self.controller.show_frame(page_name),
            font=(FONT_FAMILY, 13),
            fg_color="transparent",
            text_color=COLOR_TEXT,
            hover_color=COLOR_NAV_HOVER,
            anchor="w",
            corner_radius=4,
            height=36
        )
        btn.pack(fill="x", padx=12, pady=2)
        return btn

    def set_active(self, page_name):
        for name, btn in self.nav_buttons.items():
            if name == page_name:
                btn.configure(fg_color=COLOR_NAV_ACTIVE, text_color=COLOR_ACCENT,
                               font=(FONT_FAMILY, 13, "bold"))
            else:
                btn.configure(fg_color="transparent", text_color=COLOR_TEXT,
                               font=(FONT_FAMILY, 13, "normal"))

    def show_logs(self):
        try:
            if os.path.exists(log_file):
                os.system(f'notepad {log_file}' if os.name == 'nt' else f'open {log_file}')
            else:
                messagebox.showinfo("Info", "No logs found yet")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open logs: {str(e)}")

    def delete_logs(self):
        try:
            if messagebox.askyesno("Confirm", "Are you sure you want to clear all logs?"):
                with open(log_file, 'w') as log:
                    log.write('')
                messagebox.showinfo("Success", "Logs cleared successfully")
                logging.info("Logs have been cleared")
        except Exception as e:
            messagebox.showerror("Error", f"Could not clear logs: {str(e)}")

    def exit_app(self):
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            logging.info("Application closed")
            self.controller.destroy()



class Card(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(
            parent, fg_color=COLOR_CARD, corner_radius=6,
            border_width=1, border_color=COLOR_BORDER, **kwargs
        )


class HomePage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=COLOR_BG)
        self.controller = controller

        header = ctk.CTkLabel(
            self, text="Welcome to SecureVault",
            font=(FONT_FAMILY, 22, "bold"),
            text_color=COLOR_TEXT, anchor="w"
        )
        header.pack(fill="x", padx=36, pady=(36, 4))

        sub = ctk.CTkLabel(
            self, text="Choose an action below to encrypt or decrypt a file.",
            font=(FONT_FAMILY, 13),
            text_color=COLOR_SUBTEXT, anchor="w"
        )
        sub.pack(fill="x", padx=36, pady=(0, 24))

        cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        cards_frame.pack(fill="x", padx=36)
        cards_frame.grid_columnconfigure(0, weight=1)
        cards_frame.grid_columnconfigure(1, weight=1)

        encrypt_card = self._build_action_card(
            cards_frame, "Encrypt a file",
            "Protect a file with a generated or existing key.",
            "Encrypt File", COLOR_GREEN, COLOR_GREEN_HOVER,
            lambda: controller.show_frame("EncryptPage")
        )
        encrypt_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        decrypt_card = self._build_action_card(
            cards_frame, "Decrypt a file",
            "Restore an encrypted file using its key.",
            "Decrypt File", COLOR_ACCENT, COLOR_ACCENT_HOVER,
            lambda: controller.show_frame("DecryptPage")
        )
        decrypt_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        # Recent activity card
        activity_card = Card(self)
        activity_card.pack(fill="both", expand=True, padx=36, pady=(24, 36))

        activity_title = ctk.CTkLabel(
            activity_card, text="Recent activity",
            font=(FONT_FAMILY, 13, "bold"),
            text_color=COLOR_TEXT, anchor="w"
        )
        activity_title.pack(fill="x", padx=18, pady=(16, 8))

        self.activity_text = ctk.CTkTextbox(
            activity_card, font=(FONT_FAMILY, 11),
            fg_color=COLOR_CARD, text_color=COLOR_SUBTEXT,
            border_width=0, wrap="word"
        )
        self.activity_text.pack(fill="both", expand=True, padx=18, pady=(0, 16))
        self.activity_text.configure(state="disabled")

    def _build_action_card(self, parent, title, desc, button_text, color, hover, command):
        card = Card(parent)

        title_label = ctk.CTkLabel(
            card, text=title, font=(FONT_FAMILY, 15, "bold"),
            text_color=COLOR_TEXT, anchor="w"
        )
        title_label.pack(fill="x", padx=18, pady=(18, 4))

        desc_label = ctk.CTkLabel(
            card, text=desc, font=(FONT_FAMILY, 11),
            text_color=COLOR_SUBTEXT, anchor="w", justify="left", wraplength=260
        )
        desc_label.pack(fill="x", padx=18, pady=(0, 16))

        action_button = ctk.CTkButton(
            card, text=button_text, command=command,
            font=(FONT_FAMILY, 12, "bold"),
            fg_color=color, hover_color=hover,
            corner_radius=4, height=36
        )
        action_button.pack(fill="x", padx=18, pady=(0, 18))

        return card

    def on_show(self):
        try:
            if os.path.exists(log_file):
                with open(log_file, "r") as f:
                    lines = f.readlines()[-8:]
                text = "".join(lines) if lines else "No activity yet."
            else:
                text = "No activity yet."
        except Exception:
            text = "No activity yet."

        self.activity_text.configure(state="normal")
        self.activity_text.delete("1.0", "end")
        self.activity_text.insert("1.0", text)
        self.activity_text.configure(state="disabled")


class BaseCryptoPage(ctk.CTkFrame):
    PAGE_TITLE = ""
    PAGE_DESC = ""
    ACTION_TEXT = ""
    ACTION_COLOR = COLOR_ACCENT
    ACTION_HOVER = COLOR_ACCENT_HOVER

    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=COLOR_BG)
        self.controller = controller

        header = ctk.CTkLabel(
            self, text=self.PAGE_TITLE,
            font=(FONT_FAMILY, 22, "bold"),
            text_color=COLOR_TEXT, anchor="w"
        )
        header.pack(fill="x", padx=36, pady=(36, 4))

        sub = ctk.CTkLabel(
            self, text=self.PAGE_DESC,
            font=(FONT_FAMILY, 13),
            text_color=COLOR_SUBTEXT, anchor="w"
        )
        sub.pack(fill="x", padx=36, pady=(0, 20))

        card = Card(self)
        card.pack(fill="both", expand=True, padx=36, pady=(0, 16))

        self.input_entry = self._build_field(card, "Input file", self.select_input_file, top_pad=20)
        self.output_entry = self._build_field(card, "Output file", self.select_output_file)

        # Key field
        key_label = ctk.CTkLabel(
            card, text="Encryption key", font=(FONT_FAMILY, 12, "bold"),
            text_color=COLOR_TEXT, anchor="w"
        )
        key_label.pack(fill="x", padx=18, pady=(16, 6))

        key_row = ctk.CTkFrame(card, fg_color="transparent")
        key_row.pack(fill="x", padx=18)

        self.key_entry = ctk.CTkEntry(
            key_row, placeholder_text="Paste a key, or generate one",
            font=(FONT_FAMILY, 12), height=36,
            fg_color="#ffffff", border_color=COLOR_BORDER, border_width=1,
            text_color=COLOR_TEXT, corner_radius=4
        )
        self.key_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        gen_button = ctk.CTkButton(
            key_row, text="Generate", command=self.gen_key,
            font=(FONT_FAMILY, 12), width=100, height=36,
            fg_color="#f0f0f0", hover_color="#e2e2e2",
            text_color=COLOR_TEXT, corner_radius=4,
            border_width=1, border_color=COLOR_BORDER
        )
        gen_button.pack(side="left")

        hint = ctk.CTkLabel(
            card, text="Use the same key to encrypt and decrypt a file.",
            font=(FONT_FAMILY, 10), text_color=COLOR_SUBTEXT, anchor="w"
        )
        hint.pack(fill="x", padx=18, pady=(8, 20))

        # Footer: status + action button
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(fill="x", padx=36, pady=(0, 36))

        self.message_label = ctk.CTkLabel(
            footer, text="", font=(FONT_FAMILY, 11),
            text_color=COLOR_SUBTEXT, anchor="w"
        )
        self.message_label.pack(side="left", fill="x", expand=True)

        action_button = ctk.CTkButton(
            footer, text=self.ACTION_TEXT, command=self.perform_action,
            font=(FONT_FAMILY, 13, "bold"),
            fg_color=self.ACTION_COLOR, hover_color=self.ACTION_HOVER,
            corner_radius=4, height=40, width=160
        )
        action_button.pack(side="right")

    def _build_field(self, parent, label_text, select_func, top_pad=16):
        label = ctk.CTkLabel(
            parent, text=label_text, font=(FONT_FAMILY, 12, "bold"),
            text_color=COLOR_TEXT, anchor="w"
        )
        label.pack(fill="x", padx=18, pady=(top_pad, 6))

        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=18)

        entry = ctk.CTkEntry(
            row, placeholder_text=f"No {label_text.lower()} selected",
            font=(FONT_FAMILY, 12), height=36,
            fg_color="#ffffff", border_color=COLOR_BORDER, border_width=1,
            text_color=COLOR_TEXT, corner_radius=4
        )
        entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        browse_button = ctk.CTkButton(
            row, text="Browse", command=select_func,
            font=(FONT_FAMILY, 12), width=100, height=36,
            fg_color="#f0f0f0", hover_color="#e2e2e2",
            text_color=COLOR_TEXT, corner_radius=4,
            border_width=1, border_color=COLOR_BORDER
        )
        browse_button.pack(side="left")

        return entry

    def gen_key(self):
        try:
            key = Fernet.generate_key()
            self.key_entry.delete(0, "end")
            self.key_entry.insert(0, key.decode())
            pyperclip.copy(key.decode())
            self.show_message("Key generated and copied to clipboard", COLOR_GREEN)
            logging.info("New encryption key generated successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate key: {str(e)}")
            logging.error(f"Key generation failed: {str(e)}")

    def select_input_file(self):
        filename = tkinter.filedialog.askopenfilename(title="Select File")
        if filename:
            self.input_entry.delete(0, "end")
            self.input_entry.insert(0, filename)
            self.show_message(f"Input set to {os.path.basename(filename)}", COLOR_SUBTEXT)

    def select_output_file(self):
        filename = tkinter.filedialog.asksaveasfilename(title="Save File As")
        if filename:
            self.output_entry.delete(0, "end")
            self.output_entry.insert(0, filename)
            self.show_message(f"Output set to {os.path.basename(filename)}", COLOR_SUBTEXT)

    def show_message(self, text, color):
        self.message_label.configure(text=text, text_color=color)

    def on_show(self):
        self.show_message("", COLOR_SUBTEXT)

    def perform_action(self):
        raise NotImplementedError


class EncryptPage(BaseCryptoPage):
    PAGE_TITLE = "Encrypt a file"
    PAGE_DESC = "Select a file and a key, then encrypt to create a protected copy."
    ACTION_TEXT = "Encrypt File"
    ACTION_COLOR = COLOR_GREEN
    ACTION_HOVER = COLOR_GREEN_HOVER

    def perform_action(self):
        input_file = self.input_entry.get()
        output_file = self.output_entry.get()
        file_key = self.key_entry.get()

        if not input_file or not output_file or not file_key:
            messagebox.showwarning("Missing Input", "Please fill in all fields")
            return

        if not os.path.exists(input_file):
            messagebox.showerror("File Error", f"Input file not found: {input_file}")
            return

        try:
            f = Fernet(file_key.encode() if isinstance(file_key, str) else file_key)

            with open(input_file, 'rb') as in_file:
                file_data = in_file.read()

            encrypted_data = f.encrypt(file_data)

            with open(output_file, 'wb') as out_file:
                out_file.write(encrypted_data)

            self.input_entry.delete(0, "end")
            self.output_entry.delete(0, "end")
            self.key_entry.delete(0, "end")

            input_filename = os.path.basename(input_file)
            output_filename = os.path.basename(output_file)
            logging.info(f"Encryption successful | Input: {input_filename} | Output: {output_filename}")

            messagebox.showinfo("Success", "File encrypted successfully")
            self.show_message("Encryption complete", COLOR_GREEN)

        except Exception as e:
            messagebox.showerror("Encryption Error", f"Failed to encrypt file:\n{str(e)}")
            logging.error(f"Encryption failed: {str(e)}")
            self.show_message("Encryption failed", COLOR_RED)


class DecryptPage(BaseCryptoPage):
    PAGE_TITLE = "Decrypt a file"
    PAGE_DESC = "Select an encrypted file and its key to restore the original."
    ACTION_TEXT = "Decrypt File"
    ACTION_COLOR = COLOR_ACCENT
    ACTION_HOVER = COLOR_ACCENT_HOVER

    def perform_action(self):
        input_file = self.input_entry.get()
        output_file = self.output_entry.get()
        file_key = self.key_entry.get()

        if not input_file or not output_file or not file_key:
            messagebox.showwarning("Missing Input", "Please fill in all fields")
            return

        if not os.path.exists(input_file):
            messagebox.showerror("File Error", f"Input file not found: {input_file}")
            return

        try:
            f = Fernet(file_key.encode() if isinstance(file_key, str) else file_key)

            with open(input_file, 'rb') as in_file:
                file_data = in_file.read()

            decrypted_data = f.decrypt(file_data)

            with open(output_file, 'wb') as out_file:
                out_file.write(decrypted_data)

            self.input_entry.delete(0, "end")
            self.output_entry.delete(0, "end")
            self.key_entry.delete(0, "end")

            input_filename = os.path.basename(input_file)
            output_filename = os.path.basename(output_file)
            logging.info(f"Decryption successful | Input: {input_filename} | Output: {output_filename}")

            messagebox.showinfo("Success", "File decrypted successfully")
            self.show_message("Decryption complete", COLOR_GREEN)

        except Exception as e:
            messagebox.showerror("Decryption Error", f"Failed to decrypt file:\n{str(e)}")
            logging.error(f"Decryption failed: {str(e)}")
            self.show_message("Decryption failed — wrong key or corrupted file", COLOR_RED)


if __name__ == "__main__":
    app = FileEncryptorApp()
    app.mainloop()