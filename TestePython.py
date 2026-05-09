# main.py
# SOCIAL GLOBAL CHAT - ETAPA 1 PREMIUM UI
# Login + Cadastro + Perfil + Chat + Visual Bonito

import tkinter as tk
from tkinter import messagebox
import sqlite3
from datetime import datetime

# =====================================
# CORES PREMIUM
# =====================================

BG = "#0F172A"          # fundo escuro
CARD = "#1E293B"        # cards
PRIMARY = "#3B82F6"     # azul neon
SECONDARY = "#8B5CF6"   # roxo neon
TEXT = "#F8FAFC"        # branco suave
MUTED = "#94A3B8"       # cinza suave
SUCCESS = "#22C55E"     # verde
DANGER = "#EF4444"      # vermelho

FONT_TITLE = ("Arial", 24, "bold")
FONT_NORMAL = ("Arial", 12)
FONT_BIG = ("Arial", 14, "bold")

# =====================================
# DATABASE
# =====================================

conn = sqlite3.connect("social_global_chat.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    bio TEXT,
    status TEXT,
    xp INTEGER,
    level INTEGER,
    created_at TEXT
)
""")

conn.commit()

# =====================================
# APP
# =====================================

current_user = None

root = tk.Tk()
root.title("Social Global Chat")
root.geometry("900x700")
root.configure(bg=BG)
root.resizable(False, False)

# =====================================
# HELPERS
# =====================================

def clear_screen():
    for widget in root.winfo_children():
        widget.destroy()


def create_title(text):
    tk.Label(
        root,
        text=text,
        font=FONT_TITLE,
        bg=BG,
        fg=TEXT
    ).pack(pady=20)


def create_button(text, command):
    return tk.Button(
        root,
        text=text,
        command=command,
        font=FONT_NORMAL,
        bg=PRIMARY,
        fg="white",
        activebackground=SECONDARY,
        activeforeground="white",
        relief="flat",
        width=22,
        height=2,
        cursor="hand2"
    )


def create_entry(show=None):
    return tk.Entry(
        root,
        font=FONT_NORMAL,
        bg=CARD,
        fg=TEXT,
        insertbackground=TEXT,
        relief="flat",
        width=35,
        show=show
    )


def create_label(text):
    tk.Label(
        root,
        text=text,
        font=FONT_NORMAL,
        bg=BG,
        fg=MUTED
    ).pack(pady=5)


# =====================================
# LOGIN
# =====================================

def login_screen():
    global current_user

    clear_screen()
    current_user = None

    create_title("SOCIAL GLOBAL CHAT")

    create_label("Nome de usuário")
    username_entry = create_entry()
    username_entry.pack(pady=5)

    create_label("Senha")
    password_entry = create_entry(show="*")
    password_entry.pack(pady=5)

    def login():
        global current_user

        username = username_entry.get().strip()
        password = password_entry.get().strip()

        cursor.execute("""
        SELECT id FROM users
        WHERE username = ? AND password = ?
        """, (username, password))

        user = cursor.fetchone()

        if user:
            current_user = user[0]
            messagebox.showinfo(
                "Login",
                f"Bem-vindo, {username}!"
            )
            profile_screen()
        else:
            messagebox.showerror(
                "Erro",
                "Usuário ou senha incorretos."
            )

    create_button("Entrar", login).pack(pady=20)
    create_button("Criar Conta", register_screen).pack()


# =====================================
# REGISTER
# =====================================

def register_screen():
    clear_screen()

    create_title("CRIAR CONTA")

    create_label("Nome de usuário")
    username_entry = create_entry()
    username_entry.pack()

    create_label("Senha")
    password_entry = create_entry(show="*")
    password_entry.pack()

    create_label("Biografia")
    bio_entry = create_entry()
    bio_entry.pack()

    create_label("Status")
    status_entry = create_entry()
    status_entry.pack()

    def register():
        username = username_entry.get().strip()
        password = password_entry.get().strip()
        bio = bio_entry.get().strip()
        status = status_entry.get().strip()

        if not username or not password:
            messagebox.showerror(
                "Erro",
                "Preencha usuário e senha."
            )
            return

        try:
            cursor.execute("""
            INSERT INTO users
            (username, password, bio, status, xp, level, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                username,
                password,
                bio,
                status,
                0,
                1,
                datetime.now().strftime("%d/%m/%Y %H:%M")
            ))

            conn.commit()

            messagebox.showinfo(
                "Sucesso",
                "Conta criada com sucesso!"
            )

            login_screen()

        except:
            messagebox.showerror(
                "Erro",
                "Esse usuário já existe."
            )

    create_button("Criar Conta", register).pack(pady=20)
    create_button("Voltar", login_screen).pack()


# =====================================
# PROFILE
# =====================================

def profile_screen():
    clear_screen()

    cursor.execute("""
    SELECT username, bio, status, xp, level, created_at
    FROM users
    WHERE id = ?
    """, (current_user,))

    user = cursor.fetchone()

    if not user:
        login_screen()
        return

    username, bio, status, xp, level, created_at = user

    create_title("MEU PERFIL")

    info = [
        f"Usuário: {username}",
        f"Bio: {bio}",
        f"Status: {status}",
        f"XP: {xp}",
        f"Nível: {level}",
        f"Criado em: {created_at}"
    ]

    for item in info:
        tk.Label(
            root,
            text=item,
            font=FONT_BIG,
            bg=BG,
            fg=TEXT
        ).pack(pady=6)

    def gain_xp():
        new_xp = xp + 50
        new_level = level

        if new_xp >= level * 100:
            new_level += 1

        cursor.execute("""
        UPDATE users
        SET xp = ?, level = ?
        WHERE id = ?
        """, (
            new_xp,
            new_level,
            current_user
        ))

        conn.commit()

        messagebox.showinfo(
            "XP",
            "Você ganhou 50 XP!"
        )

        profile_screen()

    create_button("Ganhar XP", gain_xp).pack(pady=15)
    create_button("Chat Global", chat_screen).pack(pady=10)
    create_button("Sair", login_screen).pack(pady=10)


# =====================================
# CHAT GLOBAL
# =====================================

chat_messages = []


def chat_screen():
    clear_screen()

    create_title("CHAT GLOBAL")

    chat_box = tk.Text(
        root,
        width=80,
        height=18,
        bg=CARD,
        fg=TEXT,
        font=FONT_NORMAL,
        relief="flat",
        state="disabled"
    )
    chat_box.pack(pady=10)

    message_entry = tk.Entry(
        root,
        width=60,
        font=FONT_NORMAL,
        bg=CARD,
        fg=TEXT,
        insertbackground=TEXT,
        relief="flat"
    )
    message_entry.pack(pady=10)

    def refresh_chat():
        chat_box.config(state="normal")
        chat_box.delete("1.0", tk.END)

        for msg in chat_messages:
            chat_box.insert(tk.END, msg + "\n")

        chat_box.config(state="disabled")

    def send_message():
        text = message_entry.get().strip()

        if not text:
            return

        cursor.execute("""
        SELECT username FROM users
        WHERE id = ?
        """, (current_user,))

        username = cursor.fetchone()[0]
        now = datetime.now().strftime("%H:%M")

        full_message = f"[{now}] {username}: {text}"
        chat_messages.append(full_message)

        message_entry.delete(0, tk.END)
        refresh_chat()

    create_button("Enviar", send_message).pack(pady=10)
    create_button("Voltar ao Perfil", profile_screen).pack()

    refresh_chat()


# =====================================
# START
# =====================================

login_screen()
root.mainloop()