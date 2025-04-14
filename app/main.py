import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3

def connect_db():
    return sqlite3.connect("../sql/project1.db")

def fetch_inventory_grouped_by_location():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT l.location_id, l.location_name, i.name, inv.quantity, inv.expiration_date
        FROM Locations l
        LEFT JOIN Inventory inv ON inv.location_id = l.location_id
        LEFT JOIN Items i ON inv.item_id = i.item_id
        ORDER BY l.location_name
    ''')
    rows = cursor.fetchall()
    conn.close()

    inventory_by_location = {}
    for loc_id, location, name, qty, exp_date in rows:
        if location not in inventory_by_location:
            inventory_by_location[location] = []
        if name:
            inventory_by_location[location].append((name, qty, exp_date))
    return inventory_by_location


app = tk.Tk()
app.title("Fridge & Pantry Manager")
app.geometry("700x600")

# Scrollbar
container = ttk.Frame(app)
container.pack(fill="both", expand=True)

canvas = tk.Canvas(container)
scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
scrollable_frame = ttk.Frame(canvas)

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(
        scrollregion=canvas.bbox("all")
    )
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# Load and show inventory
inventory_data = fetch_inventory_grouped_by_location()

for location, items in inventory_data.items():
    frame = ttk.LabelFrame(scrollable_frame, text=location, padding=10)
    frame.pack(fill="x", padx=10, pady=5)

    tree = ttk.Treeview(frame, columns=("Item", "Quantity", "Expiration"), show="headings")
    tree.heading("Item", text="Item")
    tree.heading("Quantity", text="Quantity")
    tree.heading("Expiration", text="Expiration Date")
    tree.pack(fill="x")

    for item, qty, exp in items:
        tree.insert("", "end", values=(item, qty, exp))

app.mainloop()
