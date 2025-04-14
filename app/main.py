import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
import sqlite3
from datetime import datetime

def connect_db():
    return sqlite3.connect("../sql/project1.db")

        
def fetch_inventory_grouped_by_location():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT l.location_id, l.location_name, i.name, inv.quantity, inv.expiration_date, inv.inventory_id
        FROM Locations l
        LEFT JOIN Inventory inv ON inv.location_id = l.location_id
        LEFT JOIN Items i ON inv.item_id = i.item_id
        ORDER BY l.location_name
    ''')
    
    rows = cursor.fetchall()
    conn.close()

    inventory_by_location = {}

    for loc_id, location, name, qty, exp_date, inv_id in rows:
        if location not in inventory_by_location:
            inventory_by_location[location] = []
        if name:
            inventory_by_location[location].append((name, qty, exp_date, inv_id))
            
    return inventory_by_location


#Add item
def open_add_item_window():
    add_window = tk.Toplevel(app)
    add_window.title("Add New Item")
    add_window.geometry("400x400")

    tk.Label(add_window, text="Item Name").pack()
    item_name_entry = tk.Entry(add_window)
    item_name_entry.pack()

    tk.Label(add_window, text="Category").pack()
    category_var = tk.StringVar()
    category_menu = ttk.Combobox(add_window, textvariable=category_var)
    category_menu.pack()

    tk.Label(add_window, text="Location").pack()
    location_var = tk.StringVar()
    location_menu = ttk.Combobox(add_window, textvariable=location_var)
    location_menu.pack()

    tk.Label(add_window, text="Quantity").pack()
    quantity_entry = tk.Entry(add_window)
    quantity_entry.pack()

    tk.Label(add_window, text="Expiration Date (YYYY-MM-DD)").pack()
    expiration_entry = tk.Entry(add_window)
    expiration_entry.pack()


    # Load categories and locations from DB
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT category_id, category_name FROM Categories")
    categories = cursor.fetchall()
    cursor.execute("SELECT location_id, location_name FROM Locations")
    locations = cursor.fetchall()
    conn.close()

    category_menu["values"] = [name for _, name in categories]
    location_menu["values"] = [name for _, name in locations]

    
    def submit_item():
        name = item_name_entry.get().strip()
        category_name = category_var.get()
        location_name = location_var.get()
        quantity = quantity_entry.get()
        expiration = expiration_entry.get()

        if not name or not category_name or not location_name or not quantity:
            messagebox.showwarning("Missing Data", "Please fill all required fields.")
            return

        try:
            quantity = int(quantity)
        except ValueError:
            messagebox.showerror("Invalid Quantity", "Quantity must be a number.")
            return

        # Get IDs from names
        category_id = next(cid for cid, cname in categories if cname == category_name)
        location_id = next(lid for lid, lname in locations if lname == location_name)

        conn = connect_db()
        cursor = conn.cursor()

        # Check if item already exists
        cursor.execute("SELECT item_id FROM Items WHERE name = ?", (name,))
        row = cursor.fetchone()
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if row:
            item_id = row[0]
        else:            
            cursor.execute("INSERT INTO Items (name, category_id, created_at) VALUES (?, ?, ?)", (name, category_id, now))
            item_id = cursor.lastrowid

        cursor.execute('''
            INSERT INTO Inventory (item_id, expiration_date, quantity, location_id, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (item_id, expiration or None, quantity, location_id, now))

        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Item added successfully!")
        add_window.destroy()
        display_inventory()
        canvas.yview_moveto(0)

    tk.Button(add_window, text="Add Item", command=submit_item).pack(pady=10)


# Load and show inventory
def display_inventory():
    for widget in scrollable_frame.winfo_children():
        widget.destroy()
    inventory_data = fetch_inventory_grouped_by_location()

    for location, items in inventory_data.items():
        frame = ttk.LabelFrame(scrollable_frame, text=location, padding=10)
        frame.pack(fill="x", padx=10, pady=5)

        tree = ttk.Treeview(frame, columns=("Item", "Quantity", "Expiration"), show="headings")
        tree.heading("Item", text="Item")
        tree.heading("Quantity", text="Quantity")
        tree.heading("Expiration", text="Expiration Date")
        tree.pack(fill="x")

        for item, qty, exp, inv_id in items:
           tree.insert("", "end", values=(item, qty, exp), tags=(str(inv_id),))

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=5)

        #Delete btn
        delete_btn = tk.Button(btn_frame, text="Delete Selected", command=lambda t=tree: delete_selected_item(t))
        delete_btn.pack(side="left", padx=5)

        #Edit Quantity btn
        edit_btn = tk.Button(btn_frame, text="Edit Quantity", command=lambda t=tree: edit_quantity(t))
        edit_btn.pack(side="left", padx=5)

#Delete an item from INVENTORY
def delete_selected_item(tree):
    selected = tree.selection()
    if not selected:
        return
    inv_id = tree.item(selected[0], "tags")[0]
    confirm = messagebox.askyesno("Delete", "Are you sure you want to delete this item?")
    if confirm:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Inventory WHERE inventory_id = ?", (inv_id,))
        conn.commit()
        conn.close()
        tree.delete(selected[0])
        messagebox.showinfo("Success", "Item deleted successfully!")
    else:
        messagebox.showwarning("No Selection", "No items deleted")

#Edit an item from INVENTORY
def edit_quantity(tree):
    selected_item = tree.selection()
    if selected_item:
        inv_id = tree.item(selected_item[0], 'tags')[0]
        old_qty = tree.item(selected_item[0], 'values')[1]

        # Prompt user to enter new quantity
        new_qty = simpledialog.askinteger("Edit Quantity", f"Enter new quantity for item (current: {old_qty}):", initialvalue=old_qty, minvalue=0)
        
        if new_qty is not None:
            conn = connect_db()
            cursor = conn.cursor()
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Update the quantity in the database
            cursor.execute("UPDATE Inventory SET quantity = ?, updated_at = ? WHERE inventory_id = ?", (new_qty, now, inv_id))
            conn.commit()
            conn.close()

            # Update the quantity in the Treeview
            tree.item(selected_item[0], values=(tree.item(selected_item[0], 'values')[0], new_qty, tree.item(selected_item[0], 'values')[2]))

            messagebox.showinfo("Success", "Quantity updated successfully!")
    else:
        messagebox.showwarning("No Selection", "Please select an item to edit.")
        
    
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

#Add item button
add_button = tk.Button(app, text="Add New Item", command=open_add_item_window)
add_button.pack(pady=10)

display_inventory()


app.mainloop()
