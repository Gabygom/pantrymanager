import tkinter as tk
from tkinter import messagebox
import sqlite3

def connect_db():
    conn = sqlite3.connect("../sql/project1.db")
    return conn

def test_connection():
    try:
        conn = connect_db()
        conn.execute("SELECT 1")
        messagebox.showinfo("Success", "Database connected successfully!")
        conn.close()
    except Exception as e:
        messagebox.showerror("Error", "Failed to connect: {e}")

app = tk.Tk()
app.title("Fridge & Pantry Manager")
app.geometry("800x600")

test_button = tk.Button(app, text="Test DB Connection", command=test_connection)
test_button.pack(pady=20)

app.mainloop()
