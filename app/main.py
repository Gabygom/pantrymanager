import tkinter as tk
from tkinter import messagebox, ttk
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

def fetch_inventory(tree):
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT Inventory.inventory_id, Items.name, Categories.category_name, Inventory.quantity,
               Locations.location_name, Inventory.expiration_date
        FROM Inventory
        JOIN Items ON Inventory.item_id = Items.item_id
        JOIN Categories ON Items.category_id = Categories.category_id
        JOIN Locations ON Inventory.location_id = Locations.location_id
    """)
    
    rows = cursor.fetchall()
    conn.close()

    for item in tree.get_children():
        tree.delete(item)

    # Insert new data
    for row in rows:
        tree.insert("", "end", values=row)
        
app = tk.Tk()
app.title("Fridge & Pantry Manager")
app.geometry("800x600")

test_button = tk.Button(app, text="Test DB Connection", command=test_connection)
test_button.pack(pady=20)

columns = ("ID", "Item", "Category", "Quantity", "Location", "Expiration Date")
tree = ttk.Treeview(app, columns=columns, show="headings")

for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=100)

tree.pack(fill="both", expand=True)

load_button = tk.Button(app, text="Load Inventory", command=lambda: fetch_inventory(tree))
load_button.pack(pady=10)

app.mainloop()
